from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from programasposgrado.models import Maestrias
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from usuarios.models import PerfilUsuario, DocumentosUsuario
from usuarios.forms import  DocumentoUsuarioForm
from django.contrib import messages
import os
from django.conf import settings

# Create your views here.


def usuarrioad_create(request):
    maestrias_list = Maestrias.objects.all()
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        ci = request.POST.get('ci', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        fecha_nacimiento = request.POST.get('fecha_nacimiento', '').strip()
        nacionalidad = request.POST.get('nacionalidad', '').strip()
        sexo = request.POST.get('sexo', '').strip()
        titulotercernivel = request.POST.get('titulotercernivel', '').strip()
        provincia = request.POST.get('provincia', '').strip()

        if not (first_name and last_name and email and ci and telefono and fecha_nacimiento and nacionalidad and sexo and titulotercernivel and provincia):
            messages.error(request, 'Todos los campos son obligatorios.')
            return render(request, 'usuarioad_create.html', {
                'maestrias_list': maestrias_list,
            })
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Correo electrónico no válido.')
            return render(request, 'usuarioad_create.html', {
                'maestrias_list': maestrias_list,
            })
        if User.objects.filter(email=email).exists():
            messages.error(request, 'El correo electrónico ya está registrado.')
            return render(request, 'usuarioad_create.html', {
                'maestrias_list': maestrias_list,
            })
        if User.objects.filter(username=ci).exists():
            messages.error(request, 'El número de cédula ya está registrado.')
            return render(request, 'usuarioad_create.html', {
                'maestrias_list': maestrias_list,
            })
        user = User.objects.create_user(
            username=ci,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=ci  
        )
        PerfilUsuario.objects.create(
            user=user,
            ci=ci,
            rol=1,
            telefono=telefono,
            fecha_nacimiento=fecha_nacimiento,
            nacionalidad=nacionalidad,
            sexo=sexo,
            titulotercernivel=titulotercernivel,
            provincia=provincia
        )
        user.save()
        login(request, user)
        return redirect('perfil')
    else:
       
        return render(request, 'usuarioad_create.html', {

            'maestrias_list': maestrias_list,
            'error': 'Error al crear el usuario. Por favor, verifica los datos.',
        })



def informacionad_upload(request, user_id):
    user = get_object_or_404(User, id=user_id)
    perfil_usuario = get_object_or_404(PerfilUsuario, user=user)

    # Busca (o crea) el registro de documentos para este usuario
    documentos_usuario, created = DocumentosUsuario.objects.get_or_create(usuario=perfil_usuario)

    if request.method == 'POST':
        form = DocumentoUsuarioForm(request.POST, request.FILES, instance=documentos_usuario)
        if form.is_valid():
            # Solo reemplaza los archivos que llegaron en el request.FILES
            for field in ['titulo3', 'solicitudinscripcion', 'experiencialaboral', 'comprobantepago']:
                if request.FILES.get(field):  # solo si viene nuevo
                    new_file = form.cleaned_data.get(field)
                    old_file = getattr(documentos_usuario, field)
                    print(f"Nuevo: {new_file} Antiguo {old_file}")
                    
                    if old_file and os.path.isfile(old_file.path):
                        print(f"Eliminando archivo antiguo: {old_file.path}")
                        os.remove(old_file.path)  # borra físicamente el archivo viejo
                    setattr(documentos_usuario, field, new_file)

            # Guarda el formulario para actualizar los campos
            if documentos_usuario.titulo3:
                documentos_usuario.estado_titulo3 = 'Enviado'
            else:
                documentos_usuario.estado_titulo3 = 'Pendiente'
            
            if documentos_usuario.solicitudinscripcion:
                documentos_usuario.estado_solicitudinscripcion = 'Enviado'
            else:
                documentos_usuario.estado_solicitudinscripcion = 'Pendiente'

            if documentos_usuario.experiencialaboral:
                documentos_usuario.estado_experiencialaboral = 'Enviado'
            else:
                documentos_usuario.estado_experiencialaboral = 'Pendiente'

            if documentos_usuario.comprobantepago:
                documentos_usuario.estado_comprobantepago = 'Enviado'
            else:
                documentos_usuario.estado_comprobantepago = 'Pendiente'
            

            documentos_usuario.save()
            eliminar_archivos_huerfanos(request)
            messages.success(request, 'Documentos actualizados exitosamente.')
            return redirect('perfil')  # ajusta al nombre correcto de tu vista destino
        else:
            messages.error(request, 'Error al subir los documentos. Revisa los archivos y vuelve a intentarlo.')
    else:
        form = DocumentoUsuarioForm(instance=documentos_usuario)

    return render(request, 'informacionad_upload.html', {
        'user': user,
        'perfil_usuario': perfil_usuario,
        'form': form,
        'documentos_usuario': documentos_usuario,
    })


def eliminar_archivos_huerfanos(request):
    documentos_dir = os.path.join(settings.MEDIA_ROOT, 'documentos')

    if not os.path.exists(documentos_dir):
        messages.warning(request, 'La carpeta documentos no existe.')
        return

    # Archivos usados en base de datos
    archivos_usados = set()
    for doc in DocumentosUsuario.objects.all():
        for field in ['titulo3', 'solicitudinscripcion', 'experiencialaboral', 'comprobantepago']:
            archivo = getattr(doc, field)
            if archivo:
                archivos_usados.add(os.path.basename(archivo.name))

    # Archivos en disco
    archivos_en_disco = os.listdir(documentos_dir)
    archivos_huerfanos = [f for f in archivos_en_disco if f not in archivos_usados]

    if not archivos_huerfanos:
        messages.success(request, 'No se encontraron archivos huérfanos.')
        return

    # Eliminar archivos huérfanos
    for archivo in archivos_huerfanos:
        archivo_path = os.path.join(documentos_dir, archivo)
        try:
            os.remove(archivo_path)
        except Exception as e:
            messages.error(request, f'Error al eliminar {archivo}: {str(e)}')

