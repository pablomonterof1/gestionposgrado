from django.shortcuts import render, redirect, get_object_or_404
from usuarios.models import PerfilUsuario, User, PerfilAcademicoUsuario
from programasposgrado.models import PeriodosAcademicos, ProgramaPosgrado, Maestrias, Modalidad, Modulos
from seleccionperfiles.models import TernaModuloPM
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import transaction


# Create your views here.
@login_required
def seleccionp(request):
    perfiles_list = PerfilUsuario.objects.all()
    return render(request, 'seleccionp.html', {
        'perfiles_list': perfiles_list,
    })

@login_required
def periodosacademicosp(request):
    periodosacademicos_list = PeriodosAcademicos.objects.all()
    return render(request, 'periodosacademicos_sp.html', {
        'periodosacademicos_list': periodosacademicos_list,
    })

@login_required
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

@login_required
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

@login_required
def ternamodulopmsp(request, programa_id, modulo_id):
    programa = ProgramaPosgrado.objects.filter(id=programa_id).first()
    modulo = Modulos.objects.filter(id=modulo_id).first()
    try:
        terna = TernaModuloPM.objects.get(modulo_id=modulo, programa_posgrado=programa)
    except TernaModuloPM.DoesNotExist:
        terna = None  
    print(terna)
    if not terna:
        messages.error(request, "Aún no existe una terna.")
    
    return render(request, 'terna_sp.html', {
        'terna': terna,
        'modulo_id': modulo_id,
        'programa_id': programa_id,
    })

@login_required
def crearternamodulopmmsp(request, programa_id, modulo_id):
    terna, created = TernaModuloPM.objects.get_or_create(
        programa_posgrado_id=programa_id,
        modulo_id=modulo_id
    )

    docentes_list = PerfilUsuario.objects.filter(rol=2)

    # Excluir docentes ya asignados
    usados = []
    if terna.docente1_idoneo:
        usados.append(terna.docente1_idoneo.id)
    if terna.docente2:
        usados.append(terna.docente2.id)
    if terna.docente3:
        usados.append(terna.docente3.id)

    docentes_list = docentes_list.exclude(user__id__in=usados)

    for docente in docentes_list:
        perfil_academico = PerfilAcademicoUsuario.objects.filter(usuario=docente.id).first()
        if perfil_academico:
            docente.titulo_grado = perfil_academico.titulo_grado or 'N/A'
            docente.titulo_postgrado_maestria = perfil_academico.titulo_postgrado_maestria or 'N/A'
            docente.titulo_postgrado_doctorado = perfil_academico.titulo_postgrado_doctorado or 'N/A'
        else:
            docente.titulo_grado = 'N/A'
            docente.titulo_postgrado_maestria = 'N/A'
            docente.titulo_postgrado_doctorado = 'N/A'

    if request.method == 'POST':
        docente_id = request.POST.get('docente_id')
        estado = request.POST.get('Estado')

        try:
            docente = PerfilUsuario.objects.get(id=docente_id).user  
        except PerfilUsuario.DoesNotExist:
            messages.error(request, "Docente no válido.")
            return redirect('crearternamodulopmmsp', programa_id=programa_id, modulo_id=modulo_id)

        if docente in [terna.docente1_idoneo, terna.docente2, terna.docente3]:
            messages.error(request, "Este docente ya forma parte de la terna.")
            return redirect('crearternamodulopmmsp', programa_id=programa_id, modulo_id=modulo_id)

        with transaction.atomic():
            if estado == 'idoneo':
                if terna.docente1_idoneo:
                    messages.error(request, "Ya existe un Idóneo asignado.")
                else:
                    terna.docente1_idoneo = docente
                    terna.save()
                    messages.success(request, "Docente asignado como Idóneo.")
            elif estado == 'elegible1':
                if terna.docente2:
                    messages.error(request, "Ya existe un Elegible 1 asignado.")
                else:
                    terna.docente2 = docente
                    terna.save()
                    messages.success(request, "Docente asignado como Elegible 1.")
            elif estado == 'elegible2':
                if terna.docente3:
                    messages.error(request, "Ya existe un Elegible 2 asignado.")
                else:
                    terna.docente3 = docente
                    terna.save()
                    messages.success(request, "Docente asignado como Elegible 2.")
            else:
                messages.error(request, "Rol no válido.")

        if terna.docente1_idoneo and terna.docente2 and terna.docente3:
            messages.success(request, "Terna completa.")
            return redirect('ternapmmsp', programa_id=programa_id, modulo_id=modulo_id)

        return redirect('crearternamodulopmmsp', programa_id=programa_id, modulo_id=modulo_id)

    return render(request, 'crear_terna_sp.html', {
        'docentes_list': docentes_list,
        'terna': terna,
        'programa_id': programa_id,
        'modulo_id': modulo_id,
    })

@login_required
def modificarternamodulopmmsp(request, programa_id, modulo_id):
    terna = get_object_or_404(TernaModuloPM, programa_posgrado_id=programa_id, modulo_id=modulo_id)

    if request.method == 'POST':
        # Recolectar nuevos IDs y roles del form
        docente1_id = request.POST.get('docente1_id')
        docente2_id = request.POST.get('docente2_id')
        docente3_id = request.POST.get('docente3_id')

        # Actualizar solo si vienen valores nuevos
        if docente1_id:
            terna.docente1_idoneo_id = docente1_id
        if docente2_id:
            terna.docente2_id = docente2_id
        if docente3_id:
            terna.docente3_id = docente3_id

        terna.save()
        return redirect('ternapmmsp', programa_id=programa_id, modulo_id=modulo_id)

    perfiles_docentes = PerfilUsuario.objects.filter(rol=2).select_related('user')

    # FILTRA: que no estén ya en la terna
    docentes_list = []
    for perfil in perfiles_docentes:
        if perfil.user.id not in [
            terna.docente1_idoneo_id,
            terna.docente2_id,
            terna.docente3_id
        ]:
            try:
                perfil_academico = PerfilAcademicoUsuario.objects.get(usuario=perfil)
            except PerfilAcademicoUsuario.DoesNotExist:
                perfil_academico = None

            docentes_list.append({
                'id': perfil.user.id,
                'user': perfil.user,
                'ci': perfil.ci,
                'titulo_grado': getattr(perfil_academico, 'titulo_grado', ''),
                'titulo_postgrado_maestria': getattr(perfil_academico, 'titulo_postgrado_maestria', ''),
                'titulo_postgrado_doctorado': getattr(perfil_academico, 'titulo_postgrado_doctorado', ''),
            })

    context = {
        'terna': terna,
        'programa_id': programa_id,
        'modulo_id': modulo_id,
        'docentes_list': docentes_list,
    }
    return render(request, 'modificar_terna_sp.html', context)



