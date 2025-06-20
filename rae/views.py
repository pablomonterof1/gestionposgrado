from django.shortcuts import render, redirect
from .models import ReactivosMultipleChoice
from programasposgrado.models import Maestrias, PeriodosAcademicos, Modalidad, ProgramaPosgrado, Modulos
from django.contrib.auth.decorators import login_required
from .forms import ReactivosMultipleChoiceForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from main.views import es_estudiante, es_docente, es_coordinador, es_editor
from django.contrib import messages

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
<<<<<<< HEAD
    reactivos_list = ReactivosMultipleChoice.objects.filter(
        modulo=modulo_id).order_by('created')
=======
    reactivos_list = ReactivosMultipleChoice.objects.filter(modulo=modulo_id, programadeposgrado=programa_id).order_by('created')
>>>>>>> bb1335e6b4376e4f100ad702bb93f9266f0a92d4
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

<<<<<<< HEAD
=======
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

>>>>>>> bb1335e6b4376e4f100ad702bb93f9266f0a92d4

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

<<<<<<< HEAD
=======
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
                request, "Revise que todos los campos sean válidos o ya existe un reactivo con este enunciado.")
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

>>>>>>> bb1335e6b4376e4f100ad702bb93f9266f0a92d4

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

<<<<<<< HEAD
=======
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

>>>>>>> bb1335e6b4376e4f100ad702bb93f9266f0a92d4

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

<<<<<<< HEAD
=======
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

>>>>>>> bb1335e6b4376e4f100ad702bb93f9266f0a92d4

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
