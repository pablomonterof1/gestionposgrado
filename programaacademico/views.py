from django.shortcuts import render, redirect, get_object_or_404
from .forms import AdmisionForm, DisenoCurricularForm, TitulacionForm
from .models import Admision, DisenoCurricular, Titulacion
from programasposgrado.models import ProgramaPosgrado, Maestrias, PeriodosAcademicos, Modalidad
from django.contrib.auth.decorators import login_required

import plotly.express as px
from django.utils.safestring import mark_safe
import pandas as pd


######################################## ADMISION###########################################
# Create your views here.
@login_required
def admision(request, programa_id):
    admision_list = Admision.objects.filter(
        programadeposgrado=programa_id).order_by('-valor')
    programaposgrado = ProgramaPosgrado.objects.get(id=programa_id)
    maestria = programaposgrado.maestria
    maestrianombre = Maestrias.objects.get(id=maestria)
    periodoacademico = programaposgrado.periodoacademico
    periodoacademiconombre = PeriodosAcademicos.objects.get(id=periodoacademico)
    modalidad = programaposgrado.modalidad
    modalidadnombre = Modalidad.objects.get(id=modalidad)

    # Gráfico de admisiones
    df = pd.DataFrame(list(admision_list.values('tipodedato', 'valor')))
    if not df.empty:
        fig = px.bar(df, x='tipodedato', y='valor', title='Valores de Admisión',
                     labels={'tipodedato': 'Admisión', 'valor': 'Valor'}, color='valor')
        grafico_html = fig.to_html(full_html=False)
    else:
        grafico_html = "<p>No hay datos disponibles para mostrar el gráfico.</p>"



    return render(request, 'admision.html', {
        'admision_list': admision_list,
        'maestrianombre': maestrianombre,
        'periodoacademiconombre': periodoacademiconombre,
        'modalidadnombre': modalidadnombre,
        'programaposgrado': programaposgrado,
        'grafico': mark_safe(grafico_html)
    })


@login_required
def admision_create(request, programa_id):
    programaposgrado = ProgramaPosgrado.objects.get(id=programa_id)
    maestria = programaposgrado.maestria
    maestrianombre = Maestrias.objects.get(id=maestria)
    periodoacademico = programaposgrado.periodoacademico
    periodoacademiconombre = PeriodosAcademicos.objects.get(id=periodoacademico)
    modalidad = programaposgrado.modalidad
    modalidadnombre = Modalidad.objects.get(id=modalidad)
    if request.method == 'POST':
        try:
            form = AdmisionForm(request.POST)
            form.instance.programadeposgrado = programaposgrado
            form.save()
            return redirect('admision', programa_id=programa_id)
        except ValueError:
            return render(request, 'admision_create.html', {
                'form': AdmisionForm,
                'error': 'Error al crear la admisión'
            })
    else:
        return render(request, 'admision_create.html', {
            'form': AdmisionForm,
            'programa_id': programa_id,
            'maestrianombre': maestrianombre,
            'periodoacademiconombre': periodoacademiconombre,
            'modalidadnombre': modalidadnombre,
        })


@login_required
def admision_detail(request, admision_id):
    if request.method == 'POST':
        admision = get_object_or_404(Admision, id=admision_id)
        admisionform = AdmisionForm(request.POST, instance=admision)
        if admisionform.is_valid():
            admisionform.save()
            return redirect('admision', programa_id=admision.programadeposgrado.id)
    else:
        admision = get_object_or_404(Admision, id=admision_id)
        admisionform = AdmisionForm(instance=admision)
        return render(request, 'admision_detail.html', {
            'admision': admision,
            'admisionform': admisionform
        })


@login_required
def admision_delete(request, admision_id,):

    admision = get_object_or_404(Admision, id=admision_id)

    if request.method == 'POST':
        admision.delete()
        return redirect('admision', programa_id=admision.programadeposgrado.id)
    else:
        return render(request, 'admision',  {
            'error': 'Error al eliminar la admisión',
        })


######################################## DISEÑOCURRICULAR###########################################

@login_required
def disenocurricular(request, programa_id):
    disenodisenocurricular_list = DisenoCurricular.objects.filter(
        programadeposgrado=programa_id).order_by('tipodedato')
    programaposgrado = ProgramaPosgrado.objects.get(id=programa_id)
    maestria = programaposgrado.maestria
    maestrianombre = Maestrias.objects.get(id=maestria)
    periodoacademico = programaposgrado.periodoacademico
    periodoacademiconombre = PeriodosAcademicos.objects.get(id=periodoacademico)
    modalidad = programaposgrado.modalidad
    modalidadnombre = Modalidad.objects.get(id=modalidad)

    return render(request, 'disenocurricular.html', {
        'disenodisenocurricular_list': disenodisenocurricular_list,
        'maestrianombre': maestrianombre,
        'periodoacademiconombre': periodoacademiconombre,
        'modalidadnombre': modalidadnombre,
        'programaposgrado': programaposgrado,

    })


@login_required
def disenocurricular_create(request, programa_id):
    programaposgrado = ProgramaPosgrado.objects.get(id=programa_id)
    maestria = programaposgrado.maestria
    maestrianombre = Maestrias.objects.get(id=maestria)
    periodoacademico = programaposgrado.periodoacademico
    periodoacademiconombre = PeriodosAcademicos.objects.get(id=periodoacademico)
    modalidad = programaposgrado.modalidad
    modalidadnombre = Modalidad.objects.get(id=modalidad)
    if request.method == 'POST':
        try:
            form = DisenoCurricularForm(request.POST)
            form.instance.programadeposgrado = programaposgrado
            form.save()
            return redirect('disenocurricular', programa_id=programa_id)
        except ValueError:
            return render(request, 'disenocurricular_create.html', {
                'form': DisenoCurricularForm,
                'error': 'Error al crear el diseño curricular'
            })
    else:
        return render(request, 'disenocurricular_create.html', {
            'form': DisenoCurricularForm,
            'programa_id': programa_id,
            'maestrianombre': maestrianombre,
            'periodoacademiconombre': periodoacademiconombre,
            'modalidadnombre': modalidadnombre,
        })


@login_required
def disenocurricular_detail(request, disenocurricular_id):
    if request.method == 'POST':
        disenocurricular = get_object_or_404(
            DisenoCurricular, id=disenocurricular_id)
        disenocurricularform = DisenoCurricularForm(
            request.POST, instance=disenocurricular)
        if disenocurricularform.is_valid():
            disenocurricularform.save()
            return redirect('disenocurricular', programa_id=disenocurricular.programadeposgrado.id)
    else:
        disenocurricular = get_object_or_404(
            DisenoCurricular, id=disenocurricular_id)
        disenocurricularform = DisenoCurricularForm(instance=disenocurricular)
        return render(request, 'disenocurricular_detail.html', {
            'disenocurricular': disenocurricular,
            'disenocurricularform': disenocurricularform
        })


@login_required
def disenocurricular_delete(request, disenocurricular_id,):

    disenocurricular = get_object_or_404(
        DisenoCurricular, id=disenocurricular_id)

    if request.method == 'POST':
        disenocurricular.delete()
        return redirect('disenocurricular', programa_id=disenocurricular.programadeposgrado.id)
    else:
        return render(request, 'disenocurricular',  {
            'error': 'Error al eliminar el diseño curricular',
        })


######################################## TITULACIÓN###########################################

@login_required
def titulacion(request, programa_id):
    titulacion_list = Titulacion.objects.filter(
        programadeposgrado=programa_id).order_by('tipodedato')
    programaposgrado = ProgramaPosgrado.objects.get(id=programa_id)
    maestria = programaposgrado.maestria
    maestrianombre = Maestrias.objects.get(id=maestria)
    periodoacademico = programaposgrado.periodoacademico
    periodoacademiconombre = PeriodosAcademicos.objects.get(id=periodoacademico)
    modalidad = programaposgrado.modalidad
    modalidadnombre = Modalidad.objects.get(id=modalidad)

    # Gráfico de titulación
    df = pd.DataFrame(list(titulacion_list.values('nombre', 'valor')))
    if not df.empty:
        fig = px.pie(df, names='nombre', values='valor', title='Tilulación x programa',
                     labels={'nombre': 'Nombre', 'valor': 'Valor'}, color='valor')
         # Tamaño del gráfico
        fig.update_layout(
        width=800,  # Ancho del gráfico en píxeles
        height=600  # Alto del gráfico en píxeles
        )
        grafico_html = fig.to_html(full_html=False)
    else:
        grafico_html = "<p>No hay datos disponibles para mostrar el gráfico.</p>"
    
   
    return render(request, 'titulacion.html', {
        'titulacion_list': titulacion_list,
        'maestrianombre': maestrianombre,
        'periodoacademiconombre': periodoacademiconombre,
        'modalidadnombre': modalidadnombre,
        'programaposgrado': programaposgrado,
        'grafico': mark_safe(grafico_html)

    })


@login_required
def titulacion_create(request, programa_id):
    programaposgrado = ProgramaPosgrado.objects.get(id=programa_id)
    maestria = programaposgrado.maestria
    maestrianombre = Maestrias.objects.get(id=maestria)
    periodoacademico = programaposgrado.periodoacademico
    periodoacademiconombre = PeriodosAcademicos.objects.get(id=periodoacademico)
    modalidad = programaposgrado.modalidad
    modalidadnombre = Modalidad.objects.get(id=modalidad)
    if request.method == 'POST':
        try:
            form = TitulacionForm(request.POST)
            form.instance.programadeposgrado = programaposgrado
            form.save()
            return redirect('titulacion', programa_id=programa_id)
        except ValueError:
            return render(request, 'titulacion_create.html', {
                'form': TitulacionForm,
                'error': 'Error al crear la titulación'
            })
    else:
        return render(request, 'titulacion_create.html', {
            'form': TitulacionForm,
            'programa_id': programa_id,
            'maestrianombre': maestrianombre,
            'periodoacademiconombre': periodoacademiconombre,
            'modalidadnombre': modalidadnombre,
        })


@login_required
def titulacion_detail(request, titulacion_id):
    if request.method == 'POST':
        titulacion = get_object_or_404(Titulacion, id=titulacion_id)
        titulacionform = TitulacionForm(request.POST, instance=titulacion)
        if titulacionform.is_valid():
            titulacionform.save()
            return redirect('titulacion', programa_id=titulacion.programadeposgrado.id)
    else:
        titulacion = get_object_or_404(Titulacion, id=titulacion_id)
        titulacionform = TitulacionForm(instance=titulacion)
        return render(request, 'titulacion_detail.html', {
            'titulacion': titulacion,
            'titulacionform': titulacionform
        })


@login_required
def titulacion_delete(request, titulacion_id,):

    titulacion = get_object_or_404(Titulacion, id=titulacion_id)

    if request.method == 'POST':
        titulacion.delete()
        return redirect('titulacion', programa_id=titulacion.programadeposgrado.id)
    else:
        return render(request, 'titulacion',  {
            'error': 'Error al eliminar la titulación',
        })
