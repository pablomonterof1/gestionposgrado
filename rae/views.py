from django.urls import reverse
from django.utils import timezone
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
import random
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
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa

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
    for modulo in modulos_list:
        modulo.reactivos = ReactivosMultipleChoice.objects.filter(
            programadeposgrado=programa_id, modulo=modulo.id)
        modulo.numeroreactivosmodulorae = ReactivosModuloRAE.objects.filter(
            programadeposgrado=programa_id, modulo=modulo).first()
        modulo.total_reactivos = modulo.reactivos.count()
        modulo.max_para_input = modulo.total_reactivos // 2

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
    evaluaciones = EvaluacionPrograma.objects.filter(programa=programa)

    return render(request, 'evaluacionrae_programaposgrado.html', {
        'programa': programa,
        'evaluaciones': evaluaciones
    })


def obtener_reactivos_para_evaluacion(programa, tipo, estudiante=None):
    

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

        # Excluir los usados en simulacro si estamos generando la evaluación final
        if tipo == 'final':
            simulacro = EvaluacionPrograma.objects.filter(programa=programa, tipo='simulacro').first()
            if simulacro and estudiante:
                usados_ids = ReactivoEvaluacion.objects.filter(
                    evaluacion_estudiante__evaluacion=simulacro,
                    evaluacion_estudiante__estudiante=estudiante
                ).values_list('reactivo_id', flat=True)
                reactivos_query = reactivos_query.exclude(id__in=usados_ids)

        reactivos_list = list(reactivos_query)

        if len(reactivos_list) >= num_reactivos:
            seleccionados = random.sample(reactivos_list, num_reactivos)
        else:
            seleccionados = reactivos_list  # menos de lo necesario, tomar todo

        seleccionados_estudiante.extend(seleccionados)

    return seleccionados_estudiante


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
        reactivos = obtener_reactivos_para_evaluacion(programa, tipo)

        for est in estudiantes:
            evaluacion_estudiante, creado = EvaluacionEstudiante.objects.get_or_create(
                evaluacion=evaluacion,
                estudiante=est.usuario
            )

            # Eliminar los anteriores
            ReactivoEvaluacion.objects.filter(evaluacion_estudiante=evaluacion_estudiante).delete()
            # Obtener los reactivos únicos para este estudiante
            reactivos = obtener_reactivos_para_evaluacion(programa, tipo, estudiante=est.usuario)
            
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
def evaluacionesrae_disponibles(request):
    ahora = timezone.now()
    evaluaciones = EvaluacionEstudiante.objects.filter(
        estudiante=request.user,
        evaluacion__activa=True,
        evaluacion__fecha_inicio__lte=ahora,
        evaluacion__fecha_fin__gte=ahora,
        respondido=False
    ).select_related('evaluacion')
    evaluacionesrealizadas = EvaluacionEstudiante.objects.filter(
        estudiante=request.user,
        respondido=True
    ).select_related('evaluacion')

    return render(request, 'evaluacionesrae_disponibles.html', {
        'evaluaciones': evaluaciones,
        'evaluacionesrealizadas': evaluacionesrealizadas
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

            if respuesta and reactivo_eval.reactivo.correcta == respuesta:
                reactivo_eval.correcta = True
                score += 2
            else:
                reactivo_eval.correcta = False

            reactivo_eval.save()

        evaluacion_est.calificacion = score
        evaluacion_est.respondido = True
        evaluacion_est.save()

        messages.success(request, f"Evaluación finalizada. Calificación: {score}/100")
        return redirect('evaluacionesrae_disponibles')

    return render(request, 'evaluacionrae_rendir.html', {
        'reactivos': reactivos,
        'evaluacion_est': evaluacion_est
    })


@login_required
def resultadorae_estudiante(request, evaluacion_id):
    evaluacion_est = get_object_or_404(
        EvaluacionEstudiante,
        evaluacion__id=evaluacion_id,
        estudiante=request.user
    )

    if not evaluacion_est.respondido:
        return redirect('evaluacionesrae_disponibles')

    reactivos = ReactivoEvaluacion.objects.filter(evaluacion_estudiante=evaluacion_est)

    return render(request, 'resultadorae_estudiante.html', {
        'evaluacion_est': evaluacion_est,
        'reactivos': reactivos,
    })


@login_required
def resultadosrae_programa(request, programa_id, tipo):
    programa = get_object_or_404(ProgramaPosgrado, id=programa_id)
    evaluacion = get_object_or_404(EvaluacionPrograma, programa=programa, tipo=tipo)

    content_type = ContentType.objects.get_for_model(ProgramaPosgrado)
    matriculas = MatriculaUsuario.objects.filter(
        content_type=content_type,
        object_id=programa.id,
        rol_en_programa='estudiante'
    ).select_related('usuario')

    resultados = []
    for mat in matriculas:
        evaluacion_est = EvaluacionEstudiante.objects.filter(evaluacion=evaluacion, estudiante=mat.usuario).first()
        resultados.append({
            'estudiante': mat.usuario,
            'respondido': evaluacion_est.respondido if evaluacion_est else False,
            'calificacion': evaluacion_est.calificacion if evaluacion_est else None,
            'detalle_url': reverse('detalle_resultado_estudiante', args=[evaluacion.id, mat.usuario.id]) if evaluacion_est.respondido else None,
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