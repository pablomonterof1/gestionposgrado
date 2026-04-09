from django.shortcuts import render, get_object_or_404
from programasposgrado.models import (
    ProgramaPosgrado, Maestrias, PeriodosAcademicos,
    PerfildeIngreso, Modalidad, CampoAmplio, Modulos
)
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from usuarios.models import MatriculaUsuario, MatriculaDocenteModulo
from rae.models import ReactivosMultipleChoice, EvaluacionPrograma
from administracionposgrado.models import (
    CoordinadorPrograma, ValorProgramaPosgrado, EstudianteProgramaGestion
)
from datosposgrado.models import ContratosDocentes, ContratoTutor


# Create your views here.
def home(request):
    return render(request, 'home.html')


def dashboard(request):
    programasdeposgrado_list = ProgramaPosgrado.objects.all().order_by('-created')
    for programa in programasdeposgrado_list:
        programa.maestria = Maestrias.objects.get(id=programa.maestria)
        programa.periodoacademico = PeriodosAcademicos.objects.get(id=programa.periodoacademico)
        programa.modalidad = Modalidad.objects.get(id=programa.modalidad)
    return render(request, 'dashboard.html', {
        'programasdeposgrado_list': programasdeposgrado_list
    })

def periodosacademicosmain(request):
    periodosacademicos_list = PeriodosAcademicos.objects.all().order_by('-fecha_inicio')
    return render(request, 'periodosacademicos_main.html', {
        'periodosacademicos_list': periodosacademicos_list
    })

def programasdemaestria(request, periodo_id):
    programasdeposgrado_list = ProgramaPosgrado.objects.filter(periodoacademico=periodo_id).order_by('-created')
    for programa in programasdeposgrado_list:
        programa.maestria = Maestrias.objects.get(id=programa.maestria)
        programa.periodoacademico = PeriodosAcademicos.objects.get(id=programa.periodoacademico)
        programa.modalidad = Modalidad.objects.get(id=programa.modalidad)
    programasdeposgrado_list = sorted(
        programasdeposgrado_list,
        key=lambda p: p.periodoacademico.nombre,
        reverse=False
    )
    return render(request, 'dashboard.html', {
        'programasdeposgrado_list': programasdeposgrado_list
    })


@login_required
def ProgramaMaestria(request, programa_id):
    programaposgrado = get_object_or_404(ProgramaPosgrado, id=programa_id)

    # =========================
    # Datos base del programa
    # =========================
    maestria = programaposgrado.maestria
    maestrianombre = Maestrias.objects.get(id=maestria)

    periodoacademico = programaposgrado.periodoacademico
    periodoacademiconombre = PeriodosAcademicos.objects.get(id=periodoacademico)

    modalidad = programaposgrado.modalidad
    modalidadnombre = Modalidad.objects.get(id=modalidad)

    campoamplionombre = CampoAmplio.objects.filter(
        id=programaposgrado.campoamplio
    ).first()

    # =========================
    # ContentType del programa
    # =========================
    programa_ct = ContentType.objects.get_for_model(ProgramaPosgrado)

    # =========================
    # Estudiantes
    # =========================
    total_estudiantes = MatriculaUsuario.objects.filter(
        content_type=programa_ct,
        object_id=programaposgrado.id
    ).count()

    # =========================
    # Docentes y módulos
    # =========================
    total_docentes = MatriculaDocenteModulo.objects.filter(
        programa=programaposgrado.id
    ).values('docente').distinct().count()

    total_modulos = Modulos.objects.filter(
        maestria=programaposgrado.maestria
    ).count()

    modulos_con_docente = MatriculaDocenteModulo.objects.filter(
        programa=programaposgrado.id
    ).count()

    modulos_sin_docente = max(total_modulos - modulos_con_docente, 0)

    # =========================
    # RAE
    # =========================
    total_reactivos = ReactivosMultipleChoice.objects.filter(
        programadeposgrado=programaposgrado
    ).count()

    reactivos_validados = ReactivosMultipleChoice.objects.filter(
        programadeposgrado=programaposgrado,
        estado=2
    ).count()

    reactivos_pendientes = ReactivosMultipleChoice.objects.filter(
        programadeposgrado=programaposgrado,
        estado=1
    ).count()

    evaluaciones_activas = EvaluacionPrograma.objects.filter(
        programa=programaposgrado,
        activa=True
    ).count()

    total_simulacros = EvaluacionPrograma.objects.filter(
        programa=programaposgrado,
        tipo='simulacro'
    ).count()

    total_finales = EvaluacionPrograma.objects.filter(
        programa=programaposgrado,
        tipo='final'
    ).count()

    # =========================
    # Coordinador actual
    # =========================
    coordinador_obj = CoordinadorPrograma.objects.filter(
        programa_content_type=programa_ct,
        programa_object_id=programaposgrado.id
    ).select_related('coordinador').order_by('-fecha_inicio', '-id').first()

    coordinador_actual = (
        coordinador_obj.coordinador.get_full_name()
        if coordinador_obj and coordinador_obj.coordinador
        else 'No registrado'
    )

    # =========================
    # Valores del programa
    # =========================
    valor_programa = ValorProgramaPosgrado.objects.filter(
        programa_content_type=programa_ct,
        programa_object_id=programaposgrado.id
    ).first()

    valor_inscripcion = valor_programa.valorinscripcion if valor_programa else 'No registrado'
    valor_matricula = valor_programa.valormatricula if valor_programa else 'No registrado'
    plan_pago = valor_programa.get_plan_pago_display() if valor_programa else 'No registrado'

    # =========================
    # Gestión estudiantes
    # =========================
    gestion_estudiantes = EstudianteProgramaGestion.objects.filter(
        programa_content_type=programa_ct,
        programa_object_id=programaposgrado.id
    )

    estudiantes_matricula_pagada = gestion_estudiantes.filter(
        pago_matricula=True
    ).count()

    estudiantes_titulacion = gestion_estudiantes.filter(
        Q(modalidad__isnull=False) |
        Q(avance_porcentaje__isnull=False) |
        Q(fecha_sustentacion_oral__isnull=False) |
        Q(fecha_aprob_complexivo__isnull=False)
    ).count()

    titulos_entregados = gestion_estudiantes.filter(
        estado_titulo='ENTREGADO'
    ).count()

    estudiantes_sin_avance = gestion_estudiantes.filter(
        avance_porcentaje__isnull=True
    ).count()

    # =========================
    # Pendientes de pago
    # =========================
    docentes_pendientes_pago = ContratosDocentes.objects.filter(
        programa_content_type=programa_ct,
        programa_object_id=programaposgrado.id
    ).filter(
        Q(gestion__isnull=True) | Q(gestion__pago_realizado=False)
    ).count()

    tutores_pendientes_pago = ContratoTutor.objects.filter(
        programa_content_type=programa_ct,
        programa_object_id=programaposgrado.id
    ).filter(
        Q(gestion__isnull=True) | Q(gestion__pago_realizado=False)
    ).count()

    return render(request, 'programamaestria.html', {
        'programaposgrado': programaposgrado,
        'maestrianombre': maestrianombre,
        'periodoacademiconombre': periodoacademiconombre,
        'modalidadnombre': modalidadnombre,
        'campoamplionombre': campoamplionombre,

        'total_estudiantes': total_estudiantes,
        'total_docentes': total_docentes,
        'total_modulos': total_modulos,
        'reactivos_validados': reactivos_validados,
        'evaluaciones_activas': evaluaciones_activas,
        'coordinador_actual': coordinador_actual,

        'modulos_con_docente': modulos_con_docente,
        'modulos_sin_docente': modulos_sin_docente,
        'total_reactivos': total_reactivos,
        'total_simulacros': total_simulacros,
        'total_finales': total_finales,

        'valor_inscripcion': valor_inscripcion,
        'valor_matricula': valor_matricula,
        'plan_pago': plan_pago,
        'estudiantes_matricula_pagada': estudiantes_matricula_pagada,
        'estudiantes_titulacion': estudiantes_titulacion,
        'titulos_entregados': titulos_entregados,

        'reactivos_pendientes': reactivos_pendientes,
        'docentes_pendientes_pago': docentes_pendientes_pago,
        'tutores_pendientes_pago': tutores_pendientes_pago,
        'estudiantes_sin_avance': estudiantes_sin_avance,
    })


def es_estudiante(user):
    return user.is_authenticated and user.perfilusuario.rol == 1 or user.is_superuser

def es_docente(user):
    return user.is_authenticated and user.perfilusuario.rol == 2 or user.is_superuser

def es_coordinador(user):
    return user.is_authenticated and user.perfilusuario.rol == 3 or user.is_superuser

def es_editor(user):
    return user.is_authenticated and user.perfilusuario.rol == 4 or user.is_superuser

def es_tutor(user):
    return user.is_authenticated and user.perfilusuario.rol == 5 or user.is_superuser


