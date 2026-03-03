from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.db import IntegrityError, transaction
from .forms import CustomUserCreationForm, UserSelfForm, PerfilUsuarioSelfForm, PerfilAcademicoSelfForm, UserSelfFormDP
from django.contrib.auth.decorators import login_required
from .models import PerfilUsuario, MatriculaUsuario, MatriculaDocenteModulo, PerfilAcademicoUsuario
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from programasposgrado.models import ProgramaPosgrado, ProgramaPosgradoEM, Maestrias, Modulos, ModulosEM
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.http import url_has_allowed_host_and_scheme

# Create your views here.


def _get_safe_next(request, default_name='home'):
    """
    Devuelve una URL 'next' segura o el reverse de default_name.
    """
    raw_next = request.POST.get('next') or request.GET.get('next')
    if raw_next and url_has_allowed_host_and_scheme(
        url=raw_next,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return raw_next
    return reverse(default_name)


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
        next_url = request.GET.get('next', '')
        return render(request, 'signin.html', {
            'form': AuthenticationForm(),
            'next': next_url
        })
    else:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is None:
            return render(request, 'signin.html', {
                'form': AuthenticationForm(),
                'error': 'Usuario o contraseña incorrectos',
                'next': request.POST.get('next', '')
            })
        else:
            login(request, user)
            # ✅ Captura next desde el POST (no GET)
            next_url = request.POST.get('next')
            if next_url:
                return redirect(next_url)
            else:
                return redirect('home')

@method_decorator(login_required, name='dispatch')
class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'password_change_form.html'

    def get_success_url(self):
        return reverse('password_change_done')

@method_decorator(login_required, name='dispatch')
class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'password_change_done.html'

@login_required
def signout(request):
    logout(request)
    return redirect('home')


@login_required
def perfil(request):
    """
    Vista de perfil del usuario autenticado.
    Crea PerfilUsuario y PerfilAcademico si aún no existen (para evitar errores en el template).
    """
    perfil, _ = PerfilUsuario.objects.get_or_create(user=request.user)
    academico, _ = PerfilAcademicoUsuario.objects.get_or_create(usuario=perfil)

    # Datos “extra” opcionales para mostrar en el perfil (no obligatorio)
    # - Matrículas como estudiante
    mats = MatriculaUsuario.objects.filter(usuario=request.user).order_by('-fecha_matricula')

    # - Asignaciones a módulos como docente (si aplica)
    mods_doc = MatriculaDocenteModulo.objects.filter(docente=request.user).order_by('-fecha_matricula')

    ctx = {
        'user_obj': request.user,
        'perfil': perfil,
        'academico': academico,
        'matriculas': mats,
        'modulos_docente': mods_doc,
    }
    return render(request, 'perfil.html', ctx)


@login_required
@transaction.atomic
def perfil_editar(request):
    """
    Edición de datos del usuario autenticado (sus datos básicos, perfil y perfil académico).
    No cambia contraseña (eso va en perfil_password).
    """
    perfil, _ = PerfilUsuario.objects.get_or_create(user=request.user)
    academico, _ = PerfilAcademicoUsuario.objects.get_or_create(usuario=perfil)

    if request.method == 'POST':
        f_user = UserSelfForm(request.POST, instance=request.user)
        f_perfil = PerfilUsuarioSelfForm(request.POST, instance=perfil, user_instance=request.user)
        f_acad = PerfilAcademicoSelfForm(request.POST, instance=academico)

        # Validaciones de unicidad (email/CI) se manejan en los forms
        if f_user.is_valid() and f_perfil.is_valid() and f_acad.is_valid():
            f_user.save()
            f_perfil.instance.rol = perfil.rol  # Mantener rol actual
            f_perfil.save()
            f_acad.save()
            messages.success(request, 'Tus datos fueron actualizados correctamente.')
            return redirect('perfil')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        f_user = UserSelfForm(instance=request.user)
        f_perfil = PerfilUsuarioSelfForm(instance=perfil, user_instance=request.user)
        f_acad = PerfilAcademicoSelfForm(instance=academico)

    return render(request, 'perfil_editar.html', {
        'f_user': f_user,
        'f_perfil': f_perfil,
        'f_acad': f_acad,
    })


@login_required
@transaction.atomic
def usuario_editar_dp(request, user_id):
    """
    Edición de datos del usuario autenticado (sus datos básicos, perfil y perfil académico).
    No cambia contraseña (eso va en perfil_password).
    """
    usuario = get_object_or_404(User, id=user_id)
    perfil, _ = PerfilUsuario.objects.get_or_create(user=usuario)
    academico, _ = PerfilAcademicoUsuario.objects.get_or_create(usuario=perfil)

    next_url = _get_safe_next(request)

    if request.method == 'POST':
        g_user = UserSelfFormDP(request.POST, instance=usuario)
        g_perfil = PerfilUsuarioSelfForm(request.POST, instance=perfil, user_instance=usuario)
        g_acad = PerfilAcademicoSelfForm(request.POST, instance=academico)
        # Validaciones de unicidad (email/CI) se manejan en los forms
        if g_user.is_valid() and g_perfil.is_valid() and g_acad.is_valid():
            g_user.save()
            g_perfil.instance.rol = perfil.rol 
            g_perfil.save()
            g_acad.save()
            messages.success(request, 'Los datos fueron actualizados correctamente.')
            return redirect(next_url)
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
            # ---- Mostrar TODOS los errores de los 3 formularios ----
            for form in [g_user, g_perfil, g_acad]:
                for field, errors in form.errors.items():
                    for error in errors:
                        if field == '__all__':
                            # errores generales del form
                            messages.error(request, f"Error: {error}")
                        else:
                            label = form.fields[field].label if field in form.fields else field
                            messages.error(request, f"{label}: {error}")
                # errores no asociados a un campo (non_field_errors)
                for error in form.non_field_errors():
                    messages.error(request, f"Error general: {error}")
            # --------------------------------------------------------
    else:
        g_user = UserSelfForm(instance=usuario)
        g_perfil = PerfilUsuarioSelfForm(instance=perfil, user_instance=usuario)
        g_acad = PerfilAcademicoSelfForm(instance=academico)

    return render(request, 'usuario_editar_dp.html', {
        'g_user': g_user,
        'g_perfil': g_perfil,
        'g_acad': g_acad,
        'next_url': next_url,
    })



@login_required
@transaction.atomic
def perfil_password(request):
    """
    Cambio de contraseña para el usuario autenticado.
    """
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            # Mantener la sesión
            update_session_auth_hash(request, user)
            messages.success(request, 'Tu contraseña se actualizó correctamente.')
            return redirect('perfil')
        else:
            messages.error(request, 'Corrige los errores del formulario.')
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'perfil_password.html', {'form': form})


@login_required
def datosUsuario(request):
    # 1) Crear perfiles faltantes en batch (1 query para traer IDs + 1 bulk_create)
    usuarios_ids_sin_perfil = list(
        User.objects.filter(perfilusuario__isnull=True).values_list('id', flat=True)
    )

    if usuarios_ids_sin_perfil:
        perfiles = [PerfilUsuario(user_id=uid) for uid in usuarios_ids_sin_perfil]
        PerfilUsuario.objects.bulk_create(perfiles, ignore_conflicts=True)

    # 2) Traer usuarios activos + su perfil en la misma consulta (evita N+1 en template)
    datosUsuario_list = User.objects.filter(is_active=True).select_related('perfilusuario')

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
def coordinadorpmmsp_create(request, modulo_id, programa_id):
    origen = request.GET.get('origen', '')

    if request.method == 'POST':
        origen = request.POST.get('origen', origen)
        nombre = request.POST.get('nombre', '').strip()
        apellido = request.POST.get('apellido', '').strip()
        cedula = request.POST.get('cedula', '').strip()
        titulo = request.POST.get('titulo_grado', '').strip()
        titulo_maestria = request.POST.get('titulo_postgrado_maestria', '').strip()
        titulo_doctorado = request.POST.get('titulo_postgrado_doctorado', '').strip()
        correo = request.POST.get('correo', '').strip()
    
    # Validación básica de campos vacíos
        if not nombre or not apellido or not cedula or not correo:
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('coordinadorpmmsp_create', programa_id=programa_id, modulo_id=modulo_id)

    # Validación de formato de correo
        try:
            validate_email(correo)
        except ValidationError:
            messages.error(request, 'El correo electrónico no es válido.')
            return redirect('coordinadorpmmsp_create', programa_id=programa_id, modulo_id=modulo_id)

    # Verificar duplicados
        if User.objects.filter(username=cedula).exists():
            messages.error(request, 'Ya existe un usuario con esa cédula.')
            return render(request, 'coordinadorpmmsp_create.html', {
                'programa_id': programa_id,
                'modulo_id': modulo_id
            })

        if User.objects.filter(email=correo).exists():
            messages.error(
            request, 'Ya existe un usuario con ese correo electrónico.')
            return render(request, 'coordinadorpmmsp_create.html', {
                'programa_id': programa_id,
                'modulo_id': modulo_id
            })
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
        ci=cedula,
        rol=3,  # Asignar rol de coordinador
        )
        perfil.save()
        perfil_academico = PerfilAcademicoUsuario.objects.create(
            usuario=perfil,
            titulo_grado=titulo,
            titulo_postgrado_maestria=titulo_maestria,
            titulo_postgrado_doctorado=titulo_doctorado,
        )
        perfil_academico.save()
        messages.success(request, 'Coordinador creado exitosamente.')
        if origen == 'crear_ternacoordinador':
            return redirect('crearternamodulocoordinadorpmsp', programa_id=programa_id, modulo_id=modulo_id)
        elif origen == 'modificar_ternacoordinador':
            return redirect('modificarternamodulocoordinadorpmsp', programa_id=programa_id, modulo_id=modulo_id)
        else:
            return redirect('ternamodulocoordinadorpmsp', programa_id=programa_id, modulo_id=modulo_id)

    return render(request, 'coordinadorpmmsp_create.html', {
        'programa_id': programa_id,
        'modulo_id': modulo_id,
        'origen': origen,
    })

@login_required
def docentedp_create(request, periodo_id):
    if request.method == 'POST':

        # Validar si el correo o CI ya existen
        if User.objects.filter(email=request.POST['email']).exists():
            messages.error(request, "El correo electrónico ya está registrado.")
            return render(request, 'docentedp_create.html', {
                'form': CustomUserCreationForm(),
                'periodo_id': periodo_id,
            })
        if PerfilUsuario.objects.filter(ci=request.POST['ci']).exists():
            messages.error(request, "La cédula ya está registrada.")
            return render(request, 'docentedp_create.html', {
                'form': CustomUserCreationForm(),
                'periodo_id': periodo_id,
            })

        try:
            ci = request.POST['ci'].strip()

            # Si no se proporciona username, usa la cédula
            username = request.POST.get('username', ci).strip() or ci

            # Si no se proporcionan contraseñas, usa la cédula
            password = request.POST.get('password1', ci).strip() or ci

            # Crear usuario principal
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=request.POST.get('first_name', '').strip(),
                last_name=request.POST.get('last_name', '').strip(),
                email=request.POST.get('email', '').strip(),
            )
            user.save()

            # Crear perfil general
            perfil = PerfilUsuario.objects.create(
                user=user,
                ci=ci,
                rol=2,
                telefono=request.POST.get('telefono', '').strip() or None,
                fecha_nacimiento=request.POST.get('fecha_nacimiento') or None,
                nacionalidad=request.POST.get('nacionalidad', '').strip() or None,
                sexo=request.POST.get('sexo') or None,
                provincia=request.POST.get('provincia', '').strip() or None,
            )

            # Crear perfil académico
            PerfilAcademicoUsuario.objects.create(
                usuario=perfil,
                titulo_grado=request.POST.get('titulo_grado', '').strip(),
                titulo_postgrado_maestria=request.POST.get('titulo_postgrado_maestria', '').strip(),
                titulo_postgrado_doctorado=request.POST.get('titulo_postgrado_doctorado', '').strip(),
            )

            messages.success(request, f"✅ Usuario {user.get_full_name()} creado correctamente.")
            return redirect('contratosdocentes_create', periodo_id=periodo_id)

        except IntegrityError:
            messages.error(request, "El nombre de usuario ya existe o los datos son inválidos.")
            return render(request, 'docentedp_create.html', {
                'form': CustomUserCreationForm(),
                'periodo_id': periodo_id,
            })
    # GET
    return render(request, 'docentedp_create.html', {
        'form': CustomUserCreationForm(),
        'periodo_id': periodo_id,
        })


@login_required
def docentepm_create(request, programa_id):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        apellido = request.POST.get('apellido', '').strip()
        cedula = request.POST.get('cedula', '').strip()
        titulo = request.POST.get('titulo_grado', '').strip()
        titulo_maestria = request.POST.get('titulo_postgrado_maestria', '').strip()
        titulo_doctorado = request.POST.get('titulo_postgrado_doctorado', '').strip()
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
        user.save()
        perfilusuario=PerfilUsuario.objects.create(user=user, rol=2, ci=cedula)
        perfilusuario.save()
        perfil_academico = PerfilAcademicoUsuario.objects.create(
            usuario=perfilusuario,
            titulo_grado=titulo,
            titulo_postgrado_maestria=titulo_maestria,
            titulo_postgrado_doctorado=titulo_doctorado,
        )
        perfil_academico.save()
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
        titulo = request.POST.get('titulo_grado', '').strip()
        titulo_maestria = request.POST.get('titulo_postgrado_maestria', '').strip()
        titulo_doctorado = request.POST.get('titulo_postgrado_doctorado', '').strip()
        correo = request.POST.get('correo', '').strip()
    
    # Validación básica de campos vacíos
        if not nombre or not apellido or not cedula or not correo:
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('docentespmmsp_create', programa_id=programa_id, modulo_id=modulo_id)

    # Validación de formato de correo
        try:
            validate_email(correo)
        except ValidationError:
            messages.error(request, 'El correo electrónico no es válido.')
            return redirect('docentespmmsp_create', programa_id=programa_id, modulo_id=modulo_id)

    # Verificar duplicados
        if User.objects.filter(username=cedula).exists():
            messages.error(request, 'Ya existe un usuario con esa cédula.')
            return render(request, 'docentespmmsp_create.html', {
                'programa_id': programa_id,
                'modulo_id': modulo_id
            })

        if User.objects.filter(email=correo).exists():
            messages.error(
            request, 'Ya existe un usuario con ese correo electrónico.')
            return render(request, 'docentespmmsp_create.html', {
                'programa_id': programa_id,
                'modulo_id': modulo_id
            })
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
        ci=cedula,
        rol=2,  # Asignar rol de docente
        )
        perfil.save()
        perfil_academico = PerfilAcademicoUsuario.objects.create(
            usuario=perfil,
            titulo_grado=titulo,
            titulo_postgrado_maestria=titulo_maestria,
            titulo_postgrado_doctorado=titulo_doctorado,
        )
        perfil_academico.save()
        messages.success(request, 'Docente creado exitosamente.')
        return redirect('crearternamodulopmmsp', programa_id=programa_id, modulo_id=modulo_id)
        
    return render(request,'docentespmmsp_create.html',
                {'programa_id': programa_id,
                'modulo_id': modulo_id,
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

        # Validar si el correo o CI ya existen
        if User.objects.filter(email=request.POST['email']).exists():
            messages.error(request, "El correo electrónico ya está registrado.")
            return render(request, 'tutordp_create.html', {
                'form': CustomUserCreationForm(),
                'periodo_id': periodo_id,
            })
        if PerfilUsuario.objects.filter(ci=request.POST['ci']).exists():
            messages.error(request, "La cédula ya está registrada.")
            return render(request, 'tutordp_create.html', {
                'form': CustomUserCreationForm(),
                'periodo_id': periodo_id,
            })

        try:
            ci = request.POST['ci'].strip()

            # Si no se proporciona username, usa la cédula
            username = request.POST.get('username', ci).strip() or ci

            # Si no se proporcionan contraseñas, usa la cédula
            password = request.POST.get('password1', ci).strip() or ci

            # Crear usuario principal
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=request.POST.get('first_name', '').strip(),
                last_name=request.POST.get('last_name', '').strip(),
                email=request.POST.get('email', '').strip(),
            )
            user.save()

            # Crear perfil general
            perfil = PerfilUsuario.objects.create(
                user=user,
                ci=ci,
                rol=5,
                telefono=request.POST.get('telefono', '').strip() or None,
                fecha_nacimiento=request.POST.get('fecha_nacimiento') or None,
                nacionalidad=request.POST.get('nacionalidad', '').strip() or None,
                sexo=request.POST.get('sexo') or None,
                provincia=request.POST.get('provincia', '').strip() or None,
            )

            # Crear perfil académico
            PerfilAcademicoUsuario.objects.create(
                usuario=perfil,
                titulo_grado=request.POST.get('titulo_grado', '').strip(),
                titulo_postgrado_maestria=request.POST.get('titulo_postgrado_maestria', '').strip(),
                titulo_postgrado_doctorado=request.POST.get('titulo_postgrado_doctorado', '').strip(),
            )

            messages.success(request, f"✅ Usuario {user.get_full_name()} creado correctamente.")
            return redirect('contratotutor_create', periodo_id=periodo_id)

        except IntegrityError:
            messages.error(request, "El nombre de usuario ya existe o los datos son inválidos.")
            return render(request, 'tutordp_create.html', {
                'form': CustomUserCreationForm(),
                'periodo_id': periodo_id,
            })
    # GET
    return render(request, 'tutordp_create.html', {
        'form': CustomUserCreationForm(),
        'periodo_id': periodo_id,
        })


@login_required
def coordinadordp_create(request, periodo_id):
    if request.method == 'POST':

        # Validar si el correo o CI ya existen
        if User.objects.filter(email=request.POST['email']).exists():
            messages.error(request, "El correo electrónico ya está registrado.")
            return render(request, 'coordinadordp_create.html', {
                'form': CustomUserCreationForm(),
                'periodo_id': periodo_id,
            })
        if PerfilUsuario.objects.filter(ci=request.POST['ci']).exists():
            messages.error(request, "La cédula ya está registrada.")
            return render(request, 'coordinadordp_create.html', {
                'form': CustomUserCreationForm(),
                'periodo_id': periodo_id,
            })

        try:
            ci = request.POST['ci'].strip()

            # Si no se proporciona username, usa la cédula
            username = request.POST.get('username', ci).strip() or ci

            # Si no se proporcionan contraseñas, usa la cédula
            password = request.POST.get('password1', ci).strip() or ci

            # Crear usuario principal
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=request.POST.get('first_name', '').strip(),
                last_name=request.POST.get('last_name', '').strip(),
                email=request.POST.get('email', '').strip(),
            )
            user.save()

            # Crear perfil general
            perfil = PerfilUsuario.objects.create(
                user=user,
                ci=ci,
                rol=3,
                telefono=request.POST.get('telefono', '').strip() or None,
                fecha_nacimiento=request.POST.get('fecha_nacimiento') or None,
                nacionalidad=request.POST.get('nacionalidad', '').strip() or None,
                sexo=request.POST.get('sexo') or None,
                provincia=request.POST.get('provincia', '').strip() or None,
            )

            # Crear perfil académico
            PerfilAcademicoUsuario.objects.create(
                usuario=perfil,
                titulo_grado=request.POST.get('titulo_grado', '').strip(),
                titulo_postgrado_maestria=request.POST.get('titulo_postgrado_maestria', '').strip(),
                titulo_postgrado_doctorado=request.POST.get('titulo_postgrado_doctorado', '').strip(),
            )

            messages.success(request, f"✅ Usuario {user.get_full_name()} creado correctamente.")
            return redirect('contratocoordinador_create', periodo_id=periodo_id)

        except IntegrityError:
            messages.error(request, "El nombre de usuario ya existe o los datos son inválidos.")
            return render(request, 'coordinadordp_create.html', {
                'form': CustomUserCreationForm(),
                'periodo_id': periodo_id,
            })
    # GET
    return render(request, 'coordinadordp_create.html', {
        'form': CustomUserCreationForm(),
        'periodo_id': periodo_id,
        })


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
            programa=programa.id,
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

        obj, created = MatriculaDocenteModulo.objects.update_or_create(
            programa=programa.id,
            content_type=modulo_ct,
            object_id=modulo.id,
            defaults={'docente': docente}
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


@login_required
@transaction.atomic
def CrearUsuarioCompleto(request):
    if request.method == 'POST':
        # Validación básica de contraseñas
        if request.POST['password1'] != request.POST['password2']:
            messages.error(request, "Las contraseñas no coinciden.")
            return render(request, 'crearusuariocompleto.html', {'form': CustomUserCreationForm()})

        # Validar si el correo o CI ya existen
        if User.objects.filter(email=request.POST['email']).exists():
            messages.error(request, "El correo electrónico ya está registrado.")
            return render(request, 'crearusuariocompleto.html', {'form': CustomUserCreationForm()})
        if PerfilUsuario.objects.filter(ci=request.POST['ci']).exists():
            messages.error(request, "La cédula ya está registrada.")
            return render(request, 'crearusuariocompleto.html', {'form': CustomUserCreationForm()})

        try:
            ci = request.POST['ci'].strip()

            # Si no se proporciona username, usa la cédula
            username = request.POST.get('username', ci).strip() or ci

            # Si no se proporcionan contraseñas, usa la cédula
            password = request.POST.get('password1', ci).strip() or ci

            # Crear usuario principal
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=request.POST.get('first_name', '').strip(),
                last_name=request.POST.get('last_name', '').strip(),
                email=request.POST.get('email', '').strip(),
            )
            user.save()

            # Crear perfil general
            perfil = PerfilUsuario.objects.create(
                user=user,
                ci=ci,
                rol=request.POST.get('rol'),
                telefono=request.POST.get('telefono', '').strip() or None,
                fecha_nacimiento=request.POST.get('fecha_nacimiento') or None,
                nacionalidad=request.POST.get('nacionalidad', '').strip() or None,
                sexo=request.POST.get('sexo') or None,
                provincia=request.POST.get('provincia', '').strip() or None,
            )

            # Crear perfil académico
            PerfilAcademicoUsuario.objects.create(
                usuario=perfil,
                titulo_grado=request.POST.get('titulo_grado', '').strip(),
                titulo_postgrado_maestria=request.POST.get('titulo_postgrado_maestria', '').strip(),
                titulo_postgrado_doctorado=request.POST.get('titulo_postgrado_doctorado', '').strip(),
            )

            messages.success(request, f"✅ Usuario {user.get_full_name()} creado correctamente.")
            return redirect('gestionusuarios')

        except IntegrityError:
            messages.error(request, "El nombre de usuario ya existe o los datos son inválidos.")
            return render(request, 'crearusuariocompleto.html', {'form': CustomUserCreationForm()})

    # GET
    return render(request, 'crearusuariocompleto.html', {'form': CustomUserCreationForm()})



@login_required
@transaction.atomic
def usuario_editar(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    perfil, _ = PerfilUsuario.objects.get_or_create(user=user)
    academico, _ = PerfilAcademicoUsuario.objects.get_or_create(usuario=perfil)

    if request.method == 'POST':
        # --------- User ---------
        username = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        email      = request.POST.get('email', '').strip()

        # Unicidad de email (excluyendo al propio usuario)
        if email and User.objects.exclude(pk=user.pk).filter(email=email).exists():
            messages.error(request, 'El correo electrónico ya está registrado por otro usuario.')
            return render(request, 'usuario_editar.html', {'user_obj': user, 'perfil': perfil, 'academico': academico})

        # --------- PerfilUsuario ---------
        ci              = (request.POST.get('ci') or '').strip() or None
        rol             = request.POST.get('rol') or None
        telefono        = (request.POST.get('telefono') or '').strip() or None
        fecha_nacimiento= request.POST.get('fecha_nacimiento') or None
        nacionalidad    = (request.POST.get('nacionalidad') or '').strip() or None
        sexo            = request.POST.get('sexo') or None
        provincia       = (request.POST.get('provincia') or '').strip() or None

        # Unicidad de CI (excluyendo su propio perfil)
        if ci and PerfilUsuario.objects.exclude(pk=perfil.pk).filter(ci=ci).exists():
            messages.error(request, 'La cédula/CI ya está registrada en otro usuario.')
            return render(request, 'usuario_editar.html', {'user_obj': user, 'perfil': perfil, 'academico': academico})

        # --------- PerfilAcademicoUsuario ---------
        titulo_grado   = (request.POST.get('titulo_grado') or '').strip() or None
        titulo_maestria= (request.POST.get('titulo_postgrado_maestria') or '').strip() or None
        titulo_doctor  = (request.POST.get('titulo_postgrado_doctorado') or '').strip() or None

        # --------- Password (opcional) ---------
        new_pass1 = request.POST.get('password1') or ''
        new_pass2 = request.POST.get('password2') or ''
        if new_pass1 or new_pass2:
            if new_pass1 != new_pass2:
                messages.error(request, 'Las contraseñas no coinciden.')
                return render(request, 'usuario_editar.html', {'user_obj': user, 'perfil': perfil, 'academico': academico})
            if len(new_pass1) < 6:
                messages.error(request, 'La contraseña debe tener al menos 6 caracteres.')
                return render(request, 'usuario_editar.html', {'user_obj': user, 'perfil': perfil, 'academico': academico})
            user.set_password(new_pass1)

        # --------- Guardar ---------
        user.username  = username or user.username
        user.first_name= first_name
        user.last_name = last_name
        user.email     = email
        user.save()

        perfil.ci               = ci
        perfil.rol              = rol if rol else None
        perfil.telefono         = telefono
        perfil.fecha_nacimiento = fecha_nacimiento or None
        perfil.nacionalidad     = nacionalidad
        perfil.sexo             = sexo if sexo else None
        perfil.provincia        = provincia
        perfil.save()

        academico.titulo_grado                 = titulo_grado
        academico.titulo_postgrado_maestria    = titulo_maestria
        academico.titulo_postgrado_doctorado   = titulo_doctor
        academico.save()

        messages.success(request, 'Datos actualizados correctamente.')
        return redirect('gestionusuarios')  # o vuelve a la misma página: return redirect('usuario_editar', user_id=user.id)

    # GET
    return render(request, 'usuario_editar.html', {
        'user_obj': user,
        'perfil': perfil,
        'academico': academico,
    })