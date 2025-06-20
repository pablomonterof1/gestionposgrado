from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import MaestriaForm, ModuloForm, EspecialidadesMedicasForm, ModuloEMForm
from .models import Maestrias, PeriodosAcademicos, PerfildeIngreso, Modalidad, ProgramaPosgrado, CampoAmplio, Modulos, EspecialidadesMedicas, ModulosEM, ProgramaPosgradoEM


# Create your views here.

################################## MAESTRIAS############################################
@login_required
def maestrias(request):
    maestrias_list = Maestrias.objects.all().order_by('-created')
    return render(request, 'maestrias.html', {
        'maestrias_list': maestrias_list
    })


@login_required
def maestrias_create(request):
    if request.method == 'POST':
        form = MaestriaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('maestrias')
        else:
            return render(request, 'maestrias_create.html', {
                'form': form,
                'error': 'Error al crear la maestría'
            })
    else:
        form = MaestriaForm()
        return render(request, 'maestrias_create.html', {
            'form': form
        })


@login_required
def maestrias_detail(request, maestria_id):
    maestria = get_object_or_404(Maestrias, id=maestria_id)
    if request.method == 'POST':
        form = MaestriaForm(request.POST, instance=maestria)
        if form.is_valid():
            form.save()
            return redirect('maestrias')
    else:
        form = MaestriaForm(instance=maestria)
    return render(request, 'maestrias_detail.html', {
        'maestria': maestria,
        'form': form
    })


@login_required
def maestrias_delete(request, maestria_id):
    maestria = get_object_or_404(Maestrias, id=maestria_id)
    maestrias_list = Maestrias.objects.all().order_by('-created')
    if request.method == 'POST':
        maestria.delete()
        return redirect('maestrias')
    return render(request, 'maestrias.html', {
        'maestrias_list': maestrias_list,
        'error': 'Error al eliminar la maestría',
    })


################################## periodoacademicoS############################################

@login_required
def periodosacademicos(request):
    periodosacademicos_list = PeriodosAcademicos.objects.all().order_by('fecha_inicio')
    return render(request, 'periodosacademicos.html', {
        'periodosacademicos_list': periodosacademicos_list
    })

################################## MODALIDAD############################################


@login_required
def modalidad(request):
    modalidad_list = Modalidad.objects.all().order_by('-created')
    return render(request, 'modalidad.html', {
        'modalidad_list': modalidad_list
    })

################################## PERFILDEINGRESO############################################


@login_required
def perfildeingreso(request):
    perfildeingreso_list = PerfildeIngreso.objects.all().order_by('-created')
    return render(request, 'perfildeingreso.html', {
        'perfildeingreso_list': perfildeingreso_list
    })


################################## CAMPOAMPLIO############################################

@login_required
def campoamplio(request):
    campoamplio_list = CampoAmplio.objects.all().order_by('-created')
    return render(request, 'campoamplio.html', {
        'campoamplio_list': campoamplio_list
    })


################################## MODULOS############################################

@login_required
def modulos(request, maestria_id):
    maestria = get_object_or_404(Maestrias, id=maestria_id)
    modulos_list = Modulos.objects.filter(maestria=maestria).order_by('nombre')
    return render(request, 'modulos.html', {
        'maestria': maestria,
        'modulos_list': modulos_list
    })


@login_required
def modulos_create(request, maestria_id):
    maestria = get_object_or_404(Maestrias, id=maestria_id)
    if request.method == 'POST':
        form = ModuloForm(request.POST)
        if form.is_valid():
            modulo = form.save(commit=False)
            modulo.maestria = maestria
            modulo.save()
            return redirect('modulos', maestria_id=maestria.id)
        else:
            return render(request, 'modulos_create.html', {
                'form': form,
                'error': 'Error al crear el módulo'
            })
    else:
        form = ModuloForm()
        return render(request, 'modulos_create.html', {
            'form': form,
            'maestria': maestria
        })


@login_required
def modulos_update(request, modulo_id):
    modulo = get_object_or_404(Modulos, id=modulo_id)
    maestria = Maestrias.objects.get(id=modulo.maestria.id)
    if request.method == 'POST':
        form = ModuloForm(request.POST, instance=modulo)
        if form.is_valid():
            form.save()
            return redirect('modulos', maestria_id=modulo.maestria.id)
    else:
        form = ModuloForm(instance=modulo)
    return render(request, 'modulos_update.html', {
        'modulo': modulo,
        'form': form,
        'maestria': maestria
    })


@login_required
def modulos_delete(request, modulo_id):
    modulo = get_object_or_404(Modulos, id=modulo_id)
    maestria = Maestrias.objects.get(id=modulo.maestria.id)
    modulos_list = Modulos.objects.filter(
        maestria=maestria).order_by('-created')
    if request.method == 'POST':
        modulo.delete()
        return redirect('modulos', maestria_id=maestria.id)
    return render(request, 'modulos.html', {
        'modulos_list': modulos_list,
        'error': 'Error al eliminar el módulo',
        'maestria': maestria
    })

################################## PROGRAMADEPOSGRADO############################################


@login_required
def programasdeposgrado(request):
    programadeposgrado_list = ProgramaPosgrado.objects.all().order_by('campoamplio')
    for programadeposgrado in programadeposgrado_list:
        # Obtener los objetos relacionados para mostrar sus nombres en lugar de IDs
        programadeposgrado.maestria = Maestrias.objects.get(
            id=programadeposgrado.maestria)
        programadeposgrado.campoamplio = CampoAmplio.objects.get(
            id=programadeposgrado.campoamplio)
        programadeposgrado.periodoacademico = PeriodosAcademicos.objects.get(
            id=programadeposgrado.periodoacademico)
        programadeposgrado.modalidad = Modalidad.objects.get(
            id=programadeposgrado.modalidad)
    return render(request, 'programasdeposgrado.html', {
        'programadeposgrado_list': programadeposgrado_list
    })


@login_required
def programadeposgrado_select(request):
    campoamplio_list = CampoAmplio.objects.all().order_by('-nombre')
    maestrias_list = Maestrias.objects.all().order_by('-created')
    periodoacademico_list = PeriodosAcademicos.objects.all().order_by('fecha_inicio')
    modalidad_list = Modalidad.objects.all().order_by('-created')
    return render(request, 'programadeposgrado_select.html', {
        'campoamplio_list': campoamplio_list,
        'maestrias_list': maestrias_list,
        'periodoacademico_list': periodoacademico_list,
        'modalidad_list': modalidad_list
    })


@login_required
def programadeposgrado_create(request):
    if request.method == 'POST':
        campoamplio_id = request.POST.get('campoamplio_id')
        maestria_id = request.POST.get('maestria_id')
        pacademico_id = request.POST.get('pacademico_id')
        modalidad_id = request.POST.get('modalidad_id')
        cohorte = request.POST.get('cohorte')

        campoamplio_list = CampoAmplio.objects.all().order_by('-nombre')
        maestrias_list = Maestrias.objects.all().order_by('-created')
        pacademico_list = PeriodosAcademicos.objects.all().order_by('fecha_inicio')
        modalidad_list = Modalidad.objects.all().order_by('-created')

        print(
            f"POST: campoamplio_id={campoamplio_id}, maestria_id={maestria_id}, periodoacademico_id={pacademico_id}, modalidad_id={modalidad_id}")

        # Validar duplicados si es necesario
        if ProgramaPosgrado.objects.filter(campoamplio=campoamplio_id, maestria=maestria_id, periodoacademico=pacademico_id, modalidad=modalidad_id, cohorte=cohorte).exists():
            return render(request, 'programadeposgrado_select.html', {
                'error': 'Ya existe un programa de posgrado con esta combinación.',
                'campoamplio_list': campoamplio_list,
                'maestrias_list': maestrias_list,
                'pacademico_list': pacademico_list,
                'modalidad_list': modalidad_list
            })

        ProgramaPosgrado.objects.create(
            campoamplio=campoamplio_id,
            maestria=maestria_id,
            periodoacademico=pacademico_id,
            modalidad=modalidad_id,
            cohorte=cohorte

        )
        return redirect('programasdeposgrado')  # o a donde necesites

    # Si es GET, redirige o muestra selección
    return redirect('programadeposgrado_select')


@login_required
def programadeposgrado_update(request, programadeposgrado_id):
    programadeposgrado = get_object_or_404(
        ProgramaPosgrado, id=programadeposgrado_id)
    programadeposgrado.campoamplio = CampoAmplio.objects.get(
        id=programadeposgrado.campoamplio)
    programadeposgrado.maestria = Maestrias.objects.get(
        id=programadeposgrado.maestria)
    programadeposgrado.periodoacademico = PeriodosAcademicos.objects.get(
        id=programadeposgrado.periodoacademico)
    programadeposgrado.modalidad = Modalidad.objects.get(
        id=programadeposgrado.modalidad)
    campoamplio_list = CampoAmplio.objects.all().order_by('-nombre')
    maestrias_list = Maestrias.objects.all().order_by('-created')
    periodoacademicos_list = PeriodosAcademicos.objects.all().order_by('fecha_inicio')
    modalidad_list = Modalidad.objects.all().order_by('-created')
    cohorte = request.POST.get('cohorte')
    if request.method == 'POST':
        campoamplio_id = request.POST.get('campoamplio_id')
        maestria_id = request.POST.get('maestria_id')
        periodoacademico_id = request.POST.get('periodoacademico_id')
        modalidad_id = request.POST.get('modalidad_id')

        # Validar duplicados si es necesario
        if ProgramaPosgrado.objects.filter(campoamplio=campoamplio_id, maestria=maestria_id, periodoacademico=periodoacademico_id, modalidad=modalidad_id, cohorte=cohorte).exists():
            return render(request, 'programadeposgrado_update.html', {
                'error': 'Ya existe un programa de posgrado con esta combinación.',
                'programadeposgrado': programadeposgrado,
                'campoamplio_list': campoamplio_list,
                'maestrias_list': maestrias_list,
                'periodoacademicos_list': periodoacademicos_list,
                'modalidad_list': modalidad_list
            })

        programadeposgrado.campoamplio = campoamplio_id
        programadeposgrado.maestria = maestria_id
        programadeposgrado.periodoacademico = periodoacademico_id
        programadeposgrado.modalidad = modalidad_id
        programadeposgrado.cohorte = cohorte
        programadeposgrado.save()
        return redirect('programasdeposgrado')
    else:

        return render(request, 'programadeposgrado_update.html', {
            'programadeposgrado': programadeposgrado,
            'campoamplio_list': campoamplio_list,
            'maestrias_list': maestrias_list,
            'periodoacademicos_list': periodoacademicos_list,
            'modalidad_list': modalidad_list
        })


@login_required
def programadeposgrado_delete(request, programadeposgrado_id):
    programadeposgradodelete = get_object_or_404(
        ProgramaPosgrado, id=programadeposgrado_id)
    programadeposgrado_list = ProgramaPosgrado.objects.all().order_by('-created')
    for programadeposgrado in programadeposgrado_list:
        programadeposgrado.maestria = Maestrias.objects.get(
            id=programadeposgrado.maestria)
        programadeposgrado.campoamplio = CampoAmplio.objects.get(
            id=programadeposgrado.campoamplio)
        programadeposgrado.periodoacademico = PeriodosAcademicos.objects.get(
            id=programadeposgrado.periodoacademico)
        programadeposgrado.modalidad = Modalidad.objects.get(
            id=programadeposgrado.modalidad)
    if request.method == 'POST':
        programadeposgradodelete.delete()
        return redirect('programasdeposgrado')
    return render(request, 'programasdeposgrado.html', {
        'programadeposgrado_list': programadeposgrado_list,
        'error': 'Error al eliminar el programa de posgrado',
    })


################################## EPECIALIDADESMEDICAS############################################


@login_required
def especialidadesmedicas(request):
    especialidadesmedicas_list = EspecialidadesMedicas.objects.all().order_by('-created')
    return render(request, 'especialidadesmedicas.html', {
        'especialidadesmedicas_list': especialidadesmedicas_list
    })


@login_required
def especialidadesmedicas_create(request):
    if request.method == 'POST':
        form = EspecialidadesMedicasForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('especialidadesmedicas')
        else:
            return render(request, 'especialidadesmedicas_create.html', {
                'form': form,
                'error': 'Error al crear la Especiualidad médica'
            })
    else:
        form = EspecialidadesMedicasForm()
        return render(request, 'especialidadesmedicas_create.html', {
            'form': form
        })


@login_required
def especialidadesmedicas_detail(request, especialidadesmedicas_id):
    especialidadesmedicas = get_object_or_404(
        EspecialidadesMedicas, id=especialidadesmedicas_id)
    if request.method == 'POST':
        form = EspecialidadesMedicasForm(
            request.POST, instance=especialidadesmedicas)
        if form.is_valid():
            form.save()
            return redirect('especialidadesmedicas')
    else:
        form = EspecialidadesMedicasForm(instance=especialidadesmedicas)
    return render(request, 'especialidadesmedicas_detail.html', {
        'especialidadesmedicas': especialidadesmedicas,
        'form': form
    })


@login_required
def especialidadesmedicas_delete(request, especialidadesmedicas_id):
    especialidadesmedicas = get_object_or_404(
        EspecialidadesMedicas, id=especialidadesmedicas_id)
    especialidadesmedicas_list = EspecialidadesMedicas.objects.all().order_by('-created')
    if request.method == 'POST':
        especialidadesmedicas.delete()
        return redirect('especialidadesmedicas')
    return render(request, 'especialidadesmedicas.html', {
        'especialidadesmedicas_list': especialidadesmedicas_list,
        'error': 'Error al eliminar la especialidad',
    })


################################## MODULOSEM############################################

@login_required
def modulosem(request, especialidadesmedicas_id):
    especialidad = get_object_or_404(
        EspecialidadesMedicas, id=especialidadesmedicas_id)
    modulosem_list = ModulosEM.objects.filter(
        especialidad=especialidad).order_by('nombre')
    return render(request, 'modulosem.html', {
        'especialidad': especialidad,
        'modulosem_list': modulosem_list
    })


@login_required
def modulosem_create(request, especialidadesmedicas_id):
    especialidad = get_object_or_404(
        EspecialidadesMedicas, id=especialidadesmedicas_id)
    if request.method == 'POST':
        form = ModuloEMForm(request.POST)
        if form.is_valid():
            moduloem = form.save(commit=False)
            moduloem.especialidad = especialidad
            moduloem.save()
            return redirect('modulosem', especialidadesmedicas_id=especialidad.id)
        else:
            return render(request, 'modulosem_create.html', {
                'form': form,
                'error': 'Error al crear el módulo'
            })
    else:
        form = ModuloEMForm()
        return render(request, 'modulosem_create.html', {
            'form': form,
            'especialidad': especialidad
        })


@login_required
def modulosem_update(request, moduloem_id):
    moduloem = get_object_or_404(ModulosEM, id=moduloem_id)
    especialidad = EspecialidadesMedicas.objects.get(
        id=moduloem.especialidad.id)
    if request.method == 'POST':
        form = ModuloEMForm(request.POST, instance=moduloem)
        if form.is_valid():
            form.save()
            return redirect('modulosem', especialidadesmedicas_id=moduloem.especialidad.id)
    else:
        form = ModuloEMForm(instance=moduloem)
    return render(request, 'modulosem_update.html', {
        'moduloem': moduloem,
        'form': form,
        'especialidad': especialidad
    })


@login_required
def modulosem_delete(request, moduloem_id):
    moduloem = get_object_or_404(ModulosEM, id=moduloem_id)
    especialidad = EspecialidadesMedicas.objects.get(
        id=moduloem.especialidad.id)
    modulosem_list = ModulosEM.objects.filter(
        especialidad=especialidad).order_by('-created')
    if request.method == 'POST':
        moduloem.delete()
        return redirect('modulosem', especialidadesmedicas_id=especialidad.id)
    return render(request, 'modulosem.html', {
        'modulosem_list': modulosem_list,
        'error': 'Error al eliminar la especialidad',
        'especialidad': especialidad
    })


################################## PROGRAMADEESPECIALIDADESMEDICAS ############################################


@login_required
def programasdeespecialidadesmedicas(request):
    programasdeespecialidadesmedicas_list = ProgramaPosgradoEM.objects.all(
    ).order_by('campoamplio')
    for programasdeespecialidadesmedicas in programasdeespecialidadesmedicas_list:
        # Obtener los objetos relacionados para mostrar sus nombres en lugar de IDs
        programasdeespecialidadesmedicas.especialidad = EspecialidadesMedicas.objects.get(
            id=programasdeespecialidadesmedicas.especialidad)
        programasdeespecialidadesmedicas.campoamplio = CampoAmplio.objects.get(
            id=programasdeespecialidadesmedicas.campoamplio)
        programasdeespecialidadesmedicas.periodoacademico = PeriodosAcademicos.objects.get(
            id=programasdeespecialidadesmedicas.periodoacademico)
        programasdeespecialidadesmedicas.modalidad = Modalidad.objects.get(
            id=programasdeespecialidadesmedicas.modalidad)
    return render(request, 'programasdeespecialidadesmedicas.html', {
        'programasdeespecialidadesmedicas_list': programasdeespecialidadesmedicas_list
    })


@login_required
def programasdeespecialidadesmedicas_select(request):
    campoamplio_list = CampoAmplio.objects.all().order_by('-nombre')
    especialidad_list = EspecialidadesMedicas.objects.all().order_by('-created')
    periodoacademico_list = PeriodosAcademicos.objects.all().order_by('fecha_inicio')
    modalidad_list = Modalidad.objects.all().order_by('-created')
    return render(request, 'programadeespecialidadesmedicas_select.html', {
        'campoamplio_list': campoamplio_list,
        'especialidad_list': especialidad_list,
        'periodoacademico_list': periodoacademico_list,
        'modalidad_list': modalidad_list
    })


@login_required
def programasdeespecialidadesmedicas_create(request):
    if request.method == 'POST':
        campoamplio_id = request.POST.get('campoamplio_id')
        especialidad_id = request.POST.get('especialidad_id')
        pacademico_id = request.POST.get('pacademico_id')
        modalidad_id = request.POST.get('modalidad_id')
        cohorte = request.POST.get('cohorte')

        campoamplio_list = CampoAmplio.objects.all().order_by('-nombre')
        especialidad_list = EspecialidadesMedicas.objects.all().order_by('-created')
        pacademico_list = PeriodosAcademicos.objects.all().order_by('fecha_inicio')
        modalidad_list = Modalidad.objects.all().order_by('-created')

        if ProgramaPosgradoEM.objects.filter(campoamplio=campoamplio_id, especialidad=especialidad_id, periodoacademico=pacademico_id, modalidad=modalidad_id, cohorte=cohorte).exists():
            return render(request, 'programadeespecialidadesmedicas_select.html', {
                'error': 'Ya existe un programa de especialidades médicas con esta combinación.',
                'campoamplio_list': campoamplio_list,
                'especialidad_list': especialidad_list,
                'pacademico_list': pacademico_list,
                'modalidad_list': modalidad_list
            })

        ProgramaPosgradoEM.objects.create(
            campoamplio=campoamplio_id,
            especialidad=especialidad_id,
            periodoacademico=pacademico_id,
            modalidad=modalidad_id,
            cohorte=cohorte
        )
        # o a donde necesites
        return redirect('programasdeespecialidadesmedicas')

    # Si es GET, redirige o muestra selección
    return redirect('programasdeespecialidadesmedicas_select')



@login_required
def programasdeespecialidadesmedicas_update(request, programadeespecialidadesmedicas_id):
    programadeespecialidadesmedicas = get_object_or_404(ProgramaPosgradoEM, id=programadeespecialidadesmedicas_id)
    programadeespecialidadesmedicas.campoamplio = CampoAmplio.objects.get(
        id=programadeespecialidadesmedicas.campoamplio)
    programadeespecialidadesmedicas.especialidad = EspecialidadesMedicas.objects.get(
        id=programadeespecialidadesmedicas.especialidad)
    programadeespecialidadesmedicas.periodoacademico = PeriodosAcademicos.objects.get(
        id=programadeespecialidadesmedicas.periodoacademico)
    programadeespecialidadesmedicas.modalidad = Modalidad.objects.get(
        id=programadeespecialidadesmedicas.modalidad)
    campoamplio_list = CampoAmplio.objects.all().order_by('-nombre')
    especialidades_list = EspecialidadesMedicas.objects.all().order_by('-created')
    periodoacademicos_list = PeriodosAcademicos.objects.all().order_by('fecha_inicio')
    modalidad_list = Modalidad.objects.all().order_by('-created')
    
    if request.method == 'POST':
        campoamplio_id = request.POST.get('campoamplio_id')
        especialidad_id = request.POST.get('especialidad_id')
        periodoacademico_id = request.POST.get('periodoacademico_id')
        modalidad_id = request.POST.get('modalidad_id')
        cohorte = request.POST.get('cohorte')

        # Validar duplicados si es necesario
        if ProgramaPosgradoEM.objects.filter(campoamplio=campoamplio_id, especialidad=especialidad_id, periodoacademico=periodoacademico_id, modalidad=modalidad_id, cohorte=cohorte).exists():
            return render(request, 'programadeespecialidadesmedicas_update.html', {
                'error': 'Ya existe un programa de posgrado con esta combinación.',
                'programadeespecialidadesmedicas': programadeespecialidadesmedicas,
                'campoamplio_list': campoamplio_list,
                'especialidades_list': especialidades_list,
                'periodoacademicos_list': periodoacademicos_list,
                'modalidad_list': modalidad_list
            })

        programadeespecialidadesmedicas.campoamplio = campoamplio_id
        programadeespecialidadesmedicas.especialidad = especialidad_id
        programadeespecialidadesmedicas.periodoacademico = periodoacademico_id
        programadeespecialidadesmedicas.modalidad = modalidad_id
        programadeespecialidadesmedicas.cohorte = cohorte
        programadeespecialidadesmedicas.save()
        return redirect('programasdeespecialidadesmedicas')
    else:

        return render(request, 'programadeespecialidadesmedicas_update.html', {
            'programadeespecialidadesmedicas': programadeespecialidadesmedicas,
            'campoamplio_list': campoamplio_list,
            'especialidades_list': especialidades_list,
            'periodoacademicos_list': periodoacademicos_list,
            'modalidad_list': modalidad_list
        })



@login_required
def programasdeespecialidadesmedicas_delete(request, programadeespecialidadesmedicas_id):
    programadepecialidadesmedicasdelete = get_object_or_404(
        ProgramaPosgradoEM, id=programadeespecialidadesmedicas_id)
    programadepecialidadesmedicas_list = ProgramaPosgradoEM.objects.all().order_by('-created')
    for programadepecialidadesmedicas in programadepecialidadesmedicas_list:
        programadepecialidadesmedicas.especialidad = EspecialidadesMedicas.objects.get(
            id=programadepecialidadesmedicas.especialidad)
        programadepecialidadesmedicas.campoamplio = CampoAmplio.objects.get(
            id=programadepecialidadesmedicas.campoamplio)
        programadepecialidadesmedicas.periodoacademico = PeriodosAcademicos.objects.get(
            id=programadepecialidadesmedicas.periodoacademico)
        programadepecialidadesmedicas.modalidad = Modalidad.objects.get(
            id=programadepecialidadesmedicas.modalidad)

    if request.method == 'POST':
        programadepecialidadesmedicasdelete.delete()
        return redirect('programasdeespecialidadesmedicas')
    return render(request, 'programasdeespecialidadesmedicas.html', {
        'programadepecialidadesmedicas_list': programadepecialidadesmedicas_list,
        'error': 'Error al eliminar el programa de posgrado',
    })
