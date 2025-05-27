from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from .models import PerfilUsuario
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

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
            return redirect('perfil')
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
            return redirect('perfil')


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
