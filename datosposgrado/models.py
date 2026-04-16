from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models import Q
from django.conf import settings


# -----------------------------
# Helpers: limit_choices_to
# -----------------------------
LIMIT_PROGRAMA_CT = Q(app_label='programasposgrado', model='programaposgrado') | Q(app_label='programasposgrado', model='programaposgradoem')
LIMIT_MODULO_CT   = Q(app_label='programasposgrado', model='modulos') | Q(app_label='programasposgrado', model='modulosem')


class ContratosDocentes(models.Model):
    DOCENTE_TIPO = (
        (1, 'Docente'),
        (2, 'Docente de práctica asistencial'),
    )

    # Persona (mantengo como ID entero para impacto mínimo entre apps)
    docente = models.IntegerField(db_index=True)
    docente_tipo = models.IntegerField(choices=DOCENTE_TIPO, default=1)

    # Programa (Maestría o Especialidad Médica)
    programa_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        limit_choices_to=LIMIT_PROGRAMA_CT,
        related_name='ct_contratos_docentes_programa',
        null=True, blank=True
    )
    programa_object_id = models.PositiveIntegerField(db_index=True, null=True, blank=True)
    programa = GenericForeignKey('programa_content_type', 'programa_object_id')

    # Módulo (puede ser Modulos o ModulosEM)
    modulo_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        limit_choices_to=LIMIT_MODULO_CT,
        related_name='ct_contratos_docentes_modulo',
        null=True, blank=True
    )
    modulo_object_id = models.PositiveIntegerField(db_index=True, null=True, blank=True)
    modulo_obj = GenericForeignKey('modulo_content_type', 'modulo_object_id')

    # Datos del contrato
    horasacademicas = models.IntegerField()
    valorxhora = models.DecimalField(max_digits=10, decimal_places=2)

    certificacionpresupuestaria = models.CharField(max_length=100)
    fechacertificacionpresupuestaria = models.DateField()

    plazo = models.CharField(max_length=100)
    numerocontrato = models.CharField(max_length=100)
    numeromemorandotthh = models.CharField(max_length=100)

    tipopersonalacademico = models.IntegerField(
        choices=[(1, 'Servicios profesionales')],
        default=1
    )

    adenda = models.CharField(max_length=100, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    urldocumento = models.URLField(max_length=500, blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contratos_docentes_creados',
        editable=False
    )

    class Meta:
        ordering = ['-created']
        verbose_name = 'Contrato Docente'
        verbose_name_plural = 'Contratos Docentes'
        indexes = [
            models.Index(fields=['programa_content_type', 'programa_object_id']),
            models.Index(fields=['modulo_content_type', 'modulo_object_id']),
            models.Index(fields=['docente', 'created']),
        ]

    @property
    def programa_tipo(self):
        # útil para compatibilidad: "M" o "EM"
        m = (self.programa_content_type.model or '').lower()
        return 'EM' if m == 'programaposgradoem' else 'M'

    def __str__(self):
        return f"Contrato Docente #{self.id} - DocenteID {self.docente} - {self.programa_tipo}"


class ContratoTutor(models.Model):
    # Persona (IDs enteros)
    tutor = models.IntegerField(db_index=True)
    maestrante = models.IntegerField(db_index=True)

    # Programa (Maestría o Especialidad)
    programa_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        limit_choices_to=LIMIT_PROGRAMA_CT,
        related_name='ct_contratos_tutor_programa',
        null=True, blank=True
    )
    programa_object_id = models.PositiveIntegerField(db_index=True, null=True, blank=True)
    programa = GenericForeignKey('programa_content_type', 'programa_object_id')

    # (En tutorías no siempre tienes módulo; si sí lo necesitas, puedes agregar GFK de módulo aquí también)
    # Por ahora lo dejo SIN módulo para mantenerlo como tu modelo actual.

    plazo = models.CharField(max_length=100)
    certificacionpresupuestaria = models.CharField(max_length=100)
    fechacertificacionpresupuestaria = models.DateField()
    valorcontrato = models.DecimalField(max_digits=10, decimal_places=2)
    numerocontrato = models.CharField(max_length=100)
    numeromemorandotthh = models.CharField(max_length=100)

    tipopersonalacademico = models.IntegerField(
        choices=[(1, 'Servicios profesionales')],
        default=1
    )

    adenda = models.CharField(max_length=100, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    urldocumento = models.URLField(max_length=500, blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contratos_tutor_creados',
        editable=False
    )

    class Meta:
        ordering = ['-created']
        verbose_name = 'Contrato de Tutor'
        verbose_name_plural = 'Contratos de Tutor'
        indexes = [
            models.Index(fields=['programa_content_type', 'programa_object_id']),
            models.Index(fields=['tutor', 'created']),
            models.Index(fields=['maestrante', 'created']),
        ]

    @property
    def programa_tipo(self):
        m = (self.programa_content_type.model or '').lower()
        return 'EM' if m == 'programaposgradoem' else 'M'

    def __str__(self):
        return f"Contrato Tutor #{self.id} - TutorID {self.tutor} - {self.programa_tipo}"


class ContratoCoordinador(models.Model):
    coordinador = models.IntegerField(db_index=True)

    # Programa (Maestría o Especialidad)
    programa_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        limit_choices_to=LIMIT_PROGRAMA_CT,
        related_name='ct_contratos_coord_programa',
        null=True, blank=True
    )
    programa_object_id = models.PositiveIntegerField(db_index=True, null=True, blank=True)
    programa = GenericForeignKey('programa_content_type', 'programa_object_id')

    certificacionpresupuestaria = models.CharField(max_length=100)
    fechacertificacionpresupuestaria = models.DateField()
    plazo = models.CharField(max_length=100, null=True, blank=True)

    fechainicio = models.DateField(null=True, blank=True)
    fechafin = models.DateField(null=True, blank=True)

    honorario = models.DecimalField(max_digits=10, decimal_places=2)
    numerocontrato = models.CharField(max_length=100)
    cargo = models.CharField(max_length=100)
    noactasseleccion = models.CharField(max_length=100)
    oficioentregadoporth = models.CharField(max_length=100)
    modalidadcontractuar = models.CharField(max_length=100)

    observaciones = models.TextField(blank=True, null=True)
    urldocumento = models.URLField(max_length=500, blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contratos_coordinador_creados',
        editable=False
    )

    class Meta:
        ordering = ['-created']
        verbose_name = 'Contrato de Coordinador'
        verbose_name_plural = 'Contratos de Coordinador'
        indexes = [
            models.Index(fields=['programa_content_type', 'programa_object_id']),
            models.Index(fields=['coordinador', 'created']),
        ]

    @property
    def programa_tipo(self):
        m = (self.programa_content_type.model or '').lower()
        return 'EM' if m == 'programaposgradoem' else 'M'

    def __str__(self):
        return f"Contrato Coordinador #{self.id} - CoordID {self.coordinador} - {self.programa_tipo}"