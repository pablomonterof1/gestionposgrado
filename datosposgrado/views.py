from collections import Counter, defaultdict
from decimal import Decimal
from django.db.models import Value

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ContratosDocentes, ContratoTutor, ContratoCoordinador
from programasposgrado.models import ProgramaPosgrado, Maestrias, PeriodosAcademicos, Modalidad, Modulos, CampoAmplio
from programasposgrado.models import ProgramaPosgradoEM, EspecialidadesMedicas, ModulosEM
from usuarios.models import PerfilUsuario, PerfilAcademicoUsuario
from django.contrib.auth.models import User
from django.http import JsonResponse
from .forms import ContratosDocentesForm, ContratoTutorForm, ContratoCoordinadorForm
from django.contrib import messages
from main.decorators import role_required
from django.db import transaction
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.views.decorators.http import require_GET
from django.views.decorators.http import require_http_methods
from django.views.decorators.http import require_POST

# Create your views here.

@role_required([4, 7, 8])  
def periodosacademicosdp(request):
    periodosacademicos_list = PeriodosAcademicos.objects.all().order_by('-fecha_inicio')
    return render(request, 'periodosacademicos_dp.html', {
        'periodosacademicos_list': periodosacademicos_list,
    })

@role_required([4, 7, 8])
def datosposgrado(request, periodo_id):
    periodoacademico = PeriodosAcademicos.objects.get(id=periodo_id)
    return render(request, 'datosposgrado.html', {
        'periodo_id': periodo_id,
        'periodoacademico': periodoacademico,
    })


@role_required([4, 7, 8])
def contratosdocentes(request, periodo_id):
    # Periodo (solo para encabezado)
    periodoacademico = get_object_or_404(PeriodosAcademicos, id=periodo_id)

    # --- ContentTypes ---
    ct_prog_m  = ContentType.objects.get_for_model(ProgramaPosgrado)
    ct_prog_em = ContentType.objects.get_for_model(ProgramaPosgradoEM)
    ct_mod_m   = ContentType.objects.get_for_model(Modulos)
    ct_mod_em  = ContentType.objects.get_for_model(ModulosEM)

    # --- 1) IDs de programas del periodo (por cada modelo) ---
    prog_m_ids = list(
        ProgramaPosgrado.objects.filter(periodoacademico=periodo_id)
        .values_list('id', flat=True)
    )
    prog_em_ids = list(
        ProgramaPosgradoEM.objects.filter(periodoacademico=periodo_id)
        .values_list('id', flat=True)
    )

    # Si no hay programas en el periodo, devolver vacío rápido
    if not prog_m_ids and not prog_em_ids:
        return render(request, 'contratosdocentes.html', {
            'docentes_list': PerfilUsuario.objects.filter(rol__in=[2,5,7]).select_related('user'),
            'contratos_por_periordo': [],
            'periodo_id': periodo_id,
            'periodoacademico': periodoacademico,
        })

    # --- 2) Contratos del periodo (sin usar programa_tipo) ---
    contratos = list(
        ContratosDocentes.objects.filter(
            Q(programa_content_type=ct_prog_m,  programa_object_id__in=prog_m_ids) |
            Q(programa_content_type=ct_prog_em, programa_object_id__in=prog_em_ids)
        ).order_by('-created')
    )

    # --- 3) Batch: usuarios/docentes ---
    docente_user_ids = sorted({c.docente for c in contratos if c.docente})
    usuarios = {u.id: u for u in User.objects.filter(id__in=docente_user_ids).select_related('perfilusuario')}

    # --- 4) Batch: programas (M y EM) ---
    contrato_prog_m_ids = sorted({c.programa_object_id for c in contratos if c.programa_content_type_id == ct_prog_m.id})
    contrato_prog_em_ids = sorted({c.programa_object_id for c in contratos if c.programa_content_type_id == ct_prog_em.id})

    programas_m = {p.id: p for p in ProgramaPosgrado.objects.filter(id__in=contrato_prog_m_ids)}
    programas_em = {p.id: p for p in ProgramaPosgradoEM.objects.filter(id__in=contrato_prog_em_ids)}

    # --- 5) Batch: módulos (M y EM) ---
    contrato_mod_m_ids = sorted({c.modulo_object_id for c in contratos if c.modulo_content_type_id == ct_mod_m.id})
    contrato_mod_em_ids = sorted({c.modulo_object_id for c in contratos if c.modulo_content_type_id == ct_mod_em.id})

    modulos_m = {m.id: m for m in Modulos.objects.filter(id__in=contrato_mod_m_ids)}
    modulos_em = {m.id: m for m in ModulosEM.objects.filter(id__in=contrato_mod_em_ids)}

    # --- 6) Batch: catálogos de programa (modalidad, campo amplio, maestría/especialidad) ---
    maestria_ids = sorted({p.maestria for p in programas_m.values() if getattr(p, 'maestria', None)})
    especialidad_ids = sorted({p.especialidad for p in programas_em.values() if getattr(p, 'especialidad', None)})

    modalidad_ids = sorted({p.modalidad for p in list(programas_m.values()) + list(programas_em.values()) if getattr(p, 'modalidad', None)})
    campo_ids = sorted({p.campoamplio for p in list(programas_m.values()) + list(programas_em.values()) if getattr(p, 'campoamplio', None)})
    periodo_ids = sorted({p.periodoacademico for p in list(programas_m.values()) + list(programas_em.values()) if getattr(p, 'periodoacademico', None)})

    maestrias = {m.id: m for m in Maestrias.objects.filter(id__in=maestria_ids)}
    especialidades = {e.id: e for e in EspecialidadesMedicas.objects.filter(id__in=especialidad_ids)}
    modalidades = {m.id: m for m in Modalidad.objects.filter(id__in=modalidad_ids)}
    campos = {c.id: c for c in CampoAmplio.objects.filter(id__in=campo_ids)}
    periodos = {p.id: p for p in PeriodosAcademicos.objects.filter(id__in=periodo_ids)}

    # --- 7) “Anexar” objetos para el template (sin consultas extra) ---
    for c in contratos:
        # Docente
        c.docente_obj = usuarios.get(c.docente)

        # Programa
        if c.programa_content_type_id == ct_prog_m.id:
            prog = programas_m.get(c.programa_object_id)
            c.programadeposgrado_obj = prog
            c.maestria_obj = maestrias.get(getattr(prog, 'maestria', None)) if prog else None
        else:
            prog = programas_em.get(c.programa_object_id)
            c.programadeposgrado_obj = prog
            c.maestria_obj = especialidades.get(getattr(prog, 'especialidad', None)) if prog else None

        # Modalidad / Campo / Periodo (en ambos, si existen)
        c.modalidad_obj = modalidades.get(getattr(prog, 'modalidad', None)) if prog else None
        c.campoamplio_obj = campos.get(getattr(prog, 'campoamplio', None)) if prog else None
        c.periodoacademico_obj = periodos.get(getattr(prog, 'periodoacademico', None)) if prog else None

        # Módulo
        if c.modulo_content_type_id == ct_mod_m.id:
            c.modulo_obj = modulos_m.get(c.modulo_object_id)
        else:
            c.modulo_obj = modulos_em.get(c.modulo_object_id)
    

    docentes_list = PerfilUsuario.objects.filter(rol__in=[2,5,7])

    return render(request, 'contratosdocentes.html', {
        'docentes_list': docentes_list,
        'contratos_por_periordo': contratos,
        'periodo_id': periodo_id,
        'periodoacademico': periodoacademico,
    })

@role_required([4, 7, 8])
def contratotutor(request, periodo_id):
    # 1) ContentTypes
    ct_prog_m = ContentType.objects.get_for_model(ProgramaPosgrado)
    ct_prog_em = ContentType.objects.get_for_model(ProgramaPosgradoEM)

    # 2) Programas del periodo (IDs)
    prog_m_qs = ProgramaPosgrado.objects.filter(periodoacademico=periodo_id)
    prog_em_qs = ProgramaPosgradoEM.objects.filter(periodoacademico=periodo_id)

    prog_m_ids = list(prog_m_qs.values_list('id', flat=True))
    prog_em_ids = list(prog_em_qs.values_list('id', flat=True))

    # 3) Contratos del periodo (1 consulta)
    contratos = list(
        ContratoTutor.objects.filter(
            Q(programa_content_type=ct_prog_m, programa_object_id__in=prog_m_ids) |
            Q(programa_content_type=ct_prog_em, programa_object_id__in=prog_em_ids)
        ).order_by('-created')
    )

    # 4) Cargar usuarios en bloque (tutores y maestrantes)
    user_ids = set()
    for c in contratos:
        if c.tutor:
            user_ids.add(c.tutor)
        if c.maestrante:
            user_ids.add(c.maestrante)

    users_map = {u.id: u for u in User.objects.filter(id__in=user_ids)}

    # 5) Mapas de programas (en bloque)
    prog_m_map = {p.id: p for p in prog_m_qs}
    prog_em_map = {p.id: p for p in prog_em_qs}

    # 6) Catálogos en bloque (Maestrías/Especialidades, modalidad, campo, periodo)
    maestria_ids = set(p.maestria for p in prog_m_qs)
    especialidad_ids = set(p.especialidad for p in prog_em_qs)

    modalidad_ids = set(p.modalidad for p in prog_m_qs) | set(p.modalidad for p in prog_em_qs)
    campo_ids = set(p.campoamplio for p in prog_m_qs) | set(p.campoamplio for p in prog_em_qs)
    periodo_ids = set(p.periodoacademico for p in prog_m_qs) | set(p.periodoacademico for p in prog_em_qs)

    maestrias_map = {m.id: m for m in Maestrias.objects.filter(id__in=maestria_ids)}
    especialidades_map = {e.id: e for e in EspecialidadesMedicas.objects.filter(id__in=especialidad_ids)}

    modalidad_map = {m.id: m for m in Modalidad.objects.filter(id__in=modalidad_ids)}
    campo_map = {c.id: c for c in CampoAmplio.objects.filter(id__in=campo_ids)}
    periodos_map = {p.id: p for p in PeriodosAcademicos.objects.filter(id__in=periodo_ids)}

    # 7) Enriquecer objetos para el template (sin más queries)
    for c in contratos:
        c.tutor_obj = users_map.get(c.tutor)
        c.maestrante_obj = users_map.get(c.maestrante)

        c.programa_obj = None
        c.programa_nombre = None
        c.modalidad_obj = None
        c.campoamplio_obj = None
        c.periodoacademico_obj = None
        c.cohorte_label = None

        if c.programa_content_type_id == ct_prog_m.id:
            prog = prog_m_map.get(c.programa_object_id)
            c.programa_obj = prog
            if prog:
                c.programa_nombre = maestrias_map.get(prog.maestria)
                c.modalidad_obj = modalidad_map.get(prog.modalidad)
                c.campoamplio_obj = campo_map.get(prog.campoamplio)
                c.periodoacademico_obj = periodos_map.get(prog.periodoacademico)
                c.cohorte_label = prog.get_cohorte_display()

        elif c.programa_content_type_id == ct_prog_em.id:
            prog = prog_em_map.get(c.programa_object_id)
            c.programa_obj = prog
            if prog:
                c.programa_nombre = especialidades_map.get(prog.especialidad)
                c.modalidad_obj = modalidad_map.get(prog.modalidad)
                c.campoamplio_obj = campo_map.get(prog.campoamplio)
                c.periodoacademico_obj = periodos_map.get(prog.periodoacademico)
                c.cohorte_label = prog.get_cohorte_display()

    tutor_list = PerfilUsuario.objects.filter(rol__in=[5,2,7])
    periodoacademico = get_object_or_404(PeriodosAcademicos, id=periodo_id)

    return render(request, 'contratotutor.html', {
        'periodo_id': periodo_id,
        'tutor_list': tutor_list,
        'contratos_por_periordo': contratos,
        'periodoacademico': periodoacademico,
    })

@role_required([4, 7, 8])
def contratocoordinador(request, periodo_id):
    periodoacademico = get_object_or_404(PeriodosAcademicos, id=periodo_id)

    ct_pp = ContentType.objects.get_for_model(ProgramaPosgrado)
    ct_em = ContentType.objects.get_for_model(ProgramaPosgradoEM)

    programas_pp = list(ProgramaPosgrado.objects.filter(periodoacademico=periodo_id))
    programas_em = list(ProgramaPosgradoEM.objects.filter(periodoacademico=periodo_id))

    pp_ids = [p.id for p in programas_pp]
    em_ids = [p.id for p in programas_em]

    contratos = list(
        ContratoCoordinador.objects.filter(
            (Q(programa_content_type=ct_pp) & Q(programa_object_id__in=pp_ids)) |
            (Q(programa_content_type=ct_em) & Q(programa_object_id__in=em_ids))
        ).order_by('-created')
    )

    # maps para resolver objetos
    coordinador_ids = {c.coordinador for c in contratos if c.coordinador}
    users_map = {u.id: u for u in User.objects.filter(id__in=coordinador_ids)}

    pp_map = {p.id: p for p in programas_pp}
    em_map = {p.id: p for p in programas_em}

    maestrias_map = {m.id: m for m in Maestrias.objects.filter(id__in=[p.maestria for p in programas_pp])}
    especialidades_map = {e.id: e for e in EspecialidadesMedicas.objects.filter(id__in=[p.especialidad for p in programas_em])}

    modalidad_ids = {p.modalidad for p in programas_pp if p.modalidad} | {p.modalidad for p in programas_em if p.modalidad}
    campo_ids = {p.campoamplio for p in programas_pp if p.campoamplio} | {p.campoamplio for p in programas_em if p.campoamplio}
    periodo_ids = {p.periodoacademico for p in programas_pp if p.periodoacademico} | {p.periodoacademico for p in programas_em if p.periodoacademico}

    modalidad_map = {m.id: m for m in Modalidad.objects.filter(id__in=modalidad_ids)}
    campo_map = {c.id: c for c in CampoAmplio.objects.filter(id__in=campo_ids)}
    periodos_map = {p.id: p for p in PeriodosAcademicos.objects.filter(id__in=periodo_ids)}

    for c in contratos:
        c.coordinador_obj = users_map.get(c.coordinador)

        c.programa_obj = None
        c.nombre_programa = None
        c.modalidad_obj = None
        c.campoamplio_obj = None
        c.periodoacademico_obj = None
        c.cohorte_display = None

        if c.programa_content_type_id == ct_pp.id:
            prog = pp_map.get(c.programa_object_id)
            c.programa_obj = prog
            if prog:
                c.nombre_programa = maestrias_map.get(prog.maestria).nombre if maestrias_map.get(prog.maestria) else f"ID {prog.maestria}"
                c.modalidad_obj = modalidad_map.get(prog.modalidad)
                c.campoamplio_obj = campo_map.get(prog.campoamplio)
                c.periodoacademico_obj = periodos_map.get(prog.periodoacademico)
                c.cohorte_display = prog.get_cohorte_display()

        elif c.programa_content_type_id == ct_em.id:
            prog = em_map.get(c.programa_object_id)
            c.programa_obj = prog
            if prog:
                c.nombre_programa = especialidades_map.get(prog.especialidad).nombre if especialidades_map.get(prog.especialidad) else f"ID {prog.especialidad}"
                c.modalidad_obj = modalidad_map.get(prog.modalidad)
                c.campoamplio_obj = campo_map.get(prog.campoamplio)
                c.periodoacademico_obj = periodos_map.get(prog.periodoacademico)
                c.cohorte_display = prog.get_cohorte_display()

    coordinadores_list = PerfilUsuario.objects.filter(rol=3).select_related('user')

    return render(request, 'contratocoordinador.html', {
        'periodo_id': periodo_id,
        'periodoacademico': periodoacademico,
        'coordinadores_list': coordinadores_list,
        'contratos_por_periordo': contratos,
    })


@role_required([4, 7])
@transaction.atomic
def contratosdocentes_create(request, periodo_id):
    """
    Crea contrato docente con GenericForeignKey:
      - programa: ProgramaPosgrado o ProgramaPosgradoEM
      - modulo:   Modulos o ModulosEM

    POST espera:
      - docente (PerfilUsuario.id)
      - programa_mix: "PP-12" o "EM-5"
      - modulo_mix:   "M-33"  o "MEM-8"
      - docente_tipo (1/2)
    """

    # ---------------------------
    # Helpers (sin ifs repetidos)
    # ---------------------------
    PROGRAMA_MAP = {
        "PP": ProgramaPosgrado,
        "EM": ProgramaPosgradoEM,
    }
    MODULO_MAP = {
        "M": Modulos,
        "MEM": ModulosEM,
    }

    def parse_mix(mix_value: str, mapping: dict, label: str):
        """
        Convierte 'PP-12' -> (ModelClass, object_id int)
        """
        if not mix_value or "-" not in mix_value:
            raise ValueError(f"Seleccione un {label} válido.")
        pref, sid = mix_value.split("-", 1)
        if pref not in mapping:
            raise ValueError(f"Seleccione un {label} válido.")
        try:
            oid = int(sid)
        except ValueError:
            raise ValueError(f"Seleccione un {label} válido.")
        return mapping[pref], oid

    # ---------------------------
    # POST
    # ---------------------------
    if request.method == "POST":
        form = ContratosDocentesForm(request.POST)

        # campos que NO están en el ModelForm (porque son selects custom)
        docente_id = request.POST.get("docente")
        programa_mix = request.POST.get("programa_mix")
        modulo_mix = request.POST.get("modulo_mix")
        docente_tipo = int(request.POST.get("docente_tipo", 1))

        if not docente_id:
            messages.error(request, "Seleccione un docente.")
            return redirect("contratosdocentes_create", periodo_id=periodo_id)

        # validar lo del form (campos del contrato)
        if not form.is_valid():
            messages.error(request, "Corrija los errores del formulario.")
            # si quieres verlos en consola:
            # print(form.errors)
            return render(request, "contratosdocentes_create.html", _build_context_create(periodo_id, form))

        # docente
        docente = PerfilUsuario.objects.filter(id=docente_id).select_related("user").first()
        if not docente:
            messages.error(request, "El docente seleccionado no existe.")
            return redirect("contratosdocentes_create", periodo_id=periodo_id)

        # programa (GFK)
        try:
            ProgramaModel, programa_id = parse_mix(programa_mix, PROGRAMA_MAP, "programa")
        except ValueError as e:
            messages.error(request, str(e))
            return redirect("contratosdocentes_create", periodo_id=periodo_id)

        programa_obj = ProgramaModel.objects.filter(id=programa_id).first()
        if not programa_obj:
            messages.error(request, "El programa seleccionado no existe.")
            return redirect("contratosdocentes_create", periodo_id=periodo_id)

        # módulo (GFK)
        try:
            ModuloModel, modulo_id = parse_mix(modulo_mix, MODULO_MAP, "módulo")
        except ValueError as e:
            messages.error(request, str(e))
            return redirect("contratosdocentes_create", periodo_id=periodo_id)

        modulo_obj = ModuloModel.objects.filter(id=modulo_id).first()
        if not modulo_obj:
            messages.error(request, "El módulo seleccionado no existe.")
            return redirect("contratosdocentes_create", periodo_id=periodo_id)

        # guardar contrato (optimizado: usar form.save(commit=False))
        obj = form.save(commit=False)

        obj.docente = docente.user.id
        obj.docente_tipo = docente_tipo

        obj.programa_content_type = ContentType.objects.get_for_model(ProgramaModel)
        obj.programa_object_id = programa_obj.id

        obj.modulo_content_type = ContentType.objects.get_for_model(ModuloModel)
        obj.modulo_object_id = modulo_obj.id

        obj.save()

        messages.success(request, "Contrato creado correctamente.")
        return redirect("contratosdocentes", periodo_id=periodo_id)

    # ---------------------------
    # GET
    # ---------------------------
    form = ContratosDocentesForm()
    return render(request, "contratosdocentes_create.html", _build_context_create(periodo_id, form))


def _build_context_create(periodo_id, form):
    """
    Context del create (GET o POST con errores)
    Optimizado: pocas consultas y sin loops N+1 pesados.
    """
    docentes_list = PerfilUsuario.objects.filter(rol__in=[2,5,7]).select_related("user", "user__perfilusuario")

    programas_m = list(ProgramaPosgrado.objects.filter(periodoacademico=periodo_id))
    programas_em = list(ProgramaPosgradoEM.objects.filter(periodoacademico=periodo_id))

    # Resolver nombres sin N+1 (tus modelos guardan IDs como BigIntegerField)
    maestrias_map = {m.id: m for m in Maestrias.objects.filter(id__in=[p.maestria for p in programas_m])}
    espec_map = {e.id: e for e in EspecialidadesMedicas.objects.filter(id__in=[p.especialidad for p in programas_em])}
    periodos_map = {pa.id: pa for pa in PeriodosAcademicos.objects.filter(id=periodo_id)}

    for p in programas_m:
        p.maestria_obj = maestrias_map.get(p.maestria)
        p.periodo_obj = periodos_map.get(periodo_id)

    for p in programas_em:
        p.especialidad_obj = espec_map.get(p.especialidad)
        p.periodo_obj = periodos_map.get(periodo_id)

    periodoacademico = PeriodosAcademicos.objects.get(id=periodo_id)

    return {
        "docentes_list": docentes_list,
        "programas_m": programas_m,
        "programas_em": programas_em,
        "periodoacademico": periodoacademico,
        "modalidad_list": Modalidad.objects.all(),
        "maestrias_list": Maestrias.objects.all(),
        "periodo_id": periodo_id,
        "form": form,
    }


def build_programa_choices(periodo_id):
    # Programas del periodo (aquí periodoacademico es BigIntegerField)
    programas_pp = list(ProgramaPosgrado.objects.filter(periodoacademico=periodo_id))
    programas_em = list(ProgramaPosgradoEM.objects.filter(periodoacademico=periodo_id))

    # IDs a resolver
    pp_maestria_ids = {p.maestria for p in programas_pp}
    em_especialidad_ids = {p.especialidad for p in programas_em}

    # Periodo (uno solo, pero lo resolvemos seguro)
    periodo_nombre = (
        PeriodosAcademicos.objects.filter(id=periodo_id)
        .values_list('nombre', flat=True)
        .first()
        or f"ID {periodo_id}"
    )

    # Map Maestrias / Especialidades por id
    maestrias_map = {
        m.id: m.nombre
        for m in Maestrias.objects.filter(id__in=pp_maestria_ids).only('id', 'nombre')
    }
    especialidades_map = {
        e.id: e.nombre
        for e in EspecialidadesMedicas.objects.filter(id__in=em_especialidad_ids).only('id', 'nombre')
    }

    # Choices PP
    choices_pp = []
    for p in programas_pp:
        nombre = maestrias_map.get(p.maestria, f"ID {p.maestria}")
        p.nombre_programa = nombre  # por si lo usas en template
        choices_pp.append((f"PP-{p.id}", f"{periodo_nombre} - {nombre}"))

    # Choices EM
    choices_em = []
    for p in programas_em:
        nombre = especialidades_map.get(p.especialidad, f"ID {p.especialidad}")
        p.nombre_programa = nombre
        choices_em.append((f"EM-{p.id}", f"{periodo_nombre} - {nombre}"))

    # ✅ Estructura correcta para optgroups en Django ChoiceField
    programa_choices = [
        ("Maestrías", choices_pp),
        ("Especialidades Médicas", choices_em),
    ]

    return programa_choices, programas_pp, programas_em


@role_required([4, 7])
@transaction.atomic
def contratotutor_create(request, periodo_id):
    periodoacademico = get_object_or_404(PeriodosAcademicos, id=periodo_id)

    programa_choices, programas_pp, programas_em = build_programa_choices(periodo_id)

    if request.method == 'POST':
        form = ContratoTutorForm(request.POST, programa_choices=programa_choices)

        if form.is_valid():
            tutor_perfil = get_object_or_404(PerfilUsuario, id=request.POST.get('tutor'))
            maestrante_perfil = get_object_or_404(PerfilUsuario, id=request.POST.get('maestrante'))

            obj = form.save(commit=False)
            obj.tutor = tutor_perfil.user.id
            obj.maestrante = maestrante_perfil.user.id
            obj.save()

            messages.success(request, "Contrato de tutor creado correctamente.")
            return redirect('contratotutor', periodo_id=periodo_id)

        # debug
        print("=== FORM ERRORS (as_text) ===")
        print(form.errors.as_text())
        print("=== FORM ERRORS (json) ===")
        print(form.errors.get_json_data())

        messages.error(request, "Por favor corrija los errores del formulario.")

    else:
        form = ContratoTutorForm(programa_choices=programa_choices)

    tutor_list = PerfilUsuario.objects.filter(rol__in=[5,2,7]).select_related('user')
    maestrantes_list = PerfilUsuario.objects.select_related('user')

    return render(request, 'contratotutor_create.html', {
        'periodo_id': periodo_id,
        'periodoacademico': periodoacademico,
        'form': form,
        'tutor_list': tutor_list,
        'maestrantes_list': maestrantes_list,
        'programas_pp': programas_pp,
        'programas_em': programas_em,
    })

@role_required([4, 7])
@transaction.atomic
def contratocoordinador_create(request, periodo_id):
    """
    Crea contrato de coordinador con GFK:

    programa_mix:
      - "PP-<id>" => ProgramaPosgrado (Maestrías)
      - "EM-<id>" => ProgramaPosgradoEM (Especialidades)
    """

    periodoacademico = get_object_or_404(PeriodosAcademicos, id=periodo_id)

    # ✅ choices para que NO marque invalid_choice
    programa_choices, programas_pp, programas_em = build_programa_choices(periodo_id)

    if request.method == 'POST':
        form = ContratoCoordinadorForm(request.POST, programa_choices=programa_choices)

        if form.is_valid():
            coordinador_perfil = get_object_or_404(PerfilUsuario, id=request.POST.get('coordinador'))

            obj = form.save(commit=False)

            # ✅ tu modelo guarda coordinador como IntegerField (User.id)
            obj.coordinador = coordinador_perfil.user.id

            # ✅ programa_content_type + programa_object_id ya quedan seteados en el clean() del form
            obj.save()

            messages.success(request, "Contrato de coordinador creado correctamente.")
            return redirect('contratocoordinador', periodo_id=periodo_id)

        # debug
        print("=== FORM ERRORS (as_text) ===")
        print(form.errors.as_text())
        print("=== FORM ERRORS (json) ===")
        print(form.errors.get_json_data())

        messages.error(request, "Por favor corrija los errores del formulario.")

    else:
        form = ContratoCoordinadorForm(programa_choices=programa_choices)

    coordinadores_list = PerfilUsuario.objects.filter(rol=3).select_related('user')

    # Opcional: para mostrar nombres en el template (igual que tutores)
    maestrias_map = {m.id: m for m in Maestrias.objects.filter(id__in=[p.maestria for p in programas_pp])}
    especialidades_map = {e.id: e for e in EspecialidadesMedicas.objects.filter(id__in=[p.especialidad for p in programas_em])}

    for p in programas_pp:
        p.nombre_programa = maestrias_map.get(p.maestria).nombre if maestrias_map.get(p.maestria) else f"ID {p.maestria}"

    for p in programas_em:
        p.nombre_programa = especialidades_map.get(p.especialidad).nombre if especialidades_map.get(p.especialidad) else f"ID {p.especialidad}"

    return render(request, 'contratocoordinador_create.html', {
        'periodo_id': periodo_id,
        'periodoacademico': periodoacademico,
        'form': form,

        'coordinadores_list': coordinadores_list,
        'programas_pp': programas_pp,
        'programas_em': programas_em,
    })

@require_GET
@role_required([4, 7])
def obtener_modulos_por_programa(request, tipo, programa_id):


    if tipo == 'PP':
        programa = get_object_or_404(ProgramaPosgrado, id=programa_id)
        maestria_id = programa.maestria

        modulos_qs = Modulos.objects.filter(maestria=maestria_id).values('id', 'nombre')

        data = [
            {"id": m["id"], "nombre": m["nombre"], "mix": f"M-{m['id']}"}
            for m in modulos_qs
        ]
        return JsonResponse(data, safe=False)

    elif tipo == 'EM':
        programa = get_object_or_404(ProgramaPosgradoEM, id=programa_id)
        especialidad_id = programa.especialidad

        modulos_qs = ModulosEM.objects.filter(especialidad=especialidad_id).values('id', 'nombre')

        data = [
            {"id": m["id"], "nombre": m["nombre"], "mix": f"MEM-{m['id']}"}
            for m in modulos_qs
        ]
        return JsonResponse(data, safe=False)

    return JsonResponse({'error': 'Tipo no válido'}, status=400)




@role_required([4, 7, 8])
@require_http_methods(["GET", "POST"])
@transaction.atomic
def contratosdocentes_update(request, contratosdocentes_id, periodo_id):
    contratodocente = get_object_or_404(ContratosDocentes, id=contratosdocentes_id)
    periodoacademico = get_object_or_404(PeriodosAcademicos, id=periodo_id)

    # ---------------------------
    # Permisos / roles
    # 4 = edición
    # 7 = analista
    # 8 = técnico contratos (solo URL)
    # ---------------------------
    rol = None
    if hasattr(request.user, "perfilusuario"):
        rol = request.user.perfilusuario.rol

    tiene_permiso_edicion = request.user.is_superuser or rol == 4
    tiene_permiso_analista = request.user.is_superuser or rol == 7
    tiene_permiso_tecnico_contratos = request.user.is_superuser or rol == 8

    puede_editar_todo = tiene_permiso_edicion or tiene_permiso_analista

    # ContentTypes
    ct_prog_pp = ContentType.objects.get_for_model(ProgramaPosgrado)
    ct_prog_em = ContentType.objects.get_for_model(ProgramaPosgradoEM)
    ct_mod_m = ContentType.objects.get_for_model(Modulos)
    ct_mod_mem = ContentType.objects.get_for_model(ModulosEM)

    # ---------------------------
    # POST
    # ---------------------------
    if request.method == "POST":

        # =========================================================
        # CASO 1: Rol restringido (solo puede cambiar urldocumento)
        # =========================================================
        if not puede_editar_todo:
            urldocumento = (request.POST.get("urldocumento") or "").strip()
            contratodocente.urldocumento = urldocumento
            contratodocente.save(update_fields=["urldocumento"])

            messages.success(request, "URL del documento actualizada con éxito.")
            return redirect("contratosdocentes", periodo_id=periodo_id)

        # =========================================================
        # CASO 2: Usuario con permisos completos
        # =========================================================
        form = ContratosDocentesForm(request.POST, instance=contratodocente)

        docente_perfil_id = request.POST.get("docente")
        programa_mix = (request.POST.get("programa_mix") or "").strip()
        modulo_mix = (request.POST.get("modulo_mix") or "").strip()
        docente_tipo_raw = request.POST.get("docente_tipo", 1)

        try:
            docente_tipo = int(docente_tipo_raw)
        except (TypeError, ValueError):
            docente_tipo = 1

        if not docente_perfil_id:
            messages.error(request, "Seleccione un docente.")
            return redirect("contratosdocentes_update", contratosdocentes_id=contratosdocentes_id, periodo_id=periodo_id)

        if "-" not in programa_mix:
            messages.error(request, "Seleccione un programa válido.")
            return redirect("contratosdocentes_update", contratosdocentes_id=contratosdocentes_id, periodo_id=periodo_id)

        if "-" not in modulo_mix:
            messages.error(request, "Seleccione un módulo válido.")
            return redirect("contratosdocentes_update", contratosdocentes_id=contratosdocentes_id, periodo_id=periodo_id)

        if not form.is_valid():
            messages.error(request, "Por favor corrija los errores del formulario.")
        else:
            prog_tipo, prog_id = programa_mix.split("-", 1)   # PP / EM
            mod_tipo, mod_id = modulo_mix.split("-", 1)       # M / MEM

            try:
                prog_id = int(prog_id)
                mod_id = int(mod_id)
            except ValueError:
                messages.error(request, "Programa o módulo inválido.")
                return redirect("contratosdocentes_update", contratosdocentes_id=contratosdocentes_id, periodo_id=periodo_id)

            docente_perfil = get_object_or_404(PerfilUsuario, id=docente_perfil_id)

            # 1) Resolver programa
            if prog_tipo == "PP":
                programa_obj = get_object_or_404(
                    ProgramaPosgrado,
                    id=prog_id,
                    periodoacademico=periodo_id
                )
                programa_ct = ct_prog_pp
                docente_tipo = 1  # En PP siempre 1

            elif prog_tipo == "EM":
                programa_obj = get_object_or_404(
                    ProgramaPosgradoEM,
                    id=prog_id,
                    periodoacademico=periodo_id
                )
                programa_ct = ct_prog_em

                if docente_tipo not in (1, 2):
                    docente_tipo = 1
            else:
                messages.error(request, "Tipo de programa no válido.")
                return redirect("contratosdocentes_update", contratosdocentes_id=contratosdocentes_id, periodo_id=periodo_id)

            # 2) Validar coherencia módulo/programa
            if prog_tipo == "PP" and mod_tipo != "M":
                messages.error(request, "El tipo de módulo no corresponde al tipo de programa.")
                return redirect("contratosdocentes_update", contratosdocentes_id=contratosdocentes_id, periodo_id=periodo_id)

            if prog_tipo == "EM" and mod_tipo != "MEM":
                messages.error(request, "El tipo de módulo no corresponde al tipo de programa.")
                return redirect("contratosdocentes_update", contratosdocentes_id=contratosdocentes_id, periodo_id=periodo_id)

            # 3) Resolver módulo
            if mod_tipo == "M":
                modulo_obj = get_object_or_404(Modulos, id=mod_id)
                modulo_ct = ct_mod_m

                ok = Modulos.objects.filter(
                    id=mod_id,
                    maestria=programa_obj.maestria
                ).exists()

                if not ok:
                    messages.error(request, "El módulo seleccionado no pertenece a la maestría del programa.")
                    return redirect("contratosdocentes_update", contratosdocentes_id=contratosdocentes_id, periodo_id=periodo_id)

            elif mod_tipo == "MEM":
                modulo_obj = get_object_or_404(ModulosEM, id=mod_id)
                modulo_ct = ct_mod_mem

                ok = ModulosEM.objects.filter(
                    id=mod_id,
                    especialidad=programa_obj.especialidad
                ).exists()

                if not ok:
                    messages.error(request, "El módulo seleccionado no pertenece a la especialidad del programa.")
                    return redirect("contratosdocentes_update", contratosdocentes_id=contratosdocentes_id, periodo_id=periodo_id)

            else:
                messages.error(request, "Tipo de módulo no válido.")
                return redirect("contratosdocentes_update", contratosdocentes_id=contratosdocentes_id, periodo_id=periodo_id)

            # 4) Guardar
            contrato = form.save(commit=False)
            contrato.docente = docente_perfil.user.id
            contrato.docente_tipo = docente_tipo

            contrato.programa_content_type = programa_ct
            contrato.programa_object_id = programa_obj.id

            contrato.modulo_content_type = modulo_ct
            contrato.modulo_object_id = modulo_obj.id

            contrato.save()
            messages.success(request, "Contrato actualizado con éxito.")
            return redirect("contratosdocentes", periodo_id=periodo_id)

    else:
        form = ContratosDocentesForm(instance=contratodocente)

    # ---------------------------
    # Context (GET o POST con errores)
    # ---------------------------
    docentes_list = PerfilUsuario.objects.filter(rol__in=[2, 5, 7]).select_related("user", "user__perfilusuario")

    programas_pp = list(ProgramaPosgrado.objects.filter(periodoacademico=periodo_id))
    programas_em = list(ProgramaPosgradoEM.objects.filter(periodoacademico=periodo_id))

    pp_maestria_ids = {p.maestria for p in programas_pp if p.maestria}
    em_especialidad_ids = {p.especialidad for p in programas_em if p.especialidad}

    maestrias_map = {
        m.id: m
        for m in Maestrias.objects.filter(id__in=pp_maestria_ids).only("id", "nombre")
    }
    especialidades_map = {
        e.id: e
        for e in EspecialidadesMedicas.objects.filter(id__in=em_especialidad_ids).only("id", "nombre")
    }

    for p in programas_pp:
        p.maestria_obj = maestrias_map.get(p.maestria)
        p.periodo_obj = periodoacademico

    for p in programas_em:
        p.especialidad_obj = especialidades_map.get(p.especialidad)
        p.periodo_obj = periodoacademico

    docente_inicial = PerfilUsuario.objects.filter(user_id=contratodocente.docente).only("id").first()
    initial_docente_id = docente_inicial.id if docente_inicial else None

    initial_programa_tipo = ""
    initial_programa_id = None
    show_docente_tipo = False
    modulos_list = []

    if contratodocente.programa_content_type_id == ct_prog_pp.id:
        initial_programa_tipo = "PP"
        initial_programa_id = contratodocente.programa_object_id

        prog = next((x for x in programas_pp if x.id == initial_programa_id), None)
        if prog:
            mods = Modulos.objects.filter(maestria=prog.maestria).values("id", "nombre")
            modulos_list = [
                {"id": m["id"], "nombre": m["nombre"], "mix": f"M-{m['id']}"}
                for m in mods
            ]

    elif contratodocente.programa_content_type_id == ct_prog_em.id:
        initial_programa_tipo = "EM"
        initial_programa_id = contratodocente.programa_object_id
        show_docente_tipo = True

        prog = next((x for x in programas_em if x.id == initial_programa_id), None)
        if prog:
            mods = ModulosEM.objects.filter(especialidad=prog.especialidad).values("id", "nombre")
            modulos_list = [
                {"id": m["id"], "nombre": m["nombre"], "mix": f"MEM-{m['id']}"}
                for m in mods
            ]

    initial_programa_mix = (
        f"{initial_programa_tipo}-{initial_programa_id}"
        if initial_programa_tipo and initial_programa_id
        else ""
    )

    initial_modulo_mix = ""
    if contratodocente.modulo_content_type_id == ct_mod_m.id:
        initial_modulo_mix = f"M-{contratodocente.modulo_object_id}"
    elif contratodocente.modulo_content_type_id == ct_mod_mem.id:
        initial_modulo_mix = f"MEM-{contratodocente.modulo_object_id}"

    return render(request, "contratosdocentes_update.html", {
        "periodo_id": periodo_id,
        "periodoacademico": periodoacademico,
        "form": form,
        "contratodocente": contratodocente,

        "docentes_list": docentes_list,
        "programas_m": programas_pp,
        "programas_e": programas_em,

        "initial_docente_id": initial_docente_id,
        "initial_programa_mix": initial_programa_mix,
        "initial_programa_tipo": initial_programa_tipo,
        "initial_programa_id": initial_programa_id,
        "initial_modulo_mix": initial_modulo_mix,
        "modulos_list": modulos_list,

        "show_docente_tipo": show_docente_tipo,

        # No es obligatorio si ya usas context processor,
        # pero no molesta y deja el template consistente.
        "tiene_permiso_edicion": tiene_permiso_edicion,
        "tiene_permiso_analista": tiene_permiso_analista,
        "tiene_permiso_tecnico_contratos": tiene_permiso_tecnico_contratos,
    })


    
@role_required([4, 7, 8])
@transaction.atomic
def contratotutor_update(request, contratotutor_id, periodo_id):
    contratotutor = get_object_or_404(ContratoTutor, id=contratotutor_id)
    periodoacademico = get_object_or_404(PeriodosAcademicos, id=periodo_id)

    # ---------------------------
    # Permisos / roles
    # 4 = edición
    # 7 = analista
    # 8 = técnico contratos (solo URL)
    # ---------------------------
    rol = None
    if hasattr(request.user, 'perfilusuario'):
        rol = request.user.perfilusuario.rol

    tiene_permiso_edicion = request.user.is_superuser or rol == 4
    tiene_permiso_analista = request.user.is_superuser or rol == 7
    tiene_permiso_tecnico_contratos = request.user.is_superuser or rol == 8

    puede_editar_todo = tiene_permiso_edicion or tiene_permiso_analista

    # choices para que NO marque invalid_choice
    programa_choices, programas_pp, programas_em = build_programa_choices(periodo_id)

    # valor inicial del select programa_mix según GFK guardado
    initial_programa_mix = ""
    if contratotutor.programa_content_type_id and contratotutor.programa_object_id:
        ct_model = contratotutor.programa_content_type.model_class()
        if ct_model == ProgramaPosgrado:
            initial_programa_mix = f"PP-{contratotutor.programa_object_id}"
        elif ct_model == ProgramaPosgradoEM:
            initial_programa_mix = f"EM-{contratotutor.programa_object_id}"

    if request.method == 'POST':

        # =========================================================
        # CASO 1: Rol restringido (solo puede cambiar urldocumento)
        # =========================================================
        if not puede_editar_todo:
            urldocumento = (request.POST.get('urldocumento') or '').strip()
            contratotutor.urldocumento = urldocumento
            contratotutor.save(update_fields=['urldocumento'])

            messages.success(request, "URL del documento actualizada con éxito.")
            return redirect('contratotutor', periodo_id=periodo_id)

        # =========================================================
        # CASO 2: Usuario con permisos completos
        # =========================================================
        form = ContratoTutorForm(
            request.POST,
            instance=contratotutor,
            programa_choices=programa_choices
        )

        if form.is_valid():
            tutor_perfil = get_object_or_404(PerfilUsuario, id=request.POST.get('tutor'))
            maestrante_perfil = get_object_or_404(PerfilUsuario, id=request.POST.get('maestrante'))

            obj = form.save(commit=False)  # aquí ya viene seteado ct+obj_id desde el clean()
            obj.tutor = tutor_perfil.user.id
            obj.maestrante = maestrante_perfil.user.id
            obj.save()

            messages.success(request, "Contrato actualizado con éxito.")
            return redirect('contratotutor', periodo_id=periodo_id)

        print("=== FORM ERRORS (as_text) ===")
        print(form.errors.as_text())
        print("=== FORM ERRORS (json) ===")
        print(form.errors.get_json_data())

        messages.error(request, "Por favor corrija los errores del formulario.")

    else:
        form = ContratoTutorForm(
            instance=contratotutor,
            initial={'programa_mix': initial_programa_mix},
            programa_choices=programa_choices
        )

    tutor_list = PerfilUsuario.objects.filter(rol__in=[5, 2, 7]).select_related('user')
    maestrantes_list = PerfilUsuario.objects.select_related('user')

    # opcional (solo si usas nombre_programa en template)
    maestrias_map = {
        m.id: m for m in Maestrias.objects.filter(id__in=[p.maestria for p in programas_pp])
    }
    especialidades_map = {
        e.id: e for e in EspecialidadesMedicas.objects.filter(id__in=[p.especialidad for p in programas_em])
    }

    for p in programas_pp:
        p.nombre_programa = maestrias_map.get(p.maestria).nombre if maestrias_map.get(p.maestria) else f"ID {p.maestria}"

    for p in programas_em:
        p.nombre_programa = especialidades_map.get(p.especialidad).nombre if especialidades_map.get(p.especialidad) else f"ID {p.especialidad}"

    return render(request, 'contratotutor_update.html', {
        'periodo_id': periodo_id,
        'periodoacademico': periodoacademico,
        'form': form,
        'contratotutor': contratotutor,
        'tutor_list': tutor_list,
        'maestrantes_list': maestrantes_list,
        'programas_pp': programas_pp,
        'programas_em': programas_em,

        # no es indispensable si ya vienen por context processor,
        # pero ayuda a que el template quede consistente
        'tiene_permiso_edicion': tiene_permiso_edicion,
        'tiene_permiso_analista': tiene_permiso_analista,
        'tiene_permiso_tecnico_contratos': tiene_permiso_tecnico_contratos,
    })

@role_required([4, 7, 8])
@transaction.atomic
def contratocoordinador_update(request, contratocoordinador_id, periodo_id):
    contratocoordinador = get_object_or_404(ContratoCoordinador, id=contratocoordinador_id)
    periodoacademico = get_object_or_404(PeriodosAcademicos, id=periodo_id)

    # ---------------------------
    # Permisos / roles
    # 4 = edición
    # 7 = analista
    # 8 = técnico contratos (solo URL)
    # ---------------------------
    rol = None
    if hasattr(request.user, 'perfilusuario'):
        rol = request.user.perfilusuario.rol

    tiene_permiso_edicion = request.user.is_superuser or rol == 4
    tiene_permiso_analista = request.user.is_superuser or rol == 7
    tiene_permiso_tecnico_contratos = request.user.is_superuser or rol == 8

    puede_editar_todo = tiene_permiso_edicion or tiene_permiso_analista

    # ✅ choices para que NO marque invalid_choice
    programa_choices, programas_pp, programas_em = build_programa_choices(periodo_id)

    # ✅ valor inicial del select programa_mix según GFK guardado
    initial_programa_mix = ""
    if contratocoordinador.programa_content_type_id and contratocoordinador.programa_object_id:
        ct_model = contratocoordinador.programa_content_type.model_class()
        if ct_model == ProgramaPosgrado:
            initial_programa_mix = f"PP-{contratocoordinador.programa_object_id}"
        elif ct_model == ProgramaPosgradoEM:
            initial_programa_mix = f"EM-{contratocoordinador.programa_object_id}"

    if request.method == 'POST':

        # =========================================================
        # CASO 1: Rol restringido (solo puede cambiar urldocumento)
        # =========================================================
        if not puede_editar_todo:
            urldocumento = (request.POST.get('urldocumento') or '').strip()
            contratocoordinador.urldocumento = urldocumento
            contratocoordinador.save(update_fields=['urldocumento'])

            messages.success(request, "URL del documento actualizada con éxito.")
            return redirect('contratocoordinador', periodo_id=periodo_id)

        # =========================================================
        # CASO 2: Usuario con permisos completos
        # =========================================================
        form = ContratoCoordinadorForm(
            request.POST,
            instance=contratocoordinador,
            programa_choices=programa_choices
        )

        if form.is_valid():
            coordinador_perfil = get_object_or_404(PerfilUsuario, id=request.POST.get('coordinador'))

            obj = form.save(commit=False)  # ✅ aquí ya viene seteado ct+obj_id desde el clean()
            obj.coordinador = coordinador_perfil.user.id  # IntegerField => User.id
            obj.save()

            messages.success(request, "Contrato actualizado con éxito.")
            return redirect('contratocoordinador', periodo_id=periodo_id)

        # debug útil (opcional)
        print("=== FORM ERRORS (as_text) ===")
        print(form.errors.as_text())
        print("=== FORM ERRORS (json) ===")
        print(form.errors.get_json_data())

        messages.error(request, "Por favor corrija los errores del formulario.")

    else:
        form = ContratoCoordinadorForm(
            instance=contratocoordinador,
            initial={'programa_mix': initial_programa_mix},
            programa_choices=programa_choices
        )

    coordinadores_list = PerfilUsuario.objects.filter(rol=3).select_related('user')

    # ✅ si el template usa nombre_programa (como tutores), lo seteamos aquí
    maestrias_map = {
        m.id: m for m in Maestrias.objects.filter(id__in=[p.maestria for p in programas_pp])
    }
    especialidades_map = {
        e.id: e for e in EspecialidadesMedicas.objects.filter(id__in=[p.especialidad for p in programas_em])
    }

    for p in programas_pp:
        p.nombre_programa = maestrias_map.get(p.maestria).nombre if maestrias_map.get(p.maestria) else f"ID {p.maestria}"

    for p in programas_em:
        p.nombre_programa = especialidades_map.get(p.especialidad).nombre if especialidades_map.get(p.especialidad) else f"ID {p.especialidad}"

    return render(request, 'contratocoordinador_update.html', {
        'periodo_id': periodo_id,
        'periodoacademico': periodoacademico,
        'form': form,
        'contratocoordinador': contratocoordinador,
        'coordinadores_list': coordinadores_list,
        'programas_pp': programas_pp,
        'programas_em': programas_em,
        'initial_programa_mix': initial_programa_mix,

        # aunque ya venga por context processor, ayuda a mantener consistente el template
        'tiene_permiso_edicion': tiene_permiso_edicion,
        'tiene_permiso_analista': tiene_permiso_analista,
        'tiene_permiso_tecnico_contratos': tiene_permiso_tecnico_contratos,
    })

# =========================================================
# DELETE: CONTRATOS DOCENTES (valida periodo para PP y EM)
# =========================================================
@role_required([4, 7])
@require_POST
@transaction.atomic
def contratosdocentes_delete(request, contratosdocentes_id, periodo_id):
    ct_pp = ContentType.objects.get_for_model(ProgramaPosgrado)
    ct_em = ContentType.objects.get_for_model(ProgramaPosgradoEM)

    pp_ids = list(
        ProgramaPosgrado.objects.filter(periodoacademico=periodo_id)
        .values_list('id', flat=True)
    )
    em_ids = list(
        ProgramaPosgradoEM.objects.filter(periodoacademico=periodo_id)
        .values_list('id', flat=True)
    )

    # Si no hay programas en el periodo, no debería poder borrarse nada "de ese periodo"
    if not pp_ids and not em_ids:
        messages.error(request, "No existen programas en este período.")
        return redirect('contratosdocentes', periodo_id=periodo_id)

    contrato = get_object_or_404(
        ContratosDocentes,
        Q(id=contratosdocentes_id) & (
            Q(programa_content_type=ct_pp, programa_object_id__in=pp_ids) |
            Q(programa_content_type=ct_em, programa_object_id__in=em_ids)
        )
    )

    contrato.delete()
    messages.success(request, "Contrato eliminado con éxito.")
    return redirect('contratosdocentes', periodo_id=periodo_id)


# =========================================================
# DELETE: CONTRATO TUTOR (valida periodo para PP y EM)
# =========================================================
@role_required([4, 7])
@require_POST
@transaction.atomic
def contratotutor_delete(request, contratotutor_id, periodo_id):
    ct_pp = ContentType.objects.get_for_model(ProgramaPosgrado)
    ct_em = ContentType.objects.get_for_model(ProgramaPosgradoEM)

    pp_ids = list(
        ProgramaPosgrado.objects.filter(periodoacademico=periodo_id)
        .values_list('id', flat=True)
    )
    em_ids = list(
        ProgramaPosgradoEM.objects.filter(periodoacademico=periodo_id)
        .values_list('id', flat=True)
    )

    if not pp_ids and not em_ids:
        messages.error(request, "No existen programas en este período.")
        return redirect('contratotutor', periodo_id=periodo_id)

    contrato = get_object_or_404(
        ContratoTutor,
        Q(id=contratotutor_id) & (
            Q(programa_content_type=ct_pp, programa_object_id__in=pp_ids) |
            Q(programa_content_type=ct_em, programa_object_id__in=em_ids)
        )
    )

    contrato.delete()
    messages.success(request, "Contrato eliminado con éxito.")
    return redirect('contratotutor', periodo_id=periodo_id)


# =========================================================
# DELETE: CONTRATO COORDINADOR (valida periodo para PP y EM)
# =========================================================
@role_required([4, 7])
@require_POST
@transaction.atomic
def contratocoordinador_delete(request, contratocoordinador_id, periodo_id):
    ct_pp = ContentType.objects.get_for_model(ProgramaPosgrado)
    ct_em = ContentType.objects.get_for_model(ProgramaPosgradoEM)

    pp_ids = list(
        ProgramaPosgrado.objects.filter(periodoacademico=periodo_id)
        .values_list('id', flat=True)
    )
    em_ids = list(
        ProgramaPosgradoEM.objects.filter(periodoacademico=periodo_id)
        .values_list('id', flat=True)
    )

    if not pp_ids and not em_ids:
        messages.error(request, "No existen programas en este período.")
        return redirect('contratocoordinador', periodo_id=periodo_id)

    contrato = get_object_or_404(
        ContratoCoordinador,
        Q(id=contratocoordinador_id) & (
            Q(programa_content_type=ct_pp, programa_object_id__in=pp_ids) |
            Q(programa_content_type=ct_em, programa_object_id__in=em_ids)
        )
    )

    contrato.delete()
    messages.success(request, "Contrato eliminado con éxito.")
    return redirect('contratocoordinador', periodo_id=periodo_id)

##################################################################################
####################################REPORTES######################################
##################################################################################


#################################HELPERS########################################

def _safe_full_name(user):
    if not user:
        return "-"
    nombre = f"{user.last_name or ''} {user.first_name or ''}".strip()
    return nombre if nombre else (user.username or f"Usuario {user.id}")



def _get_user_cedula_map(user_ids):
    """
    Devuelve {user_id: ci} usando PerfilUsuario.ci.
    """
    if not user_ids:
        return {}

    qs = PerfilUsuario.objects.filter(
        user_id__in=user_ids
    ).values('user_id', 'ci')

    return {
        r['user_id']: (r.get('ci') or '')
        for r in qs
    }


def _build_program_catalogs_from_contracts(contratos_doc=None, contratos_tut=None, contratos_coord=None):
    """
    Carga en bloque todos los programas/módulos/catálogos usados en los contratos.
    Evita N+1.
    """
    contratos_doc = contratos_doc or []
    contratos_tut = contratos_tut or []
    contratos_coord = contratos_coord or []

    ct_prog_pp = ContentType.objects.get_for_model(ProgramaPosgrado)
    ct_prog_em = ContentType.objects.get_for_model(ProgramaPosgradoEM)
    ct_mod_m = ContentType.objects.get_for_model(Modulos)
    ct_mod_em = ContentType.objects.get_for_model(ModulosEM)

    programa_pp_ids = set()
    programa_em_ids = set()
    modulo_m_ids = set()
    modulo_em_ids = set()

    for c in contratos_doc:
        if c.programa_content_type_id == ct_prog_pp.id and c.programa_object_id:
            programa_pp_ids.add(c.programa_object_id)
        elif c.programa_content_type_id == ct_prog_em.id and c.programa_object_id:
            programa_em_ids.add(c.programa_object_id)

        if c.modulo_content_type_id == ct_mod_m.id and c.modulo_object_id:
            modulo_m_ids.add(c.modulo_object_id)
        elif c.modulo_content_type_id == ct_mod_em.id and c.modulo_object_id:
            modulo_em_ids.add(c.modulo_object_id)

    for c in contratos_tut:
        if c.programa_content_type_id == ct_prog_pp.id and c.programa_object_id:
            programa_pp_ids.add(c.programa_object_id)
        elif c.programa_content_type_id == ct_prog_em.id and c.programa_object_id:
            programa_em_ids.add(c.programa_object_id)

    for c in contratos_coord:
        if c.programa_content_type_id == ct_prog_pp.id and c.programa_object_id:
            programa_pp_ids.add(c.programa_object_id)
        elif c.programa_content_type_id == ct_prog_em.id and c.programa_object_id:
            programa_em_ids.add(c.programa_object_id)

    programas_pp = {
        p.id: p for p in ProgramaPosgrado.objects.filter(id__in=programa_pp_ids)
    }
    programas_em = {
        p.id: p for p in ProgramaPosgradoEM.objects.filter(id__in=programa_em_ids)
    }
    modulos_m = {
        m.id: m for m in Modulos.objects.filter(id__in=modulo_m_ids)
    }
    modulos_em = {
        m.id: m for m in ModulosEM.objects.filter(id__in=modulo_em_ids)
    }

    maestria_ids = {p.maestria for p in programas_pp.values() if getattr(p, 'maestria', None)}
    especialidad_ids = {p.especialidad for p in programas_em.values() if getattr(p, 'especialidad', None)}
    modalidad_ids = {
        p.modalidad for p in list(programas_pp.values()) + list(programas_em.values())
        if getattr(p, 'modalidad', None)
    }
    campo_ids = {
        p.campoamplio for p in list(programas_pp.values()) + list(programas_em.values())
        if getattr(p, 'campoamplio', None)
    }
    periodo_ids = {
        p.periodoacademico for p in list(programas_pp.values()) + list(programas_em.values())
        if getattr(p, 'periodoacademico', None)
    }

    maestrias = {m.id: m for m in Maestrias.objects.filter(id__in=maestria_ids)}
    especialidades = {e.id: e for e in EspecialidadesMedicas.objects.filter(id__in=especialidad_ids)}
    modalidades = {m.id: m for m in Modalidad.objects.filter(id__in=modalidad_ids)}
    campos = {c.id: c for c in CampoAmplio.objects.filter(id__in=campo_ids)}
    periodos = {p.id: p for p in PeriodosAcademicos.objects.filter(id__in=periodo_ids)}

    return {
        'ct_prog_pp': ct_prog_pp,
        'ct_prog_em': ct_prog_em,
        'ct_mod_m': ct_mod_m,
        'ct_mod_em': ct_mod_em,
        'programas_pp': programas_pp,
        'programas_em': programas_em,
        'modulos_m': modulos_m,
        'modulos_em': modulos_em,
        'maestrias': maestrias,
        'especialidades': especialidades,
        'modalidades': modalidades,
        'campos': campos,
        'periodos': periodos,
    }


def _resolve_programa_data(contrato, catalogs):
    """
    Devuelve información homogénea del programa para cualquier tipo de contrato.
    """
    ct_prog_pp = catalogs['ct_prog_pp']
    ct_prog_em = catalogs['ct_prog_em']

    programa = None
    programa_nombre = "-"
    modalidad_nombre = "-"
    campo_nombre = "-"
    periodo_nombre = "-"
    cohorte = "-"
    programa_tipo = "-"

    if contrato.programa_content_type_id == ct_prog_pp.id:
        programa = catalogs['programas_pp'].get(contrato.programa_object_id)
        programa_tipo = "Maestría"
        if programa:
            maestria = catalogs['maestrias'].get(programa.maestria)
            modalidad = catalogs['modalidades'].get(programa.modalidad)
            campo = catalogs['campos'].get(programa.campoamplio)
            periodo = catalogs['periodos'].get(programa.periodoacademico)

            programa_nombre = maestria.nombre if maestria else f"ID {programa.maestria}"
            modalidad_nombre = modalidad if modalidad else "-"
            campo_nombre = campo.nombre if campo else "-"
            periodo_nombre = periodo.nombre if periodo else "-"
            cohorte = programa.get_cohorte_display() if hasattr(programa, 'get_cohorte_display') else "-"

    elif contrato.programa_content_type_id == ct_prog_em.id:
        programa = catalogs['programas_em'].get(contrato.programa_object_id)
        programa_tipo = "Especialidad Médica"
        if programa:
            especialidad = catalogs['especialidades'].get(programa.especialidad)
            modalidad = catalogs['modalidades'].get(programa.modalidad)
            campo = catalogs['campos'].get(programa.campoamplio)
            periodo = catalogs['periodos'].get(programa.periodoacademico)

            programa_nombre = especialidad.nombre if especialidad else f"ID {programa.especialidad}"
            modalidad_nombre = modalidad if modalidad else "-"
            campo_nombre = campo.nombre if campo else "-"
            periodo_nombre = periodo.nombre if periodo else "-"
            cohorte = programa.get_cohorte_display() if hasattr(programa, 'get_cohorte_display') else "-"

    return {
        'programa': programa,
        'programa_nombre': programa_nombre,
        'programa_tipo': programa_tipo,
        'modalidad_nombre': modalidad_nombre,
        'campo_nombre': campo_nombre,
        'periodo_nombre': periodo_nombre,
        'cohorte': cohorte,
    }


def _resolve_modulo_data(contrato, catalogs):
    """
    Solo aplica a contratos docentes.
    """
    ct_mod_m = catalogs['ct_mod_m']
    ct_mod_em = catalogs['ct_mod_em']

    if getattr(contrato, 'modulo_content_type_id', None) == ct_mod_m.id:
        mod = catalogs['modulos_m'].get(contrato.modulo_object_id)
        return mod.nombre if mod else "-"

    if getattr(contrato, 'modulo_content_type_id', None) == ct_mod_em.id:
        mod = catalogs['modulos_em'].get(contrato.modulo_object_id)
        return mod.nombre if mod else "-"

    return "-"


def _build_person_contract_rows(user_id):
    """
    Unifica el historial completo de una persona en una sola lista.
    """
    contratos_doc = list(
        ContratosDocentes.objects.filter(docente=user_id).only(
            'id', 'docente', 'docente_tipo', 'programa_content_type', 'programa_object_id',
            'modulo_content_type', 'modulo_object_id', 'horasacademicas', 'valorxhora',
            'numerocontrato', 'certificacionpresupuestaria', 'fechacertificacionpresupuestaria',
            'plazo', 'numeromemorandotthh', 'adenda', 'observaciones', 'urldocumento', 'created'
        )
    )

    contratos_tut = list(
        ContratoTutor.objects.filter(
            Q(tutor=user_id) | Q(maestrante=user_id)
        ).only(
            'id', 'tutor', 'maestrante', 'programa_content_type', 'programa_object_id',
            'plazo', 'certificacionpresupuestaria', 'fechacertificacionpresupuestaria',
            'valorcontrato', 'numerocontrato', 'numeromemorandotthh',
            'adenda', 'observaciones', 'urldocumento', 'created'
        )
    )

    contratos_coord = list(
        ContratoCoordinador.objects.filter(coordinador=user_id).only(
            'id', 'coordinador', 'programa_content_type', 'programa_object_id',
            'certificacionpresupuestaria', 'fechacertificacionpresupuestaria',
            'plazo', 'fechainicio', 'fechafin', 'honorario',
            'numerocontrato', 'cargo', 'noactasseleccion',
            'oficioentregadoporth', 'modalidadcontractuar',
            'observaciones', 'urldocumento', 'created'
        )
    )

    catalogs = _build_program_catalogs_from_contracts(contratos_doc, contratos_tut, contratos_coord)

    filas = []

    for c in contratos_doc:
        prog = _resolve_programa_data(c, catalogs)
        modulo_nombre = _resolve_modulo_data(c, catalogs)
        total_valor = (c.horasacademicas or 0) * (c.valorxhora or Decimal('0.00'))

        filas.append({
            'tipo_contrato': 'Docente',
            'rol_en_contrato': 'Docente',
            'contrato_id': c.id,
            'created': c.created,
            'numerocontrato': c.numerocontrato,
            'programa_nombre': prog['programa_nombre'],
            'programa_tipo': prog['programa_tipo'],
            'periodo_nombre': prog['periodo_nombre'],
            'modalidad_nombre': prog['modalidad_nombre'],
            'campo_nombre': prog['campo_nombre'],
            'cohorte': prog['cohorte'],
            'modulo_nombre': modulo_nombre,
            'valor': total_valor,
            'urldocumento': c.urldocumento,
            'observaciones': c.observaciones,
        })

    for c in contratos_tut:
        prog = _resolve_programa_data(c, catalogs)
        rol_en_contrato = 'Tutor' if c.tutor == user_id else 'Maestrante'

        filas.append({
            'tipo_contrato': 'Tutoría',
            'rol_en_contrato': rol_en_contrato,
            'contrato_id': c.id,
            'created': c.created,
            'numerocontrato': c.numerocontrato,
            'programa_nombre': prog['programa_nombre'],
            'programa_tipo': prog['programa_tipo'],
            'periodo_nombre': prog['periodo_nombre'],
            'modalidad_nombre': prog['modalidad_nombre'],
            'campo_nombre': prog['campo_nombre'],
            'cohorte': prog['cohorte'],
            'modulo_nombre': '-',
            'valor': c.valorcontrato,
            'urldocumento': c.urldocumento,
            'observaciones': c.observaciones,
        })

    for c in contratos_coord:
        prog = _resolve_programa_data(c, catalogs)

        filas.append({
            'tipo_contrato': 'Coordinación',
            'rol_en_contrato': 'Coordinador',
            'contrato_id': c.id,
            'created': c.created,
            'numerocontrato': c.numerocontrato,
            'programa_nombre': prog['programa_nombre'],
            'programa_tipo': prog['programa_tipo'],
            'periodo_nombre': prog['periodo_nombre'],
            'modalidad_nombre': prog['modalidad_nombre'],
            'campo_nombre': prog['campo_nombre'],
            'cohorte': prog['cohorte'],
            'modulo_nombre': '-',
            'valor': c.honorario,
            'urldocumento': c.urldocumento,
            'observaciones': c.observaciones,
        })

    filas.sort(key=lambda x: x['created'], reverse=True)
    return filas


def _get_global_contract_summary():
    """
    Resumen global optimizado sin traer objetos completos.
    """
    docentes_ids = list(ContratosDocentes.objects.values_list('docente', flat=True))
    tutores_ids = list(ContratoTutor.objects.values_list('tutor', flat=True))
    maestrantes_ids = list(ContratoTutor.objects.values_list('maestrante', flat=True))
    coordinadores_ids = list(ContratoCoordinador.objects.values_list('coordinador', flat=True))

    contratos_doc_count = len(docentes_ids)
    contratos_tut_count = ContratoTutor.objects.count()
    contratos_coord_count = len(coordinadores_ids)

    todos_ids = docentes_ids + tutores_ids + maestrantes_ids + coordinadores_ids
    user_counter = Counter(todos_ids)

    return {
        'contratos_docentes': contratos_doc_count,
        'contratos_tutores': contratos_tut_count,
        'contratos_coordinadores': contratos_coord_count,
        'contratos_total': contratos_doc_count + contratos_tut_count + contratos_coord_count,
        'personas_unicas': len(user_counter),
        'personas_multiples': sum(1 for _, n in user_counter.items() if n > 1),
        'top_ids': [uid for uid, _ in user_counter.most_common(15)],
        'counter': user_counter,
    }

def _build_role_counters():
    """
    Devuelve contadores por usuario para cada tipo de participación.
    Hace pocas consultas y luego todo queda en memoria.
    """
    docentes_ids = list(ContratosDocentes.objects.values_list('docente', flat=True))
    tutores_ids = list(ContratoTutor.objects.values_list('tutor', flat=True))
    maestrantes_ids = list(ContratoTutor.objects.values_list('maestrante', flat=True))
    coordinadores_ids = list(ContratoCoordinador.objects.values_list('coordinador', flat=True))

    return {
        'docente': Counter(docentes_ids),
        'tutor': Counter(tutores_ids),
        'maestrante': Counter(maestrantes_ids),
        'coordinador': Counter(coordinadores_ids),
    }

#################################HELPERS########################################
#################################VIEWS########################################

@role_required([4, 7, 8])
def dashboard_contrataciones_general(request):
    q = (request.GET.get('q') or '').strip()

    resumen = _get_global_contract_summary()
    counter = resumen['counter']
    top_ids = resumen['top_ids']
    role_counters = _build_role_counters()
    doc_counter = role_counters['docente']
    tut_counter = role_counters['tutor']
    mae_counter = role_counters['maestrante']
    coord_counter = role_counters['coordinador']

    # usuarios top
    users_map = {
        u.id: u
        for u in User.objects.filter(id__in=top_ids).select_related('perfilusuario')
    }
    cedulas_map = _get_user_cedula_map(top_ids)

    top_personas = []
    for uid in top_ids:
        user = users_map.get(uid)
        if not user:
            continue

        top_personas.append({
            'user_id': uid,
            'nombre': _safe_full_name(user),
            'cedula': cedulas_map.get(uid, ''),
            'total': counter.get(uid, 0),
            'como_docente': doc_counter.get(uid, 0),
            'como_tutor': tut_counter.get(uid, 0),
            'como_maestrante': mae_counter.get(uid, 0),
            'como_coordinador': coord_counter.get(uid, 0),
        })

    resultados_busqueda = []

    if q:
        user_ids_posibles = set()

        # búsqueda por nombre / username / email
        users_qs = User.objects.filter(
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(username__icontains=q) |
            Q(email__icontains=q)
        ).values_list('id', flat=True)
        user_ids_posibles.update(users_qs)

        # búsqueda por cédula (PerfilUsuario.ci)
        ids = PerfilUsuario.objects.filter(
            ci__icontains=q
        ).values_list('user_id', flat=True)

        user_ids_posibles.update(ids)

        user_ids_posibles = list(user_ids_posibles)

        users_found = {
            u.id: u for u in User.objects.filter(id__in=user_ids_posibles)
        }
        cedulas_found = _get_user_cedula_map(user_ids_posibles)

        for uid in user_ids_posibles:
            total_doc = doc_counter.get(uid, 0)
            total_tut = tut_counter.get(uid, 0)
            total_mae = mae_counter.get(uid, 0)
            total_coord = coord_counter.get(uid, 0)

            total = total_doc + total_tut + total_mae + total_coord
            if total == 0:
                continue

            user = users_found.get(uid)
            if not user:
                continue

            resultados_busqueda.append({
                'user_id': uid,
                'nombre': _safe_full_name(user),
                'cedula': cedulas_found.get(uid, ''),
                'total': total,
                'como_docente': total_doc,
                'como_tutor': total_tut,
                'como_maestrante': total_mae,
                'como_coordinador': total_coord,
            })

        resultados_busqueda.sort(key=lambda x: (-x['total'], x['nombre']))

    # contratos recientes
    doc_recientes = list(
        ContratosDocentes.objects.order_by('-created').only(
            'id', 'docente', 'numerocontrato', 'created'
        )[:8]
    )
    tut_recientes = list(
        ContratoTutor.objects.order_by('-created').only(
            'id', 'tutor', 'maestrante', 'numerocontrato', 'created'
        )[:8]
    )
    coord_recientes = list(
        ContratoCoordinador.objects.order_by('-created').only(
            'id', 'coordinador', 'numerocontrato', 'created'
        )[:8]
    )

    recientes_ids = set()
    for c in doc_recientes:
        if c.docente:
            recientes_ids.add(c.docente)
    for c in tut_recientes:
        if c.tutor:
            recientes_ids.add(c.tutor)
        if c.maestrante:
            recientes_ids.add(c.maestrante)
    for c in coord_recientes:
        if c.coordinador:
            recientes_ids.add(c.coordinador)

    recientes_users = {u.id: u for u in User.objects.filter(id__in=recientes_ids)}

    recientes = []
    for c in doc_recientes:
        recientes.append({
            'tipo': 'Docente',
            'persona': _safe_full_name(recientes_users.get(c.docente)),
            'numerocontrato': c.numerocontrato,
            'created': c.created,
        })
    for c in tut_recientes:
        recientes.append({
            'tipo': 'Tutoría',
            'persona': _safe_full_name(recientes_users.get(c.tutor)),
            'numerocontrato': c.numerocontrato,
            'created': c.created,
        })
    for c in coord_recientes:
        recientes.append({
            'tipo': 'Coordinación',
            'persona': _safe_full_name(recientes_users.get(c.coordinador)),
            'numerocontrato': c.numerocontrato,
            'created': c.created,
        })

    recientes.sort(key=lambda x: x['created'], reverse=True)
    recientes = recientes[:12]

    return render(request, 'dashboard_contrataciones_general.html', {
        'resumen': resumen,
        'top_personas': top_personas,
        'resultados_busqueda': resultados_busqueda,
        'q': q,
        'recientes': recientes,
    })

@role_required([4, 7, 8])
def detalle_contrataciones_persona(request, user_id):
    user = get_object_or_404(User, id=user_id)
    filas = _build_person_contract_rows(user_id)

    cedulas_map = _get_user_cedula_map([user_id])
    cedula = cedulas_map.get(user_id, '')

    total_docente = sum(1 for f in filas if f['tipo_contrato'] == 'Docente')
    total_tutoria = sum(1 for f in filas if f['tipo_contrato'] == 'Tutoría')
    total_coordinacion = sum(1 for f in filas if f['tipo_contrato'] == 'Coordinación')

    periodos = sorted({f['periodo_nombre'] for f in filas if f['periodo_nombre'] and f['periodo_nombre'] != '-'})
    programas = sorted({f['programa_nombre'] for f in filas if f['programa_nombre'] and f['programa_nombre'] != '-'})

    total_valor = Decimal('0.00')
    for f in filas:
        if f['valor']:
            total_valor += Decimal(f['valor'])

    return render(request, 'detalle_contrataciones_persona.html', {
        'persona': user,
        'nombre_completo': _safe_full_name(user),
        'cedula': cedula,
        'filas': filas,
        'total_general': len(filas),
        'total_docente': total_docente,
        'total_tutoria': total_tutoria,
        'total_coordinacion': total_coordinacion,
        'periodos_distintos': len(periodos),
        'programas_distintos': len(programas),
        'total_valor': total_valor,
    })
#################################VIEWS########################################


