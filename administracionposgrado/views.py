from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import timedelta

from .models import (
    ProgramaPosgrado,  # viene re-exportado desde .models (alias a programasposgrado)
    ValorProgramaPosgrado, CoordinadorPrograma, CoordinadorPagos,
    ContratoDocenteGestion, ContratoTutorGestion, EstudianteProgramaGestion
)
from .forms import (
    ValorProgramaPosgradoForm, CoordinadorProgramaForm, CoordinadorPagosForm,
    ContratoDocenteGestionForm, ContratoTutorGestionForm, EstudianteProgramaGestionForm, ProgramaPAOForm
)
from datosposgrado.models import ContratoCoordinador, ContratosDocentes, ContratoTutor
from usuarios.models import PerfilUsuario, PerfilAcademicoUsuario
from programasposgrado.models import Maestrias, Modulos, ProgramaPosgradoEM, ModulosEM

from django.db import transaction
from usuarios.models import User, MatriculaUsuario
from django.urls import reverse
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum
from django.conf import settings
from xhtml2pdf import pisa
import os
from django.template.loader import get_template
from django.http import HttpResponse
from django.utils import timezone
from main.decorators import role_required


# ---------------------------------------------------
# Helpers GFK
# ---------------------------------------------------
def _ct_for(obj):
    return ContentType.objects.get_for_model(obj.__class__)

def _programa_filter(programa):
    ct = _ct_for(programa)
    return {"programa_content_type": ct, "programa_object_id": programa.id}

def _get_programa_or_404(programa_id):
    """
    Soporta ProgramaPosgrado (Maestría) y ProgramaPosgradoEM (Especialidad).
    """
    try:
        return get_object_or_404(ProgramaPosgrado, id=programa_id)
    except Exception:
        return get_object_or_404(ProgramaPosgradoEM, id=programa_id)

def _resolve_modulos_map(contratos_docentes):
    """
    Devuelve un dict {(ct_id, object_id): modulo_obj} para Modulos y ModulosEM.
    Evita N+1 al mostrar nombre de módulo.
    """
    pares = []
    for c in contratos_docentes:
        if c.modulo_content_type_id and c.modulo_object_id:
            pares.append((c.modulo_content_type_id, c.modulo_object_id))

    if not pares:
        return {}

    # separar ids por tipo
    ct_mod_m = ContentType.objects.get_for_model(Modulos).id
    ct_mod_em = ContentType.objects.get_for_model(ModulosEM).id

    ids_m = [oid for (ctid, oid) in pares if ctid == ct_mod_m]
    ids_em = [oid for (ctid, oid) in pares if ctid == ct_mod_em]

    mod_map = {}
    if ids_m:
        for m in Modulos.objects.filter(id__in=ids_m):
            mod_map[(ct_mod_m, m.id)] = m
    if ids_em:
        for m in ModulosEM.objects.filter(id__in=ids_em):
            mod_map[(ct_mod_em, m.id)] = m

    return mod_map


# Create your views here.
@role_required([3, 4, 7])
def informacionprogramaposgrado(request, programa_id):
    programa = _get_programa_or_404(programa_id)
    fin = _calc_programa_finanzas(programa)

    return render(request, 'info_programaposgrado.html', {
        'programa_id': programa_id,
        'programa': programa,
        'fin': fin,
    })


@login_required
@role_required([3, 4, 7])
def valorprogramaposgrado_detail(request, programa_id):
    programa = _get_programa_or_404(programa_id)

    vp = ValorProgramaPosgrado.objects.filter(**_programa_filter(programa)).first()
    if not vp:
        return redirect('valorprogramaposgrado_create', programa_id=programa.id)

    return redirect('valorprogramaposgrado_update', programa_id=programa.id)


@login_required
@role_required([3, 4])
def valorprogramaposgrado_create(request, programa_id):
    programa = _get_programa_or_404(programa_id)

    existente = ValorProgramaPosgrado.objects.filter(**_programa_filter(programa)).first()
    if existente:
        messages.info(request, 'El valor de este programa ya existe. Puedes editarlo.')
        return redirect('valorprogramaposgrado_update', programa_id=programa.id)

    if request.method == 'POST':
        form = ValorProgramaPosgradoForm(request.POST)
        if form.is_valid():
            vp = form.save(commit=False)
            vp.programa = programa  # ✅ asigna GFK
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
    programa = _get_programa_or_404(programa_id)

    vp = ValorProgramaPosgrado.objects.filter(**_programa_filter(programa)).first()
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
    programa = _get_programa_or_404(programa_id)
    pf = _programa_filter(programa)

    contratos = list(
        ContratoCoordinador.objects
        .filter(**pf)
        .order_by('-created')
    )

    coord_ids = [c.coordinador for c in contratos if c.coordinador]
    usuarios = {u.id: u for u in User.objects.filter(id__in=coord_ids)}

    periodos = CoordinadorPrograma.objects.filter(
        programa_content_type=pf["programa_content_type"],
        programa_object_id=pf["programa_object_id"],
        coordinador_id__in=coord_ids
    ).order_by('-fecha_inicio', '-created')

    periodos_por_coord = {}
    for p in periodos:
        periodos_por_coord.setdefault(p.coordinador_id, []).append(p)

    filas = []
    for c in contratos:
        u = usuarios.get(c.coordinador)
        filas.append({
            'contrato': c,
            'usuario': u,
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
    programa = _get_programa_or_404(programa_id)
    coordinador = get_object_or_404(User, id=coordinador_id)

    base_instance = CoordinadorPrograma(
        coordinador=coordinador,
        programa=programa  # ✅ setea GFK
    )

    if request.method == 'POST':
        form = CoordinadorProgramaForm(request.POST, instance=base_instance)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()
            messages.success(request, 'Periodo creado correctamente.')
            return redirect('contratos_coordinadores_programa', programa_id=programa.id)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, error)
                    else:
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
    programa = _get_programa_or_404(programa_id)
    coordinador = get_object_or_404(User, id=coordinador_id)
    pf = _programa_filter(programa)

    periodo = get_object_or_404(
        CoordinadorPrograma,
        pk=pk,
        programa_content_type=pf["programa_content_type"],
        programa_object_id=pf["programa_object_id"],
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
    programa = _get_programa_or_404(programa_id)
    coordinador = get_object_or_404(User, id=coordinador_id)
    pf = _programa_filter(programa)

    periodo = get_object_or_404(
        CoordinadorPrograma,
        pk=pk,
        programa_content_type=pf["programa_content_type"],
        programa_object_id=pf["programa_object_id"],
        coordinador=coordinador
    )

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
    programa = _get_programa_or_404(programa_id)
    pf = _programa_filter(programa)

    contratos = list(
        ContratoCoordinador.objects
        .filter(**pf)
        .order_by('-created')
    )

    coord_ids = sorted({c.coordinador for c in contratos if c.coordinador})
    usuarios = {u.id: u for u in User.objects.filter(id__in=coord_ids)}

    pagos = (
        CoordinadorPagos.objects
        .filter(programa_content_type=pf["programa_content_type"], programa_object_id=pf["programa_object_id"])
        .select_related('contrato', 'coordinador')
        .order_by('-mes_pago', '-created')
    )

    pagos_por_contrato = {}
    total_programa = Decimal('0.00')
    for p in pagos:
        pagos_por_contrato.setdefault(p.contrato_id, []).append(p)
        total_programa += (p.valor_total or Decimal('0.00'))

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

    return render(request, 'pagos_coordinadores_programa.html', {
        'programa': programa,
        'secciones': secciones,
        'total_programa': total_programa,
    })


@login_required
@role_required([3, 4])
@transaction.atomic
def coordinadorpago_create_by_contrato(request, programa_id, contrato_id):
    programa = _get_programa_or_404(programa_id)
    contrato = get_object_or_404(ContratoCoordinador, pk=contrato_id)

    # ✅ Validación de pertenencia por GFK
    pf = _programa_filter(programa)
    if (contrato.programa_content_type_id != pf["programa_content_type"].id) or (contrato.programa_object_id != pf["programa_object_id"]):
        messages.error(request, 'El contrato no pertenece a este programa.')
        return redirect('pagos_coordinadores_programa', programa_id=programa.id)

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
            pago.programa = programa  # ✅ setea GFK
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
    programa = _get_programa_or_404(programa_id)
    pf = _programa_filter(programa)

    pago = get_object_or_404(
        CoordinadorPagos,
        pk=pago_id,
        programa_content_type=pf["programa_content_type"],
        programa_object_id=pf["programa_object_id"]
    )

    contrato = get_object_or_404(ContratoCoordinador, pk=pago.contrato_id)
    coordinador = get_object_or_404(User, id=pago.coordinador_id)

    if request.method == 'POST':
        form = CoordinadorPagosForm(
            request.POST,
            instance=pago,
            programa=programa,
            coordinador_id=coordinador.id,
            contrato_fijo=contrato.id
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
    programa = _get_programa_or_404(programa_id)
    pf = _programa_filter(programa)

    pago = get_object_or_404(
        CoordinadorPagos,
        pk=pago_id,
        programa_content_type=pf["programa_content_type"],
        programa_object_id=pf["programa_object_id"]
    )

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
    programa = _get_programa_or_404(programa_id)
    pf = _programa_filter(programa)

    contratos = list(
        ContratosDocentes.objects
        .filter(**pf)
        .order_by('-created')
    )

    docente_ids = sorted({c.docente for c in contratos if c.docente})
    usuarios = {u.id: u for u in User.objects.filter(id__in=docente_ids)}

    perfiles = {p.user_id: p for p in PerfilUsuario.objects.filter(user_id__in=docente_ids)}

    acad_por_user = {}
    for pa in PerfilAcademicoUsuario.objects.select_related('usuario__user').all():
        uid = pa.usuario.user_id
        if uid in docente_ids:
            tit = pa.titulo_postgrado_doctorado or pa.titulo_postgrado_maestria or pa.titulo_grado
            if uid not in acad_por_user or (pa.titulo_postgrado_doctorado and acad_por_user[uid] != pa.titulo_postgrado_doctorado):
                acad_por_user[uid] = tit

    gestiones = {g.contrato_id: g for g in ContratoDocenteGestion.objects.filter(contrato_id__in=[c.id for c in contratos])}

    mod_map = _resolve_modulos_map(contratos)

    filas = []
    total_contratado = Decimal('0.00')
    total_pagado = Decimal('0.00')

    for c in contratos:
        u = usuarios.get(c.docente)
        perfil = perfiles.get(c.docente)
        titulo = acad_por_user.get(c.docente, '')

        valor_total = (c.horasacademicas or 0) * (c.valorxhora or Decimal('0.00'))
        total_contratado += Decimal(valor_total)

        key_mod = (c.modulo_content_type_id, c.modulo_object_id)
        modulo_obj = mod_map.get(key_mod)
        modulo_nombre = getattr(modulo_obj, 'nombre', None) if modulo_obj else (f"ID {c.modulo_object_id}" if c.modulo_object_id else "")

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
    programa = _get_programa_or_404(programa_id)
    pf = _programa_filter(programa)

    contrato = get_object_or_404(ContratosDocentes, pk=contrato_id)

    # ✅ pertenencia por GFK
    if (contrato.programa_content_type_id != pf["programa_content_type"].id) or (contrato.programa_object_id != pf["programa_object_id"]):
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
    programa = _get_programa_or_404(programa_id)
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
    programa = _get_programa_or_404(programa_id)
    pf = _programa_filter(programa)

    contratos = list(
        ContratoTutor.objects.filter(**pf).order_by('-created')
    )

    tutor_ids = {c.tutor for c in contratos if c.tutor}
    est_ids = {c.maestrante for c in contratos if c.maestrante}
    user_ids = sorted(tutor_ids | est_ids)
    usuarios = {u.id: u for u in User.objects.filter(id__in=user_ids)}

    perfiles = {p.user_id: p for p in PerfilUsuario.objects.filter(user_id__in=user_ids)}

    gestiones = {g.contrato_id: g for g in ContratoTutorGestion.objects.filter(
        contrato_id__in=[c.id for c in contratos]
    )}
    # Obtener gestiones de estudiantes para este programa
    gestiones_estudiantes = {
        g.usuario_id: g
        for g in EstudianteProgramaGestion.objects.filter(
            usuario_id__in=est_ids,
            programa_content_type=pf["programa_content_type"],
            programa_object_id=pf["programa_object_id"]
        ).select_related('modalidad')
    }
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
        gestion_estudiante = gestiones_estudiantes.get(c.maestrante)

        filas.append({
            'contrato': c,
            'tutor_user': tutor,
            'tutor_perfil': perfil_tutor,
            'estudiante_user': est,
            'gestion': g,
            'gestion_estudiante': gestion_estudiante,
            'modalidad': gestion_estudiante.modalidad if gestion_estudiante else None,
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
    programa = _get_programa_or_404(programa_id)
    pf = _programa_filter(programa)

    contrato = get_object_or_404(ContratoTutor, pk=contrato_id)

    if (contrato.programa_content_type_id != pf["programa_content_type"].id) or (contrato.programa_object_id != pf["programa_object_id"]):
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
            except Exception:
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
    programa = _get_programa_or_404(programa_id)
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
    programa = _get_programa_or_404(programa_id)
    pf = _programa_filter(programa)

    ct_prog = pf["programa_content_type"]
    matriculas = (
        MatriculaUsuario.objects
        .filter(content_type=ct_prog, object_id=programa.id, rol_en_programa='estudiante')
        .select_related('usuario')
        .order_by('-fecha_matricula')
    )

    user_ids = [m.usuario_id for m in matriculas]
    usuarios = {u.id: u for u in User.objects.filter(id__in=user_ids)}
    perfiles = {p.user_id: p for p in PerfilUsuario.objects.filter(user_id__in=user_ids)}

    gestiones = {
        g.usuario_id: g
        for g in EstudianteProgramaGestion.objects.filter(
            usuario_id__in=user_ids,
            programa_content_type=pf["programa_content_type"],
            programa_object_id=pf["programa_object_id"]
        )
    }

    vp = ValorProgramaPosgrado.objects.filter(**pf).first()

    valores_programa = None
    total_programa = None
    plan_pago = None
    cuota_mensual = None

    if vp:
        plan_pago = vp.plan_pago
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
        'plan_pago': plan_pago,
    })


@login_required
@role_required([3, 4])
@transaction.atomic
def estudiante_programa_gestion_upsert(request, programa_id, user_id):
    programa = _get_programa_or_404(programa_id)
    user = get_object_or_404(User, id=user_id)
    pf = _programa_filter(programa)

    obj, created = EstudianteProgramaGestion.objects.get_or_create(
        usuario=user,
        programa_content_type=pf["programa_content_type"],
        programa_object_id=pf["programa_object_id"]
    )

    vp = ValorProgramaPosgrado.objects.filter(**pf).first()
    plan_pago = vp.plan_pago if vp else None

    if request.method == 'POST':
        form = EstudianteProgramaGestionForm(request.POST, instance=obj)
        if form.is_valid():
            g = form.save(commit=False)
            g.usuario = user
            g.programa = programa  # ✅ setea GFK

            if plan_pago == getattr(vp, 'PLAN_2', '2_COLEGIATURAS'):
                g.cuotas_pagadas = 0
            if g.cuotas_pagadas is None:
                g.cuotas_pagadas = 0

            g.full_clean()
            g.save()
            messages.success(request, 'Datos del estudiante guardados correctamente.')
            url = reverse('estudiantes_programa_list', args=[programa.id])
            return redirect(f"{url}#est-{user.id}")
        else:
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
        'plan_pago': plan_pago,
        'vp': vp,
    })


def _calc_programa_finanzas(programa):
    cero = Decimal('0.00')
    pf = _programa_filter(programa)

    vp = ValorProgramaPosgrado.objects.filter(**pf).first()
    moneda = vp.moneda if vp else 'USD'
    plan_pago = getattr(vp, 'plan_pago', getattr(ValorProgramaPosgrado, 'PLAN_2', '2_COLEGIATURAS'))
    cuota_mensual = getattr(vp, 'cuota_mensual', None) or cero

    ingresos_insc = ingresos_mat = ingresos_cole1 = ingresos_cole2 = ingresos_cuotas10 = cero
    total_cuotas_pagadas = 0

    if vp:
        gestiones = EstudianteProgramaGestion.objects.filter(
            programa_content_type=pf["programa_content_type"],
            programa_object_id=pf["programa_object_id"]
        ).only(
            'pago_inscripcion', 'pago_matricula',
            'pago_primera_colegiatura', 'pago_segunda_colegiatura',
            'cuotas_pagadas'
        )

        pagaron_insc = gestiones.filter(pago_inscripcion=True).count()
        pagaron_mat = gestiones.filter(pago_matricula=True).count()

        ingresos_insc = (vp.valorinscripcion or cero) * Decimal(pagaron_insc)
        ingresos_mat = (vp.valormatricula or cero) * Decimal(pagaron_mat)

        if plan_pago == ValorProgramaPosgrado.PLAN_2:
            pagaron_c1 = gestiones.filter(pago_primera_colegiatura=True).count()
            pagaron_c2 = gestiones.filter(pago_segunda_colegiatura=True).count()
            ingresos_cole1 = (vp.primeracolegiatura or cero) * Decimal(pagaron_c1)
            ingresos_cole2 = (vp.segundacolegiatura or cero) * Decimal(pagaron_c2)
        else:
            total_cuotas_pagadas = sum((g.cuotas_pagadas or 0) for g in gestiones)
            ingresos_cuotas10 = cuota_mensual * Decimal(total_cuotas_pagadas)

    total_ingresos = ingresos_insc + ingresos_mat + ingresos_cole1 + ingresos_cole2 + ingresos_cuotas10

    eg_coordinadores = (
        CoordinadorPagos.objects
        .filter(programa_content_type=pf["programa_content_type"], programa_object_id=pf["programa_object_id"])
        .aggregate(s=Sum('valor_total'))['s'] or cero
    )

    docentes_pagados_ids = list(
        ContratoDocenteGestion.objects
        .filter(
            contrato__programa_content_type=pf["programa_content_type"],
            contrato__programa_object_id=pf["programa_object_id"],
            pago_realizado=True
        )
        .values_list('contrato_id', flat=True)
    )
    eg_docentes = cero
    if docentes_pagados_ids:
        eg_docentes = sum(
            (c.horasacademicas or 0) * (c.valorxhora or cero)
            for c in ContratosDocentes.objects.filter(id__in=docentes_pagados_ids)
        )

    tutores_pagados_ids = list(
        ContratoTutorGestion.objects
        .filter(
            contrato__programa_content_type=pf["programa_content_type"],
            contrato__programa_object_id=pf["programa_object_id"],
            pago_realizado=True
        )
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

        'ingresos_inscripcion': ingresos_insc,
        'ingresos_matricula': ingresos_mat,
        'ingresos_colegiatura1': ingresos_cole1,
        'ingresos_colegiatura2': ingresos_cole2,

        'ingresos_cuotas10': ingresos_cuotas10,
        'total_cuotas_pagadas': total_cuotas_pagadas,

        'egresos_coordinadores': eg_coordinadores,
        'egresos_docentes': eg_docentes,
        'egresos_tutores': eg_tutores,
    }


# ---------------- PDF helpers (igual que tu original) ----------------
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
    programa = _get_programa_or_404(programa_id)
    pf = _programa_filter(programa)

    fin = _calc_programa_finanzas(programa)
    vp = ValorProgramaPosgrado.objects.filter(**pf).first()

    contratos_coord = list(ContratoCoordinador.objects.filter(**pf))
    pagos_coord = (
        CoordinadorPagos.objects
        .filter(programa_content_type=pf["programa_content_type"], programa_object_id=pf["programa_object_id"])
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

    contratos_doc = list(ContratosDocentes.objects.filter(**pf))
    mod_map = _resolve_modulos_map(contratos_doc)

    gest_doc = {
        g.contrato_id: g for g in ContratoDocenteGestion.objects.filter(contrato__in=contratos_doc)
    }

    doc_detalle = []
    for c in contratos_doc:
        docente = User.objects.filter(id=c.docente).first()
        key_mod = (c.modulo_content_type_id, c.modulo_object_id)
        modulo_obj = mod_map.get(key_mod)
        modulo_nombre = getattr(modulo_obj, 'nombre', None) if modulo_obj else (f"ID {c.modulo_object_id}" if c.modulo_object_id else "")
        valor_total = (c.horasacademicas or 0) * (c.valorxhora or Decimal('0.00'))
        g = gest_doc.get(c.id)
        doc_detalle.append({
            'contrato': c,
            'docente': docente,
            'modulo': modulo_nombre,
            'valor_total': valor_total,
            'gestion': g,
        })

    contratos_tut = list(ContratoTutor.objects.filter(**pf))
    gest_tut = {
        g.contrato_id: g for g in ContratoTutorGestion.objects.filter(contrato__in=contratos_tut)
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

    matriculas = (
        MatriculaUsuario.objects
        .filter(content_type=pf["programa_content_type"], object_id=programa.id, rol_en_programa='estudiante')
        .select_related('usuario')
        .order_by('usuario__last_name', 'usuario__first_name')
    )
    perfiles = {
        p.user_id: p for p in PerfilUsuario.objects.filter(
            user_id__in=[m.usuario_id for m in matriculas]
        )
    }
    gest_est = {
        g.usuario_id: g for g in EstudianteProgramaGestion.objects.filter(
            programa_content_type=pf["programa_content_type"],
            programa_object_id=pf["programa_object_id"]
        )
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

def _calcular_paos_desde_programa(programa):
    """
    Calcula 3 PAO a partir de:
    - fechafin del programa
    - num_semanas_programa

    Regla:
    inicio_pao_n = fin_anterior + 1 día
    fin_pao_n = inicio_pao_n + N semanas - 1 día
    """
    fechafin = getattr(programa, 'fechafin', None)
    num_semanas = getattr(programa, 'num_semanas_programa', None)

    if not fechafin or not num_semanas:
        return None

    def calc_periodo(fecha_inicio_base, semanas):
        fecha_inicio = fecha_inicio_base + timedelta(days=1)
        fecha_fin = fecha_inicio + timedelta(weeks=semanas) - timedelta(days=1)
        return {
            'inicio': fecha_inicio,
            'fin': fecha_fin,
            'semanas': semanas,
        }

    pao1 = calc_periodo(fechafin, num_semanas)
    pao2 = calc_periodo(pao1['fin'], num_semanas)
    pao3 = calc_periodo(pao2['fin'], num_semanas)

    return {
        'pao1': pao1,
        'pao2': pao2,
        'pao3': pao3,
    }

@login_required
@role_required([3, 4, 7])
@transaction.atomic
def programa_pao_configurar(request, programa_id):
    programa = _get_programa_or_404(programa_id)

    initial = {
        'fechainicio': getattr(programa, 'fechainicio', None),
        'fechafin': getattr(programa, 'fechafin', None),
        'num_semanas_programa': getattr(programa, 'num_semanas_programa', None),
    }

    if request.method == 'POST':
        form = ProgramaPAOForm(request.POST)
        if form.is_valid():
            programa.fechainicio = form.cleaned_data['fechainicio']
            programa.fechafin = form.cleaned_data['fechafin']
            programa.num_semanas_programa = form.cleaned_data['num_semanas_programa']
            programa.save(update_fields=['fechainicio', 'fechafin', 'num_semanas_programa'])

            messages.success(request, 'Datos del programa guardados correctamente para el cálculo de PAO.')
            return redirect('programa_pao_configurar', programa_id=programa.id)
        else:
            messages.error(request, 'Corrige los errores del formulario.')
    else:
        form = ProgramaPAOForm(initial=initial)

    programa_actualizado = _get_programa_or_404(programa_id)
    paos = _calcular_paos_desde_programa(programa_actualizado)

    return render(request, 'programa_pao_form.html', {
        'programa': programa_actualizado,
        'programa_id': programa_id,
        'form': form,
        'paos': paos,
    })