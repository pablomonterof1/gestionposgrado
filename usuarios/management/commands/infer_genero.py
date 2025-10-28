# usuarios/management/commands/infer_genero.py
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import User
from usuarios.models import PerfilUsuario
from programasposgrado.models import ProgramaPosgrado
from usuarios.models import PerfilUsuario
import csv
import os
import re

try:
    import gender_guesser.detector as gender_detector  # pip install gender-guesser
    HAS_GENDER_GUESSER = True
except Exception:
    HAS_GENDER_GUESSER = False

SPANISH_EXCEPTIONS = {
    # nombre en minúsculas -> 'M' / 'F'
    'andrea': 'F',   # en ES suele ser femenino
    'noa': None,     # ambivalente
    'cruz': None,
    'josé maría': 'M',
    'maría josé': 'F',
    'maria jose': 'F',
    'jose maria': 'M',
    'guadalupe': 'F',
    'trinidad': None,
    'angel': 'M',
    'ángel': 'M',
    'angela': 'F',
    'ángela': 'F',
}

def split_first_name(full_name: str) -> str:
    if not full_name:
        return ''
    # quita dobles espacios y tildes para el detector; conserva versión con tildes para excepciones
    first_token = full_name.strip().split()[0]
    return first_token

def normalize(s: str) -> str:
    import unicodedata
    if not s:
        return ''
    return ''.join(
        c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn'
    ).lower().strip()

def infer_from_rules(first_name_original: str):
    """
    Devuelve (sexo:'M'/'F'/None, confidence: float[0..1], metodo:str)
    """
    if not first_name_original:
        return (None, 0.0, 'empty')

    first = first_name_original.strip().lower()
    first_norm = normalize(first_name_original)

    # 1) Excepciones específicas
    if first in SPANISH_EXCEPTIONS:
        sex = SPANISH_EXCEPTIONS[first]
        return (sex, 0.95 if sex else 0.0, 'exception')

    # 2) Heurística simple por terminación
    if first_norm.endswith('o'):
        return ('M', 0.7, 'endswith_o')
    if first_norm.endswith('a'):
        return ('F', 0.7, 'endswith_a')

    # 3) Sin señal clara
    return (None, 0.0, 'unknown')

def infer_with_gender_guesser(first_name_original: str):
    # gender_guesser devuelve: 'male','female','mostly_male','mostly_female','andy','unknown'
    d = gender_detector.Detector(case_sensitive=False)
    res = d.get_gender(first_name_original or '')
    mapping = {
        'male': ('M', 0.9),
        'mostly_male': ('M', 0.75),
        'female': ('F', 0.9),
        'mostly_female': ('F', 0.75),
        'andy': (None, 0.0),
        'unknown': (None, 0.0),
    }
    sex, conf = mapping.get(res, (None, 0.0))
    return (sex, conf, f'gender_guesser:{res}')

class Command(BaseCommand):
    help = "Intenta inferir PerfilUsuario.sexo desde el nombre (sin pisar datos existentes)."

    def add_arguments(self, parser):
        parser.add_argument('--programa', type=int, nargs='*', help='IDs de ProgramaPosgrado a limitar.')
        parser.add_argument('--min-confidence', type=float, default=0.75, help='Umbral de confianza (0..1).')
        parser.add_argument('--dry-run', action='store_true', help='No guarda cambios, solo muestra.')
        parser.add_argument('--csv-out', type=str, default='genero_backfill.csv', help='Ruta CSV de cambios propuestos.')

    def handle(self, *args, **opts):
        programas_ids = opts.get('programa')
        min_conf = float(opts.get('min_confidence') or 0.75)
        dry_run = bool(opts.get('dry_run'))
        csv_out = opts.get('csv_out')

        # Universo de usuarios: todos los PerfilUsuario sin sexo
        qs = PerfilUsuario.objects.filter(sexo__isnull=True)

        # Si se limita por programa, filtra por usuarios matriculados al/los programa(s)
        if programas_ids:
            from django.contrib.contenttypes.models import ContentType
            from usuarios.models import MatriculaUsuario
            ctype = ContentType.objects.get_for_model(ProgramaPosgrado)
            user_ids = (MatriculaUsuario.objects
                        .filter(content_type=ctype, object_id__in=programas_ids, rol_en_programa='estudiante')
                        .values_list('usuario_id', flat=True)
                        .distinct())
            qs = qs.filter(user_id__in=list(user_ids))

        total = qs.count()
        self.stdout.write(self.style.NOTICE(f'Perfiles a evaluar: {total} (min_conf={min_conf}, dry_run={dry_run})'))

        rows = []
        updated = 0

        for perf in qs.select_related('user'):
            user = perf.user
            # Primero intenta con first_name; si viene vacío, usa el display del username como fallback
            first = split_first_name(user.first_name or user.get_full_name() or user.username)

            # 1) gender_guesser (si está disponible)
            sex, conf, method = (None, 0.0, 'none')
            if HAS_GENDER_GUESSER:
                sex, conf, method = infer_with_gender_guesser(first)

            # 2) Si no hay sexo confiable, heurística local
            if sex is None or conf < min_conf:
                sex2, conf2, m2 = infer_from_rules(first)
                # Escoge el de mayor confianza
                if (sex2 is not None and conf2 > conf):
                    sex, conf, method = sex2, conf2, m2

            # Registrar
            rows.append({
                'user_id': user.id,
                'username': user.username,
                'nombre': user.get_full_name(),
                'first_name': first,
                'inferred': sex or '',
                'confidence': conf,
                'method': method,
            })

            # Guardar si pasa el umbral
            if sex and conf >= min_conf and not dry_run:
                perf.sexo = sex
                perf.save(update_fields=['sexo'])
                updated += 1

        # CSV de respaldo
        if csv_out:
            path = os.path.abspath(csv_out)
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['user_id','username','nombre','first_name','inferred','confidence','method'])
                writer.writeheader()
                writer.writerows(rows)
            self.stdout.write(self.style.SUCCESS(f'CSV escrito en: {path}'))

        self.stdout.write(self.style.SUCCESS(f'Actualizados: {updated} / {total}'))
