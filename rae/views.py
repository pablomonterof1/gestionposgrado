from django.shortcuts import render, redirect
from .models import ReactivosMultipleChoice
from programasposgrado.models import Maestrias, PeriodosAcademicos, Modalidad, ProgramaPosgrado, Modulos
from django.contrib.auth.decorators import login_required
from .forms import ReactivosMultipleChoiceForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from main.views import es_estudiante, es_docente, es_coordinador, es_editor

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
    periodoacademiconombre = PeriodosAcademicos.objects.get(id=periodoacademico)
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
    reactivos_list = ReactivosMultipleChoice.objects.filter(modulo=modulo_id).order_by('created')
    modulo = Modulos.objects.get(id=modulo_id)
    modulonombre = modulo.nombre
    programaposgrado = ProgramaPosgrado.objects.get(id=programa_id)
    maestria = programaposgrado.maestria
    maestrianombre = Maestrias.objects.get(id=maestria)
    periodoacademico = programaposgrado.periodoacademico
    periodoacademiconombre = PeriodosAcademicos.objects.get(id=periodoacademico)
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
            return redirect('reactivosmodulo', programa_id=programa_id, modulo_id=modulo_id)
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