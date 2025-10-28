from django.urls import reverse
from django.utils import timezone
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
import random
from usuarios.models import MatriculaUsuario
from .models import ReactivosMultipleChoice, ReactivosModuloRAE, EvaluacionPrograma, EvaluacionEstudiante, ReactivoEvaluacion, ReactivoPorEvaluacion, ComponenteRAE, SubcomponenteRAE, SubcomponenteModuloRAE
from programasposgrado.models import Maestrias, PeriodosAcademicos, Modalidad, ProgramaPosgrado, Modulos
from django.contrib.auth.decorators import login_required
from .forms import ReactivosMultipleChoiceForm, ComponenteRAEForm, SubcomponenteRAEForm, SubcomponenteFormSet, SubcomponenteAsignarModulosForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from main.views import es_estudiante, es_docente, es_coordinador, es_editor
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from datetime import timedelta
import xlsxwriter
import io
from django.utils.html import strip_tags
from decimal import Decimal
from usuarios.models import PerfilUsuario

# Create your views here.

########################################### REACTIVOS###########################################################


@login_required
def reactivosprograma(request, programa_id):
    reactivos_list = ReactivosMultipleChoice.objects.filter(
        programadeposgrado=programa_id)
    programaposgrado = ProgramaPosgrado.objects.get(id=programa_id)
    maestria = programaposgrado.maestria
    modulos_list = Modulos.objects.filter(maestria=maestria)
    maestrianombre = Maestrias.objects.get(id=maestria)
    periodoacademico = programaposgrado.periodoacademico
    periodoacademiconombre = PeriodosAcademicos.objects.get(
        id=periodoacademico)
    modalidad = programaposgrado.modalidad
    modalidadnombre = Modalidad.objects.get(id=modalidad)
    return render(request, 'reactivos.html', {
        'reactivos_list': reactivos_list,
        'maestrianombre': maestrianombre,
        'periodoacademiconombre': periodoacademiconombre,
        'modalidadnombre': modalidadnombre,
        'programaposgrado': programaposgrado,
        'modulos_list': modulos_list,
    })


@login_required
def reactivosmodulo(request, programa_id, modulo_id):
    reactivos_list = ReactivosMultipleChoice.objects.filter(
        modulo=modulo_id, programadeposgrado=programa_id).order_by('created')
    modulo = Modulos.objects.get(id=modulo_id)
    modulonombre = modulo.nombre
    programaposgrado = ProgramaPosgrado.objects.get(id=programa_id)
    maestria = programaposgrado.maestria
    maestrianombre = Maestrias.objects.get(id=maestria)
    periodoacademico = programaposgrado.periodoacademico
    periodoacademiconombre = PeriodosAcademicos.objects.get(
        id=periodoacademico)
    modalidad = programaposgrado.modalidad
    modalidadnombre = Modalidad.objects.get(id=modalidad)
    for r in reactivos_list:
        try:
            r.usuario_obj = User.objects.get(id=r.usuario)
        except User.DoesNotExist:
            r.usuario_obj = None

    return render(request, 'reactivos_modulo.html', {
        'reactivos_list': reactivos_list,
        'maestrianombre': maestrianombre,
        'periodoacademiconombre': periodoacademiconombre,
        'modalidadnombre': modalidadnombre,
        'programaposgrado': programaposgrado,
        'modulonombre': modulonombre,
        'modulo': modulo,

    })


@login_required
def reactivosmodulodocente(request, programa_id, modulo_id):
    reactivos_list = ReactivosMultipleChoice.objects.filter(
        modulo=modulo_id, programadeposgrado=programa_id, usuario=request.user.id).order_by('created')
    modulo = Modulos.objects.get(id=modulo_id)
    modulonombre = modulo.nombre
    programaposgrado = ProgramaPosgrado.objects.get(id=programa_id)
    maestria = programaposgrado.maestria
    maestrianombre = Maestrias.objects.get(id=maestria)
    periodoacademico = programaposgrado.periodoacademico
    periodoacademiconombre = PeriodosAcademicos.objects.get(
        id=periodoacademico)
    modalidad = programaposgrado.modalidad
    modalidadnombre = Modalidad.objects.get(id=modalidad)
    for r in reactivos_list:
        try:
            r.usuario_obj = User.objects.get(id=r.usuario)
        except User.DoesNotExist:
            r.usuario_obj = None

    return render(request, 'reactivos_modulodocente.html', {
        'reactivos_list': reactivos_list,
        'maestrianombre': maestrianombre,
        'periodoacademiconombre': periodoacademiconombre,
        'modalidadnombre': modalidadnombre,
        'programaposgrado': programaposgrado,
        'modulonombre': modulonombre,
        'modulo': modulo,

    })


@user_passes_test(es_docente)
def reactivosmc_create(request, programa_id, modulo_id):
    reactivos_list = ReactivosMultipleChoice.objects.filter(modulo=modulo_id)
    modulo = Modulos.objects.get(id=modulo_id)
    modulonombre = modulo.nombre
    programaposgrado = ProgramaPosgrado.objects.get(id=programa_id)
    maestria = programaposgrado.maestria
    maestrianombre = Maestrias.objects.get(id=maestria)
    if request.method == 'POST':
        form = ReactivosMultipleChoiceForm(request.POST)
        if form.is_valid():

            reactivo = form.save(commit=False)
            reactivo.programadeposgrado = ProgramaPosgrado.objects.get(
                id=programa_id)
            reactivo.modulo = Modulos.objects.get(id=modulo_id)
            reactivo.usuario = request.user.id
            reactivo.save()
            messages.success(request, "Reactivo creado correctamente.")
            return redirect('reactivosmodulo', programa_id=programa_id, modulo_id=modulo_id)
        else:
            messages.error(
                request, "Revise que todos los campos sean válidos o ya existe un reactivo con este enunciado.")
    else:
        form = ReactivosMultipleChoiceForm()
    return render(request, 'reactivosmc_create.html', {
        'maestrianombre': maestrianombre,
        'programaposgrado': programaposgrado,
        'modulonombre': modulonombre,
        'modulo': modulo,
        'reactivos_list': reactivos_list,
        'form': form,
    })


@user_passes_test(es_docente)
def reactivosdocente_create(request, programa_id, modulo_id):
    reactivos_list = ReactivosMultipleChoice.objects.filter(modulo=modulo_id)
    modulo = Modulos.objects.get(id=modulo_id)
    modulonombre = modulo.nombre
    programaposgrado = ProgramaPosgrado.objects.get(id=programa_id)
    maestria = programaposgrado.maestria
    maestrianombre = Maestrias.objects.get(id=maestria)
    if request.method == 'POST':
        form = ReactivosMultipleChoiceForm(request.POST)
        if form.is_valid():

            reactivo = form.save(commit=False)
            reactivo.programadeposgrado = ProgramaPosgrado.objects.get(
                id=programa_id)
            reactivo.modulo = Modulos.objects.get(id=modulo_id)
            reactivo.usuario = request.user.id
            reactivo.save()
            messages.success(request, "Reactivo creado correctamente.")
            return redirect('reactivosmodulodocente', programa_id=programa_id, modulo_id=modulo_id)
        else:
            messages.error(
                request, "Ya existe un reactivo con este enunciado o revise que todos los campos sean válidos.")
    else:
        form = ReactivosMultipleChoiceForm()
    return render(request, 'reactivosdocente_create.html', {
        'maestrianombre': maestrianombre,
        'programaposgrado': programaposgrado,
        'modulonombre': modulonombre,
        'modulo': modulo,
        'reactivos_list': reactivos_list,
        'form': form,
    })


@login_required
def reactivosmc_update(request, reactivo_id):
    reactivo = ReactivosMultipleChoice.objects.get(id=reactivo_id)
    programadeposgrado = reactivo.programadeposgrado
    modulo_id = reactivo.modulo
    if request.method == 'POST':
        form = ReactivosMultipleChoiceForm(request.POST, instance=reactivo)
        if form.is_valid():
            form.save()
            return redirect('reactivosmodulo', programa_id=programadeposgrado.id, modulo_id=modulo_id.id)
    else:
        form = ReactivosMultipleChoiceForm(instance=reactivo)
    return render(request, 'reactivosmc_update.html', {
        'form': form,
        'reactivo': reactivo,
        'programadeposgrado': programadeposgrado,
        'modulo_id': modulo_id,
    })


@login_required
def reactivosdocente_update(request, reactivo_id):
    reactivo = ReactivosMultipleChoice.objects.get(id=reactivo_id)
    programadeposgrado = reactivo.programadeposgrado
    modulo_id = reactivo.modulo
    if request.method == 'POST':
        form = ReactivosMultipleChoiceForm(request.POST, instance=reactivo)
        if form.is_valid():
            form.save()
            return redirect('reactivosmodulodocente', programa_id=programadeposgrado.id, modulo_id=modulo_id.id)
    else:
        form = ReactivosMultipleChoiceForm(instance=reactivo)
    return render(request, 'reactivosdocente_update.html', {
        'form': form,
        'reactivo': reactivo,
        'programadeposgrado': programadeposgrado,
        'modulo_id': modulo_id,
    })


@login_required
def reactivosmc_validate(request, reactivo_id):
    reactivo = ReactivosMultipleChoice.objects.get(id=reactivo_id)
    programadeposgrado = reactivo.programadeposgrado
    modulo_id = reactivo.modulo
    action = request.POST.get('action')
    if request.method == 'POST':
        form = ReactivosMultipleChoiceForm(request.POST, instance=reactivo)
        if form.is_valid():
            reactivo = form.save(commit=False)
            if action == 'validar':
                reactivo.estado = 2
                reactivo.save()
            if action == 'rechazar':
                reactivo.estado = 3
                reactivo.save()
            return redirect('reactivosmodulo', programa_id=programadeposgrado.id, modulo_id=modulo_id.id)
    else:
        form = ReactivosMultipleChoiceForm(instance=reactivo)
    return render(request, 'reactivosmc_validate.html', {
        'form': form,
        'reactivo': reactivo,
        'programadeposgrado': programadeposgrado,
        'modulo_id': modulo_id,
    })


@login_required
def reactivosmc_delete(request, reactivo_id):
    reactivo = ReactivosMultipleChoice.objects.get(id=reactivo_id)
    programa_id = reactivo.programadeposgrado.id
    modulo_id = reactivo.modulo
    if request.method == 'POST':
        reactivo.delete()
        return redirect('reactivosmodulo', programa_id=programa_id, modulo_id=modulo_id.id)
    return render(request, 'reactivosmc_delete.html', {
        'reactivo': reactivo,
        'programa_id': programa_id,
        'modulo_id': modulo_id,
    })


@login_required
def reactivosdocente_delete(request, reactivo_id):
    reactivo = ReactivosMultipleChoice.objects.get(id=reactivo_id)
    programa_id = reactivo.programadeposgrado.id
    modulo_id = reactivo.modulo
    if request.method == 'POST':
        reactivo.delete()
        return redirect('reactivosmodulodocente', programa_id=programa_id, modulo_id=modulo_id.id)
    return render(request, 'reactivosdocente_delete.html', {
        'reactivo': reactivo,
        'programa_id': programa_id,
        'modulo_id': modulo_id,
    })


@login_required
def reactivos_programaposgrado(request, programa_id):
    reactivos_list = ReactivosMultipleChoice.objects.filter(
        programadeposgrado=programa_id).order_by('created')
    programaposgrado = ProgramaPosgrado.objects.get(id=programa_id)
    maestria = programaposgrado.maestria
    maestrianombre = Maestrias.objects.get(id=maestria)
    periodoacademico = programaposgrado.periodoacademico
    periodoacademiconombre = PeriodosAcademicos.objects.get(
        id=periodoacademico)
    modalidad = programaposgrado.modalidad
    modalidadnombre = Modalidad.objects.get(id=modalidad)
    for r in reactivos_list:
        try:
            r.usuario_obj = User.objects.get(id=r.usuario)
            r.modulo_obj = Modulos.objects.get(id=r.modulo)
        except User.DoesNotExist:
            r.usuario_obj = None

    return render(request, 'reactivos_programaposgrado.html', {
        'reactivos_list': reactivos_list,
        'maestrianombre': maestrianombre,
        'periodoacademiconombre': periodoacademiconombre,
        'modalidadnombre': modalidadnombre,
        'programaposgrado': programaposgrado,
    })


@login_required
def rae_programaposgrado(request, programa_id):
    programaposgrado = ProgramaPosgrado.objects.get(id=programa_id)
    maestria = programaposgrado.maestria
    maestrianombre = Maestrias.objects.get(id=maestria)
    periodoacademico = programaposgrado.periodoacademico
    periodoacademiconombre = PeriodosAcademicos.objects.get(
        id=periodoacademico)
    modalidad = programaposgrado.modalidad
    modalidadnombre = Modalidad.objects.get(id=modalidad)

    modulos_list = Modulos.objects.filter(
        maestria=maestria).order_by('codificacion')
    totalreactivosrae = 0
    for modulo in modulos_list:
        modulo.reactivos = ReactivosMultipleChoice.objects.filter(
            programadeposgrado=programa_id, modulo=modulo.id, estado=2)
        modulo.numeroreactivosmodulorae = ReactivosModuloRAE.objects.filter(
            programadeposgrado=programa_id, modulo=modulo).first()
        if modulo.numeroreactivosmodulorae:
            totalreactivosrae = modulo.numeroreactivosmodulorae.numero_reactivos_modulo + totalreactivosrae
        modulo.total_reactivos = modulo.reactivos.count()
        modulo.max_para_input = modulo.total_reactivos // 2

    return render(request, 'rae_programaposgrado.html', {
        'maestrianombre': maestrianombre,
        'periodoacademiconombre': periodoacademiconombre,
        'modalidadnombre': modalidadnombre,
        'programaposgrado': programaposgrado,
        'modulos_list': modulos_list,
        'totalreactivosrae': totalreactivosrae,
    })


@login_required
def reactivosmodulorae_create(request, programa_id, modulo_id):
    programaposgrado = ProgramaPosgrado.objects.get(id=programa_id)
    modulo = Modulos.objects.get(id=modulo_id)
    if request.method == 'POST':
        numero_reactivos_modulo = request.POST.get(
            'numero_reactivos_modulo_rae')
        observaciones = request.POST.get('observaciones', '')
        reactivos_modulo_rae, created = ReactivosModuloRAE.objects.update_or_create(
            programadeposgrado=programaposgrado,
            modulo=modulo,
            defaults={
                'numero_reactivos_modulo': numero_reactivos_modulo,
                'observaciones': observaciones
            }
        )
        messages.success(
            request, "Reactivos del módulo RAE actualizados correctamente.")
        return redirect('rae_programaposgrado', programa_id=programa_id)
    else:
        reactivos_modulo_rae = ReactivosModuloRAE.objects.filter(
            programadeposgrado=programa_id, modulo=modulo_id).first()
    return render(request, 'rae_programaposgrado.html', {
        'programaposgrado': programaposgrado,
        'modulo': modulo,
        'reactivos_modulo_rae': reactivos_modulo_rae,
    })


@login_required
def evaluacionrae_programaposgrado(request, programa_id):
    programa = get_object_or_404(ProgramaPosgrado, id=programa_id)
    evaluaciones = EvaluacionPrograma.objects.filter(programa=programa).order_by('-activa')

    return render(request, 'evaluacionrae_programaposgrado.html', {
        'programa': programa,
        'evaluaciones': evaluaciones
    })


def obtener_reactivos_para_evaluacion(programa, tipo, estudiante=None):
    import random
    seleccionados_estudiante = []
    modulos = Modulos.objects.filter(maestria=programa.maestria)

    for modulo in modulos:
        try:
            config = ReactivosModuloRAE.objects.get(programadeposgrado=programa, modulo=modulo)
            num_reactivos = config.numero_reactivos_modulo
        except ReactivosModuloRAE.DoesNotExist:
            continue

        reactivos_query = ReactivosMultipleChoice.objects.filter(
            programadeposgrado=programa,
            modulo=modulo,
            estado=2
        )

 
        if tipo == 'final' and estudiante:
            simulacro_activo = EvaluacionPrograma.objects.filter(
                programa=programa,
                tipo='simulacro',
                activa=True
            ).first()

            if simulacro_activo:
                usados_ids = ReactivoEvaluacion.objects.filter(
                    evaluacion_estudiante__evaluacion=simulacro_activo,
                    evaluacion_estudiante__estudiante=estudiante
                ).values_list('reactivo_id', flat=True)
                reactivos_query = reactivos_query.exclude(id__in=usados_ids)

        reactivos_list = list(reactivos_query)

        if len(reactivos_list) >= num_reactivos:
            seleccionados = random.sample(reactivos_list, num_reactivos)
        else:
            seleccionados = reactivos_list

        seleccionados_estudiante.extend(seleccionados)

    return seleccionados_estudiante

@csrf_exempt
@login_required
def evaluacionrae_activar(request, programa_id, tipo):
    programa = get_object_or_404(ProgramaPosgrado, id=programa_id)

    if request.method == 'POST':
        fecha_inicio = request.POST['fecha_inicio']
        fecha_fin = request.POST['fecha_fin']
        duracion = request.POST['duracion']
        valor = request.POST['valor']

        # Desactivar cualquier evaluación activa del mismo tipo
        EvaluacionPrograma.objects.filter(
            programa=programa,
            tipo=tipo,
            activa=True
        ).update(activa=False)

        evaluacion = EvaluacionPrograma.objects.create(
            programa=programa,
            tipo=tipo,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            duracion_minutos=duracion,
            valorpregunta=valor,
            activa=True
        )

        # Obtener reactivos aleatorios por módulo y guardarlos para esta evaluación
        import random
        modulos = Modulos.objects.filter(maestria=programa.maestria)

        usados_ids = []
        for modulo in modulos:
            try:
                config = ReactivosModuloRAE.objects.get(programadeposgrado=programa, modulo=modulo)
            except ReactivosModuloRAE.DoesNotExist:
                continue

            reactivos = ReactivosMultipleChoice.objects.filter(
                programadeposgrado=programa,
                modulo=modulo,
                estado=2
            )

            if tipo == 'final':
                simulacro = EvaluacionPrograma.objects.filter(programa=programa, tipo='simulacro').first()
                if simulacro:
                    usados_ids = ReactivoPorEvaluacion.objects.filter(
                        evaluacion=simulacro
                    ).values_list('reactivo_id', flat=True)
                    reactivos = reactivos.exclude(id__in=usados_ids)

            reactivos_list = list(reactivos)
            if len(reactivos_list) >= config.numero_reactivos_modulo:
                seleccionados = random.sample(reactivos_list, config.numero_reactivos_modulo)
            else:
                seleccionados = reactivos_list

            for reactivo in seleccionados:
                ReactivoPorEvaluacion.objects.create(evaluacion=evaluacion, reactivo=reactivo)

        messages.success(request, f"Evaluación {tipo} activada correctamente.")
        return redirect('evaluacionrae_programaposgrado', programa_id=programa.id)

    return render(request, 'evaluacionrae_activar.html', {
        'programa': programa,
        'tipo': tipo
    })

@login_required
def evaluacionrae_update(request, evaluacion_id):
    evaluacion = get_object_or_404(EvaluacionPrograma, id=evaluacion_id)
    if request.method == 'POST':
        fecha_inicio = request.POST['fecha_inicio']
        fecha_fin = request.POST['fecha_fin']
        duracion = request.POST['duracion']
        valor = request.POST['valor']

        evaluacion.fecha_inicio = fecha_inicio
        evaluacion.fecha_fin = fecha_fin
        evaluacion.duracion_minutos = duracion
        evaluacion.valorpregunta = valor

        evaluacion.save()
        messages.success(request, "Evaluación actualizada correctamente.")
        return redirect('evaluacionrae_programaposgrado', programa_id=evaluacion.programa.id)
    return render(request, 'evaluacionrae_update.html', {
        'evaluacion': evaluacion
    })

@login_required
def reactivos_por_evaluacion(request, evaluacion_id):
    evaluacion = get_object_or_404(EvaluacionPrograma, id=evaluacion_id)
    reactivos = ReactivoPorEvaluacion.objects.filter(evaluacion=evaluacion).select_related('reactivo')

    return render(request, 'reactivos_por_evaluacion.html', {
        'evaluacion': evaluacion,
        'reactivos': reactivos
    })



@login_required
def evaluacionesrae_disponibles(request, programa_id):
    ahora = timezone.localtime()

    # 1. Todas las evaluaciones activas para el programa del usuario, y en fecha
    evaluaciones_programa = EvaluacionPrograma.objects.filter(
        activa=True,
        fecha_inicio__lte=ahora,
        fecha_fin__gte=ahora,
        programa=programa_id
    )

    # 2. Evaluaciones ya respondidas por este estudiante
    evaluaciones_respondidas_ids = EvaluacionEstudiante.objects.filter(
        estudiante=request.user,
        respondido=True
    ).values_list('evaluacion_id', flat=True)

    # 3. Filtrar para mostrar solo las que NO ha respondido aún
    evaluaciones_disponibles = evaluaciones_programa.exclude(id__in=evaluaciones_respondidas_ids)

    return render(request, 'evaluacionesrae_disponibles.html', {
        'evaluaciones': evaluaciones_disponibles,
        'evaluacionesrealizadas': EvaluacionEstudiante.objects.filter(
            estudiante=request.user,
            evaluacion__programa=programa_id,
            respondido=True
        ).select_related('evaluacion')
    })



@login_required
def evaluacionrae_rendir(request, evaluacion_id):
    evaluacion = get_object_or_404(EvaluacionPrograma, id=evaluacion_id)

    if timezone.localtime() < evaluacion.fecha_inicio or timezone.localtime() > (evaluacion.fecha_fin + timedelta(minutes=evaluacion.duracion_minutos+10)):
        return HttpResponseForbidden("Evaluación no disponible")

    evaluacion_est, creado = EvaluacionEstudiante.objects.get_or_create(
        evaluacion=evaluacion,
        estudiante=request.user
    )

    # Si es la primera vez que entra, le asignamos los reactivos desde la evaluación general
    if creado or not ReactivoEvaluacion.objects.filter(evaluacion_estudiante=evaluacion_est).exists():
        reactivos_generales = ReactivoPorEvaluacion.objects.filter(evaluacion=evaluacion)
        for r in reactivos_generales:
            ReactivoEvaluacion.objects.create(
                evaluacion_estudiante=evaluacion_est,
                reactivo=r.reactivo
            )

    reactivos = ReactivoEvaluacion.objects.filter(evaluacion_estudiante=evaluacion_est)

    if request.method == 'POST':
        score = 0
        for reactivo_eval in reactivos:
            respuesta = request.POST.get(f"pregunta_{reactivo_eval.id}")
            if respuesta:
                reactivo_eval.respuesta_estudiante = respuesta
                reactivo_eval.correcta = (respuesta == reactivo_eval.reactivo.correcta)
                if reactivo_eval.correcta:
                    score += evaluacion.valorpregunta
                reactivo_eval.save()

        evaluacion_est.calificacion = score
        evaluacion_est.respondido = True
        evaluacion_est.save()

        messages.success(request, f"Evaluación finalizada. Calificación: {score}/100")
        return redirect('evaluacionesrae_disponibles', programa_id=evaluacion.programa.id)

    return render(request, 'evaluacionrae_rendir.html', {
        'reactivos': reactivos,
        'evaluacion_est': evaluacion_est,
        'duracion': evaluacion.duracion_minutos,
        'evaluacion': evaluacion,
    })

@csrf_exempt
@require_POST
@login_required
def guardar_parcial_rae(request, evaluacion_id):
    evaluacion_est = get_object_or_404(EvaluacionEstudiante, id=evaluacion_id, estudiante=request.user)
    reactivos = ReactivoEvaluacion.objects.filter(evaluacion_estudiante=evaluacion_est)

    for reactivo in reactivos:
        respuesta = request.POST.get(f'pregunta_{reactivo.id}')
        if respuesta:
            reactivo.respuesta_estudiante = respuesta
            reactivo.correcta = (respuesta == reactivo.reactivo.correcta)
            reactivo.save()

    return JsonResponse({'status': 'ok'})


@login_required
def resultadorae_estudiante(request, evaluacion_id):
    evaluacion_est = get_object_or_404(
        EvaluacionEstudiante,
        evaluacion__id=evaluacion_id,
        estudiante=request.user
    )

    evaluacion = get_object_or_404(EvaluacionPrograma, id=evaluacion_id)

    if not evaluacion_est.respondido:
        return redirect('evaluacionesrae_disponibles', programa_id=evaluacion.programa.id)

    reactivos = ReactivoEvaluacion.objects.filter(evaluacion_estudiante=evaluacion_est)

    return render(request, 'resultadorae_estudiante.html', {
        'evaluacion_est': evaluacion_est,
        'reactivos': reactivos,
        'evaluacion': evaluacion
    })


@login_required
def resultadosrae_programa(request, programa_id, evaluacion_id):
    programa = get_object_or_404(ProgramaPosgrado, id=programa_id)
    evaluacion = get_object_or_404(EvaluacionPrograma, programa=programa, id=evaluacion_id)

    # Estudiantes matriculados al programa
    content_type = ContentType.objects.get_for_model(ProgramaPosgrado)
    matriculas = (
        MatriculaUsuario.objects
        .filter(content_type=content_type, object_id=programa.id, rol_en_programa='estudiante')
        .select_related('usuario')
        .order_by('usuario__last_name', 'usuario__first_name')
    )

    # Todas las evaluaciones existentes de esos estudiantes para esta evaluación
    evals = (
        EvaluacionEstudiante.objects
        .filter(evaluacion=evaluacion, estudiante__in=[m.usuario for m in matriculas])
        .select_related('estudiante')
    )
    eval_por_user = {e.estudiante_id: e for e in evals}

    resultados = []
    for m in matriculas:
        u = m.usuario
        ev = eval_por_user.get(u.id)

        respondido = ev.respondido if ev else False
        calificacion = ev.calificacion if ev else None

        resultados.append({
            'id': u.id,  # para tu form id="form-borrar-{{ res.id }}"
            'estudiante': u,
            'respondido': respondido,
            'calificacion': calificacion,
            'detalle_url': reverse('detalle_resultado_estudiante', args=[evaluacion.id, u.id]) if respondido else None,
            'borrar_url': reverse('detalle_resultado_estudiante_borrar', args=[evaluacion.id, u.id]) if respondido else None,
        })

    return render(request, 'resultadosrae_programa.html', {
        'programa': programa,
        'evaluacion': evaluacion,
        'resultados': resultados
    })




@login_required
def detalle_resultado_estudiante(request, evaluacion_id, estudiante_id):
    evaluacion = get_object_or_404(EvaluacionPrograma, id=evaluacion_id)
    estudiante = get_object_or_404(User, id=estudiante_id)

    evaluacion_est = get_object_or_404(EvaluacionEstudiante,
        evaluacion=evaluacion, estudiante=estudiante
    )

    respuestas = ReactivoEvaluacion.objects.filter(evaluacion_estudiante=evaluacion_est).select_related('reactivo')

    return render(request, 'detalle_resultado_estudiante.html', {
        'evaluacion': evaluacion,
        'estudiante': estudiante,
        'respuestas': respuestas,
        'calificacion': evaluacion_est.calificacion
    })

@login_required
def detalle_resultado_estudiante_borrar(request, evaluacion_id, estudiante_id):

    evaluacion = get_object_or_404(EvaluacionPrograma, id=evaluacion_id)
    estudiante = get_object_or_404(User, id=estudiante_id)

    evaluacion_est = get_object_or_404(EvaluacionEstudiante,
        evaluacion=evaluacion, estudiante=estudiante
    )
    reactivos = ReactivoEvaluacion.objects.filter(evaluacion_estudiante=evaluacion_est)
    for reactivo in reactivos:
        reactivo.respuesta_estudiante = None
        reactivo.correcta = False
        reactivo.save()

    if request.method == 'POST':
        evaluacion_est.respondido = False
        evaluacion_est.calificacion = None
        evaluacion_est.save()
        messages.error(request, "Resultados eliminados correctamente.")
        return redirect('resultadosrae_programa', programa_id=evaluacion.programa.id, evaluacion_id=evaluacion.id)

    return redirect('resultadosrae_programa', programa_id=evaluacion.programa.id, evaluacion_id=evaluacion.id)


def resultado_estudiante_pdf(request, evaluacion_id):
    evaluacion_est = EvaluacionEstudiante.objects.get(evaluacion__id=evaluacion_id, estudiante=request.user)
    reactivos = ReactivoEvaluacion.objects.filter(evaluacion_estudiante=evaluacion_est)

    template = get_template('resultadorae_pdf.html')  # Nombre del nuevo HTML
    html = template.render({'evaluacion_est': evaluacion_est, 'reactivos': reactivos})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="resultado_{request.user.username}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=500)

    return response


@login_required
def evaluacionrae_eliminar(request, evaluacion_id):
    evaluacion = get_object_or_404(EvaluacionPrograma, id=evaluacion_id)

    # Solo permitir si no ha sido respondida o está inactiva
    estudiantes_respondieron = EvaluacionEstudiante.objects.filter(
        evaluacion=evaluacion,
        respondido=True
    ).exists()

    if estudiantes_respondieron:
        messages.error(request, "No se puede eliminar esta evaluación porque ya ha sido respondida.")
        return redirect('evaluacionrae_programaposgrado', programa_id=evaluacion.programa.id)

    # Eliminar reactivos intermedios asociados a la evaluación
    ReactivoPorEvaluacion.objects.filter(evaluacion=evaluacion).delete()

    # Eliminar estudiantes (si existieran)
    EvaluacionEstudiante.objects.filter(evaluacion=evaluacion).delete()

    # Eliminar la evaluación
    evaluacion.delete()

    messages.success(request, "Evaluación eliminada correctamente.")
    return redirect('evaluacionrae_programaposgrado', programa_id=evaluacion.programa.id)


@login_required
def exportar_resultados_excel(request, programa_id, evaluacion_id):
    programa = get_object_or_404(ProgramaPosgrado, id=programa_id)
    evaluacion = get_object_or_404(EvaluacionPrograma, id=evaluacion_id, programa=programa)

    # === Estudiantes matriculados en el programa ===
    content_type = ContentType.objects.get_for_model(ProgramaPosgrado)
    matriculas = (
        MatriculaUsuario.objects
        .filter(content_type=content_type, object_id=programa.id, rol_en_programa='estudiante')
        .select_related("usuario")
    )

    # === Evaluaciones de esos estudiantes en esta evaluación ===
    evaluaciones_estudiantes = (
        EvaluacionEstudiante.objects
        .filter(evaluacion=evaluacion, estudiante__in=[m.usuario for m in matriculas])
        .select_related("estudiante")
    )
    eval_est_por_usuario = {e.estudiante_id: e for e in evaluaciones_estudiantes}

    # Perfiles para Sexo (evita N+1 queries)
    perfiles = {p.user_id: p for p in PerfilUsuario.objects.filter(user__in=[m.usuario for m in matriculas])}

    # === Reactivos de la evaluación (base) ===
    reactivos_qs = (
        ReactivoPorEvaluacion.objects
        .filter(evaluacion=evaluacion)
        .select_related("reactivo", "reactivo__modulo")
        .order_by("reactivo__id")
    )
    reactivos_list = [r.reactivo for r in reactivos_qs]

    # === Respuestas de todos (acceso O(1)) ===
    respuestas = (
        ReactivoEvaluacion.objects
        .filter(evaluacion_estudiante__in=evaluaciones_estudiantes)
        .select_related("evaluacion_estudiante", "reactivo")
    )
    respuestas_dict = {}
    for r in respuestas:
        respuestas_dict.setdefault(r.evaluacion_estudiante_id, {})[r.reactivo_id] = r

    # === Mapeo Módulo -> (Componente, Subcomponente) del PROGRAMA ===
    asignaciones = (
        SubcomponenteModuloRAE.objects
        .filter(subcomponente__componente__programa=programa)
        .select_related('subcomponente', 'subcomponente__componente', 'modulo')
    )
    asig_por_modulo = {}
    for a in asignaciones:
        asig_por_modulo[a.modulo_id] = {
            'comp_nombre': a.subcomponente.componente.nombre,
            'comp_orden': a.subcomponente.componente.orden,
            'sub_nombre': a.subcomponente.nombre,
            'sub_orden': a.subcomponente.orden,
        }

    # === Orden final de columnas: Componente.orden, Subcomponente.orden, Modulo.codificacion/nombre, Reactivo.id ===
    def sort_key(reactivo):
        modulo = getattr(reactivo, 'modulo', None)
        modulo_id = getattr(modulo, 'id', None)
        cod = getattr(modulo, 'codificacion', '') or ''
        mnombre = getattr(modulo, 'nombre', '') or ''
        info = asig_por_modulo.get(modulo_id)
        if info:
            comp_o = info['comp_orden']
            comp_n = info['comp_nombre']
            sub_o  = info['sub_orden']
            sub_n  = info['sub_nombre']
        else:
            # Reactivos sin asignación se van al final agrupados
            comp_o = 9999
            comp_n = 'Sin asignación'
            sub_o  = 9999
            sub_n  = 'Sin asignación'
        modulo_orden = (cod or mnombre)
        return (comp_o, comp_n, sub_o, sub_n, modulo_orden, reactivo.id)

    reactivos_list = sorted(reactivos_list, key=sort_key)

    # === Cabeceras paralelas ya con el orden correcto ===
    comp_names, sub_names, mod_names = [], [], []
    for rx in reactivos_list:
        modulo_obj = getattr(rx, 'modulo', None)
        codigo = getattr(modulo_obj, 'codificacion', '') if modulo_obj else ''
        nombre = getattr(modulo_obj, 'nombre', '') if modulo_obj else ''
        modulo_nombre = f"{codigo} — {nombre}" if codigo else (nombre or '—')

        modulo_id = getattr(modulo_obj, 'id', None)
        info = asig_por_modulo.get(modulo_id)
        if info:
            comp_names.append(info['comp_nombre'])
            sub_names.append(info['sub_nombre'])
        else:
            comp_names.append('Sin asignación')
            sub_names.append('Sin asignación')
        mod_names.append(modulo_nombre)

    # === Calcular tramos contiguos (para merges) ===
    from collections import OrderedDict, defaultdict
    tramo_comp = OrderedDict()            # comp_name -> (start_col, end_col)
    tramo_sub_en_comp = defaultdict(list) # comp_name -> list of (sub_name, start_col, end_col)

    def calcular_tramos(nombres):
        tramos = []
        actual, start = None, 0
        for i, name in enumerate(nombres):
            if actual is None:
                actual, start = name, i
            elif name != actual:
                tramos.append((actual, start, i - 1))
                actual, start = name, i
        if actual is not None:
            tramos.append((actual, start, len(nombres) - 1))
        return tramos

    # Columnas fijas
    row_comp, row_sub, row_mod, row_head, row_start_data = 0, 1, 2, 3, 4
    base_col = 4  # 0:Estudiante, 1:Usuario, 2:Sexo, 3:Calificación -> reactivos desde 4

    tramos_comp = calcular_tramos(comp_names)
    for comp_name, s, e in tramos_comp:
        tramo_comp[comp_name] = (base_col + s, base_col + e)
        sub_tramos = calcular_tramos(sub_names[s:e+1])
        for (sub_name, ss, ee) in sub_tramos:
            tramo_sub_en_comp[comp_name].append((sub_name, base_col + s + ss, base_col + s + ee))

    # === Crear Excel ===
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {"in_memory": True})
    ws = workbook.add_worksheet("Resultados")

    # Formatos
    header    = workbook.add_format({"bold": True, "align": "center", "valign": "vcenter", "border": 1})
    subheader = workbook.add_format({"align": "center", "valign": "vcenter", "border": 1})
    cell      = workbook.add_format({})
    num2      = workbook.add_format({"num_format": "0.00"})
    num3      = workbook.add_format({"num_format": "0.000"})
    total_fmt = workbook.add_format({"bold": True, "top": 1})

    # Encabezados fijos
    ws.write(row_head, 0, "Estudiante", header)
    ws.write(row_head, 1, "Usuario", header)
    ws.write(row_head, 2, "Sexo", header)
    ws.write(row_head, 3, "Calificación", header)

    # Componente (merge), Subcomponente (merge), Módulo (por columna) y Enunciado (por columna)
    if reactivos_list:
        for comp_name, (c0, c1) in tramo_comp.items():
            ws.merge_range(row_comp, c0, row_comp, c1, comp_name, header)
            for (sub_name, s0, s1) in tramo_sub_en_comp[comp_name]:
                ws.merge_range(row_sub, s0, row_sub, s1, sub_name, subheader)

        for i, modulo_nombre in enumerate(mod_names):
            ws.write(row_mod, base_col + i, modulo_nombre, subheader)

        for i, rx in enumerate(reactivos_list):
            ws.write(row_head, base_col + i, strip_tags(rx.enunciado)[:50], header)

    # === Datos ===
    valor_preg = Decimal(evaluacion.valorpregunta)
    for row, m in enumerate(matriculas, start=row_start_data):
        est = m.usuario
        # Sexo
        perfil = perfiles.get(est.id)
        sexo_val = ''
        if perfil and perfil.sexo:
            sexo_val = {'M': 'Masculino', 'F': 'Femenino', 'O': 'Otro'}.get(perfil.sexo, perfil.sexo)

        ws.write(row, 0, f"{est.first_name} {est.last_name}", cell)
        ws.write(row, 1, est.username, cell)
        ws.write(row, 2, sexo_val, cell)

        evaluacion_est = eval_est_por_usuario.get(est.id)
        calificacion = float(evaluacion_est.calificacion) if (evaluacion_est and evaluacion_est.calificacion is not None) else ""
        ws.write(row, 3, calificacion, num2 if calificacion != "" else cell)

        # Puntaje por reactivo (valorpregunta si correcta, 0 si incorrecta, "" si sin respuesta)
        for i, rx in enumerate(reactivos_list):
            col = base_col + i
            puntaje = ""
            if evaluacion_est:
                resp = respuestas_dict.get(evaluacion_est.id, {}).get(rx.id)
                if resp is not None and resp.respuesta_estudiante:
                    puntaje = float(valor_preg) if resp.correcta else 0.0

            if puntaje == "":
                ws.write(row, col, "", cell)
            else:
                # Si valorpregunta tiene 3 decimales, usamos num3; si no, num2
                try:
                    use_num3 = evaluacion.valorpregunta.as_tuple().exponent < -2
                except Exception:
                    use_num3 = False
                ws.write(row, col, puntaje, num3 if use_num3 else num2)

    # === Fila de promedio por reactivo ===
    last_row = row_start_data + len(matriculas)
    if reactivos_list and last_row > row_start_data:
        ws.write(last_row, 0, "Promedio por reactivo", total_fmt)
        ws.write(last_row, 1, "", total_fmt)
        ws.write(last_row, 2, "", total_fmt)
        ws.write(last_row, 3, "", total_fmt)
        for i in range(len(reactivos_list)):
            col = base_col + i
            col_letter = xlsxwriter.utility.xl_col_to_name(col)
            # Promedia solo números; AVERAGE ignora celdas vacías
            formula = f"=AVERAGE({col_letter}{row_start_data+1}:{col_letter}{last_row})"
            ws.write_formula(last_row, col, formula, total_fmt)

    # Anchos de columnas
    ws.set_column(0, 0, 28)   # Estudiante
    ws.set_column(1, 1, 16)   # Usuario
    ws.set_column(2, 2, 10)   # Sexo
    ws.set_column(3, 3, 14)   # Calificación
    if reactivos_list:
        ws.set_column(base_col, base_col + len(reactivos_list) - 1, 12)

    workbook.close()
    output.seek(0)

    filename = f"resultados_{programa.id}_{evaluacion.tipo}.xlsx"
    response = HttpResponse(
        output.read(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename=\"{filename}\"'
    return response


# === 1) Pantalla de estructura del programa ===
@login_required
def estructura_rae_programa(request, programa_id):
    programa = get_object_or_404(ProgramaPosgrado, id=programa_id)

    # Para encabezados (siguiendo tu estilo)
    maestria = programa.maestria
    maestrianombre = Maestrias.objects.get(id=maestria)
    periodoacademico = programa.periodoacademico
    periodoacademiconombre = PeriodosAcademicos.objects.get(id=periodoacademico)
    modalidad = programa.modalidad
    modalidadnombre = Modalidad.objects.get(id=modalidad)

    componentes = (
        ComponenteRAE.objects.filter(programa=programa)
        .prefetch_related('subcomponentes__modulos_asignados__modulo')
        .order_by('orden', 'id')
    )

    # Módulos de la maestría (útil para mostrar si hay sin asignar)
    modulos_maestria = Modulos.objects.filter(maestria=maestria).order_by('codificacion', 'nombre')

    # Módulos ya utilizados en alguna asignación
    usados_ids = SubcomponenteModuloRAE.objects.filter(
        subcomponente__componente__programa=programa
    ).values_list('modulo_id', flat=True)

    modulos_sin_asignar = modulos_maestria.exclude(id__in=usados_ids)

    return render(request, 'estructura_rae_programa.html', {
        'programa': programa,
        'maestrianombre': maestrianombre,
        'periodoacademiconombre': periodoacademiconombre,
        'modalidadnombre': modalidadnombre,
        'componentes': componentes,
        'modulos_sin_asignar': modulos_sin_asignar,
    })


# === 2) Crear componente + subcomponentes (inline) ===
@login_required
def componente_rae_create(request, programa_id):
    programa = get_object_or_404(ProgramaPosgrado, id=programa_id)
    if request.method == 'POST':
        form = ComponenteRAEForm(request.POST)
        if form.is_valid():
            componente = form.save(commit=False)
            componente.programa = programa
            componente.save()
            formset = SubcomponenteFormSet(request.POST, instance=componente)
            if formset.is_valid():
                formset.save()
                messages.success(request, 'Componente creado correctamente.')
                return redirect('estructura_rae_programa', programa_id=programa.id)
            else:
                # Si el inline tiene errores, no perder el componente
                componente.delete()
        else:
            formset = SubcomponenteFormSet(request.POST)
    else:
        form = ComponenteRAEForm()
        formset = SubcomponenteFormSet()

    return render(request, 'componente_form.html', {
        'programa': programa,
        'form': form,
        'formset': formset,
        'accion': 'Crear'
    })


# === 3) Editar componente + subcomponentes ===
@login_required
def componente_rae_update(request, componente_id):
    componente = get_object_or_404(ComponenteRAE, id=componente_id)
    programa = componente.programa

    if request.method == 'POST':
        form = ComponenteRAEForm(request.POST, instance=componente)
        formset = SubcomponenteFormSet(request.POST, instance=componente)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Componente actualizado correctamente.')
            return redirect('estructura_rae_programa', programa_id=programa.id)
    else:
        form = ComponenteRAEForm(instance=componente)
        formset = SubcomponenteFormSet(instance=componente)

    return render(request, 'componente_form.html', {
        'programa': programa,
        'form': form,
        'formset': formset,
        'accion': 'Editar'
    })


# === 4) Eliminar componente (cascada a subcomponentes y asignaciones) ===
@login_required
def componente_rae_delete(request, componente_id):
    componente = get_object_or_404(ComponenteRAE, id=componente_id)
    programa = componente.programa
    if request.method == 'POST':
        componente.delete()
        messages.success(request, 'Componente eliminado.')
        return redirect('estructura_rae_programa', programa_id=programa.id)
    return render(request, 'confirm_delete.html', {
        'obj': componente,
        'back_url': reverse('estructura_rae_programa', args=[programa.id])
    })


# === 5) Asignar módulos a un subcomponente ===
@login_required
def subcomponente_asignar_modulos(request, subcomponente_id):
    sub = get_object_or_404(SubcomponenteRAE, id=subcomponente_id)
    programa = sub.componente.programa

    if request.method == 'POST':
        form = SubcomponenteAsignarModulosForm(request.POST, subcomponente=sub)
        if form.is_valid():
            form.save()
            messages.success(request, 'Asignaciones de módulos guardadas correctamente.')
            return redirect('estructura_rae_programa', programa_id=programa.id)
    else:
        form = SubcomponenteAsignarModulosForm(subcomponente=sub)

    return render(request, 'subcomponente_asignar_modulos.html', {
        'programa': programa,
        'subcomponente': sub,
        'form': form
    })


# === 6) Eliminar subcomponente (si lo necesitas explícito) ===
@login_required
def subcomponente_rae_delete(request, subcomponente_id):
    sub = get_object_or_404(SubcomponenteRAE, id=subcomponente_id)
    programa = sub.componente.programa
    if request.method == 'POST':
        sub.delete()
        messages.success(request, 'Subcomponente eliminado.')
        return redirect('estructura_rae_programa', programa_id=programa.id)
    return render(request, 'confirm_delete.html', {
        'obj': sub,
        'back_url': reverse('estructura_rae_programa', args=[programa.id])
    })