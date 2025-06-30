from django.shortcuts import render
from usuarios.models import PerfilUsuario,User
from programasposgrado.models import PeriodosAcademicos, ProgramaPosgrado, Maestrias, Modalidad, Modulos
from seleccionperfiles.models import TernaModuloPM
from django.contrib import messages

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

def datosmodulossp(request, programa_id):
    programapostrgrado = ProgramaPosgrado.objects.filter(id=programa_id).first()  
    maestria = Maestrias.objects.filter(id=programapostrgrado.maestria).first() if programapostrgrado else None
    print(maestria)
    modulos_list = Modulos.objects.filter(maestria=maestria.id)
    return render(request, 'datosmodulos_sp.html', {
        'programa_id': programa_id,
        'maestria': maestria,
        'modulos_list': modulos_list,
    })

def ternamodulopmsp(request, programa_id, modulo_id):
    terna = TernaModuloPM.objects.filter(modulo_id=modulo_id).first()
    if not terna:
        messages.error(
                request, "Aún no existe una terna.")
    
    return render(request, 'terna_sp.html', {
        'terna': terna,
        'modulo_id': modulo_id,
        'programa_id': programa_id,
    })

def crearternamodulopmmsp(request, programa_id, modulo_id):
    print(modulo_id,  programa_id)
    terna = TernaModuloPM.objects.filter(modulo=modulo_id, programa_posgrado=programa_id).first()
    if request.method == 'POST':
        docente1_idoneo_id = User.objects.get(id=d.docente)
        docente2_id = request.POST.get('docente2')  
        docente3_id = request.POST.get('docente3')
        responsable_id = request.POST.get('responsable')
        fecha_creacion = request.POST.get('fecha_creacion')
        messages.success(request, "Terna creada exitosamente.")
        return render(request, 'crear_terna_sp.html', {
            'terna': None,
        })
    else:
        messages.error(request, "Error al crear la terna.")
    
    return render(request, 'crear_terna_sp.html', {
        'terna': terna,
        'docente1_idoneo': docente1_idoneo_id,
        'docente2': docente2_id,
        'docente3': docente3_id,
        'responsable': responsable_id,
        'fecha_creacion': fecha_creacion,
        'programa_id': programa_id,
        'modulo_id': modulo_id, 
    })