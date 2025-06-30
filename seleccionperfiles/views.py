from django.shortcuts import render, redirect
from usuarios.models import PerfilUsuario, User
from programasposgrado.models import PeriodosAcademicos, ProgramaPosgrado, Maestrias, Modalidad, Modulos
from seleccionperfiles.models import TernaModuloPM
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

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
    terna = TernaModuloPM.objects.filter(modulo_id=modulo_id).first()
    if not terna:
        messages.error(
                request, "Aún no existe una terna.")
    
    return render(request, 'terna_sp.html', {
        'terna': terna,
        'modulo_id': modulo_id,
        'programa_id': programa_id,
    })

@login_required
def crearternamodulopmmsp(request, programa_id, modulo_id):
    print(modulo_id,  programa_id)
    terna = TernaModuloPM.objects.filter(modulo=modulo_id, programa_posgrado=programa_id).first()
    docentes_list= PerfilUsuario.objects.filter(
        rol=2,
    ),
    if request.method == 'POST':
        messages.success(request, "Terna creada exitosamente.")
        return render(request, 'crear_terna_sp.html', {
            'terna': None,
        })
    else:
        messages.error(request, "Error al crear la terna.")
    
    return render(request, 'crear_terna_sp.html', {
        'docentes_list': docentes_list,
        'terna': terna,
        'programa_id': programa_id,
        'modulo_id': modulo_id, 
    })

@login_required
def docentepmmsp_create(request, periodo_id):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        apellido = request.POST.get('apellido', '').strip()
        cedula = request.POST.get('cedula', '').strip()
        perfil_academico = request.POST.get('perfil_academico', '').strip()
        correo = request.POST.get('correo', '').strip()

        # Validación básica de campos vacíos
        if not nombre or not apellido or not cedula or not correo:
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('docentedp_create', periodo_id=periodo_id)

        # Validación de formato de correo
        try:
            validate_email(correo)
        except ValidationError:
            messages.error(request, 'El correo electrónico no es válido.')
            return redirect('docentedp_create', periodo_id=periodo_id)

        # Verificar duplicados
        if User.objects.filter(username=cedula).exists():
            messages.error(request, 'Ya existe un usuario con esa cédula.')
            return redirect('docentedp_create', periodo_id=periodo_id)

        if User.objects.filter(email=correo).exists():
            messages.error(
                request, 'Ya existe un usuario con ese correo electrónico.')
            return redirect('docentedp_create', periodo_id=periodo_id)

        # Crear el usuario
        user = User.objects.create_user(
            username=cedula,
            password=cedula,
            first_name=nombre,
            last_name=apellido,
            email=correo
        )
        PerfilUsuario.objects.create(user=user, rol=2, ci=cedula)
        messages.success(request, 'Docente creado exitosamente.')
        return redirect('crearternamodulopmmsp', periodo_id=periodo_id)

    return render(request, 'crearternamodulopmmsp.html',
                  {'periodo_id': periodo_id})