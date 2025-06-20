from django.shortcuts import render
from programasposgrado.models import ProgramaPosgrado, Maestrias, PeriodosAcademicos, PerfildeIngreso, Modalidad
from django.contrib.auth.decorators import login_required


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

def programasdemaestria(request):
    programasdeposgrado_list = ProgramaPosgrado.objects.all().order_by('-created')
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
def ProgramaMaestria(request , programa_id):
    programaposgrado = ProgramaPosgrado.objects.get(id=programa_id)
    maestria = programaposgrado.maestria
    maestrianombre = Maestrias.objects.get(id=maestria)
    periodoacademico = programaposgrado.periodoacademico
    periodoacademiconombre = PeriodosAcademicos.objects.get(id=periodoacademico)
    modalidad = programaposgrado.modalidad
    modalidadnombre = Modalidad.objects.get(id=modalidad)

    return render(request, 'programamaestria.html', {
        'programaposgrado': programaposgrado,
        'maestrianombre': maestrianombre,
        'periodoacademiconombre': periodoacademiconombre,
        'modalidadnombre': modalidadnombre,
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


