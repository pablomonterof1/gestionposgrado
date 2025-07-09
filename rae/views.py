from datetime import timezone
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from random import sample
from usuarios.models import MatriculaUsuario
from .models import ReactivosMultipleChoice, ReactivosModuloRAE, EvaluacionPrograma, EvaluacionEstudiante, ReactivoEvaluacion
from programasposgrado.models import Maestrias, PeriodosAcademicos, Modalidad, ProgramaPosgrado, Modulos
from django.contrib.auth.decorators import login_required
from .forms import ReactivosMultipleChoiceForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from main.views import es_estudiante, es_docente, es_coordinador, es_editor
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType


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
            reactivo.modulo = modulo_id
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
            reactivo.modulo = modulo_id
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
            return redirect('reactivosmodulo', programa_id=programadeposgrado.id, modulo_id=modulo_id)
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
            return redirect('reactivosmodulodocente', programa_id=programadeposgrado.id, modulo_id=modulo_id)
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
            return redirect('reactivosmodulo', programa_id=programadeposgrado.id, modulo_id=modulo_id)
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
        return redirect('reactivosmodulo', programa_id=programa_id, modulo_id=modulo_id)
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
        return redirect('reactivosmodulodocente', programa_id=programa_id, modulo_id=modulo_id)
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
    for modulo in modulos_list:
        modulo.reactivos = ReactivosMultipleChoice.objects.filter(
            programadeposgrado=programa_id, modulo=modulo.id)
        modulo.numeroreactivosmodulorae = ReactivosModuloRAE.objects.filter(
            programadeposgrado=programa_id, modulo=modulo.id).first()

    return render(request, 'rae_programaposgrado.html', {
        'maestrianombre': maestrianombre,
        'periodoacademiconombre': periodoacademiconombre,
        'modalidadnombre': modalidadnombre,
        'programaposgrado': programaposgrado,
        'modulos_list': modulos_list,
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
            modulo=modulo_id,
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
    evaluaciones = EvaluacionPrograma.objects.filter(programa=programa)

    return render(request, 'evaluacionrae_programaposgrado.html', {
        'programa': programa,
        'evaluaciones': evaluaciones
    })


def obtener_reactivos_para_evaluacion(programa, tipo):
    reactivos_seleccionados = []

    # Obtener la maestría desde el programa
    maestria_id = programa.maestria
    modulos = Modulos.objects.filter(maestria_id=maestria_id)

    # Obtener reactivos ya usados en evaluaciones anteriores del mismo tipo
    evaluaciones_previas = EvaluacionPrograma.objects.filter(programa=programa, tipo=tipo)
    reactivos_usados_ids = ReactivoEvaluacion.objects.filter(
        evaluacion_estudiante__evaluacion__in=evaluaciones_previas
    ).values_list('reactivo_id', flat=True)

    for modulo in modulos:
        # Obtener la cantidad de reactivos definidos para este módulo
        config = ReactivosModuloRAE.objects.filter(
            programadeposgrado=programa,
            modulo=modulo.id
        ).first()

        if not config or config.numero_reactivos_modulo <= 0:
            continue

        # Obtener los reactivos disponibles que aún no se han usado
        reactivos_disponibles = ReactivosMultipleChoice.objects.filter(
            modulo=modulo.id,
            programadeposgrado=programa
        ).exclude(id__in=reactivos_usados_ids)

        # Seleccionar aleatoriamente los necesarios
        seleccionados = list(reactivos_disponibles.order_by('?')[:config.numero_reactivos_modulo])
        reactivos_seleccionados.extend(seleccionados)

    return reactivos_seleccionados


@login_required
def evaluacionrae_activar(request, programa_id, tipo):
    programa = get_object_or_404(ProgramaPosgrado, id=programa_id)
    if request.method == 'POST':
        fecha_inicio = request.POST['fecha_inicio']
        fecha_fin = request.POST['fecha_fin']
        evaluacion, created = EvaluacionPrograma.objects.update_or_create(
            programa=programa,
            tipo=tipo,
            defaults={
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin,
                'activa': True
            }
        )

        # Asignar a todos los estudiantes matriculados
        content_type = ContentType.objects.get_for_model(ProgramaPosgrado)
        estudiantes = MatriculaUsuario.objects.filter(
            content_type=content_type,
            object_id=programa.id,
            rol_en_programa='estudiante'
        )
        for est in estudiantes:
            evaluacion_estudiante = EvaluacionEstudiante.objects.create(
                evaluacion=evaluacion,
                estudiante=est.usuario
            )
            reactivos = obtener_reactivos_para_evaluacion(programa, tipo)
            for reactivo in reactivos:
                ReactivoEvaluacion.objects.create(
                    evaluacion_estudiante=evaluacion_estudiante,
                    reactivo=reactivo
                )
        messages.success(request, f"Evaluación {tipo} activada correctamente.")
        return redirect('evaluacionrae_programaposgrado', programa_id=programa.id)

    return render(request, 'evaluacionrae_activar.html', {
        'programa': programa,
        'tipo': tipo
    })



@login_required
def evaluacionrae_rendir(request, evaluacion_id):
    evaluacion_est = get_object_or_404(EvaluacionEstudiante, evaluacion__id=evaluacion_id, estudiante=request.user)

    if timezone.now() < evaluacion_est.evaluacion.fecha_inicio or timezone.now() > evaluacion_est.evaluacion.fecha_fin:
        return HttpResponseForbidden("Evaluación no disponible")

    reactivos = ReactivoEvaluacion.objects.filter(evaluacion_estudiante=evaluacion_est)

    if request.method == 'POST':
        score = 0
        for reactivo_eval in reactivos:
            respuesta = request.POST.get(f"pregunta_{reactivo_eval.id}")
            reactivo_eval.respuesta_estudiante = respuesta
            reactivo_eval.correcta = (respuesta == reactivo_eval.reactivo.respuesta_correcta)
            if reactivo_eval.correcta:
                score += 2
            reactivo_eval.save()
        evaluacion_est.calificacion = score
        evaluacion_est.respondido = True
        evaluacion_est.save()
        messages.success(request, f"Evaluación finalizada. Calificación: {score}/100")
        return redirect('mis_cursos')

    return render(request, 'rendir_evaluacion.html', {
        'reactivos': reactivos,
        'evaluacion_est': evaluacion_est
    })