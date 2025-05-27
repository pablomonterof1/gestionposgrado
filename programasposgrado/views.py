from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import MaestriaForm, ModuloForm
from .models import Maestrias, PeriodosAcademicos, PerfildeIngreso, Modalidad, ProgramaPosgrado, CampoAmplio, Modulos 


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
    modulos_list = Modulos.objects.filter(maestria=maestria).order_by('-created')
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
        programadeposgrado.maestria = Maestrias.objects.get(id=programadeposgrado.maestria)
        programadeposgrado.campoamplio = CampoAmplio.objects.get(id=programadeposgrado.campoamplio)
        programadeposgrado.periodoacademico = PeriodosAcademicos.objects.get(id=programadeposgrado.periodoacademico)
        programadeposgrado.modalidad = Modalidad.objects.get(id=programadeposgrado.modalidad)
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
    programadeposgrado = get_object_or_404(ProgramaPosgrado, id=programadeposgrado_id)
    programadeposgrado.campoamplio = CampoAmplio.objects.get(id=programadeposgrado.campoamplio)
    programadeposgrado.maestria = Maestrias.objects.get(id=programadeposgrado.maestria)
    programadeposgrado.periodoacademico = PeriodosAcademicos.objects.get(id=programadeposgrado.periodoacademico)
    programadeposgrado.modalidad = Modalidad.objects.get(id=programadeposgrado.modalidad)
    campoamplio_list = CampoAmplio.objects.all().order_by('-nombre')
    maestrias_list = Maestrias.objects.all().order_by('-created')
    periodoacademicos_list = PeriodosAcademicos.objects.all().order_by('fecha_inicio')
    modalidad_list = Modalidad.objects.all().order_by('-created')
    if request.method == 'POST':
        campoamplio_id = request.POST.get('campoamplio_id')
        maestria_id = request.POST.get('maestria_id')
        periodoacademico_id = request.POST.get('periodoacademico_id')
        modalidad_id = request.POST.get('modalidad_id')

        # Validar duplicados si es necesario
        if ProgramaPosgrado.objects.filter(campoamplio=campoamplio_id, maestria=maestria_id, periodoacademico=periodoacademico_id, modalidad=modalidad_id).exists():
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
    programadeposgrado = get_object_or_404(ProgramaPosgrado, id=programadeposgrado_id)
    programadeposgrado_list = ProgramaPosgrado.objects.all().order_by('-created')
    for programadeposgrado in programadeposgrado_list:
        programadeposgrado.maestria = Maestrias.objects.get(id=programadeposgrado.maestria)
        programadeposgrado.periodoacademico = PeriodosAcademicos.objects.get(id=programadeposgrado.periodoacademico)
        programadeposgrado.modalidad = Modalidad.objects.get(id=programadeposgrado.modalidad)
    if request.method == 'POST':
        programadeposgrado.delete()
        return redirect('programasdeposgrado')
    return render(request, 'programasdeposgrado.html', {
        'programadeposgrado_list': programadeposgrado_list,
        'error': 'Error al eliminar el programa de posgrado',
    })
