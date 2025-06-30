from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from .models import PerfilUsuario, MatriculaUsuario, MatriculaDocenteModulo, PerfilAcademicoUsuario
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from programasposgrado.models import ProgramaPosgrado, ProgramaPosgradoEM, Maestrias, Modulos, ModulosEM
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect

# Create your views here.


def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': CustomUserCreationForm()
        })
    else:
        if request.POST['password1'] != request.POST['password2']:
            return render(request, 'signup.html', {
                'form': CustomUserCreationForm(),
                'error': 'Las contraseñas no coinciden'
            })

        # Verificar si el correo ya está registrado
        if User.objects.filter(email=request.POST['email']).exists():
            return render(request, 'signup.html', {
                'form': CustomUserCreationForm(),
                'error': 'Este correo electrónico ya está registrado'
            })

        try:
            user = User.objects.create_user(
                username=request.POST['username'],
                password=request.POST['password1'],
                first_name=request.POST['first_name'],
                last_name=request.POST['last_name'],
                email=request.POST['email']
            )
            user.save()
            login(request, user)
            return redirect('home')
        except IntegrityError:
            return render(request, 'signup.html', {
                'form': CustomUserCreationForm(),
                'error': 'El nombre de usuario ya existe'
            })


def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {
            'form': AuthenticationForm
        })
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error': 'Usuario o contraseña incorrectos'
            })
        else:
            login(request, user)
            return redirect('home')


@login_required
def signout(request):
    logout(request)
    return redirect('home')


@login_required
def perfil(request):
    return render(request, 'perfil.html')


@login_required
def datosUsuario(request):
    usuarios_sin_perfil = User.objects.filter(perfilusuario__isnull=True)
    for usuario in usuarios_sin_perfil:
        PerfilUsuario.objects.create(user=usuario)
    datosUsuario_list = User.objects.filter(is_active=1)
    return render(request, 'gestionusuarios.html', {
        'datosUsuario_list': datosUsuario_list
    })


@login_required
def actualizar_rol_usuario(request, usuario_id):
    if request.method == 'POST':
        perfil_usuario = get_object_or_404(PerfilUsuario, user_id=usuario_id)
        nuevo_rol = request.POST.get('rol')
        perfil_usuario.rol = nuevo_rol
        perfil_usuario.save()
        return redirect('gestionusuarios')


@login_required
def docentedp_create(request, periodo_id):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        apellido = request.POST.get('apellido', '').strip()
        cedula = request.POST.get('cedula', '').strip()
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
        return redirect('contratosdocentes', periodo_id=periodo_id)

    return render(request, 'docentedp_create.html',
                  {'periodo_id': periodo_id})


@login_required
def docentepm_create(request, programa_id):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        apellido = request.POST.get('apellido', '').strip()
        cedula = request.POST.get('cedula', '').strip()
        correo = request.POST.get('correo', '').strip()

        # Validación básica de campos vacíos
        if not nombre or not apellido or not cedula or not correo:
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('docentepm_create', programa_id=programa_id)

        # Validación de formato de correo
        try:
            validate_email(correo)
        except ValidationError:
            messages.error(request, 'El correo electrónico no es válido.')
            return redirect('docentepm_create', programa_id=programa_id)

        # Verificar duplicados
        if User.objects.filter(username=cedula).exists():
            messages.error(request, 'Ya existe un usuario con esa cédula.')
            return redirect('docentepm_create', programa_id=programa_id)

        if User.objects.filter(email=correo).exists():
            messages.error(
                request, 'Ya existe un usuario con ese correo electrónico.')
            return redirect('docentepm_create', programa_id=programa_id)

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
        return redirect('docentesmatricularmodulom', programa_id=programa_id)

    return render(request, 'docentepm_create.html',
                  {'programa_id': programa_id})

#docente pmmsp

@login_required
def docentepmmsp_create(request, programa_id,  modulo_id):
    if request.method == 'POST':
       nombre = request.POST.get('nombre', '').strip()
       apellido = request.POST.get('apellido', '').strip()
       cedula = request.POST.get('cedula', '').strip()
       titulo = request.POST.get('titulo', '').strip()
       titulo_maestria = request.POST.get('titulo_maestria', '').strip()
       titulo_doctorado = request.POST.get('titulo_doctorado', '').strip()
       correo = request.POST.get('correo', '').strip()
    
       # Validación básica de campos vacíos
       if not nombre or not apellido or not cedula or not correo:
           messages.error(request, 'Todos los campos son obligatorios.')
           return redirect('docentespmmsp_create', )

       # Validación de formato de correo
       try:
           validate_email(correo)
       except ValidationError:
           messages.error(request, 'El correo electrónico no es válido.')
           return redirect('docentespmmsp_create', programa_id=programa_id, modulo_id=modulo_id)

       # Verificar duplicados
       if User.objects.filter(username=cedula).exists():
           messages.error(request, 'Ya existe un usuario con esa cédula.')
           return redirect('docentespmmsp_create', programa_id=programa_id, modulo_id=modulo_id)

       if User.objects.filter(email=correo).exists():
           messages.error(
               request, 'Ya existe un usuario con ese correo electrónico.')
           return redirect('docentespmmsp_create', programa_id=programa_id, modulo_id=modulo_id)
       # Crear el usuario
       user = User.objects.create_user(
           username=cedula,
           email=correo,
           first_name=nombre,
           last_name=apellido,
       )
       user.set_password(cedula)
       user.save()
       # Crear el perfil del usuario
       perfil = PerfilUsuario.objects.create(
           user=user,
           cedula=cedula,
           rol=2,  # Asignar rol de docente
       )
       perfil.save()

       perfil_academico = PerfilAcademicoUsuario.objects.create(
           usuario=perfil,
           titulo_grado=titulo,
           titulo_postgrado_maestria=titulo_maestria,
           titulo_postgrado_doctorado=titulo_doctorado,
       )
       messages.success(request, 'Docente creado exitosamente.')
       return redirect('crearternamodulopmmsp', programa_id=programa_id, modulo_id=modulo_id)

    
    return render(request, 'docentespmmsp_create.html', {
        'programa_id': programa_id,
        'modulo_id': modulo_id
    })
    


@login_required
def estudiantepm_create(request, programa_id):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        apellido = request.POST.get('apellido', '').strip()
        cedula = request.POST.get('cedula', '').strip()
        correo = request.POST.get('correo', '').strip()

        # Validación básica de campos vacíos
        if not nombre or not apellido or not cedula or not correo:
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('estudiantepm_create', programa_id=programa_id)

        # Validación de formato de correo
        try:
            validate_email(correo)
        except ValidationError:
            messages.error(request, 'El correo electrónico no es válido.')
            return redirect('estudiantepm_create', programa_id=programa_id)

        # Verificar duplicados
        if User.objects.filter(username=cedula).exists():
            messages.error(request, 'Ya existe un usuario con esa cédula.')
            return redirect('estudiantepm_create', programa_id=programa_id)

        if User.objects.filter(email=correo).exists():
            messages.error(
                request, 'Ya existe un usuario con ese correo electrónico.')
            return redirect('estudiantepm_create', programa_id=programa_id)

        # Crear el usuario
        user = User.objects.create_user(
            username=cedula,
            password=cedula,
            first_name=nombre,
            last_name=apellido,
            email=correo
        )
        PerfilUsuario.objects.create(user=user, rol=1, ci=cedula)
        messages.success(request, 'Estudiante creado exitosamente.')
        return redirect('usuariosmatricularprogramam', programa_id=programa_id)

    return render(request, 'estudiantepm_create.html',
                  {'programa_id': programa_id})

@login_required
def tutordp_create(request, periodo_id):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        apellido = request.POST.get('apellido', '').strip()
        cedula = request.POST.get('cedula', '').strip()
        correo = request.POST.get('correo', '').strip()

        # Validación básica de campos vacíos
        if not nombre or not apellido or not cedula or not correo:
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('tutordp_create', periodo_id=periodo_id)

        # Validación de formato de correo
        try:
            validate_email(correo)
        except ValidationError:
            messages.error(request, 'El correo electrónico no es válido.')
            return redirect('tutordp_create', periodo_id=periodo_id)

        # Verificar duplicados
        if User.objects.filter(username=cedula).exists():
            messages.error(request, 'Ya existe un usuario con esa cédula.')
            return redirect('tutordp_create', periodo_id=periodo_id)

        if User.objects.filter(email=correo).exists():
            messages.error(
                request, 'Ya existe un usuario con ese correo electrónico.')
            return redirect('tutordp_create', periodo_id=periodo_id)

        # Crear el usuario
        user = User.objects.create_user(
            username=cedula,
            password=cedula,
            first_name=nombre,
            last_name=apellido,
            email=correo
        )
        PerfilUsuario.objects.create(user=user, rol=5, ci=cedula)
        messages.success(request, 'Tutor creado exitosamente.')
        return redirect('contratotutor', periodo_id=periodo_id)

    return render(request, 'tutordp_create.html',
                  {'periodo_id': periodo_id})

@login_required
def coordinadordp_create(request, periodo_id):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        apellido = request.POST.get('apellido', '').strip()
        cedula = request.POST.get('cedula', '').strip()
        correo = request.POST.get('correo', '').strip()

        # Validación básica de campos vacíos
        if not nombre or not apellido or not cedula or not correo:
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('coordinadordp_create', periodo_id=periodo_id)

        # Validación de formato de correo
        try:
            validate_email(correo)
        except ValidationError:
            messages.error(request, 'El correo electrónico no es válido.')
            return redirect('coordinadordp_create', periodo_id=periodo_id)

        # Verificar duplicados
        if User.objects.filter(username=cedula).exists():
            messages.error(request, 'Ya existe un usuario con esa cédula.')
            return redirect('coordinadordp_create', periodo_id=periodo_id)

        if User.objects.filter(email=correo).exists():
            messages.error(
                request, 'Ya existe un usuario con ese correo electrónico.')
            return redirect('coordinadordp_create', periodo_id=periodo_id)

        # Crear el usuario
        user = User.objects.create_user(
            username=cedula,
            password=cedula,
            first_name=nombre,
            last_name=apellido,
            email=correo
        )
        PerfilUsuario.objects.create(user=user, rol=3, ci=cedula)
        messages.success(request, 'Coordinador creado exitosamente.')
        return redirect('contratocoordinador', periodo_id=periodo_id)

    return render(request, 'coordinadordp_create.html',
                  {'periodo_id': periodo_id})



@login_required
def UsuariosMatriculadosProgramaM(request, programa_id):
    programa = get_object_or_404(ProgramaPosgrado, id=programa_id)
    maestria = get_object_or_404(Maestrias, id=programa.maestria)

    # Obtener el ContentType correspondiente a ProgramaPosgrado
    programa_ct = ContentType.objects.get_for_model(ProgramaPosgrado)

    # Filtrar las matrículas que corresponden a ese ContentType y programa_id
    usuarios_matriculados_list = MatriculaUsuario.objects.filter(
        content_type=programa_ct,
        object_id=programa_id
    )

    return render(request, 'usuariosmatriculados_programam.html', {
        'programa': programa,
        'maestria': maestria,
        'usuarios_matriculados_list': usuarios_matriculados_list
    })




@login_required
def UsuariosMatricularProgramaM(request, programa_id):
    programa = get_object_or_404(ProgramaPosgrado, id=programa_id)
    maestria = get_object_or_404(Maestrias, id=programa.maestria)

    if request.method == 'POST':
        user_id = request.POST.get('usuario')  # Solo un usuario
        user = get_object_or_404(User, id=user_id)
        print(user_id)

        # Verifica si ya está matriculado
        exists = MatriculaUsuario.objects.filter(
            usuario=user,
            content_type=ContentType.objects.get_for_model(ProgramaPosgrado),
            object_id=programa_id
        ).exists()

        if not exists:
            MatriculaUsuario.objects.create(
                usuario=user,
                content_type=ContentType.objects.get_for_model(
                    ProgramaPosgrado),
                object_id=programa_id,
                rol_en_programa='Estudiante'
            )
            messages.success(
                request, f'{user.get_full_name()} matriculado exitosamente.')
        else:
            messages.warning(
                request, f'{user.get_full_name()} ya estaba matriculado.')

        return redirect('usuariosmatricularprogramam', programa_id=programa_id)

    # Mostrar usuarios no matriculados aún
    usuarios = User.objects.filter(is_active=True).exclude(
        matriculausuario__content_type=ContentType.objects.get_for_model(
            ProgramaPosgrado),
        matriculausuario__object_id=programa_id
    )


    return render(request, 'usuariosmatricular_programam.html', {
        'usuarios': usuarios,
        'programa': programa,
        'maestria': maestria
    })

@login_required
def BorrarUsuariosMatricularProgramaM(request, programa_id, usuario_id):
    usuario = get_object_or_404(User, id=usuario_id)
    programa = get_object_or_404(ProgramaPosgrado, id=programa_id)

    # Obtener el ContentType correspondiente a ProgramaPosgrado
    programa_ct = ContentType.objects.get_for_model(ProgramaPosgrado)

    try:
        matricula = MatriculaUsuario.objects.get(
            usuario=usuario,
            content_type=programa_ct,
            object_id=programa_id
        )
        matricula.delete()
        messages.warning(request, "Matrícula eliminada exitosamente.")
    except MatriculaUsuario.DoesNotExist:
        messages.error(request, "No se encontró la matrícula.")

    return redirect('usuariosmatriculadosprogramam', programa_id)

@login_required
def DocentesMatriculadosModuloM(request, programa_id):
    programa = get_object_or_404(ProgramaPosgrado, id=programa_id)
    modulos = Modulos.objects.filter(maestria=programa.maestria)

    docentes_por_modulo = {}
    modulo_ct = ContentType.objects.get_for_model(Modulos)

    for modulo in modulos:
        docentesmatriculados = MatriculaDocenteModulo.objects.filter(
            content_type=modulo_ct,
            object_id=modulo.id
        )
        docentes_por_modulo[modulo] = docentesmatriculados

    return render(request, 'docentesmatriculados_modulom.html', {
        'programa': programa,
        'docentes_por_modulo': docentes_por_modulo
    })


@login_required
def DocentesMatricularModuloM(request, programa_id):
    programa = get_object_or_404(ProgramaPosgrado, id=programa_id)
    modulos = Modulos.objects.filter(maestria=programa.maestria)
    docentes = User.objects.filter(perfilusuario__rol=2)

    if request.method == 'POST':
        docente_id = request.POST.get('docente_id')
        modulo_id = request.POST.get('modulo_id')

        docente = get_object_or_404(User, id=docente_id)
        modulo = get_object_or_404(Modulos, id=modulo_id)

        modulo_ct = ContentType.objects.get_for_model(Modulos)

        obj, created = MatriculaDocenteModulo.objects.get_or_create(
            docente=docente,
            content_type=modulo_ct,
            object_id=modulo.id,
            programa=programa.id
        )

        if created:
            messages.success(request, "Docente matriculado exitosamente.")
        else:
            messages.warning(request, "El docente ya está matriculado en este módulo.")

        return HttpResponseRedirect(request.path)

    return render(request, 'docentesmatricular_modulom.html', {
        'programa': programa,
        'modulos': modulos,
        'docentes': docentes
    })

def BorrarDocentesMatricularModuloM(request,programa_id, docente_id, modulo_id):
    docente = get_object_or_404(User, id=docente_id)
    modulo = get_object_or_404(Modulos, id=modulo_id)

    modulo_ct = ContentType.objects.get_for_model(Modulos)

    try:
        matricula = MatriculaDocenteModulo.objects.get(
            docente=docente,
            content_type=modulo_ct,
            object_id=modulo.id
        )
        matricula.delete()
        messages.success(request, "Matricula eliminada exitosamente.")
    except MatriculaDocenteModulo.DoesNotExist:
        messages.error(request, "No se encontró la matrícula.")

    return redirect('docentesmatriculadosmodulom', programa_id)


