from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from usuarios.models import PerfilUsuario, MatriculaUsuario, MatriculaDocenteModulo
from django.db.models import Count
from programasposgrado.models import  Maestrias, PeriodosAcademicos, Modalidad, ProgramaPosgrado, Modulos, ModulosEM
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

# Create your views here.

@login_required
def MisCursos(request):
    # Matriculas del usuario
    usuarioprogramaslist = MatriculaUsuario.objects.filter(usuario=request.user)
    docentemoduloslist = MatriculaDocenteModulo.objects.filter(docente=request.user)

    for estudiante in usuarioprogramaslist:
        maestria = Maestrias.objects.filter(id=estudiante.programa.maestria)
        periodocademico = PeriodosAcademicos.objects.filter(id=estudiante.programa.periodoacademico)
        modalidad = Modalidad.objects.filter(id=estudiante.programa.modalidad)
        if maestria:
            estudiante.maestria = maestria.first()
        else:
            estudiante.maestria = None

        if periodocademico:
            estudiante.periodoacademico = periodocademico.first()
        else:
            estudiante.periodoacademico = None

        if modalidad:
            estudiante.modalidad = modalidad.first()
        else:
            estudiante.modalidad = None

    for docente in docentemoduloslist:
        programa = ProgramaPosgrado.objects.filter(id=docente.programa)
        maestria = Maestrias.objects.filter(id=programa.first().maestria)
        modalidad = Modalidad.objects.filter(id=programa.first().modalidad)
        periodocademico = PeriodosAcademicos.objects.filter(id=programa.first().periodoacademico)
        modulo = Modulos.objects.filter(id=docente.modulo.id)
        moduloem = ModulosEM.objects.filter(id=docente.modulo.id)

        if maestria:
            docente.maestria = maestria.first()
            docente.programa = programa.first()
            docente.modalidad = modalidad.first()
            docente.periodoacademico = periodocademico.first()
            docente.modulo = modulo.first() 
            docente.moduloem = moduloem.first() 
            
        else:
            docente.maestria = None
            docente.programa = None
            docente.modalidad = None
            docente.periodoacademico = None
            docente.modulo = None
            docente.moduloem = None

    # Obtener los conteos de estudiantes por programa para los mismos programas del usuario
    conteos = (
        MatriculaUsuario.objects
        .filter(rol_en_programa='estudiante', content_type__in=usuarioprogramaslist.values('content_type'), object_id__in=usuarioprogramaslist.values('object_id'))
        .values('content_type', 'object_id')
        .annotate(total_estudiantes=Count('id'))
    )

    # Crear un dict para acceso rápido: {(content_type_id, object_id): total}
    conteo_dict = {
        (item['content_type'], item['object_id']): item['total_estudiantes']
        for item in conteos
    }

    # Añadir el conteo a cada matrícula del usuario
    for estudiante in usuarioprogramaslist:
        key = (estudiante.content_type.id, estudiante.object_id)
        estudiante.total_estudiantes = conteo_dict.get(key, 0)

    return render(request, 'mis_cursos.html', {
        'usuarioprogramaslist': usuarioprogramaslist,
        'docentemoduloslist': docentemoduloslist
    })


def AulaVirtual_Docente(request, programa_id, modulo_id):
    programadeposgrado = get_object_or_404(ProgramaPosgrado, id=programa_id)
    modulo = get_object_or_404(Modulos, id=modulo_id)
    return render(request, 'aulavirtual_docente.html', {
        'programadeposgrado': programadeposgrado,
        'modulo': modulo
    })

def AulaVirtual_Estudiante(request, programa_id):
    programadeposgrado = get_object_or_404(ProgramaPosgrado, id=programa_id)
    modulos_list = Modulos.objects.filter(maestria=programadeposgrado.maestria)
    for modulo in modulos_list:
        matriculadocebte = MatriculaDocenteModulo.objects.filter(object_id=modulo.id)
        docente = User.objects.filter(id__in=matriculadocebte.values_list('docente'))
        if matriculadocebte.exists():
            modulo.docente = docente.first()
        else:
            modulo.docente = None
    return render(request, 'aulavirtual_estudiante.html', {
        'programadeposgrado': programadeposgrado,
        'modulos_list': modulos_list
    })