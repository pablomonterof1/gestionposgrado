from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from .models import AreaConocimiento, SubareaConocimiento, CampoConocimiento, CursoCapacitacion, CursoParticipacion
from .forms import AreaConocimientoForm, SubareaConocimientoForm, CampoConocimientoForm, CursoCapacitacionForm, CursoResultadoForm, MatricularParticipantesCursoForm
from django.db.models.deletion import ProtectedError
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from main.decorators import role_required
from django.db.models import Q
from usuarios.models import MatriculaDocenteModulo
from programasposgrado.models import ProgramaPosgrado, ProgramaPosgradoEM
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.conf import settings
from django.contrib.staticfiles import finders
from django.template.loader import get_template
from xhtml2pdf import pisa
import os
from datetime import datetime
from collections import defaultdict


@login_required
def perfeccionamientodocente(request):
    return render(request, "perfeccionamientodocente.html")

# =========================
# ÁREAS
# =========================

@login_required
def areas_list(request):
    areas = AreaConocimiento.objects.all().order_by("codigo")
    return render(request, "areasconocimiento.html", {"areas": areas})


@login_required
def area_create(request):
    if request.method == "POST":
        form = AreaConocimientoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Área creada correctamente.")
            return redirect("pd_areasconocimiento_list")
    else:
        form = AreaConocimientoForm()

    return render(request, "areasconocimientoform.html", {
        "form": form,
        "titulo": "Crear área de conocimiento",
        "btn": "Guardar",
    })


@login_required
def area_update(request, area_id):
    area = get_object_or_404(AreaConocimiento, pk=area_id)

    if request.method == "POST":
        form = AreaConocimientoForm(request.POST, instance=area)
        if form.is_valid():
            form.save()
            messages.success(request, "Área actualizada correctamente.")
            return redirect("pd_areasconocimiento_list")
    else:
        form = AreaConocimientoForm(instance=area)

    return render(request, "areasconocimientoform.html", {
        "form": form,
        "titulo": "Editar área de conocimiento",
        "btn": "Actualizar",
    })

@login_required
def area_delete(request, area_id):
    area = get_object_or_404(AreaConocimiento, pk=area_id)

    if request.method == "POST":
        try:
            area.delete()
            messages.success(request, "Área eliminada correctamente.")
        except ProtectedError:
            messages.error(request, "No se puede eliminar el área porque tiene subáreas asociadas.")
        return redirect("pd_areasconocimiento_list")
        

    return render(request, "pdconfirm_delete.html", {
        "titulo": "Eliminar área de conocimiento",
        "obj": area,
        "volver_url": "pd_areasconocimiento_list",
        "volver_href": reverse("pd_areasconocimiento_list"),
    })

# =========================
# SUBÁREAS
# =========================

@login_required
def subareas_list(request):
    area_id = request.GET.get("area")
    subareas = SubareaConocimiento.objects.select_related("area").all().order_by("area__codigo", "codigo")

    if area_id:
        subareas = subareas.filter(area_id=area_id)

    areas = AreaConocimiento.objects.all().order_by("codigo")

    return render(request, "subareasconocimiento.html", {
        "subareas": subareas,
        "areas": areas,
        "area_id": area_id,
    })


@login_required
def subarea_create(request):
    if request.method == "POST":
        form = SubareaConocimientoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Subárea creada correctamente.")
            return redirect("pd_subareasconocimiento_list")
    else:
        form = SubareaConocimientoForm()

    return render(request, "subareasconocimientoform.html", {
        "form": form,
        "titulo": "Crear subárea de conocimiento",
        "btn": "Guardar",
    })


@login_required
def subarea_update(request, subarea_id):
    subarea = get_object_or_404(SubareaConocimiento, pk=subarea_id)

    if request.method == "POST":
        form = SubareaConocimientoForm(request.POST, instance=subarea)
        if form.is_valid():
            form.save()
            messages.success(request, "Subárea actualizada correctamente.")
            return redirect("pd_subareasconocimiento_list")
    else:
        form = SubareaConocimientoForm(instance=subarea)

    return render(request, "subareasconocimientoform.html", {
        "form": form,
        "titulo": "Editar subárea de conocimiento",
        "btn": "Actualizar",
    })

@login_required
def subarea_delete(request, subarea_id):
    subarea = get_object_or_404(SubareaConocimiento, pk=subarea_id)

    if request.method == "POST":
        try:
            subarea.delete()
            messages.success(request, "Subárea eliminada correctamente.")
        except ProtectedError:
            messages.error(request, "No se puede eliminar la subárea porque tiene campos asociados.")
        return redirect("pd_subareasconocimiento_list")

    return render(request, "pdconfirm_delete.html", {
        "titulo": "Eliminar subárea de conocimiento",
        "obj": subarea,
        "volver_url": "pd_subareasconocimiento_list",
        "volver_href": reverse("pd_subareasconocimiento_list"),
    })



# =========================
# CAMPOS
# =========================

@login_required
def campos_list(request):
    subarea_id = request.GET.get("subarea")

    campos = CampoConocimiento.objects.select_related("subarea", "subarea__area") \
        .all().order_by("subarea__area__codigo", "subarea__codigo", "codigo")

    if subarea_id:
        campos = campos.filter(subarea_id=subarea_id)

    subareas = SubareaConocimiento.objects.select_related("area").all().order_by("area__codigo", "codigo")

    return render(request, "camposconocimiento.html", {
        "campos": campos,
        "subareas": subareas,
        "subarea_id": subarea_id,
    })


@login_required
def campo_create(request):
    if request.method == "POST":
        form = CampoConocimientoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Campo creado correctamente.")
            return redirect("pd_camposconocimiento_list")
    else:
        form = CampoConocimientoForm()

    return render(request, "camposconocimientoform.html", {
        "form": form,
        "titulo": "Crear campo de conocimiento",
        "btn": "Guardar",
    })


@login_required
def campo_update(request, campo_id):
    campo = get_object_or_404(CampoConocimiento, pk=campo_id)

    if request.method == "POST":
        form = CampoConocimientoForm(request.POST, instance=campo)
        if form.is_valid():
            form.save()
            messages.success(request, "Campo actualizado correctamente.")
            return redirect("pd_camposconocimiento_list")
    else:
        form = CampoConocimientoForm(instance=campo)

    return render(request, "camposconocimientoform.html", {
        "form": form,
        "titulo": "Editar campo de conocimiento",
        "btn": "Actualizar",
    })

@login_required
def campo_delete(request, campo_id):
    campo = get_object_or_404(CampoConocimiento, pk=campo_id)

    if request.method == "POST":
        try:
            campo.delete()
            messages.success(request, "Campo eliminado correctamente.")
        except ProtectedError:
            messages.error(request, "No se puede eliminar el campo porque está siendo usado en registros asociados.")
        return redirect("pd_camposconocimiento_list")

    return render(request, "pdconfirm_delete.html", {
        "titulo": "Eliminar campo de conocimiento",
        "obj": campo,
        "volver_url": "pd_camposconocimiento_list",
        "volver_href": reverse("pd_camposconocimiento_list"),
    })

# =========================
# CURSOS
# =========================

@login_required
def cursos_list(request):
    q = request.GET.get("q", "").strip()
    area_id = request.GET.get("area", "").strip()
    subarea_id = request.GET.get("subarea", "").strip()
    campo_id = request.GET.get("campo", "").strip()

    cursos = CursoCapacitacion.objects.select_related("area", "subarea", "campo").all().order_by("-created")

    if q:
        cursos = cursos.filter(nombre__icontains=q)

    if area_id:
        cursos = cursos.filter(area_id=area_id)

    if subarea_id:
        cursos = cursos.filter(subarea_id=subarea_id)

    if campo_id:
        cursos = cursos.filter(campo_id=campo_id)

    areas = AreaConocimiento.objects.all().order_by("codigo")
    subareas = SubareaConocimiento.objects.select_related("area").all().order_by("area__codigo", "codigo")
    campos = CampoConocimiento.objects.select_related("subarea", "subarea__area").all() \
        .order_by("subarea__area__codigo", "subarea__codigo", "codigo")

    return render(request, "pdcursos.html", {
        "cursos": cursos,
        "q": q,
        "areas": areas,
        "subareas": subareas,
        "campos": campos,
        "area_id": area_id,
        "subarea_id": subarea_id,
        "campo_id": campo_id,
    })



@login_required
def curso_create(request):
    if request.method == "POST":
        form = CursoCapacitacionForm(request.POST)
        if form.is_valid():
            curso = form.save(commit=False)

            if curso.interno_externo == "interno" and curso.facilitador:
                curso.facilitador_nombres = curso.facilitador.get_full_name()

                if hasattr(curso.facilitador, "perfilusuario") and curso.facilitador.perfilusuario.ci:
                    curso.facilitador_cedula = curso.facilitador.perfilusuario.ci
                else:
                    curso.facilitador_cedula = curso.facilitador.username

            curso.save()
            messages.success(request, "Curso creado correctamente.")
            return redirect("pd_cursos_list")
    else:
        form = CursoCapacitacionForm()

    return render(request, "pdcursosform.html", {
        "form": form,
        "titulo": "Crear curso de capacitación",
        "btn": "Guardar",
    })



@login_required
def curso_update(request, curso_id):
    curso = get_object_or_404(CursoCapacitacion, pk=curso_id)

    if request.method == "POST":
        form = CursoCapacitacionForm(request.POST, instance=curso)
        if form.is_valid():
            curso_obj = form.save(commit=False)

            if curso_obj.interno_externo == "interno" and curso_obj.facilitador:
                curso_obj.facilitador_nombres = curso_obj.facilitador.get_full_name()

                if hasattr(curso_obj.facilitador, "perfilusuario") and curso_obj.facilitador.perfilusuario.ci:
                    curso_obj.facilitador_cedula = curso_obj.facilitador.perfilusuario.ci
                else:
                    curso_obj.facilitador_cedula = curso_obj.facilitador.username

            elif curso_obj.interno_externo == "externo":
                curso_obj.facilitador = None  

                if curso_obj.facilitador_nombres:
                    curso_obj.facilitador_nombres = curso_obj.facilitador_nombres.strip()
                if curso_obj.facilitador_cedula:
                    curso_obj.facilitador_cedula = curso_obj.facilitador_cedula.strip()

            curso_obj.save()
            messages.success(request, "Curso actualizado correctamente.")
            return redirect("pd_cursos_list")
    else:
        form = CursoCapacitacionForm(instance=curso)

    return render(request, "pdcursosform.html", {
        "form": form,
        "titulo": "Editar curso de capacitación",
        "btn": "Actualizar",
    })



@login_required
def curso_delete(request, curso_id):
    curso = get_object_or_404(CursoCapacitacion, pk=curso_id)

    if request.method == "POST":
        curso.delete()
        messages.success(request, "Curso eliminado correctamente.")
        return redirect("pd_cursos_list")

    return render(request, "pdconfirm_delete.html", {
        "titulo": "Eliminar curso de capacitación",
        "obj": curso,
        "volver_url": "pd_cursos_list",
        "volver_href": reverse("pd_cursos_list"),
    })

@require_GET
def ajax_subareas_por_area(request):
    area_id = request.GET.get("area_id")
    if not area_id:
        return JsonResponse({"results": []})
    subareas = SubareaConocimiento.objects.filter(area_id=area_id).order_by("codigo")
    data = [{"id": s.id, "text": f"{s.codigo} - {s.nombre}"} for s in subareas]
    return JsonResponse({"results": data})


@require_GET
def ajax_campos_por_subarea(request):
    subarea_id = request.GET.get("subarea_id")
    if not subarea_id:
        return JsonResponse({"results": []})
    campos = CampoConocimiento.objects.filter(subarea_id=subarea_id).order_by("codigo")
    data = [{"id": c.id, "text": f"{c.codigo} - {c.nombre}"} for c in campos]
    return JsonResponse({"results": data})

# =========================
# Participación y resultados
# =========================


def _inferir_programa_obj(docente: User):
    """
    Retorna el objeto programa (ProgramaPosgrado o ProgramaPosgradoEM) o None.
    Se basa en MatriculaDocenteModulo.programa (ID del programa) y toma la matrícula más reciente.
    """
    m = MatriculaDocenteModulo.objects.filter(docente=docente).order_by("-fecha_matricula").first()
    if not m or not m.programa:
        return None

    pid = int(m.programa)

    prog = ProgramaPosgrado.objects.filter(id=pid).first()
    if prog:
        return prog

    prog_em = ProgramaPosgradoEM.objects.filter(id=pid).first()
    if prog_em:
        return prog_em

    return None


# ==========================================================
# A) LISTADO MAESTRO: cursos + facilitador
# ==========================================================
@role_required([3, 7])
def participantes_cursos_list(request):
    cursos = CursoCapacitacion.objects.select_related("facilitador").all().order_by("-created")
    cursoparticipacion = CursoParticipacion.objects.all()
    for cp in cursoparticipacion:
        if cp.curso_id in cursos.values_list('id', flat=True):
            curso = next((c for c in cursos if c.id == cp.curso_id), None)
            if curso:
                if not hasattr(curso, 'num_participantes'):
                    curso.num_participantes = 0
                curso.num_participantes += 1
    return render(request, "pdparticipantescursos.html", {
        "cursos": cursos

    })


# ==========================================================
# B) DETALLE: participantes de un curso + registrar resultados
# ==========================================================
@role_required([3, 7])
def participantes_curso_detalle(request, curso_id):
    curso = get_object_or_404(CursoCapacitacion, pk=curso_id)

    participaciones = CursoParticipacion.objects.select_related("docente", "content_type") \
        .filter(curso=curso).order_by("docente__last_name", "docente__first_name")

    return render(request, "pdparticipantescurso_detalle.html", {
        "curso": curso,
        "participaciones": participaciones,
    })


# ==========================================================
# C) MATRICULAR participantes (desde el detalle del curso)
# ==========================================================


# @role_required([3, 7])
# def participantes_curso_matricular(request, curso_id):
#     curso = get_object_or_404(CursoCapacitacion, pk=curso_id)

#     # Docentes ya matriculados en este curso (para excluir del listado)
#     ya_ids = set(
#         CursoParticipacion.objects.filter(curso=curso).values_list("docente_id", flat=True)
#     )

#     # Candidatos: docentes (rol=2) que NO están matriculados en el curso
#     usuarios = User.objects.filter(perfilusuario__rol=2).exclude(id__in=ya_ids).order_by(
#         "last_name", "first_name"
#     )

#     # Armar lista con programa inferido (para mostrar en la tabla)
#     usuarios_info = []
#     for u in usuarios:
#         programa_obj = _inferir_programa_obj(u)
#         usuarios_info.append({
#             "user": u,
#             "programa": str(programa_obj) if programa_obj else "SIN PROGRAMA",
#             "programa_obj": programa_obj,  # lo usamos para matricular
#         })

#     if request.method == "POST":
#         usuario_id = request.POST.get("usuario")

#         docente = get_object_or_404(User, pk=usuario_id)

#         # Bloquear matricular al facilitador como participante
#         if curso.facilitador_id and docente.id == curso.facilitador_id:
#             messages.error(request, "El facilitador del curso no debe registrarse como participante.")
#             return redirect("pd_participantes_curso_matricular", curso_id=curso.id)

#         # Inferir programa
#         programa_obj = _inferir_programa_obj(docente)

#         # Si tu modelo permite null, esto puede ser None
#         ct = None
#         obj_id = None

#         if programa_obj:
#             # Determinar content_type según el tipo
#             if isinstance(programa_obj, ProgramaPosgrado):
#                 ct = ContentType.objects.get_for_model(ProgramaPosgrado)
#                 obj_id = programa_obj.id
#             else:
#                 ct = ContentType.objects.get_for_model(ProgramaPosgradoEM)
#                 obj_id = programa_obj.id

#         # Crear matrícula (si ya existe, no duplicar)
#         obj, created = CursoParticipacion.objects.get_or_create(
#             curso=curso,
#             docente=docente,
#             content_type=ct,
#             object_id=obj_id,
#             defaults={"rol": "participante", "estado": "inscrito"},
#         )

#         if created:
#             messages.success(request, f"Docente matriculado: {docente.get_full_name()}")
#         else:
#             messages.info(request, "Este docente ya está matriculado en el curso (o ya existía un registro).")

#         return redirect("pd_participantes_curso_matricular", curso_id=curso.id)

#     return render(request, "pdparticipantesmatricular.html", {
#         "curso": curso,
#         "usuarios_info": usuarios_info,
#     })




@role_required([3, 7])
def participantes_curso_matricular(request, curso_id):
    curso = get_object_or_404(CursoCapacitacion, pk=curso_id)

    # 1) IDs ya matriculados
    ya_ids = set(
        CursoParticipacion.objects.filter(curso=curso).values_list("docente_id", flat=True)
    )

    # 2) Docentes candidatos (trae perfilusuario en el mismo query)
    usuarios = list(
        User.objects.select_related("perfilusuario")
        .filter(perfilusuario__rol=2)
        .exclude(id__in=ya_ids)
        .order_by("last_name", "first_name")
    )
    docente_ids = [u.id for u in usuarios]

    # 3) Traer TODAS las matrículas de módulos para esos docentes, ordenadas (más reciente primero)
    # Luego elegimos en memoria la primera por docente (la más reciente)
    matriculas = (
        MatriculaDocenteModulo.objects
        .filter(docente_id__in=docente_ids)
        .order_by("docente_id", "-fecha_matricula")
        .values("docente_id", "programa")
    )

    # mapa docente_id -> programa_id (más reciente)
    docente_programa = {}
    for m in matriculas:
        did = m["docente_id"]
        if did not in docente_programa:  # primera vez = más reciente por el order_by
            docente_programa[did] = m["programa"]

    # 4) Cargar programas en 2 queries (PP y PEM)
    programa_ids = {int(pid) for pid in docente_programa.values() if pid}
    pp_map = {p.id: p for p in ProgramaPosgrado.objects.filter(id__in=programa_ids)}
    pem_map = {p.id: p for p in ProgramaPosgradoEM.objects.filter(id__in=programa_ids)}

    # 5) Construir usuarios_info sin más queries
    usuarios_info = []
    for u in usuarios:
        pid = docente_programa.get(u.id)
        programa_obj = pp_map.get(pid) or pem_map.get(pid)
        usuarios_info.append({
            "user": u,
            "programa": str(programa_obj) if programa_obj else "SIN PROGRAMA",
            "programa_obj": programa_obj,  # opcional si luego lo usas
        })

    # ========= POST: matricular uno =========
    if request.method == "POST":
        usuario_id = request.POST.get("usuario")
        docente = get_object_or_404(User, pk=usuario_id)

        if curso.facilitador_id and docente.id == curso.facilitador_id:
            messages.error(request, "El facilitador del curso no debe registrarse como participante.")
            return redirect("pd_participantes_curso_matricular", curso_id=curso.id)

        # Inferir programa rápido usando el mapa, con fallback
        pid = docente_programa.get(docente.id)
        programa_obj = pp_map.get(pid) or pem_map.get(pid)

        ct = None
        obj_id = None
        if programa_obj:
            if isinstance(programa_obj, ProgramaPosgrado):
                ct = ContentType.objects.get_for_model(ProgramaPosgrado)
            else:
                ct = ContentType.objects.get_for_model(ProgramaPosgradoEM)
            obj_id = programa_obj.id

        obj, created = CursoParticipacion.objects.get_or_create(
            curso=curso,
            docente=docente,
            content_type=ct,
            object_id=obj_id,
            defaults={"rol": "participante", "estado": "inscrito"},
        )

        if created:
            messages.success(request, f"Docente matriculado: {docente.get_full_name()}")
        else:
            messages.info(request, "Este docente ya está matriculado en el curso (o ya existía un registro).")

        return redirect("pd_participantes_curso_matricular", curso_id=curso.id)

    return render(request, "pdparticipantesmatricular.html", {
        "curso": curso,
        "usuarios_info": usuarios_info,
    })
# ==========================================================
# D) EDITAR resultados (por participante, vuelve al detalle)
# ==========================================================
@role_required([3, 7])
def participantes_resultados_update(request, participacion_id):
    p = get_object_or_404(CursoParticipacion, pk=participacion_id)
    curso_id = p.curso_id

    if request.method == "POST":
        form = CursoResultadoForm(request.POST, instance=p)
        if form.is_valid():
            form.save()
            messages.success(request, "Resultados actualizados.")
            return redirect("pd_participantes_curso_detalle", curso_id=curso_id)
    else:
        form = CursoResultadoForm(instance=p)

    return render(request, "pdparticipantesresultados_form.html", {
        "participacion": p,
        "form": form,
        "titulo": "Registrar resultados",
        "btn": "Guardar",
    })


# ==========================================================
# E) ELIMINAR matrícula (vuelve al detalle)
# ==========================================================
@role_required([3, 7])
def participantes_matricula_delete(request, participacion_id):
    p = get_object_or_404(CursoParticipacion, pk=participacion_id)
    curso_id = p.curso_id

    if request.method == "POST":
        p.delete()
        messages.success(request, "Matrícula eliminada.")
        return redirect("pd_participantes_curso_detalle", curso_id=curso_id)

    volver_href  = reverse("pd_participantes_curso_detalle", kwargs={"curso_id": curso_id})

    return render(request, "pdconfirm_delete.html", {
        "titulo": "Eliminar matrícula",
        "obj": p,
        "volver_href ": volver_href ,
    })

# =========================
# Helper xhtml2pdf: rutas static/media
# =========================
def link_callback(uri, rel):
    # STATIC
    static_path = finders.find(uri)
    if static_path:
        if isinstance(static_path, (list, tuple)):
            static_path = static_path[0]
        return static_path

    # MEDIA
    if uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
        return path

    return uri


def render_to_pdf(template_path, context):
    template = get_template(template_path)
    html = template.render(context)
    response = HttpResponse(content_type="application/pdf")
    pisa_status = pisa.CreatePDF(
        html,
        dest=response,
        link_callback=link_callback
    )
    if pisa_status.err:
        return None
    return response


# =========================
# A) Reportes: lista de cursos
# =========================
@role_required([3, 7])
def reportes_cursos_list(request):
    cursos = CursoCapacitacion.objects.all().order_by("-created")
    return render(request, "pdreportescursos_list.html", {
        "cursos": cursos
    })


# =========================
# B) PDF: reporte por curso
# =========================
@role_required([3, 7])
def reporte_curso_pdf(request, curso_id):
    curso = get_object_or_404(CursoCapacitacion, pk=curso_id)

    participaciones = CursoParticipacion.objects.select_related(
        "docente", "content_type"
    ).filter(curso=curso).order_by("docente__last_name", "docente__first_name")

    # Nombre del facilitador (interno o externo)
    if curso.interno_externo == "interno" and curso.facilitador:
        facilitador_nombre = curso.facilitador.get_full_name()
    else:
        facilitador_nombre = curso.facilitador_nombres or ""

    # Agrupar resultados por programa (posgrado)
    grupos = defaultdict(list)
    for p in participaciones:
        programa_label = str(p.programa) if p.programa else "SIN PROGRAMA"
        grupos[programa_label].append(p)

    # No asistieron: asistencia = None o 0
    no_asistieron = [
        p for p in participaciones
        if (p.porcentaje_asistencia is None) or (float(p.porcentaje_asistencia) == 0.0)
    ]

    # Resúmenes por sexo
    def sexo_usuario(u):
        if hasattr(u, "perfilusuario") and u.perfilusuario.sexo:
            return u.perfilusuario.sexo
        return None

    aprobados_h = aprobados_m = 0
    reprobados_h = reprobados_m = 0

    for p in participaciones:
        s = sexo_usuario(p.docente)
        if p.estado_resultado == "aprobado":
            if s == "M":
                aprobados_h += 1
            elif s == "F":
                aprobados_m += 1
        elif p.estado_resultado == "reprobado":
            if s == "M":
                reprobados_h += 1
            elif s == "F":
                reprobados_m += 1

    context = {
        "curso": curso,
        "facilitador_nombre": facilitador_nombre,
        "fecha_generacion": datetime.now(),
        "grupos": dict(grupos),
        "no_asistieron": no_asistieron,
        "resumen_aprobados": {
            "hombres": aprobados_h,
            "mujeres": aprobados_m,
            "total": aprobados_h + aprobados_m,
        },
        "resumen_reprobados": {
            "hombres": reprobados_h,
            "mujeres": reprobados_m,
            "total": reprobados_h + reprobados_m,
        },
        # Logo (ajusta la ruta a tu static real)
        "logo_posgrado": "img/logo_posgrado.png",
    }

    pdf = render_to_pdf("pdreporte_curso_pdf.html", context)
    if not pdf:
        messages.error(request, "Error al generar el PDF.")
        return HttpResponse("Error al generar PDF", status=500)

    filename = f"reporte_curso_{curso.id}.pdf"
    pdf["Content-Disposition"] = f'attachment; filename="{filename}"'
    return pdf