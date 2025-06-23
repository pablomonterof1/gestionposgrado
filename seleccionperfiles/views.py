from django.shortcuts import render
from usuarios.models import PerfilUsuario
from programasposgrado.models import PeriodosAcademicos, ProgramaPosgrado, Maestrias, Modalidad, Modulos

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

def datosmodulos(request, programa_id):
    programapostrgrado = ProgramaPosgrado.objects.filter(id=programa_id).first()  
    maestria = Maestrias.objects.filter(id=programapostrgrado.maestria).first() if programapostrgrado else None
    print(maestria)
    modulos_list = Modulos.objects.filter(maestria=maestria.id)
    return render(request, 'datosmodulos.html', {
        'programa_id': programa_id,
        'maestria': maestria,
        'modulos_list': modulos_list,
    })


def ternamodulopm(request, modulo_id):
    modulos = Modulos.objects.filter(id=modulo_id).first()
    if not modulos:
        return render(request, 'error.html', {'message': 'Módulo no encontrado.'})
    
    terna_modulo_pm = modulos.terna_modulopm.all()
    
    return render(request, 'ternamodulopm.html', {
        'modulo': modulos,
        'terna_modulo_pm': terna_modulo_pm,
    })