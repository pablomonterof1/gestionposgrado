from django.shortcuts import render
from usuarios.models import PerfilUsuario
from programasposgrado.models import PeriodosAcademicos, ProgramaPosgrado, Maestrias, Modalidad

# Create your views here.
def seleccionp(request):
    perfiles_list = PerfilUsuario.objects.all()
    return render(request, 'seleccionp.html', {
        'perfiles_list': perfiles_list,
    })

def periodosacademicosp(request):
    periodosacademicos_list = PeriodosAcademicos.objects.all()
    return render(request, 'periodosacademicos_sp.html', {
        'periodosacademicos_list': periodosacademicos_list,
    })

def datosposgradosp(request, periodo_id):
    programaposgrado_list = ProgramaPosgrado.objects.filter(periodoacademico=periodo_id)
    for programa in programaposgrado_list:
        programa.maestria = Maestrias.objects.filter(id=programa.maestria).first()
        programa.periodoacademico = PeriodosAcademicos.objects.filter(id=programa.periodoacademico).first()
        programa.modalidad = Modalidad.objects.filter(id=programa.modalidad).first()
    return render(request, 'datosposgrado_sp.html', {
        'periodo_id': periodo_id,
        'programaposgrado_list': programaposgrado_list,
    })