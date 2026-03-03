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

@role_required([4, 7])  # Solo editores y analistas
def periodosacademicosdp(request):
    periodosacademicos_list = PeriodosAcademicos.objects.all().order_by('-fecha_inicio')
    return render(request, 'periodosacademicos_dp.html', {
        'periodosacademicos_list': periodosacademicos_list,
    })

@role_required([4, 7])
def datosposgrado(request, periodo_id):
    periodoacademico = PeriodosAcademicos.objects.get(id=periodo_id)
    return render(request, 'datosposgrado.html', {
        'periodo_id': periodo_id,
        'periodoacademico': periodoacademico,
    })


@role_required([4, 7])
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
            'docentes_list': PerfilUsuario.objects.filter(rol__in=[2,5]).select_related('user'),
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
    

    docentes_list = PerfilUsuario.objects.filter(rol__in=[2,5])

    return render(request, 'contratosdocentes.html', {
        'docentes_list': docentes_list,
        'contratos_por_periordo': contratos,
        'periodo_id': periodo_id,
        'periodoacademico': periodoacademico,
    })

@role_required([4, 7])
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

    tutor_list = PerfilUsuario.objects.filter(rol__in=[5,2])
    periodoacademico = get_object_or_404(PeriodosAcademicos, id=periodo_id)

    return render(request, 'contratotutor.html', {
        'periodo_id': periodo_id,
        'tutor_list': tutor_list,
        'contratos_por_periordo': contratos,
        'periodoacademico': periodoacademico,
    })

@role_required([4, 7])
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
    docentes_list = PerfilUsuario.objects.filter(rol__in=[2,5]).select_related("user", "user__perfilusuario")

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

    tutor_list = PerfilUsuario.objects.filter(rol__in=[5,2]).select_related('user')
    maestrantes_list = PerfilUsuario.objects.filter(rol=1).select_related('user')

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




@role_required([4, 7])
@require_http_methods(["GET", "POST"])
@transaction.atomic
def contratosdocentes_update(request, contratosdocentes_id, periodo_id):
    contratodocente = get_object_or_404(ContratosDocentes, id=contratosdocentes_id)
    periodoacademico = get_object_or_404(PeriodosAcademicos, id=periodo_id)

    # ContentTypes
    ct_prog_pp = ContentType.objects.get_for_model(ProgramaPosgrado)
    ct_prog_em = ContentType.objects.get_for_model(ProgramaPosgradoEM)
    ct_mod_m = ContentType.objects.get_for_model(Modulos)
    ct_mod_mem = ContentType.objects.get_for_model(ModulosEM)

    # ---------------------------
    # POST
    # ---------------------------
    if request.method == "POST":
        form = ContratosDocentesForm(request.POST, instance=contratodocente)

        docente_perfil_id = request.POST.get("docente")
        programa_mix = (request.POST.get("programa_mix") or "").strip()
        modulo_mix = (request.POST.get("modulo_mix") or "").strip()
        docente_tipo = int(request.POST.get("docente_tipo", 1))

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
            prog_tipo, prog_id = programa_mix.split("-", 1)  # PP / EM
            mod_tipo, mod_id = modulo_mix.split("-", 1)      # M / MEM

            try:
                prog_id = int(prog_id)
                mod_id = int(mod_id)
            except ValueError:
                messages.error(request, "Programa o módulo inválido.")
                return redirect("contratosdocentes_update", contratosdocentes_id=contratosdocentes_id, periodo_id=periodo_id)

            docente_perfil = get_object_or_404(PerfilUsuario, id=docente_perfil_id)

            # ✅ 1) Resolver programa primero
            if prog_tipo == "PP":
                programa_obj = get_object_or_404(ProgramaPosgrado, id=prog_id, periodoacademico=periodo_id)
                programa_ct = ct_prog_pp
                # PP => siempre docente_tipo 1
                docente_tipo = 1
            elif prog_tipo == "EM":
                programa_obj = get_object_or_404(ProgramaPosgradoEM, id=prog_id, periodoacademico=periodo_id)
                programa_ct = ct_prog_em
                if docente_tipo not in (1, 2):
                    docente_tipo = 1
            else:
                messages.error(request, "Tipo de programa no válido.")
                return redirect("contratosdocentes_update", contratosdocentes_id=contratosdocentes_id, periodo_id=periodo_id)

            # ✅ 2) Validar tipo de módulo según programa
            if prog_tipo == "PP" and mod_tipo != "M":
                messages.error(request, "El tipo de módulo no corresponde al tipo de programa.")
                return redirect("contratosdocentes_update", contratosdocentes_id=contratosdocentes_id, periodo_id=periodo_id)

            if prog_tipo == "EM" and mod_tipo != "MEM":
                messages.error(request, "El tipo de módulo no corresponde al tipo de programa.")
                return redirect("contratosdocentes_update", contratosdocentes_id=contratosdocentes_id, periodo_id=periodo_id)

            # ✅ 3) Resolver módulo
            if mod_tipo == "M":
                modulo_obj = get_object_or_404(Modulos, id=mod_id)
                modulo_ct = ct_mod_m
                # Validar pertenencia a la maestría del programa
                ok = Modulos.objects.filter(id=mod_id, maestria=programa_obj.maestria).exists()
                if not ok:
                    messages.error(request, "El módulo seleccionado no pertenece a la maestría del programa.")
                    return redirect("contratosdocentes_update", contratosdocentes_id=contratosdocentes_id, periodo_id=periodo_id)

            elif mod_tipo == "MEM":
                modulo_obj = get_object_or_404(ModulosEM, id=mod_id)
                modulo_ct = ct_mod_mem
                # Validar pertenencia a la especialidad del programa
                ok = ModulosEM.objects.filter(id=mod_id, especialidad=programa_obj.especialidad).exists()
                if not ok:
                    messages.error(request, "El módulo seleccionado no pertenece a la especialidad del programa.")
                    return redirect("contratosdocentes_update", contratosdocentes_id=contratosdocentes_id, periodo_id=periodo_id)

            else:
                messages.error(request, "Tipo de módulo no válido.")
                return redirect("contratosdocentes_update", contratosdocentes_id=contratosdocentes_id, periodo_id=periodo_id)

            # ✅ 4) Guardar
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
    docentes_list = PerfilUsuario.objects.filter(rol__in=[2,5]).select_related("user", "user__perfilusuario")

    programas_pp = list(ProgramaPosgrado.objects.filter(periodoacademico=periodo_id))
    programas_em = list(ProgramaPosgradoEM.objects.filter(periodoacademico=periodo_id))

    pp_maestria_ids = {p.maestria for p in programas_pp if p.maestria}
    em_especialidad_ids = {p.especialidad for p in programas_em if p.especialidad}

    maestrias_map = {m.id: m for m in Maestrias.objects.filter(id__in=pp_maestria_ids).only("id", "nombre")}
    especialidades_map = {e.id: e for e in EspecialidadesMedicas.objects.filter(id__in=em_especialidad_ids).only("id", "nombre")}

    for p in programas_pp:
        p.maestria_obj = maestrias_map.get(p.maestria)
        p.periodo_obj = periodoacademico

    for p in programas_em:
        p.especialidad_obj = especialidades_map.get(p.especialidad)
        p.periodo_obj = periodoacademico

    docente_inicial = PerfilUsuario.objects.filter(user_id=contratodocente.docente).only("id").first()
    initial_docente_id = docente_inicial.id if docente_inicial else None

    # ✅ Iniciales: tipo + id (para evitar concatenaciones raras en template)
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
            modulos_list = [{"id": m["id"], "nombre": m["nombre"], "mix": f"M-{m['id']}"} for m in mods]

    elif contratodocente.programa_content_type_id == ct_prog_em.id:
        initial_programa_tipo = "EM"
        initial_programa_id = contratodocente.programa_object_id
        show_docente_tipo = True
        prog = next((x for x in programas_em if x.id == initial_programa_id), None)
        if prog:
            mods = ModulosEM.objects.filter(especialidad=prog.especialidad).values("id", "nombre")
            modulos_list = [{"id": m["id"], "nombre": m["nombre"], "mix": f"MEM-{m['id']}"} for m in mods]

    initial_programa_mix = f"{initial_programa_tipo}-{initial_programa_id}" if initial_programa_tipo and initial_programa_id else ""

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
    })


    
@role_required([4, 7])
@transaction.atomic
def contratotutor_update(request, contratotutor_id, periodo_id):
    contratotutor = get_object_or_404(ContratoTutor, id=contratotutor_id)
    periodoacademico = get_object_or_404(PeriodosAcademicos, id=periodo_id)

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

        # debug útil
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

    tutor_list = PerfilUsuario.objects.filter(rol__in=[5,2]).select_related('user')
    maestrantes_list = PerfilUsuario.objects.filter(rol=1).select_related('user')

    # opcional (solo si usas nombre_programa en template)
    maestrias_map = {m.id: m for m in Maestrias.objects.filter(id__in=[p.maestria for p in programas_pp])}
    especialidades_map = {e.id: e for e in EspecialidadesMedicas.objects.filter(id__in=[p.especialidad for p in programas_em])}

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
    })

@role_required([4, 7])
@transaction.atomic
def contratocoordinador_update(request, contratocoordinador_id, periodo_id):
    contratocoordinador = get_object_or_404(ContratoCoordinador, id=contratocoordinador_id)
    periodoacademico = get_object_or_404(PeriodosAcademicos, id=periodo_id)

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
    maestrias_map = {m.id: m for m in Maestrias.objects.filter(id__in=[p.maestria for p in programas_pp])}
    especialidades_map = {e.id: e for e in EspecialidadesMedicas.objects.filter(id__in=[p.especialidad for p in programas_em])}

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
        'initial_programa_mix': initial_programa_mix,  # por si lo quieres usar directo en HTML
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