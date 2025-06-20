from django.shortcuts import render, redirect, get_object_or_404
from .models import ComposicionCA, GestionAcademicaCA
from programasposgrado.models import ProgramaPosgrado, Maestrias, PeriodosAcademicos, Modalidad
from django.contrib.auth.decorators import login_required


# Create your views here.


######################################## COMPOSICIÓN###########################################
@login_required
def composicion(request, programa_id):
    composicion_list = ComposicionCA.objects.filter(programadeposgrado=programa_id).order_by('tipodedato')
    programaposgrado = get_object_or_404(ProgramaPosgrado, id=programa_id)
    maestria = programaposgrado.maestria
    maestrianombre = Maestrias.objects.get(id=maestria)
    periodoacademico = programaposgrado.periodoacademico
    periodoacademiconombre = PeriodosAcademicos.objects.get(id=periodoacademico)
    modalidad = programaposgrado.modalidad
    modalidadnombre = Modalidad.objects.get(id=modalidad)

    return render(request, 'composicionca.html', {
        'composicion_list': composicion_list,
        'programaposgrado': programaposgrado,
        'maestrianombre': maestrianombre,
        'periodoacademiconombre': periodoacademiconombre,
        'modalidadnombre': modalidadnombre
    })

