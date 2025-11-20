from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import ProgramaPosgrado, ValorProgramaPosgrado, CoordinadorPrograma, CoordinadorPagos, ContratoDocenteGestion, ContratoTutorGestion, EstudianteProgramaGestion
from .forms import ValorProgramaPosgradoForm, CoordinadorProgramaForm, CoordinadorPagosForm, ContratoDocenteGestionForm, ContratoTutorGestionForm, EstudianteProgramaGestionForm
from datosposgrado.models import ContratoCoordinador, ContratosDocentes, ContratoTutor
from usuarios.models import PerfilUsuario, PerfilAcademicoUsuario
from programasposgrado.models import Maestrias, Modulos
from django.db import transaction
from usuarios.models import User, MatriculaUsuario
from django.urls import reverse
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum, F
from django.conf import settings
from xhtml2pdf import pisa
import os
from django.template.loader import get_template
from django.http import HttpResponse
from django.utils import timezone
from main.decorators import role_required

# Create your views here.
@role_required([3, 4, 7])
def informacionprogramaposgrado(request, programa_id):
    programa = get_object_or_404(ProgramaPosgrado, id=programa_id)
    fin = _calc_programa_finanzas(programa)

    return render(request, 'info_programaposgrado.html', {
        'programa_id': programa_id,
        'programa': programa,
        'fin': fin,
    })


@login_required
@role_required([3, 4, 7])  
def valorprogramaposgrado_detail(request, programa_id):
    programa = get_object_or_404(ProgramaPosgrado, id=programa_id)
    vp = ValorProgramaPosgrado.objects.filter(programa=programa).first()
    if not vp:
        # si no existe, manda a crear
        return redirect('valorprogramaposgrado_create', programa_id=programa.id)
    # si quieres una vista de solo lectura, puedes renderizar otro template.
    # Aquí te redirijo al editar directamente:
    return redirect('valorprogramaposgrado_update', programa_id=programa.id)

@login_required
@role_required([3, 4]) 
def valorprogramaposgrado_create(request, programa_id):
    programa = get_object_or_404(ProgramaPosgrado, id=programa_id)

    # si ya existe, NO permitir crear de nuevo
    existente = ValorProgramaPosgrado.objects.filter(programa=programa).first()
    if existente:
        messages.info(request, 'El valor de este programa ya existe. Puedes editarlo.')
        return redirect('valorprogramaposgrado_update', programa_id=programa.id)

    if request.method == 'POST':
        form = ValorProgramaPosgradoForm(request.POST)
        if form.is_valid():
            vp = form.save(commit=False)
            vp.programa = programa
            # forzar USD si quieres:
            if not vp.moneda:
                vp.moneda = 'USD'
            vp.save()
            messages.success(request, 'Valores del programa guardados correctamente.')
            return redirect('valorprogramaposgrado_update', programa_id=programa.id)
    else:
        form = ValorProgramaPosgradoForm(initial={'moneda': 'USD'})

    return render(request, 'valorprogramaposgrado_form.html', {
        'programa': programa,
        'form': form,
        'modo': 'crear',
    })

@login_required
@role_required([3, 4]) 
def valorprogramaposgrado_update(request, programa_id):
    programa = get_object_or_404(ProgramaPosgrado, id=programa_id)
    vp = ValorProgramaPosgrado.objects.filter(programa=programa).first()
    if not vp:
        messages.info(request, 'Aún no existe el valor de este programa. Crea uno.')
        return redirect('valorprogramaposgrado_create', programa_id=programa.id)

    if request.method == 'POST':
        form = ValorProgramaPosgradoForm(request.POST, instance=vp)
        if form.is_valid():
            vp = form.save(commit=False)
            if not vp.moneda:
                vp.moneda = 'USD'
            vp.save()
            messages.success(request, 'Valores del programa actualizados correctamente.')
            return redirect('valorprogramaposgrado_update', programa_id=programa.id)
    else:
        form = ValorProgramaPosgradoForm(instance=vp)

    return render(request, 'valorprogramaposgrado_form.html', {
        'programa': programa,
        'form': form,
        'modo': 'editar',
        'vp': vp,
    })



@login_required
@role_required([3, 4]) 
def contratos_coordinadores_programa(request, programa_id):
    """
    Lista los contratos de coordinadores (de datosposgrado) para el programa dado y
    muestra/gestiona periodos (fecha_inicio/fecha_fin) de CoordinadorPrograma.
    """
    programa = get_object_or_404(ProgramaPosgrado, id=programa_id)

    # 1) Traer contratos por programa (sin FK)
    contratos = list(
        ContratoCoordinador.objects
        .filter(programadeposgrado=programa_id)
        .order_by('-created')
    )

    # 2) Resolver usuarios por ID en batch (evita N+1)
    coord_ids = [c.coordinador for c in contratos if c.coordinador]
    usuarios = {u.id: u for u in User.objects.filter(id__in=coord_ids)}

    # 3) Traer periodos existentes por (programa, coordinador)
    periodos = CoordinadorPrograma.objects.filter(
        programa=programa,
        coordinador_id__in=coord_ids
    ).order_by('-fecha_inicio', '-created')

    # 4) Indexar periodos por coordinador_id
    periodos_por_coord = {}
    for p in periodos:
        periodos_por_coord.setdefault(p.coordinador_id, []).append(p)

    # 5) Preparar filas simples para el template (evitando templatetags extra)
    filas = []
    for c in contratos:
        u = usuarios.get(c.coordinador)
        filas.append({
            'contrato': c,
            'usuario': u,  # puede ser None si no existe el User con ese ID
            'periodos': periodos_por_coord.get(c.coordinador, []),
            'fecha_inicio_contrato': getattr(c, 'fechainicio', None),
            'fecha_fin_contrato': getattr(c, 'fechafin', None),
        })

    return render(request, 'contratos_coordinadores_programa.html', {
        'programa': programa,
        'filas': filas,
    })


@login_required
@role_required([3, 4]) 
@transaction.atomic
def coordinadorperiodo_create(request, programa_id, coordinador_id):
    programa = get_object_or_404(ProgramaPosgrado, id=programa_id)
    coordinador = get_object_or_404(User, id=coordinador_id)

    # Instancia con FKs preasignadas
    base_instance = CoordinadorPrograma(programa=programa, coordinador=coordinador)

    if request.method == 'POST':
        form = CoordinadorProgramaForm(request.POST, instance=base_instance)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()
            messages.success(request, 'Periodo creado correctamente.')
            return redirect('contratos_coordinadores_programa', programa_id=programa.id)
        else:
            # Pasar cada error del form al sistema de mensajes
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        # errores generales (non_field_errors)
                        messages.error(request, error)
                    else:
                        # errores asociados a un campo específico
                        label = form.fields[field].label if field in form.fields else field
                        messages.error(request, f"{label}: {error}")
    else:
        form = CoordinadorProgramaForm(instance=base_instance)

    return render(request, 'coordinadorperiodo_form.html', {
        'programa': programa,
        'coordinador': coordinador,
        'form': form,
        'modo': 'crear',
    })


@login_required
@role_required([3, 4]) 
@transaction.atomic
def coordinadorperiodo_update(request, programa_id, coordinador_id, pk):
    programa = get_object_or_404(ProgramaPosgrado, id=programa_id)
    coordinador = get_object_or_404(User, id=coordinador_id)
    # Traemos el periodo existente (esto asegura que la instance tenga las FKs)
    periodo = get_object_or_404(
        CoordinadorPrograma,
        pk=pk,
        programa=programa,
        coordinador=coordinador
    )

    if request.method == 'POST':
        form = CoordinadorProgramaForm(request.POST, instance=periodo)
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.save()
                messages.success(request, 'Periodo actualizado correctamente.')
                url = reverse('contratos_coordinadores_programa', args=[programa.id])
                return redirect(f"{url}?coord={coordinador.id}#coord-{coordinador.id}")
            except ValidationError as e:
                # Si por alguna razón el modelo lanza ValidationError aquí
                if hasattr(e, "message_dict"):
                    for field, errs in e.message_dict.items():
                        for err in errs:
                            form.add_error(field if field in form.fields else None, err)
                else:
                    for err in (e.messages if hasattr(e, "messages") else [str(e)]):
                        form.add_error(None, err)
                messages.error(request, 'No se pudo actualizar. Corrige los errores indicados.')
        else:
            messages.error(request, 'No se pudo actualizar. Revisa los errores del formulario.')
    else:
        # GET → el form viene precargado con las fechas actuales
        form = CoordinadorProgramaForm(instance=periodo)

    return render(request, 'coordinadorperiodo_form.html', {
        'programa': programa,
        'coordinador': coordinador,
        'form': form,
        'modo': 'editar',
        'periodo': periodo,
    })


@login_required
@role_required([3, 4]) 
@transaction.atomic
def coordinadorperiodo_delete(request, programa_id, coordinador_id, pk):
    """
    Eliminar un periodo (confirmación).
    """
    programa = get_object_or_404(ProgramaPosgrado, id=programa_id)
    coordinador = get_object_or_404(User, id=coordinador_id)
    periodo = get_object_or_404(CoordinadorPrograma, pk=pk, programa=programa, coordinador=coordinador)

    if request.method == 'POST':
        periodo.delete()
        messages.success(request, 'Periodo eliminado correctamente.')
        return redirect('contratos_coordinadores_programa', programa_id=programa.id)

    return render(request, 'coordinadorperiodo_confirm_delete.html', {
        'programa': programa,
        'coordinador': coordinador,
        'periodo': periodo,
    })



@login_required
@role_required([3, 4]) 
def pagos_coordinadores_programa(request, programa_id):
    """
    Lista pagos agrupados por CONTRATO dentro del programa.
    Muestra total por contrato y total general del programa.
    """
    programa = get_object_or_404(ProgramaPosgrado, id=programa_id)

    # Todos los contratos de este programa (sin FK)
    contratos = list(
        ContratoCoordinador.objects
        .filter(programadeposgrado=programa.id)
        .order_by('-created')
    )

    # Mapa de coordinadores (User)
    coord_ids = sorted({c.coordinador for c in contratos if c.coordinador})
    usuarios = {u.id: u for u in User.objects.filter(id__in=coord_ids)}

    # Pagos por programa y por contrato
    pagos = CoordinadorPagos.objects.filter(programa=programa).select_related('contrato', 'coordinador').order_by('-mes_pago', '-created')

    # Indexar pagos por contrato_id
    pagos_por_contrato = {}
    total_programa = Decimal('0.00')
    for p in pagos:
        pagos_por_contrato.setdefault(p.contrato_id, []).append(p)
        total_programa += (p.valor_total or Decimal('0.00'))

    # Construir secciones por contrato (cada sección pertenece a un coordinador)
    secciones = []
    for c in contratos:
        u = usuarios.get(c.coordinador)
        lista = pagos_por_contrato.get(c.id, [])
        total_contrato = sum((p.valor_total or Decimal('0.00')) for p in lista)
        secciones.append({
            'contrato': c,
            'usuario': u,
            'pagos': lista,
            'total_contrato': total_contrato,
        })

    context = {
        'programa': programa,
        'secciones': secciones,
        'total_programa': total_programa,
    }
    return render(request, 'pagos_coordinadores_programa.html', context)


@login_required
@role_required([3, 4]) 
@transaction.atomic
def coordinadorpago_create_by_contrato(request, programa_id, contrato_id):
    """
    Crear pago en la sección de un CONTRATO específico.
    No se listan todos los contratos; solo el del ID recibido.
    """
    programa = get_object_or_404(ProgramaPosgrado, id=programa_id)
    contrato = get_object_or_404(ContratoCoordinador, pk=contrato_id)

    # Validación de pertenencia del contrato al programa
    if contrato.programadeposgrado != programa.id:
        messages.error(request, 'El contrato no pertenece a este programa.')
        return redirect('pagos_coordinadores_programa', programa_id=programa.id)

    # Resolver coordinador (User) desde entero
    coordinador = get_object_or_404(User, id=contrato.coordinador)

    if request.method == 'POST':
        form = CoordinadorPagosForm(
            request.POST,
            programa=programa,
            coordinador_id=coordinador.id,
            contrato_fijo=contrato.id
        )
        if form.is_valid():
            pago = form.save(commit=False)
            pago.programa = programa
            pago.coordinador = coordinador
            try:
                pago.full_clean()
            except Exception as e:
                from django.core.exceptions import ValidationError
                if isinstance(e, ValidationError):
                    if hasattr(e, 'message_dict'):
                        for field, errs in e.message_dict.items():
                            for err in errs:
                                form.add_error(field if field in form.fields else None, err)
                    else:
                        for err in e.messages:
                            form.add_error(None, err)
                messages.error(request, 'No se pudo registrar el pago. Corrige los errores.')
            else:
                pago.save()
                messages.success(request, 'Pago registrado correctamente.')
                url = reverse('pagos_coordinadores_programa', args=[programa.id])
                # anclar al contrato
                return redirect(f"{url}?contrato={contrato.id}#contrato-{contrato.id}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    label = form.fields[field].label if field in form.fields else field
                    messages.error(request, f"{label}: {error}")
    else:
        form = CoordinadorPagosForm(
            programa=programa,
            coordinador_id=coordinador.id,
            contrato_fijo=contrato.id,
            initial={'moneda': 'USD'}
        )

    return render(request, 'coordinadorpago_form.html', {
        'programa': programa,
        'coordinador': coordinador,
        'contrato': contrato,
        'form': form,
        'modo': 'crear',
    })


@login_required
@role_required([3, 4]) 
@transaction.atomic
def coordinadorpago_update(request, programa_id, pago_id):
    """
    Edita un pago. El contrato NO se cambia (se bloquea a su valor actual).
    """
    programa = get_object_or_404(ProgramaPosgrado, id=programa_id)
    pago = get_object_or_404(CoordinadorPagos, pk=pago_id, programa=programa)
    contrato = get_object_or_404(ContratoCoordinador, pk=pago.contrato_id)
    coordinador = get_object_or_404(User, id=pago.coordinador_id)

    if request.method == 'POST':
        form = CoordinadorPagosForm(
            request.POST,
            instance=pago,
            programa=programa,
            coordinador_id=coordinador.id,
            contrato_fijo=contrato.id  # <- bloquea el select a un solo contrato
        )
        if form.is_valid():
            obj = form.save(commit=False)
            try:
                obj.full_clean()
                obj.save()
                messages.success(request, 'Pago actualizado correctamente.')
                url = reverse('pagos_coordinadores_programa', args=[programa.id])
                return redirect(f"{url}?contrato={contrato.id}#contrato-{contrato.id}")
            except Exception as e:
                from django.core.exceptions import ValidationError
                if isinstance(e, ValidationError):
                    if hasattr(e, 'message_dict'):
                        for field, errs in e.message_dict.items():
                            for err in errs:
                                form.add_error(field if field in form.fields else None, err)
                    else:
                        for err in e.messages:
                            form.add_error(None, err)
                messages.error(request, 'No se pudo actualizar el pago. Corrige los errores.')
        else:
            messages.error(request, 'No se pudo actualizar. Revisa los errores del formulario.')
    else:
        form = CoordinadorPagosForm(
            instance=pago,
            programa=programa,
            coordinador_id=coordinador.id,
            contrato_fijo=contrato.id
        )

    return render(request, 'coordinadorpago_form.html', {
        'programa': programa,
        'coordinador': coordinador,
        'contrato': contrato,
        'form': form,
        'modo': 'editar',
        'pago': pago,
    })


@login_required
@role_required([3, 4]) 
@transaction.atomic
def coordinadorpago_delete(request, programa_id, pago_id):
    programa = get_object_or_404(ProgramaPosgrado, id=programa_id)
    pago = get_object_or_404(CoordinadorPagos, pk=pago_id, programa=programa)
    contrato = get_object_or_404(ContratoCoordinador, pk=pago.contrato_id)
    coordinador = get_object_or_404(User, id=pago.coordinador_id)

    if request.method == 'POST':
        pago.delete()
        messages.success(request, 'Pago eliminado correctamente.')
        url = reverse('pagos_coordinadores_programa', args=[programa.id])
        return redirect(f"{url}?contrato={contrato.id}#contrato-{contrato.id}")

    return render(request, 'coordinadorpago_confirm_delete.html', {
        'programa': programa,
        'coordinador': coordinador,
        'contrato': contrato,
        'pago': pago,
    })


@login_required
@role_required([3, 4]) 
def docentes_contratos_programa(request, programa_id):
    """
    Lista contratos de docentes para el programa (desde datosposgrado.ContratosDocentes),
    muestra datos de usuario/perfil/títulos y permite agregar/editar 'gestión' adicional
    (fecha_contratacion, pago_realizado, numero_factura, observaciones).
    """
    programa = get_object_or_404(ProgramaPosgrado, id=programa_id)

    # 1) Contratos del programa (sin FK)
    contratos = list(
        ContratosDocentes.objects
        .filter(programadeposgrado=programa.id)
        .order_by('-created')
    )

    # 2) Resolver docentes (User) por IDs enteros
    docente_ids = sorted({c.docente for c in contratos if c.docente})
    usuarios = {u.id: u for u in User.objects.filter(id__in=docente_ids)}
    modulo_ids = sorted({c.modulo for c in contratos if c.modulo})
    modulos = {m.id: m for m in Modulos.objects.filter(id__in=modulo_ids)}
    # 3) Perfiles (RUC/CI, teléfono)
    perfiles = {p.user_id: p for p in PerfilUsuario.objects.filter(user_id__in=docente_ids)}

    # 4) Académicos (busca un “título” representativo: doctorado > maestría > grado)
    acad_por_user = {}
    for pa in PerfilAcademicoUsuario.objects.select_related('usuario__user').all():
        uid = pa.usuario.user_id
        if uid in docente_ids:
            tit = pa.titulo_postgrado_doctorado or pa.titulo_postgrado_maestria or pa.titulo_grado
            if uid not in acad_por_user or (pa.titulo_postgrado_doctorado and acad_por_user[uid] != pa.titulo_postgrado_doctorado):
                acad_por_user[uid] = tit

    # 5) Gestión adicional existente por contrato
    gestiones = {g.contrato_id: g for g in ContratoDocenteGestion.objects.filter(contrato_id__in=[c.id for c in contratos])}

    # 6) Construir filas + totales
    filas = []
    total_contratado = Decimal('0.00')
    total_pagado = Decimal('0.00')

    for c in contratos:
        u = usuarios.get(c.docente)
        perfil = perfiles.get(c.docente)
        titulo = acad_por_user.get(c.docente, '')

        valor_total = (c.horasacademicas or 0) * (c.valorxhora or Decimal('0.00'))
        total_contratado += Decimal(valor_total)

        modulo_obj = modulos.get(c.modulo)
        modulo_nombre = getattr(modulo_obj, 'nombre', None) or f"ID {c.modulo}"

        g = gestiones.get(c.id)
        if g and g.pago_realizado:
            total_pagado += Decimal(valor_total)

        filas.append({
            'contrato': c,
            'usuario': u,
            'perfil': perfil,
            'titulo': titulo,
            'modulo_nombre': modulo_nombre,
            'valor_total': valor_total,
            'gestion': g,
        })

    total_pendiente = total_contratado - total_pagado

    return render(request, 'contratos_docentes_programa.html', {
        'programa': programa,
        'filas': filas,
        'total_contratado': total_contratado,
        'total_pagado': total_pagado,
        'total_pendiente': total_pendiente,
    })


@login_required
@role_required([3, 4]) 
def contratodocente_gestion_create(request, programa_id, contrato_id):
    programa = get_object_or_404(ProgramaPosgrado, id=programa_id)
    contrato = get_object_or_404(ContratosDocentes, pk=contrato_id)

    if contrato.programadeposgrado != programa.id:
        messages.error(request, 'El contrato no pertenece a este programa.')
        return redirect('docentes_contratos_programa', programa_id=programa.id)

    if ContratoDocenteGestion.objects.filter(contrato=contrato).exists():
        messages.info(request, 'Ya existen datos adicionales. Puedes editarlos.')
        return redirect('contratodocente_gestion_update', programa_id=programa.id, contrato_id=contrato.id)

    if request.method == 'POST':
        form = ContratoDocenteGestionForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.contrato = contrato
            obj.full_clean()
            obj.save()
            messages.success(request, 'Datos adicionales guardados correctamente.')
            url = reverse('docentes_contratos_programa', args=[programa.id])
            return redirect(f"{url}#contrato-{contrato.id}")
        else:
            messages.error(request, 'No se pudo guardar. Revisa los errores.')
    else:
        form = ContratoDocenteGestionForm()

    # Resolver docente para mostrar en la cabecera
    docente_user = User.objects.filter(id=contrato.docente).first()

    return render(request, 'contratodocente_gestion_form.html', {
        'programa': programa,
        'contrato': contrato,
        'docente_user': docente_user,
        'form': form,
        'modo': 'crear',
    })


@login_required
@role_required([3, 4]) 
def contratodocente_gestion_update(request, programa_id, contrato_id):
    programa = get_object_or_404(ProgramaPosgrado, id=programa_id)
    contrato = get_object_or_404(ContratosDocentes, pk=contrato_id)
    gestion = get_object_or_404(ContratoDocenteGestion, contrato=contrato)

    if request.method == 'POST':
        form = ContratoDocenteGestionForm(request.POST, instance=gestion)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.full_clean()
            obj.save()
            messages.success(request, 'Datos adicionales actualizados correctamente.')
            url = reverse('docentes_contratos_programa', args=[programa.id])
            return redirect(f"{url}#contrato-{contrato.id}")
        else:
            messages.error(request, 'No se pudo actualizar. Revisa los errores.')
    else:
        form = ContratoDocenteGestionForm(instance=gestion)

    docente_user = User.objects.filter(id=contrato.docente).first()

    return render(request, 'contratodocente_gestion_form.html', {
        'programa': programa,
        'contrato': contrato,
        'docente_user': docente_user,
        'form': form,
        'modo': 'editar',
        'gestion': gestion,
    })



@login_required
@role_required([3, 4]) 
def tutores_contratos_programa(request, programa_id):
    """
    Lista contratos de tutores del programa, permite ver/crear/editar datos adicionales.
    Muestra totales: contratado, pagado, pendiente.
    """
    programa = get_object_or_404(ProgramaPosgrado, id=programa_id)

    contratos = list(
        ContratoTutor.objects.filter(programadeposgrado=programa.id).order_by('-created')
    )

    # Mapear Users por IDs enteros (tutor y maestrante)
    tutor_ids = {c.tutor for c in contratos if c.tutor}
    est_ids = {c.maestrante for c in contratos if c.maestrante}
    user_ids = sorted(tutor_ids | est_ids)
    usuarios = {u.id: u for u in User.objects.filter(id__in=user_ids)}

    # Perfiles (para CI/telefono)
    perfiles = {p.user_id: p for p in PerfilUsuario.objects.filter(user_id__in=user_ids)}

    # Gestión existente
    gestiones = {g.contrato_id: g for g in ContratoTutorGestion.objects.filter(
        contrato_id__in=[c.id for c in contratos]
    )}

    filas = []
    total_contratado = Decimal('0.00')
    total_pagado = Decimal('0.00')

    for c in contratos:
        tutor = usuarios.get(c.tutor)
        est = usuarios.get(c.maestrante)
        perfil_tutor = perfiles.get(c.tutor)

        valor_total = c.valorcontrato or Decimal('0.00')
        total_contratado += valor_total

        g = gestiones.get(c.id)
        if g and g.pago_realizado:
            total_pagado += valor_total

        filas.append({
            'contrato': c,
            'tutor_user': tutor,
            'tutor_perfil': perfil_tutor,
            'estudiante_user': est,
            'gestion': g,
            'valor_total': valor_total,
        })

    total_pendiente = total_contratado - total_pagado

    return render(request, 'tutores_contratos_programa.html', {
        'programa': programa,
        'filas': filas,
        'total_contratado': total_contratado,
        'total_pagado': total_pagado,
        'total_pendiente': total_pendiente,
    })


@login_required
@role_required([3, 4]) 
def contratotutor_gestion_create(request, programa_id, contrato_id):
    programa = get_object_or_404(ProgramaPosgrado, id=programa_id)
    contrato = get_object_or_404(ContratoTutor, pk=contrato_id)

    if contrato.programadeposgrado != programa.id:
        messages.error(request, 'El contrato no pertenece a este programa.')
        return redirect('tutores_contratos_programa', programa_id=programa.id)

    if ContratoTutorGestion.objects.filter(contrato=contrato).exists():
        messages.info(request, 'Ya existen datos adicionales para este contrato. Puedes editarlos.')
        return redirect('contratotutor_gestion_update', programa_id=programa.id, contrato_id=contrato.id)

    if request.method == 'POST':
        form = ContratoTutorGestionForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.contrato = contrato
            try:
                obj.full_clean()
                obj.save()
                messages.success(request, 'Datos guardados correctamente.')
                url = reverse('tutores_contratos_programa', args=[programa.id])
                return redirect(f"{url}#contrato-{contrato.id}")
            except Exception as e:
                messages.error(request, 'No se pudo guardar. Revisa los errores.')
        else:
            messages.error(request, 'Corrige los errores del formulario.')
    else:
        form = ContratoTutorGestionForm()

    tutor_user = User.objects.filter(id=contrato.tutor).first()
    est_user = User.objects.filter(id=contrato.maestrante).first()

    return render(request, 'contratotutor_gestion_form.html', {
        'programa': programa,
        'contrato': contrato,
        'tutor_user': tutor_user,
        'est_user': est_user,
        'form': form,
        'modo': 'crear',
    })


@login_required
@role_required([3, 4]) 
def contratotutor_gestion_update(request, programa_id, contrato_id):
    programa = get_object_or_404(ProgramaPosgrado, id=programa_id)
    contrato = get_object_or_404(ContratoTutor, pk=contrato_id)
    gestion = get_object_or_404(ContratoTutorGestion, contrato=contrato)

    if request.method == 'POST':
        form = ContratoTutorGestionForm(request.POST, instance=gestion)
        if form.is_valid():
            obj = form.save(commit=False)
            try:
                obj.full_clean()
                obj.save()
                messages.success(request, 'Datos actualizados correctamente.')
                url = reverse('tutores_contratos_programa', args=[programa.id])
                return redirect(f"{url}#contrato-{contrato.id}")
            except Exception:
                messages.error(request, 'No se pudo actualizar. Revisa los errores.')
        else:
            messages.error(request, 'Corrige los errores del formulario.')
    else:
        form = ContratoTutorGestionForm(instance=gestion)

    tutor_user = User.objects.filter(id=contrato.tutor).first()
    est_user = User.objects.filter(id=contrato.maestrante).first()

    return render(request, 'contratotutor_gestion_form.html', {
        'programa': programa,
        'contrato': contrato,
        'tutor_user': tutor_user,
        'est_user': est_user,
        'form': form,
        'modo': 'editar',
        'gestion': gestion,
    })

@login_required
@role_required([3, 4]) 
def estudiantes_programa_list(request, programa_id):
    programa = get_object_or_404(ProgramaPosgrado, id=programa_id)

    ct = ContentType.objects.get_for_model(ProgramaPosgrado)
    matriculas = (
        MatriculaUsuario.objects
        .filter(content_type=ct, object_id=programa.id, rol_en_programa='estudiante')
        .select_related('usuario')
        .order_by('-fecha_matricula')
    )

    user_ids = [m.usuario_id for m in matriculas]
    usuarios = {u.id: u for u in User.objects.filter(id__in=user_ids)}
    perfiles = {p.user_id: p for p in PerfilUsuario.objects.filter(user_id__in=user_ids)}

    gestiones = {
        g.usuario_id: g
        for g in EstudianteProgramaGestion.objects.filter(usuario_id__in=user_ids, programa=programa)
    }

    # valores del programa (si existen)
    vp = ValorProgramaPosgrado.objects.filter(programa=programa).first()
    valores_programa = None
    total_programa = None
    plan_pago = None
    cuota_mensual = None

    if vp:
        plan_pago = vp.plan_pago  # '2_COLEGIATURAS' o '10_CUOTAS'
        if plan_pago == ValorProgramaPosgrado.PLAN_2:
            valores_programa = {
                'inscripcion': vp.valorinscripcion or Decimal('0.00'),
                'matricula': vp.valormatricula or Decimal('0.00'),
                'cole1': vp.primeracolegiatura or Decimal('0.00'),
                'cole2': vp.segundacolegiatura or Decimal('0.00'),
                'moneda': vp.moneda,
            }
            total_programa = sum([
                valores_programa['inscripcion'],
                valores_programa['matricula'],
                valores_programa['cole1'],
                valores_programa['cole2'],
            ], Decimal('0.00'))
        else:
            cuota_mensual = vp.cuota_mensual or Decimal('0.00')
            valores_programa = {
                'inscripcion': vp.valorinscripcion or Decimal('0.00'),
                'matricula': vp.valormatricula or Decimal('0.00'),
                'cuota_mensual': cuota_mensual,
                'valor_total': vp.valor_total or Decimal('0.00'),
                'moneda': vp.moneda,
            }
            total_programa = valores_programa['valor_total']

    filas = []
    for m in matriculas:
        u = usuarios.get(m.usuario_id)
        p = perfiles.get(m.usuario_id)
        g = gestiones.get(m.usuario_id)

        total_pagado_est = Decimal('0.00')
        if vp and g:
            # Inscripción / Matrícula (independiente del plan)
            if g.pago_inscripcion:
                total_pagado_est += valores_programa['inscripcion']
            if g.pago_matricula:
                total_pagado_est += valores_programa['matricula']

            if plan_pago == ValorProgramaPosgrado.PLAN_2:
                if g.pago_primera_colegiatura:
                    total_pagado_est += valores_programa['cole1']
                if g.pago_segunda_colegiatura:
                    total_pagado_est += valores_programa['cole2']
            else:
                # 10 cuotas: sumar n * cuota_mensual
                n = g.cuotas_pagadas or 0
                total_pagado_est += (cuota_mensual or Decimal('0.00')) * Decimal(n)

        filas.append({
            'usuario': u,
            'perfil': p,
            'gestion': g,
            'total_pagado': total_pagado_est if vp else None,
            'vp': vp,
        })

    return render(request, 'estudiantes_programa_list.html', {
        'programa': programa,
        'filas': filas,
        'valores_programa': valores_programa,
        'total_programa': total_programa,
        'plan_pago': plan_pago,              # <-- para condicionar columnas en el HTML
    })


@login_required
@role_required([3, 4]) 
@transaction.atomic
def estudiante_programa_gestion_upsert(request, programa_id, user_id):
    programa = get_object_or_404(ProgramaPosgrado, id=programa_id)
    user = get_object_or_404(User, id=user_id)

    obj, created = EstudianteProgramaGestion.objects.get_or_create(
        usuario=user, programa=programa
    )

    vp = ValorProgramaPosgrado.objects.filter(programa=programa).first()
    plan_pago = vp.plan_pago if vp else None

    if request.method == 'POST':
        form = EstudianteProgramaGestionForm(request.POST, instance=obj)
        if form.is_valid():
            g = form.save(commit=False)
            g.usuario = user
            g.programa = programa
            # Si el plan es 2 colegiaturas, fuerza 0 (None -> 0)
            if plan_pago == getattr(vp, 'PLAN_2', '2_COLEGIATURAS'):
                g.cuotas_pagadas = 0
            # En plan 10, si viene vacío, trata como 0
            if g.cuotas_pagadas is None:
                g.cuotas_pagadas = 0
            g.full_clean()
            g.save()
            messages.success(request, 'Datos del estudiante guardados correctamente.')
            url = reverse('estudiantes_programa_list', args=[programa.id])
            return redirect(f"{url}#est-{user.id}")
        else:
            #messages.error(request, 'Corrige los errores del formulario.')
                # Mostrar errores con detalle
            messages.error(request, 'Corrige los errores del formulario.')
            for field, errs in form.errors.items():
                for err in errs:
                    if field == '__all__':
                        messages.error(request, err)
                    else:
                        label = form.fields.get(field).label if field in form.fields else field
                        messages.error(request, f"{label}: {err}")
    else:
        form = EstudianteProgramaGestionForm(instance=obj)

    perfil = PerfilUsuario.objects.filter(user=user).first()
    return render(request, 'estudiante_programa_form.html', {
        'programa': programa,
        'user_obj': user,
        'perfil': perfil,
        'form': form,
        'creando': created,
        'plan_pago': plan_pago,        # <-- para condicionar el formulario
        'vp': vp,                      # opcional por si quieres mostrar cuota en el form
    })

@role_required([3, 4]) 
def _calc_programa_finanzas(programa: ProgramaPosgrado):
    """
    Retorna un dict con:
      total_ingresos, total_egresos, saldo,
      desgloses:
        - plan 2: ingresos_{inscripcion,matricula,colegiatura1,colegiatura2}
        - plan 10: ingresos_{inscripcion,matricula,cuotas10} y total_cuotas_pagadas
      además: moneda, plan_pago, cuota_mensual (si aplica), valor_total_programa
    """
    cero = Decimal('0.00')

    # ---------- Valores del programa ----------
    vp = ValorProgramaPosgrado.objects.filter(programa=programa).first()
    moneda = vp.moneda if vp else 'USD'
    plan_pago = getattr(vp, 'plan_pago', getattr(ValorProgramaPosgrado, 'PLAN_2', '2_COLEGIATURAS'))
    cuota_mensual = getattr(vp, 'cuota_mensual', None) or cero

    ingresos_insc = ingresos_mat = ingresos_cole1 = ingresos_cole2 = ingresos_cuotas10 = cero
    total_cuotas_pagadas = 0

    # ---------- INGRESOS (estudiantes) ----------
    if vp:
        gestiones = EstudianteProgramaGestion.objects.filter(programa=programa).only(
            'pago_inscripcion', 'pago_matricula',
            'pago_primera_colegiatura', 'pago_segunda_colegiatura',
            'cuotas_pagadas'
        )

        pagaron_insc = gestiones.filter(pago_inscripcion=True).count()
        pagaron_mat  = gestiones.filter(pago_matricula=True).count()

        ingresos_insc  = (vp.valorinscripcion or cero) * Decimal(pagaron_insc)
        ingresos_mat   = (vp.valormatricula or cero) * Decimal(pagaron_mat)

        if plan_pago == ValorProgramaPosgrado.PLAN_2:
            pagaron_c1   = gestiones.filter(pago_primera_colegiatura=True).count()
            pagaron_c2   = gestiones.filter(pago_segunda_colegiatura=True).count()
            ingresos_cole1 = (vp.primeracolegiatura or cero) * Decimal(pagaron_c1)
            ingresos_cole2 = (vp.segundacolegiatura or cero) * Decimal(pagaron_c2)
        else:
            # 10 cuotas: sumar n * cuota_mensual
            total_cuotas_pagadas = sum((g.cuotas_pagadas or 0) for g in gestiones)
            ingresos_cuotas10 = cuota_mensual * Decimal(total_cuotas_pagadas)

    total_ingresos = ingresos_insc + ingresos_mat + ingresos_cole1 + ingresos_cole2 + ingresos_cuotas10

    # ---------- EGRESOS ----------
    eg_coordinadores = (
        CoordinadorPagos.objects
        .filter(programa=programa)
        .aggregate(s=Sum('valor_total'))['s'] or cero
    )

    # Docentes pagados (por gestión)
    docentes_pagados_ids = list(
        ContratoDocenteGestion.objects
        .filter(contrato__programadeposgrado=programa.id, pago_realizado=True)
        .values_list('contrato_id', flat=True)
    )
    eg_docentes = cero
    if docentes_pagados_ids:
        eg_docentes = sum(
            (c.horasacademicas or 0) * (c.valorxhora or cero)
            for c in ContratosDocentes.objects.filter(id__in=docentes_pagados_ids)
        )

    # Tutores pagados (por gestión)
    tutores_pagados_ids = list(
        ContratoTutorGestion.objects
        .filter(contrato__programadeposgrado=programa.id, pago_realizado=True)
        .values_list('contrato_id', flat=True)
    )
    eg_tutores = cero
    if tutores_pagados_ids:
        eg_tutores = (
            ContratoTutor.objects
            .filter(id__in=tutores_pagados_ids)
            .aggregate(s=Sum('valorcontrato'))['s'] or cero
        )

    total_egresos = eg_coordinadores + eg_docentes + eg_tutores
    saldo = total_ingresos - total_egresos

    return {
        'moneda': moneda,
        'plan_pago': plan_pago,
        'cuota_mensual': cuota_mensual if plan_pago == ValorProgramaPosgrado.PLAN_10 else None,
        'valor_total_programa': (vp.valor_total if getattr(vp, 'valor_total', None) else None),

        'total_ingresos': total_ingresos,
        'total_egresos': total_egresos,
        'saldo': saldo,

        # Desglose plan 2
        'ingresos_inscripcion': ingresos_insc,
        'ingresos_matricula': ingresos_mat,
        'ingresos_colegiatura1': ingresos_cole1,
        'ingresos_colegiatura2': ingresos_cole2,

        # Desglose plan 10
        'ingresos_cuotas10': ingresos_cuotas10,
        'total_cuotas_pagadas': total_cuotas_pagadas,

        # Egresos
        'egresos_coordinadores': eg_coordinadores,
        'egresos_docentes': eg_docentes,
        'egresos_tutores': eg_tutores,
    }

###################REPORTE PDF#########################

# --- Resolver paths de static/media para xhtml2pdf
def _link_callback(uri, rel):
    sUrl, sRoot = settings.STATIC_URL, settings.STATIC_ROOT
    mUrl, mRoot = settings.MEDIA_URL, settings.MEDIA_ROOT

    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
    elif uri.startswith(sUrl):
        path = os.path.join(sRoot, uri.replace(sUrl, ""))
    else:
        return uri
    return path if os.path.isfile(path) else uri


@login_required
@role_required([3, 4]) 
def programa_reporte_pdf(request, programa_id):
    """
    PDF general con: resumen financiero, valores del programa,
    coordinadores (contratos/pagos), docentes (contratos/gestión),
    tutores (contratos/gestión) y estudiantes (pagos/estado).
    """
    programa = ProgramaPosgrado.objects.get(id=programa_id)

    # 1) Resumen financiero con TU helper ya existente:
    #    Debe aceptar el objeto programa y devolver un dict 'fin'
    #    con llaves: moneda, total_ingresos, total_egresos, saldo,
    #    ingresos_* y egresos_* (como ya usas en la vista HTML).
    fin = _calc_programa_finanzas(programa)

    # 2) Valores del programa
    vp = ValorProgramaPosgrado.objects.filter(programa=programa).first()

    # 3) Coordinadores (contratos + pagos)
    contratos_coord = list(
        ContratoCoordinador.objects.filter(programadeposgrado=programa.id)
    )
    pagos_coord = (
        CoordinadorPagos.objects
        .filter(programa=programa)
        .select_related('coordinador', 'contrato')
        .order_by('mes_pago')
    )
    pagos_por_contrato = {}
    for p in pagos_coord:
        pagos_por_contrato.setdefault(p.contrato_id, []).append(p)

    coord_detalle = []
    for c in contratos_coord:
        usuario = User.objects.filter(id=c.coordinador).first()
        lista = pagos_por_contrato.get(c.id, [])
        total_contrato = sum([(p.valor_total or Decimal('0.00')) for p in lista], Decimal('0.00'))
        coord_detalle.append({
            'contrato': c,
            'usuario': usuario,
            'pagos': lista,
            'total': total_contrato,
            'fecha_inicio_contrato': getattr(c, 'fechainicio', None),
            'fecha_fin_contrato': getattr(c, 'fechafin', None),
        })

    # 4) Docentes (contratos + gestión)
    contratos_doc = list(
        ContratosDocentes.objects.filter(programadeposgrado=programa.id)
    )
    modulos = {
        m.id: m for m in Modulos.objects.filter(
            id__in=[c.modulo for c in contratos_doc if c.modulo]
        )
    }
    gest_doc = {
        g.contrato_id: g for g in ContratoDocenteGestion.objects.filter(
            contrato__in=contratos_doc
        )
    }
    doc_detalle = []
    for c in contratos_doc:
        docente = User.objects.filter(id=c.docente).first()
        modulo_nombre = (modulos.get(c.modulo).nombre
                         if modulos.get(c.modulo) else f"ID {c.modulo}")
        valor_total = (c.horasacademicas or 0) * (c.valorxhora or Decimal('0.00'))
        g = gest_doc.get(c.id)
        doc_detalle.append({
            'contrato': c,
            'docente': docente,
            'modulo': modulo_nombre,
            'valor_total': valor_total,
            'gestion': g,
        })

    # 5) Tutores (contratos + gestión)
    contratos_tut = list(
        ContratoTutor.objects.filter(programadeposgrado=programa.id)
    )
    gest_tut = {
        g.contrato_id: g for g in ContratoTutorGestion.objects.filter(
            contrato__in=contratos_tut
        )
    }
    tut_detalle = []
    for c in contratos_tut:
        tutor = User.objects.filter(id=c.tutor).first()
        est = User.objects.filter(id=c.maestrante).first()
        g = gest_tut.get(c.id)
        tut_detalle.append({
            'contrato': c,
            'tutor': tutor,
            'estudiante': est,
            'gestion': g,
        })

    # 6) Estudiantes (matriculados + gestión + total pagado)
    ct = ContentType.objects.get_for_model(ProgramaPosgrado)
    matriculas = (
        MatriculaUsuario.objects
        .filter(content_type=ct, object_id=programa.id, rol_en_programa='estudiante')
        .select_related('usuario')
        .order_by('usuario__last_name', 'usuario__first_name')
    )
    perfiles = {
        p.user_id: p for p in PerfilUsuario.objects.filter(
            user_id__in=[m.usuario_id for m in matriculas]
        )
    }
    gest_est = {
        g.usuario_id: g for g in EstudianteProgramaGestion.objects.filter(programa=programa)
    }
    est_detalle = []
    for m in matriculas:
        u = m.usuario
        g = gest_est.get(u.id)
        total_pagado = Decimal('0.00')
        if vp and g:
            if g.pago_inscripcion:
                total_pagado += vp.valorinscripcion or Decimal('0.00')
            if g.pago_matricula:
                total_pagado += vp.valormatricula or Decimal('0.00')
            if g.pago_primera_colegiatura:
                total_pagado += vp.primeracolegiatura or Decimal('0.00')
            if g.pago_segunda_colegiatura:
                total_pagado += vp.segundacolegiatura or Decimal('0.00')
        est_detalle.append({
            'user': u,
            'perfil': perfiles.get(u.id),
            'gestion': g,
            'total_pagado': total_pagado,
        })

    # 7) Render del PDF
    template = get_template('reporte_programa.html')
    html = template.render({
        'programa': programa,
        'vp': vp,
        'fin': fin,
        'coord_detalle': coord_detalle,
        'doc_detalle': doc_detalle,
        'tut_detalle': tut_detalle,
        'est_detalle': est_detalle,
        'generado_por': request.user,
        'generado_en': timezone.now(),
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="reporte_programa_{programa.id}.pdf"'
    pisa.CreatePDF(src=html, dest=response, link_callback=_link_callback)
    return response