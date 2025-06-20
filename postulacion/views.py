from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from programasposgrado.models import Maestrias, EspecialidadesMedicas, ProgramaPosgradoEM
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from usuarios.models import PerfilUsuario, DocumentosUsuarioPEM
from usuarios.forms import DocumentoUsuarioForm
from django.contrib import messages
import os
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

# Create your views here.


def especialidadesmedicaspos(request):
    ppespecialidadesmedicas_list = EspecialidadesMedicas.objects.all()
    return render(request, 'especialidadesmedicaspos.html', {
        'ppespecialidadesmedicas_list': ppespecialidadesmedicas_list,
    })


@login_required
def usuarriops_create(request, em_id):
    usuario = request.user
    usuario = get_object_or_404(User, id=usuario.id)
    especialidademedica = EspecialidadesMedicas.objects.get(id=em_id)
    print(especialidademedica.id)
    perfilusuario = PerfilUsuario.objects.filter(user=usuario.id)
    if perfilusuario:
        return redirect('informacionps_upload', em_id=especialidademedica.id)

    if request.method == 'POST':
        ci = request.POST.get('ci', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        fecha_nacimiento = request.POST.get('fecha_nacimiento', '').strip()
        nacionalidad = request.POST.get('nacionalidad', '').strip()
        sexo = request.POST.get('sexo', '').strip()
        titulotercernivel = request.POST.get('titulotercernivel', '').strip()
        provincia = request.POST.get('provincia', '').strip()

        if not (ci and telefono and fecha_nacimiento and nacionalidad and sexo and titulotercernivel and provincia):
            messages.error(request, 'Todos los campos son obligatorios.')
            return render(request, 'usuariops_create.html', {
                'especialidademedica': especialidademedica,
                'usuario': usuario,
            })

        if PerfilUsuario.objects.filter(ci=ci).exists():
            messages.error(request, 'El número de cédula ya está registrado.')
            return render(request, 'usuariops_create.html', {
                'especialidademedica': especialidademedica,
                'usuario': usuario,

            })

        PerfilUsuario.objects.create(
            user=usuario,
            ci=ci,
            rol=1,
            telefono=telefono,
            fecha_nacimiento=fecha_nacimiento,
            nacionalidad=nacionalidad,
            sexo=sexo,
            titulotercernivel=titulotercernivel,
            provincia=provincia
        )
        return redirect('informacionps_upload', em_id=especialidademedica.id)
    else:

        return render(request, 'usuariops_create.html', {
            'especialidademedica': especialidademedica,
            'error': 'Error al crear el usuario. Por favor, verifica los datos.',
            'usuario': usuario,
        })


def informacionps_upload(request, em_id):
    usuario = request.user
    perfil_usuario = get_object_or_404(PerfilUsuario, user=usuario)
    especialidadmedica = get_object_or_404(EspecialidadesMedicas, id=em_id)
    # Busca (o crea) el registro de documentos para este usuario
    documentos_usuario, created = DocumentosUsuarioPEM.objects.get_or_create(
        usuario=perfil_usuario, especialidadmedica=em_id)

    if request.method == 'POST':
        form = DocumentoUsuarioForm(
            request.POST, request.FILES, instance=documentos_usuario)
        if form.is_valid():
            # Solo reemplaza los archivos que llegaron en el request.FILES
            for field in ['docidentificacion', 'titulosenescyt']:
                if request.FILES.get(field):  # solo si viene nuevo
                    new_file = form.cleaned_data.get(field)
                    old_file = getattr(documentos_usuario, field)
                    if old_file and os.path.isfile(old_file.path):
                        print(f"Eliminando archivo antiguo: {old_file.path}")
                        os.remove(old_file.path)
                    setattr(documentos_usuario, field, new_file)

            # Guarda el formulario para actualizar los campos
            if documentos_usuario.docidentificacion:
                documentos_usuario.estado_docidentificacion = 'Enviado'
            else:
                documentos_usuario.estado_docidentificacion = 'Pendiente'

            if documentos_usuario.titulosenescyt:
                documentos_usuario.estado_titulosenescyt = 'Enviado'
            else:
                documentos_usuario.estado_titulosenescyt = 'Pendiente'

            documentos_usuario.save()
            eliminar_archivos_huerfanos(request)
            messages.success(request, 'Documentos actualizados exitosamente.')
            # ajusta al nombre correcto de tu vista destino
            return render(request, 'informacionps_upload.html', {
                'usuario': usuario,
                'perfil_usuario': perfil_usuario,
                'form': form,
                'documentos_usuario': documentos_usuario,
                'especialidadmedica': especialidadmedica
            })
        else:
            messages.error(
                request, 'Debes subir 2 archivos. Revisa los archivos y vuelve a intentarlo.')
    else:
        form = DocumentoUsuarioForm(instance=documentos_usuario)

    return render(request, 'informacionps_upload.html', {
        'usuario': usuario,
        'perfil_usuario': perfil_usuario,
        'form': form,
        'documentos_usuario': documentos_usuario,
        'especialidadmedica': especialidadmedica
    })


def eliminar_archivos_huerfanos(request):
    documentos_dir = os.path.join(settings.MEDIA_ROOT, 'documentospem')

    if not os.path.exists(documentos_dir):
        messages.warning(request, 'La carpeta no existe.')
        return

    # Archivos usados en base de datos
    archivos_usados = set()
    for doc in DocumentosUsuarioPEM.objects.all():
        for field in ['docidentificacion', 'titulosenescyt']:
            archivo = getattr(doc, field)
            if archivo:
                archivos_usados.add(os.path.basename(archivo.name))

    # Archivos en disco
    archivos_en_disco = os.listdir(documentos_dir)
    archivos_huerfanos = [
        f for f in archivos_en_disco if f not in archivos_usados]

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
    messages.warning(
        request, f'Se eliminaron {len(archivos_huerfanos)} archivos anteriores.')


def documentosps_enviados(request):
    especialidadesmedicas_list = EspecialidadesMedicas.objects.all()
    return render(request, 'documentosps_enviados.html', {
        'especialidadesmedicas_list': especialidadesmedicas_list,
    })


def documentosps_validados(request, em_id):
    especialidadmedica = get_object_or_404(EspecialidadesMedicas, id=em_id)
    documentosusuariospostulacion_list = DocumentosUsuarioPEM.objects.filter(
        especialidadmedica=em_id, estado_docidentificacion="Aprobado", estado_titulosenescyt="Aprobado")
    return render(request, 'documentosps_validados.html', {
        'documentosusuariospostulacion_list': documentosusuariospostulacion_list,
        'especialidadmedica': especialidadmedica
    })


def documentosps_porvalidar(request, em_id):
    especialidadmedica = get_object_or_404(EspecialidadesMedicas, id=em_id)
    documentosusuariospostulacion_list = DocumentosUsuarioPEM.objects.filter(
        especialidadmedica=em_id, estado_docidentificacion="Enviado", estado_titulosenescyt="Enviado")
    return render(request, 'documentosps_porvalidar.html', {
        'documentosusuariospostulacion_list': documentosusuariospostulacion_list,
        'especialidadmedica': especialidadmedica
    })


def documentosps_validar(request, doc_id, em_id):
    documentosusuario = get_object_or_404(DocumentosUsuarioPEM, id=doc_id)
    especialidadmedica = get_object_or_404(EspecialidadesMedicas, id=em_id)
    documentosusuariospostulacion_list = DocumentosUsuarioPEM.objects.filter(
        especialidadmedica=em_id, estado_docidentificacion="Enviado", estado_titulosenescyt="Enviado")
    documentosusuario.estado_docidentificacion = "Aprobado"
    documentosusuario.estado_titulosenescyt = "Aprobado"
    documentosusuario.save()
    return render(request, 'documentosps_porvalidar.html', {
        'documentosusuariospostulacion_list': documentosusuariospostulacion_list,
        'especialidadmedica': especialidadmedica
    })


@require_POST
@login_required
def documentosps_novalidar(request):
    doc_id = request.POST.get('doc_id')

    especialidad_id = request.POST.get('especialidad_id')

    accion = request.POST.get('accion')
    documentosusuariospostulacion_list = DocumentosUsuarioPEM.objects.filter(
        especialidadmedica=especialidad_id, estado_docidentificacion="Enviado", estado_titulosenescyt="Enviado")
    especialidadmedica = get_object_or_404(
        EspecialidadesMedicas, id=especialidad_id)
    observacion_doc = request.POST.get('observacion_docidentificacion')
    observacion_titulo = request.POST.get('observacion_titulosenescyt')

    try:
        doc = DocumentosUsuarioPEM.objects.get(id=doc_id)
    except DocumentosUsuarioPEM.DoesNotExist:
        messages.error(request, 'Documento no encontrado.')
        return redirect('documentospsporvalidar', em_id=especialidad_id)

    # Guardar observaciones
    doc.observaciondocidentificacion = observacion_doc
    doc.observaciontitulosenescyt = observacion_titulo

    if accion == 'rectificar':
        doc.estado_docidentificacion = 'Rectificar'
        doc.estado_titulosenescyt = 'Rectificar'
        messages.warning(request, 'Solicitado rectificación del documento.')
    elif accion == 'rechazar':
        doc.estado_docidentificacion = 'Rechazado'
        doc.estado_titulosenescyt = 'Rechazado'
        messages.error(request, 'Documento rechazado.')

    doc.save()

    return redirect('documentospsporvalidar', em_id=especialidad_id)