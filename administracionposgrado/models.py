from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models import Q

from programasposgrado.models import ProgramaPosgrado, ModalidadDeTitulacion

from programasposgrado.models import ProgramaPosgradoEM

from usuarios.models import User
from datosposgrado.models import ContratoCoordinador, ContratosDocentes, ContratoTutor


# -----------------------------
# Helpers: limit_choices_to (igual concepto que datosposgrado)
# -----------------------------
LIMIT_PROGRAMA_CT = (
    Q(app_label='programasposgrado', model='programaposgrado') |
    Q(app_label='programasposgrado', model='programaposgradoem')
)


class ValorProgramaPosgrado(models.Model):
    PLAN_10 = '10_CUOTAS'
    PLAN_2 = '2_COLEGIATURAS'
    PLAN_PAGO_CHOICES = [
        (PLAN_10, '10 cuotas'),
        (PLAN_2, '2 colegiaturas'),
    ]

    # ✅ GFK: Programa (Maestría o Especialidad Médica)
    programa_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        limit_choices_to=LIMIT_PROGRAMA_CT,
        related_name='ct_valor_programa',
        null=True, blank=True
    )
    programa_object_id = models.PositiveIntegerField(db_index=True, null=True, blank=True)
    programa = GenericForeignKey('programa_content_type', 'programa_object_id')

    # Montos base
    valorinscripcion = models.DecimalField(max_digits=10, decimal_places=2)
    valormatricula = models.DecimalField(max_digits=10, decimal_places=2)

    # Total inscritos
    total_inscritos  = models.PositiveIntegerField(default=0, help_text="Total de personas inscritas al programa, se hayan matriculado o no.")

    # Plan de pago
    plan_pago = models.CharField(max_length=20, choices=PLAN_PAGO_CHOICES, default=PLAN_10)

    # Si plan = 2 colegiaturas
    primeracolegiatura = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    segundacolegiatura = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # Si plan = 10 cuotas
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cuota_mensual = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    moneda = models.CharField(max_length=10, default='USD')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']
        verbose_name = 'Valor Programa de Posgrado'
        indexes = [
            models.Index(fields=['programa_content_type', 'programa_object_id']),
        ]
        constraints = [
            # ✅ “OneToOne” lógico para GFK: 1 registro por programa
            models.UniqueConstraint(
                fields=['programa_content_type', 'programa_object_id'],
                name='uniq_valor_programa_gfk'
            )
        ]

    def __str__(self):
        programa_str = str(self.programa) if self.programa else f"Programa {self.programa_object_id}"
        base = f"{programa_str} - Inscr:{self.valorinscripcion} {self.moneda} - Matri:{self.valormatricula} {self.moneda}"
        if self.plan_pago == self.PLAN_2:
            return f"{base} - Cole1:{self.primeracolegiatura or 0} {self.moneda} - Cole2:{self.segundacolegiatura or 0} {self.moneda}"
        return f"{base} - Total:{self.valor_total or 0} {self.moneda} - Cuota:{self.cuota_mensual or 0} {self.moneda} x10"

    def clean(self):
        errors = {}

        def nonneg(name, value):
            if value is not None and value < 0:
                errors[name] = 'El valor no puede ser negativo.'

        nonneg('valorinscripcion', self.valorinscripcion)
        nonneg('valormatricula', self.valormatricula)
        nonneg('primeracolegiatura', self.primeracolegiatura)
        nonneg('segundacolegiatura', self.segundacolegiatura)
        nonneg('valor_total', self.valor_total)
        nonneg('cuota_mensual', self.cuota_mensual)

        if self.plan_pago == self.PLAN_2:
            if self.primeracolegiatura is None:
                errors['primeracolegiatura'] = 'Requerido para el plan de 2 colegiaturas.'
            if self.segundacolegiatura is None:
                errors['segundacolegiatura'] = 'Requerido para el plan de 2 colegiaturas.'
            self.valor_total = self.valor_total or None
            self.cuota_mensual = self.cuota_mensual or None

        elif self.plan_pago == self.PLAN_10:
            if self.valor_total is None:
                errors['valor_total'] = 'Requerido para el plan de 10 cuotas.'
            else:
                base = (self.valor_total or 0) - (self.valorinscripcion or 0) - (self.valormatricula or 0)
                self.cuota_mensual = round(base / 10, 2)
                if self.cuota_mensual < 0:
                    errors['valor_total'] = 'El total debe ser mayor o igual a inscripción + matrícula.'
            self.primeracolegiatura = self.primeracolegiatura or None
            self.segundacolegiatura = self.segundacolegiatura or None

        if errors:
            raise ValidationError(errors)


class CoordinadorPrograma(models.Model):
    coordinador = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='programas_coordinador'
    )

    # ✅ GFK: Programa (Maestría o Especialidad)
    programa_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        limit_choices_to=LIMIT_PROGRAMA_CT,
        related_name='ct_coordinador_programa',
        null=True, blank=True
    )
    programa_object_id = models.PositiveIntegerField(db_index=True, null=True, blank=True)
    programa = GenericForeignKey('programa_content_type', 'programa_object_id')

    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_inicio', '-created']
        verbose_name = 'Coordinador Programa'
        indexes = [
            models.Index(fields=['programa_content_type', 'programa_object_id', 'fecha_inicio']),
            models.Index(fields=['programa_content_type', 'programa_object_id', 'coordinador']),
        ]

    def __str__(self):
        programa_str = str(self.programa) if self.programa else f"Programa {self.programa_object_id}"
        return f"{self.coordinador} — {programa_str} ({self.fecha_inicio} → {self.fecha_fin})"

    def clean(self):
        if self.fecha_fin and self.fecha_inicio and self.fecha_fin < self.fecha_inicio:
            raise ValidationError("La fecha de fin no puede ser anterior a la fecha de inicio.")

        qs = CoordinadorPrograma.objects.filter(
            programa_content_type=self.programa_content_type,
            programa_object_id=self.programa_object_id,
            coordinador=self.coordinador
        )
        if self.pk:
            qs = qs.exclude(pk=self.pk)

        if self.fecha_inicio and self.fecha_fin and qs.filter(
            fecha_inicio__lte=self.fecha_fin,
            fecha_fin__gte=self.fecha_inicio
        ).exists():
            raise ValidationError("El rango de fechas se solapa con otro periodo para este coordinador en este programa.")


class CoordinadorPagos(models.Model):
    coordinador = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='pagos_coordinador'
    )

    # ✅ GFK: Programa (Maestría o Especialidad)
    programa_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        limit_choices_to=LIMIT_PROGRAMA_CT,
        related_name='ct_pagos_programa',
        null=True, blank=True
    )
    programa_object_id = models.PositiveIntegerField(db_index=True, null=True, blank=True)
    programa = GenericForeignKey('programa_content_type', 'programa_object_id')

    contrato = models.ForeignKey(
        ContratoCoordinador,
        on_delete=models.PROTECT,
        related_name='pagos_contrato'
    )

    mes_pago = models.DateField(
        help_text="Usa el primer día del mes pagado (e.g., 2025-10-01)."
    )

    numero_factura = models.CharField(max_length=100)
    urlfactura = models.URLField(max_length=500, blank=True, null=True)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    numero_oficio_tramite = models.CharField(max_length=100, blank=True, null=True)
    moneda = models.CharField(max_length=10, default='USD')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.coordinador} - {self.contrato} - {self.mes_pago:%Y-%m} - {self.valor_total} {self.moneda}"

    class Meta:
        ordering = ['-created']
        verbose_name = 'Pago Coordinador'
        verbose_name_plural = 'Pagos Coordinadores'
        indexes = [
            models.Index(fields=['programa_content_type', 'programa_object_id', 'mes_pago']),
            models.Index(fields=['coordinador', 'mes_pago']),
            models.Index(fields=['contrato', 'numero_factura']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['contrato', 'mes_pago', 'numero_factura'],
                name='uniq_contrato_mes_factura'
            )
        ]

    def clean(self):
        errors = {}

        if self.valor_total is not None and self.valor_total < 0:
            errors['valor_total'] = "El valor no puede ser negativo."

        # ✅ Consistencia con el contrato (ahora por GFK)
        if self.contrato_id:
            if self.coordinador_id and self.contrato.coordinador != self.coordinador_id:
                errors['coordinador'] = "El coordinador no coincide con el contrato seleccionado."

            # contrato.programa_content_type / contrato.programa_object_id
            if self.programa_content_type_id and self.contrato.programa_content_type_id != self.programa_content_type_id:
                errors['programa'] = "El programa no coincide con el contrato seleccionado."
            if self.programa_object_id and self.contrato.programa_object_id != self.programa_object_id:
                errors['programa'] = "El programa no coincide con el contrato seleccionado."

        if errors:
            raise ValidationError(errors)


class ContratoDocenteGestion(models.Model):
    contrato = models.OneToOneField(
        ContratosDocentes,
        on_delete=models.PROTECT,
        related_name='gestion'
    )
    fecha_contratacion = models.DateField(blank=True, null=True)
    pago_realizado = models.BooleanField(default=False)
    numero_factura = models.CharField(max_length=100, blank=True, null=True)
    urlfactura = models.URLField(max_length=500, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']
        verbose_name = 'Gestión de Contrato Docente'

    def __str__(self):
        return f"Gestión — Contrato {self.contrato.numerocontrato}"

    def clean(self):
        if self.pago_realizado and not self.numero_factura:
            raise ValidationError({'numero_factura': 'Requerido cuando el pago está marcado como realizado.'})


class ContratoTutorGestion(models.Model):
    contrato = models.OneToOneField(
        ContratoTutor,
        on_delete=models.PROTECT,
        related_name='gestion'
    )
    fecha_contratacion = models.DateField(blank=True, null=True)
    defendido = models.BooleanField(default=False, help_text="Defendido el trabajo de titulación")
    pago_realizado = models.BooleanField(default=False)
    numero_factura = models.CharField(max_length=100, blank=True, null=True)
    urlfactura = models.URLField(max_length=500, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']
        verbose_name = 'Gestión Contrato Tutor'

    def __str__(self):
        return f"Gestión Tutor — Contrato {self.contrato.numerocontrato}"

    def clean(self):
        if self.pago_realizado and not self.numero_factura:
            raise ValidationError({'numero_factura': 'Requerido cuando el pago está marcado como realizado.'})


class EstudianteProgramaGestion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gestiones_estudiante')

    # ✅ GFK: Programa (Maestría o Especialidad)
    programa_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        limit_choices_to=LIMIT_PROGRAMA_CT,
        related_name='ct_gestion_estudiante_programa',
        null=True, blank=True
    )
    programa_object_id = models.PositiveIntegerField(db_index=True, null=True, blank=True)
    programa = GenericForeignKey('programa_content_type', 'programa_object_id')

    # Pagos
    pago_inscripcion = models.BooleanField(default=True)
    pago_matricula = models.BooleanField(default=False)
    pago_primera_colegiatura = models.BooleanField(default=False)
    pago_segunda_colegiatura = models.BooleanField(default=False)

    cuotas_pagadas = models.PositiveSmallIntegerField(
        default=0,
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Número de cuotas pagadas cuando el plan del programa es 10 cuotas."
    )

    # Proceso titulación
    modalidad = models.ForeignKey(ModalidadDeTitulacion, on_delete=models.SET_NULL, blank=True, null=True)
    fecha_rubrica_aprobada = models.DateField(blank=True, null=True)

    tutor_resolucion = models.URLField(max_length=500, blank=True, null=True)
    tutor_resolucion_fecha = models.DateField(blank=True, null=True)
    tutor_contratado = models.BooleanField(default=False)

    AVANCE_CHOICES = [(0, '0 %'), (25, '25 %'), (50, '50 %'), (75, '75 %'), (100, '100 %')]
    avance_porcentaje = models.IntegerField(choices=AVANCE_CHOICES, blank=True, null=True)

    fecha_sustentacion_oral = models.DateField(blank=True, null=True)
    fecha_aprob_complexivo = models.DateField(blank=True, null=True)

    ESTADO_TITULO_CHOICES = [
        ('SICOA', 'Subido al SICOA'),
        ('IMPRESION', 'Envío a impresión'),
        ('REGISTRO', 'Registro Senescyt'),
        ('LISTO_RETIRO', 'Listo para retiro'),
        ('ENTREGADO', 'Entregado al estudiante'),
    ]
    estado_titulo = models.CharField(max_length=20, choices=ESTADO_TITULO_CHOICES, blank=True, null=True)

    BECA_CHOICES = [
        (0, 'Sin beca'),
        (25, '25%'),
        (50, '50%'),
        (75, '75%'),
        (100, '100%'),
    ]
    beca_porcentaje = models.PositiveSmallIntegerField(choices=BECA_CHOICES, default=0)
    beca_documento_url = models.URLField( max_length=500, blank=True, null=True)

    retirado = models.BooleanField(default=False)
    retiro_fecha = models.DateField(blank=True, null=True)
    retiro_documento_url = models.URLField(max_length=500, blank=True, null=True)

    reingreso = models.BooleanField(default=False)
    reingreso_fecha = models.DateField(blank=True, null=True)
    reingreso_documento_url = models.URLField(max_length=500, blank=True, null=True)
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated', '-created']
        verbose_name = 'Gestión Estudiante en Programa'
        indexes = [
            models.Index(fields=['programa_content_type', 'programa_object_id']),
            models.Index(fields=['usuario', 'updated']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['usuario', 'programa_content_type', 'programa_object_id'],
                name='uniq_estudiante_programa_gfk'
            )
        ]

    def __str__(self):
        programa_str = str(self.programa) if self.programa else f"Programa {self.programa_object_id}"
        return f"{self.usuario.get_full_name()} — {programa_str}"

    def clean(self):
        # Si marcó tutor_resolucion, pedir fecha (y viceversa) — opcional, descomenta si lo quieres obligatorio en pareja
        # if self.tutor_resolucion and not self.tutor_resolucion_fecha:
        #     raise ValidationError({'tutor_resolucion_fecha': 'Requerido si indicas número de resolución.'})
        pass