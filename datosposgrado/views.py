from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import ContratosDocentes
from programasposgrado.models import ProgramaPosgrado, Maestrias, PeriodosAcademicos, Modalidad, Modulos, CampoAmplio
from usuarios.models import PerfilUsuario
from django.contrib.auth.models import User
from django.http import JsonResponse
from .forms import ContratosDocentesForm
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
        except Maestrias.DoesNotExist:
            p.maestria = None

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


def obtener_modulos_por_maestria(request, programa_id):
    try:
        programa = ProgramaPosgrado.objects.get(id=programa_id)
        maestria = Maestrias.objects.get(id=programa.maestria)
        modulos = Modulos.objects.filter(
            maestria=maestria.id).values('id', 'nombre')

        return JsonResponse(list(modulos), safe=False)
    except ProgramaPosgrado.DoesNotExist:
        return JsonResponse({'error': 'Programa no encontrado'}, status=404)
    

def contratosdocentes_update(request, contratosdocentes_id, periodo_id):
    contratodocente = ContratosDocentes.objects.get(
        id=contratosdocentes_id)
    if request.method == 'POST':
        form = ContratosDocentesForm(request.POST, instance=contratodocente)
        if form.is_valid():
            docente_id = request.POST.get('docente')
            programadeposgrado_id = request.POST.get('programadeposgrado')
            modulo_id = request.POST.get('modulo')
         
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
    print(modulos_list)
    for p in programasdeposgrado_list:
        try:
            p.maestria = Maestrias.objects.get(id=p.maestria)
        except Maestrias.DoesNotExist:
            p.maestria = None
    return render(request, 'contratosdocentes_update.html', {
        'periodo_id': periodo_id,
        'form': form,
        'contratodocente': contratodocente,
        'docentes_list': docentes_list,
        'programasdeposgrado_list': programasdeposgrado_list,
        'modulos_list': modulos_list,
    })
    



def contratosdocentes_delete(request, contratosdocentes_id, periodo_id):
    try:
        contratosdocentes = ContratosDocentes.objects.get(
            id=contratosdocentes_id)
    
        contratosdocentes.delete()
        messages.success(request, "Contrato eliminado con éxito.")
    except ContratosDocentes.DoesNotExist:
        messages.error(request, "Contrato no encontrado.")

    return redirect('contratosdocentes', periodo_id)

