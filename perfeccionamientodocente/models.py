from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

# =========================
# 2) Areas de conocimiento 
# =========================

class AreaConocimiento(models.Model):
    codigo = models.CharField(max_length=5, unique=True)
    nombre = models.CharField(max_length=200)

    class Meta:
        verbose_name = "Área de conocimiento"
        verbose_name_plural = "Áreas de conocimiento"
        ordering = ["codigo"]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class SubareaConocimiento(models.Model):
    area = models.ForeignKey(AreaConocimiento, on_delete=models.PROTECT, related_name="subareas")
    codigo = models.CharField(max_length=5)
    nombre = models.CharField(max_length=200)

    class Meta:
        verbose_name = "Subárea de conocimiento"
        verbose_name_plural = "Subáreas de conocimiento"
        ordering = ["area__codigo", "codigo"]
        constraints = [
            models.UniqueConstraint(fields=["area", "codigo"], name="uq_subarea_area_codigo")
        ]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class CampoConocimiento(models.Model):
    subarea = models.ForeignKey(SubareaConocimiento, on_delete=models.PROTECT, related_name="campos")
    codigo = models.CharField(max_length=10)
    nombre = models.CharField(max_length=250)

    class Meta:
        verbose_name = "Campo de conocimiento"
        verbose_name_plural = "Campos de conocimiento"
        ordering = ["subarea__area__codigo", "subarea__codigo", "codigo"]
        constraints = [
            models.UniqueConstraint(fields=["subarea", "codigo"], name="uq_campo_subarea_codigo")
        ]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"



# =========================
# 2) Curso de capacitación 
# =========================

class CursoCapacitacion(models.Model):

    FINANCIAMIENTO_CHOICES = [
        ("presupuesto", "Presupuesto"),
        ("autogestion", "Autogestión"),
    ]

    MODALIDAD_CHOICES = [
        ("virtual", "Virtual"),
        ("presencial", "Presencial"),
        ("hibrida", "Híbrida"),
    ]

    # Datos del curso (matriz)
    nombre = models.CharField(max_length=255)

    area = models.ForeignKey(AreaConocimiento, on_delete=models.PROTECT, related_name="cursos")
    subarea = models.ForeignKey(SubareaConocimiento, on_delete=models.PROTECT, related_name="cursos")
    campo = models.ForeignKey(CampoConocimiento, on_delete=models.PROTECT, related_name="cursos")

    dirigido_a = models.CharField(default="Posgrado", max_length=255, blank=True, null=True)
    carrera = models.CharField(max_length=255, blank=True, null=True)

    fecha_inicio = models.DateField(blank=True, null=True)
    fecha_fin = models.DateField(blank=True, null=True)
    horario = models.CharField(max_length=200, blank=True, null=True)

    horas_totales = models.PositiveIntegerField(default=40)
    num_docentes_dirigido = models.PositiveIntegerField(blank=True, null=True)

    # Facilitador (puede ser interno/externo)
    facilitador = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True,
        limit_choices_to={'perfilusuario__rol': 2},
        related_name="cursos_facilitados"
    )
    facilitador_nombres = models.CharField(max_length=255, blank=True, null=True)
    facilitador_cedula = models.CharField(max_length=20, blank=True, null=True)

    interno_externo = models.CharField(
        max_length=10,
        choices=[("interno", "Interno"), ("externo", "Externo")],
        default="interno"
    )

    financiamiento = models.CharField(max_length=20, choices=FINANCIAMIENTO_CHOICES, default="presupuesto")
    presupuesto_monto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    modalidad = models.CharField(max_length=10, choices=MODALIDAD_CHOICES, default="virtual")
    lugar = models.CharField(max_length=255, blank=True, null=True)  # "VIRTUAL" o ubicación

    # Control
    activo = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Curso de capacitación"
        verbose_name_plural = "Cursos de capacitación"
        ordering = ["-created"]

    def __str__(self):
        return self.nombre


# =========================
# 3) Relación Curso ↔ Docente ↔ Programa (GenericForeignKey)
# =========================

class CursoParticipacion(models.Model):

    ESTADO_CHOICES = [
        ("inscrito", "Inscrito"),
        ("enviado", "Enviado"),
        ("aprobado", "Aprobado"),
        ("rechazado", "Rechazado"),
        ("finalizado", "Finalizado"),
    ]
    ESTADO_RESULTADO_CHOICES = [
        ("aprobado", "Aprobado"),
        ("reprobado", "Reprobado"),
    ]

    ROL_CHOICES = [
        ("participante", "Participante"),
        ("facilitador", "Facilitador"),
        ("ambos", "Ambos"),
    ]

    curso = models.ForeignKey(CursoCapacitacion, on_delete=models.CASCADE, related_name="participaciones")

    docente = models.ForeignKey(
        User, on_delete=models.CASCADE,
        limit_choices_to={'perfilusuario__rol': 2},
        related_name="capacitaciones"
    )

    # Programa asociado (Maestría o Especialidad)
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    programa = GenericForeignKey('content_type', 'object_id')

    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default="participante")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="inscrito")

    # Evidencias/certificación (para después)
    certificado = models.FileField(upload_to="certificados_perfeccionamiento/", blank=True, null=True)
    observacion = models.TextField(blank=True, null=True)

    fecha_registro = models.DateTimeField(auto_now_add=True)

    porcentaje_asistencia = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    nota_final = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    estado_resultado = models.CharField(
        max_length=10,
        choices=ESTADO_RESULTADO_CHOICES,
        blank=True,
        null=True
    )


    class Meta:
        verbose_name = "Participación en curso"
        verbose_name_plural = "Participaciones en cursos"
        constraints = [
            models.UniqueConstraint(
                fields=["curso", "docente", "content_type", "object_id"],
                name="uq_participacion_curso_docente_programa"
            )
        ]
        ordering = ["-fecha_registro"]

    def __str__(self):
        return f"{self.docente.get_full_name()} - {self.curso.nombre}"
