from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
<<<<<<< HEAD
from .models import ContratosDocentes, ContratoTutor, ContratoCoordinador
=======
from .models import ContratosDocentes
>>>>>>> bb1335e6b4376e4f100ad702bb93f9266f0a92d4
from programasposgrado.models import ProgramaPosgrado, Maestrias, PeriodosAcademicos, Modalidad, Modulos, CampoAmplio
from usuarios.models import PerfilUsuario
from django.contrib.auth.models import User
from django.http import JsonResponse
<<<<<<< HEAD
from .forms import ContratosDocentesForm, ContratoTutorForm, ContratoCoordinadorForm
=======
from .forms import ContratosDocentesForm
>>>>>>> bb1335e6b4376e4f100ad702bb93f9266f0a92d4
from django.contrib import messages

# Create your views here.


def periodosacademicosdp(request):
    periodosacademicos_list = PeriodosAcademicos.objects.all()
    return render(request, 'periodosacademicos_dp.html', {
        'periodosacademicos_list': periodosacademicos_list,
    })


def datosposgrado(request, periodo_id):
    return render(request, 'datosposgrado.html', {
        'periodo_id': periodo_id,
    })

<<<<<<< HEAD
=======

>>>>>>> bb1335e6b4376e4f100ad702bb93f9266f0a92d4
def contratosdocentes(request, periodo_id):
    contratos_por_periordo = []
    programasdeposgrado_list = ProgramaPosgrado.objects.filter(
        periodoacademico=periodo_id)
    for programadeposgrado in programasdeposgrado_list:
        contratosdocentes = ContratosDocentes.objects.filter(
            programadeposgrado=programadeposgrado.id)
        contratos_por_periordo.extend(contratosdocentes)
        for d in contratos_por_periordo:
            try:
                d.docente_obj = User.objects.get(id=d.docente)
                d.programadeposgrado_obj = ProgramaPosgrado.objects.get(id=d.programadeposgrado)
                d.maestria_obj = Maestrias.objects.get(id=d.programadeposgrado_obj.maestria)
                d.modalidad_obj = Modalidad.objects.get(id=d.programadeposgrado_obj.modalidad)
                d.campoamplio_obj = CampoAmplio.objects.get(id=d.programadeposgrado_obj.campoamplio)
                d.periodoacademico_obj = PeriodosAcademicos.objects.get(id=d.programadeposgrado_obj.periodoacademico)
                d.modulo_obj = Modulos.objects.get(id=d.modulo)
            except User.DoesNotExist:
                d.docente_obj = None
                d.modulo_obj = None
                d.programadeposgrado_obj = None
                d.maestria_obj = None
                d.modalidad_obj = None
                d.campoamplio_obj = None
                d.periodoacademico_obj = None

    docentes_list = PerfilUsuario.objects.filter(rol=2)

    periodoacademico = PeriodosAcademicos.objects.get(id=periodo_id)
    return render(request, 'contratosdocentes.html', {
        'docentes_list': docentes_list,
        'contratos_por_periordo': contratos_por_periordo,
        'contratosdocentes': contratosdocentes,
        'periodo_id': periodo_id,
        'periodoacademico': periodoacademico,

    })

<<<<<<< HEAD
def contratotutor(request, periodo_id):
    contratos_por_periordo = []
    programasdeposgrado_list = ProgramaPosgrado.objects.filter(
        periodoacademico=periodo_id)
    for programadeposgrado in programasdeposgrado_list:
        contratotutor = ContratoTutor.objects.filter(
            programadeposgrado=programadeposgrado.id)
        contratos_por_periordo.extend(contratotutor)
        for d in contratos_por_periordo:
            try:
                d.tutor_obj = User.objects.get(id=d.tutor)
                d.programadeposgrado_obj = ProgramaPosgrado.objects.get(id=d.programadeposgrado)
                d.maestria_obj = Maestrias.objects.get(id=d.programadeposgrado_obj.maestria)
                d.maestrante_obj = User.objects.get(id=d.maestrante)
                d.modalidad_obj = Modalidad.objects.get(id=d.programadeposgrado_obj.modalidad)
                d.campoamplio_obj = CampoAmplio.objects.get(id=d.programadeposgrado_obj.campoamplio)
                d.periodoacademico_obj = PeriodosAcademicos.objects.get(id=d.programadeposgrado_obj.periodoacademico)
            except User.DoesNotExist:
                d.tutor_obj = None
                d.programadeposgrado_obj = None
                d.maestria_obj = None
                d.maestrante_obj = None
                d.modalidad_obj = None
                d.campoamplio_obj = None
                d.periodoacademico_obj = None

    tutor_list = PerfilUsuario.objects.filter(rol=5)

    periodoacademico = PeriodosAcademicos.objects.get(id=periodo_id)
    return render(request, 'contratotutor.html', {
        'periodo_id': periodo_id,
        'tutor_list': tutor_list,
        'contratos_por_periordo': contratos_por_periordo,
        'contratotutor': contratotutor,
        'periodoacademico': periodoacademico,

    })

def contratocoordinador(request, periodo_id):
    contratos_por_periordo = []
    programasdeposgrado_list = ProgramaPosgrado.objects.filter(
        periodoacademico=periodo_id)
    for programadeposgrado in programasdeposgrado_list:
        contratocoordinador = ContratoCoordinador.objects.filter(
            programadeposgrado=programadeposgrado.id)
        contratos_por_periordo.extend(contratocoordinador)
        for d in contratos_por_periordo:
            try:
                d.coordinador_obj = User.objects.get(id=d.coordinador)
                d.programadeposgrado_obj = ProgramaPosgrado.objects.get(id=d.programadeposgrado)
                d.maestria_obj = Maestrias.objects.get(id=d.programadeposgrado_obj.maestria)
                d.modalidad_obj = Modalidad.objects.get(id=d.programadeposgrado_obj.modalidad)
                d.campoamplio_obj = CampoAmplio.objects.get(id=d.programadeposgrado_obj.campoamplio)
                d.periodoacademico_obj = PeriodosAcademicos.objects.get(id=d.programadeposgrado_obj.periodoacademico)
            except User.DoesNotExist:
                d.coordinador_obj = None
                d.programadeposgrado_obj = None
                d.maestria_obj = None
                d.modalidad_obj = None
                d.campoamplio_obj = None
                d.periodoacademico_obj = None

    coordinadores_list = PerfilUsuario.objects.filter(rol=3)

    periodoacademico = PeriodosAcademicos.objects.get(id=periodo_id)
    return render(request, 'contratocoordinador.html', {
        'periodo_id': periodo_id,
        'coordinadores_list': coordinadores_list,
        'contratos_por_periordo': contratos_por_periordo,
        'contratocoordinador': contratocoordinador,
        'periodoacademico': periodoacademico,

    })

=======
>>>>>>> bb1335e6b4376e4f100ad702bb93f9266f0a92d4

def contratosdocentes_create(request, periodo_id):
    if request.method == 'POST':
        form = ContratosDocentesForm(request.POST)
        if form.is_valid():
            docente_id = request.POST.get('docente')
            programadeposgrado_id = request.POST.get('programadeposgrado')
            modulo_id = request.POST.get('modulo')
            horasacademicas = form.cleaned_data['horasacademicas']
            valorxhora = form.cleaned_data['valorxhora']
            certificacionpresupuestaria = form.cleaned_data['certificacionpresupuestaria']
            fechacertificacionpresupuestaria = form.cleaned_data['fechacertificacionpresupuestaria']
            plazo = form.cleaned_data['plazo']
            numerocontrato = form.cleaned_data['numerocontrato']
            numeromemorandotthh = form.cleaned_data['numeromemorandotthh']
            tipopersonalacademico = form.cleaned_data['tipopersonalacademico']
            adenda = form.cleaned_data['adenda']
            obsevaciones = form.cleaned_data['obsevaciones']


            # Asegúrate de obtener los objetos reales si los campos son claves foráneas
            docente = PerfilUsuario.objects.get(id=docente_id)
            programadeposgrado = ProgramaPosgrado.objects.get(
                id=programadeposgrado_id)
            modulo = Modulos.objects.get(id=modulo_id)

            ContratosDocentes.objects.create(
                docente=docente.user.id,
                programadeposgrado=programadeposgrado.id,
                modulo=modulo.id,
                horasacademicas=horasacademicas,
                valorxhora=valorxhora,
                certificacionpresupuestaria=certificacionpresupuestaria,
                fechacertificacionpresupuestaria=fechacertificacionpresupuestaria,
                plazo=plazo,
                numerocontrato=numerocontrato,
                numeromemorandotthh=numeromemorandotthh,
                tipopersonalacademico=tipopersonalacademico,
                adenda=adenda,
                obsevaciones=obsevaciones
            )
            return redirect('contratosdocentes', periodo_id=periodo_id)
        else:
            messages.error(
                request, "Por favor corrija los errores del formulario.")

    else:
        form = ContratosDocentesForm()

    # GET o POST con errores
    docentes_list = PerfilUsuario.objects.filter(rol=2)
    programasdeposgrado_list = ProgramaPosgrado.objects.filter(
        periodoacademico=periodo_id)
    for p in programasdeposgrado_list:
        try:
            p.maestria = Maestrias.objects.get(id=p.maestria)
<<<<<<< HEAD
            p.periodoacademico = PeriodosAcademicos.objects.get(id=p.periodoacademico)
        except Maestrias.DoesNotExist:
            p.maestria = None
            p.periodoacademico = None
=======
        except Maestrias.DoesNotExist:
            p.maestria = None
>>>>>>> bb1335e6b4376e4f100ad702bb93f9266f0a92d4

    periodoacademico = PeriodosAcademicos.objects.get(id=periodo_id)
    modalidad_list = Modalidad.objects.all()
    maestrias_list = Maestrias.objects.all()

    return render(request, 'contratosdocentes_create.html', {
        'docentes_list': docentes_list,
        'programasdeposgrado_list': programasdeposgrado_list,
        'periodoacademico': periodoacademico,
        'modalidad_list': modalidad_list,
        'maestrias_list': maestrias_list,
        'periodo_id': periodo_id,
        'form': form,
    })

<<<<<<< HEAD
def contratotutor_create(request, periodo_id):
    if request.method == 'POST':
        form = ContratoTutorForm(request.POST)
        if form.is_valid():
            tutor_id = request.POST.get('tutor')
            programadeposgrado_id = request.POST.get('programadeposgrado')
            valorcontrato = form.cleaned_data['valorcontrato']
            certificacionpresupuestaria = form.cleaned_data['certificacionpresupuestaria']
            fechacertificacionpresupuestaria = form.cleaned_data['fechacertificacionpresupuestaria']
            maestrante_id = request.POST.get('maestrante')
            plazo = form.cleaned_data['plazo']
            numerocontrato = form.cleaned_data['numerocontrato']
            numeromemorandotthh = form.cleaned_data['numeromemorandotthh']
            tipopersonalacademico = form.cleaned_data['tipopersonalacademico']
            adenda = form.cleaned_data['adenda']
            obsevaciones = form.cleaned_data['obsevaciones']

            # Asegúrate de obtener los objetos reales si los campos son claves foráneas
            tutor = PerfilUsuario.objects.get(id=tutor_id)
            programadeposgrado = ProgramaPosgrado.objects.get(
                id=programadeposgrado_id)
            
            maestrante = PerfilUsuario.objects.get(id=maestrante_id)

            ContratoTutor.objects.create(
                tutor=tutor.user.id,
                programadeposgrado=programadeposgrado.id,
                maestrante=maestrante.user.id,
                plazo=plazo,
                certificacionpresupuestaria=certificacionpresupuestaria,
                fechacertificacionpresupuestaria=fechacertificacionpresupuestaria,
                valorcontrato=valorcontrato,
                numerocontrato=numerocontrato,
                numeromemorandotthh=numeromemorandotthh,
                tipopersonalacademico=tipopersonalacademico,
                adenda=adenda,
                obsevaciones=obsevaciones
            )
            return redirect('contratotutor', periodo_id=periodo_id)
        else:
            messages.error(
                request, "Por favor corrija los errores del formulario.")

    else:
        form = ContratoTutorForm()

    # GET o POST con errores
    tutor_list = PerfilUsuario.objects.filter(rol=5)
    print(tutor_list)
    programasdeposgrado_list = ProgramaPosgrado.objects.filter(
        periodoacademico=periodo_id)
    for p in programasdeposgrado_list:
        try:
            p.maestria = Maestrias.objects.get(id=p.maestria)
            p.periodoacademico = PeriodosAcademicos.objects.get(id=p.periodoacademico)

        except Maestrias.DoesNotExist:
            p.maestria = None
            p.periodoacademico = None

    periodoacademico = PeriodosAcademicos.objects.get(id=periodo_id)
    modalidad_list = Modalidad.objects.all()
    maestrias_list = Maestrias.objects.all()
    maestrantes = PerfilUsuario.objects.filter(rol=1)  # Maestrantes

    return render(request, 'contratotutor_create.html', {
        'tutor_list': tutor_list,
        'programasdeposgrado_list': programasdeposgrado_list,
        'periodoacademico': periodoacademico,
        'modalidad_list': modalidad_list,
        'maestrias_list': maestrias_list,
        'maestrantes_list': maestrantes,
        'periodo_id': periodo_id,
        'form': form,
    })

def contratocoordinador_create(request, periodo_id):
    if request.method == 'POST':
        form = ContratoCoordinadorForm(request.POST)
        if form.is_valid():
            coordinador_id = request.POST.get('coordinador')
            programadeposgrado_id = request.POST.get('programadeposgrado')
            certificacionpresupuestaria = form.cleaned_data['certificacionpresupuestaria']
            fechacertificacionpresupuestaria = form.cleaned_data['fechacertificacionpresupuestaria']
            plazo = form.cleaned_data['plazo']
            honorario = form.cleaned_data['honorario']
            numerocontrato = form.cleaned_data['numerocontrato']
            cargo = form.cleaned_data['cargo']
            noactasseleccion = form.cleaned_data['noactasseleccion']
            oficioentregadoporth = form.cleaned_data['oficioentregadoporth']
            modalidadcontractuar = form.cleaned_data['modalidadcontractuar']
            obsevaciones = form.cleaned_data['obsevaciones']

            # Asegúrate de obtener los objetos reales si los campos son claves foráneas
            coordinador = PerfilUsuario.objects.get(id=coordinador_id)
            programadeposgrado = ProgramaPosgrado.objects.get(
                id=programadeposgrado_id)

            ContratoCoordinador.objects.create(
                coordinador=coordinador.user.id,
                programadeposgrado=programadeposgrado.id,
                certificacionpresupuestaria=certificacionpresupuestaria,
                fechacertificacionpresupuestaria=fechacertificacionpresupuestaria,
                plazo=plazo,
                honorario=honorario,
                numerocontrato=numerocontrato,
                cargo=cargo,
                noactasseleccion=noactasseleccion,
                oficioentregadoporth=oficioentregadoporth,
                modalidadcontractuar=modalidadcontractuar,
                obsevaciones=obsevaciones
            )
            return redirect('contratocoordinador', periodo_id=periodo_id)
        else:
            messages.error(
                request, "Por favor corrija los errores del formulario.")

    else:
        form = ContratoCoordinadorForm()

    # GET o POST con errores
    coordinadores_list = PerfilUsuario.objects.filter(rol=3)
    print(coordinadores_list)
    programasdeposgrado_list = ProgramaPosgrado.objects.filter(
        periodoacademico=periodo_id)
    for p in programasdeposgrado_list:          
        try:
            p.maestria = Maestrias.objects.get(id=p.maestria)
            p.periodoacademico = PeriodosAcademicos.objects.get(id=p.periodoacademico)
        except Maestrias.DoesNotExist:
            p.maestria = None
            p.periodoacademico = None
    periodoacademico = PeriodosAcademicos.objects.get(id=periodo_id)
    modalidad_list = Modalidad.objects.all()
    maestrias_list = Maestrias.objects.all()
    return render(request, 'contratocoordinador_create.html', {
        'coordinadores_list': coordinadores_list,
        'programasdeposgrado_list': programasdeposgrado_list,
        'periodoacademico': periodoacademico,
        'modalidad_list': modalidad_list,
        'maestrias_list': maestrias_list,
        'periodo_id': periodo_id,
        'form': form,
    })
=======
>>>>>>> bb1335e6b4376e4f100ad702bb93f9266f0a92d4

def obtener_modulos_por_maestria(request, programa_id):
    try:
        programa = ProgramaPosgrado.objects.get(id=programa_id)
        maestria = Maestrias.objects.get(id=programa.maestria)
        modulos = Modulos.objects.filter(
            maestria=maestria.id).values('id', 'nombre')

        return JsonResponse(list(modulos), safe=False)
    except ProgramaPosgrado.DoesNotExist:
        return JsonResponse({'error': 'Programa no encontrado'}, status=404)
    

<<<<<<< HEAD

=======
>>>>>>> bb1335e6b4376e4f100ad702bb93f9266f0a92d4
def contratosdocentes_update(request, contratosdocentes_id, periodo_id):
    contratodocente = ContratosDocentes.objects.get(
        id=contratosdocentes_id)
    if request.method == 'POST':
        form = ContratosDocentesForm(request.POST, instance=contratodocente)
        if form.is_valid():
            docente_id = request.POST.get('docente')
            programadeposgrado_id = request.POST.get('programadeposgrado')
            modulo_id = request.POST.get('modulo')
<<<<<<< HEAD
=======
         
>>>>>>> bb1335e6b4376e4f100ad702bb93f9266f0a92d4
            docente = PerfilUsuario.objects.get(id=docente_id)
            programadeposgrado = ProgramaPosgrado.objects.get(
                id=programadeposgrado_id)
            modulo = Modulos.objects.get(id=modulo_id)
            form.save(commit=False)
            contratodocente.docente = docente.user.id
            contratodocente.programadeposgrado = programadeposgrado.id
            contratodocente.modulo = modulo.id
            contratodocente.horasacademicas = form.cleaned_data['horasacademicas']
            contratodocente.valorxhora = form.cleaned_data['valorxhora']
            contratodocente.certificacionpresupuestaria = form.cleaned_data['certificacionpresupuestaria']
            contratodocente.fechacertificacionpresupuestaria = form.cleaned_data['fechacertificacionpresupuestaria']
            contratodocente.plazo = form.cleaned_data['plazo']
            contratodocente.numerocontrato = form.cleaned_data['numerocontrato']
            contratodocente.numeromemorandotthh = form.cleaned_data['numeromemorandotthh']
            contratodocente.tipopersonalacademico = form.cleaned_data['tipopersonalacademico']
            contratodocente.adenda = form.cleaned_data['adenda']
            contratodocente.obsevaciones = form.cleaned_data['obsevaciones']
            contratodocente.save()
            
            messages.success(request, "Contrato actualizado con éxito.")
            return redirect('contratosdocentes', periodo_id)
        else:
            messages.error(
                request, "Por favor corrija los errores del formulario.")
    else:
        form = ContratosDocentesForm(instance=contratodocente)


    docentes_list = PerfilUsuario.objects.filter(rol=2)
    programasdeposgrado_list = ProgramaPosgrado.objects.filter(
        periodoacademico=periodo_id)
    programadeposgrado = ProgramaPosgrado.objects.get(id=contratodocente.programadeposgrado)
    maestria_id = programadeposgrado.maestria
    modulos_list = Modulos.objects.filter(maestria_id=maestria_id)
<<<<<<< HEAD
    for p in programasdeposgrado_list:
        try:
            p.maestria = Maestrias.objects.get(id=p.maestria)
            p.periodoacademico = PeriodosAcademicos.objects.get(id=p.periodoacademico)
            periodoacademico = PeriodosAcademicos.objects.get(id=periodo_id)
            modalidad_list = Modalidad.objects.all()
            maestrias_list = Maestrias.objects.all()
        except Maestrias.DoesNotExist:
            p.maestria = None
            p.periodoacademico = None
=======
    print(modulos_list)
    for p in programasdeposgrado_list:
        try:
            p.maestria = Maestrias.objects.get(id=p.maestria)
        except Maestrias.DoesNotExist:
            p.maestria = None
>>>>>>> bb1335e6b4376e4f100ad702bb93f9266f0a92d4
    return render(request, 'contratosdocentes_update.html', {
        'periodo_id': periodo_id,
        'form': form,
        'contratodocente': contratodocente,
        'docentes_list': docentes_list,
        'programasdeposgrado_list': programasdeposgrado_list,
        'modulos_list': modulos_list,
<<<<<<< HEAD
        'periodoacademico': periodoacademico,
        'modalidad_list': modalidad_list,
        'maestrias_list': maestrias_list,
    })
    

def contratotutor_update(request, contratotutor_id, periodo_id):
    contratotutor = ContratoTutor.objects.get(id=contratotutor_id)
    if request.method == 'POST':
        form = ContratoTutorForm(request.POST, instance=contratotutor)
        if form.is_valid():
            tutor_id = request.POST.get('tutor')
            programadeposgrado_id = request.POST.get('programadeposgrado')
            tutor = PerfilUsuario.objects.get(id=tutor_id)
            programadeposgrado = ProgramaPosgrado.objects.get(id=programadeposgrado_id)
            form.save(commit=False)
            contratotutor.tutor = tutor.user.id
            contratotutor.programadeposgrado = programadeposgrado.id
            contratotutor.valorcontrato = form.cleaned_data['valorcontrato']
            contratotutor.maestrante = PerfilUsuario.objects.get(id=request.POST.get('maestrante')).user.id
            contratotutor.certificacionpresupuestaria = form.cleaned_data['certificacionpresupuestaria']
            contratotutor.fechacertificacionpresupuestaria = form.cleaned_data['fechacertificacionpresupuestaria']
            contratotutor.plazo = form.cleaned_data['plazo']
            contratotutor.numerocontrato = form.cleaned_data['numerocontrato']
            contratotutor.numeromemorandotthh = form.cleaned_data['numeromemorandotthh']
            contratotutor.tipopersonalacademico = form.cleaned_data['tipopersonalacademico']
            contratotutor.adenda = form.cleaned_data['adenda']
            contratotutor.obsevaciones = form.cleaned_data['obsevaciones']
            contratotutor.save()
            
            messages.success(request, "Contrato actualizado con éxito.")
            return redirect('contratotutor', periodo_id)
        else:
            messages.error(request, "Por favor corrija los errores del formulario.")
    else:
        form = ContratoTutorForm(instance=contratotutor)

    tutor_list = PerfilUsuario.objects.filter(rol=5)
    programasdeposgrado_list = ProgramaPosgrado.objects.filter(periodoacademico=periodo_id)
    programadeposgrado = ProgramaPosgrado.objects.get(id=contratotutor.programadeposgrado)
    maestria_id = programadeposgrado.maestria
    maestrantes = PerfilUsuario.objects.filter(rol=1) 

    for p in programasdeposgrado_list:
        try:
            p.periodoacademico = PeriodosAcademicos.objects.get(id=p.periodoacademico)
            p.maestria = Maestrias.objects.get(id=p.maestria)
        except Maestrias.DoesNotExist:
            p.maestria = None
            p.periodoacademico = None
            periodoacademico = PeriodosAcademicos.objects.get(id=periodo_id)

    return render(request, 'contratotutor_update.html', {
        'periodo_id': periodo_id,
        'form': form,
        'contratotutor': contratotutor,
        'tutor_list': tutor_list,
        'programasdeposgrado_list': programasdeposgrado_list,
        'maestrantes_list': maestrantes, 
        'maestria_id': maestria_id,
        'periodoacademico': periodoacademico,
    })

def contratocoordinador_update(request, contratocoordinador_id, periodo_id):
    contratocoordinador = ContratoCoordinador.objects.get(id=contratocoordinador_id)
    if request.method == 'POST':
        form = ContratoCoordinadorForm(request.POST, instance=contratocoordinador)
        if form.is_valid():
            coordinador_id = request.POST.get('coordinador')
            programadeposgrado_id = request.POST.get('programadeposgrado')
            coordinador = PerfilUsuario.objects.get(id=coordinador_id)
            programadeposgrado = ProgramaPosgrado.objects.get(id=programadeposgrado_id)
            form.save(commit=False)
            contratocoordinador.coordinador = coordinador.user.id
            contratocoordinador.programadeposgrado = programadeposgrado.id
            contratocoordinador.certificacionpresupuestaria = form.cleaned_data['certificacionpresupuestaria']
            contratocoordinador.fechacertificacionpresupuestaria = form.cleaned_data['fechacertificacionpresupuestaria']
            contratocoordinador.plazo = form.cleaned_data['plazo']
            contratocoordinador.honorario = form.cleaned_data['honorario']
            contratocoordinador.numerocontrato = form.cleaned_data['numerocontrato']
            contratocoordinador.cargo = form.cleaned_data['cargo']
            contratocoordinador.noactasseleccion = form.cleaned_data['noactasseleccion']
            contratocoordinador.oficioentregadoporth = form.cleaned_data['oficioentregadoporth']
            contratocoordinador.modalidadcontractuar = form.cleaned_data['modalidadcontractuar']
            contratocoordinador.obsevaciones = form.cleaned_data['obsevaciones']
            contratocoordinador.save()
            
            messages.success(request, "Contrato actualizado con éxito.")
            return redirect('contratocoordinador', periodo_id)  
        else:
            messages.error(request, "Por favor corrija los errores del formulario.")
    else:
        form = ContratoCoordinadorForm(instance=contratocoordinador)

    coordinadores_list = PerfilUsuario.objects.filter(rol=3)
    programasdeposgrado_list = ProgramaPosgrado.objects.filter(periodoacademico=periodo_id)
    programadeposgrado = ProgramaPosgrado.objects.get(id=contratocoordinador.programadeposgrado)
    maestria_id = programadeposgrado.maestria

    for p in programasdeposgrado_list:
        try:
            p.periodoacademico = PeriodosAcademicos.objects.get(id=p.periodoacademico)
            p.maestria = Maestrias.objects.get(id=p.maestria)
        except Maestrias.DoesNotExist:
            p.maestria = None
            p.periodoacademico = None
    periodoacademico = PeriodosAcademicos.objects.get(id=periodo_id)
    return render(request, 'contratocoordinador_update.html', {
        'periodo_id': periodo_id,
        'form': form,
        'contratocoordinador': contratocoordinador,
        'coordinadores_list': coordinadores_list,
        'programasdeposgrado_list': programasdeposgrado_list,
        'maestria_id': maestria_id,
        'periodoacademico': periodoacademico,
    })
=======
    })
    

>>>>>>> bb1335e6b4376e4f100ad702bb93f9266f0a92d4


def contratosdocentes_delete(request, contratosdocentes_id, periodo_id):
    try:
        contratosdocentes = ContratosDocentes.objects.get(
            id=contratosdocentes_id)
    
        contratosdocentes.delete()
        messages.success(request, "Contrato eliminado con éxito.")
    except ContratosDocentes.DoesNotExist:
        messages.error(request, "Contrato no encontrado.")

    return redirect('contratosdocentes', periodo_id)

<<<<<<< HEAD
def contratotutor_delete(request, contratotutor_id, periodo_id):
    try:
        contratotutor = ContratoTutor.objects.get(
            id=contratotutor_id)
    
        contratotutor.delete()
        messages.success(request, "Contrato eliminado con éxito.")
    except ContratoTutor.DoesNotExist:
        messages.error(request, "Contrato no encontrado.")

    return redirect('contratotutor', periodo_id)

def contratocoordinador_delete(request, contratocoordinador_id, periodo_id):
    try:
        contratocoordinador = ContratoCoordinador.objects.get(
            id=contratocoordinador_id)
    
        contratocoordinador.delete()
        messages.success(request, "Contrato eliminado con éxito.")
    except ContratoCoordinador.DoesNotExist:
        messages.error(request, "Contrato no encontrado.")

    return redirect('contratocoordinador', periodo_id)


=======
>>>>>>> bb1335e6b4376e4f100ad702bb93f9266f0a92d4
