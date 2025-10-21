from django.db import models
from programasposgrado.models import ProgramaPosgrado, ModalidadDeTitulacion
from usuarios.models import User 
from django.core.exceptions import ValidationError
from datosposgrado.models import ContratoCoordinador, ContratosDocentes, ContratoTutor

# Create your models here.
class ValorProgramaPosgrado(models.Model):
    programa = models.OneToOneField(ProgramaPosgrado, on_delete=models.PROTECT, related_name='valor_programa')
    valorinscripcion = models.DecimalField(max_digits=10, decimal_places=2)
    valormatricula = models.DecimalField(max_digits=10, decimal_places=2)
    primeracolegiatura = models.DecimalField(max_digits=10, decimal_places=2)
    segundacolegiatura = models.DecimalField(max_digits=10, decimal_places=2)
    moneda = models.CharField(max_length=10, default='USD')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.programa} - {self.valorinscripcion} {self.moneda} - {self.valormatricula} {self.moneda} - {self.primeracolegiatura} {self.moneda} - {self.segundacolegiatura} {self.moneda}"

    class Meta:
        ordering = ['-created']
        verbose_name = 'Valor Programa de Posgrado'



class CoordinadorPrograma(models.Model):
    coordinador = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='programas_coordinador'
    )
    programa = models.ForeignKey(
        ProgramaPosgrado, on_delete=models.PROTECT, related_name='coordinadores_programa'
    )
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_inicio', '-created']
        verbose_name = 'Coordinador Programa'
        indexes = [
            models.Index(fields=['programa', 'fecha_inicio']),
            models.Index(fields=['programa', 'coordinador']),
        ]

    def __str__(self):
        return f"{self.coordinador} — {self.programa} ({self.fecha_inicio} → {self.fecha_fin})"

    def clean(self):
        if self.fecha_fin and self.fecha_inicio and self.fecha_fin < self.fecha_inicio:
            raise ValidationError("La fecha de fin no puede ser anterior a la fecha de inicio.")

        qs = CoordinadorPrograma.objects.filter(
            programa=self.programa,
            coordinador=self.coordinador
        )
        if self.pk:
            qs = qs.exclude(pk=self.pk)

        # solapa si: (ini<=fin_existente) y (fin>=ini_existente)
        if self.fecha_inicio and self.fecha_fin and qs.filter(
            fecha_inicio__lte=self.fecha_fin,
            fecha_fin__gte=self.fecha_inicio
        ).exists():
            raise ValidationError("El rango de fechas se solapa con otro periodo para este coordinador en este programa.")
        


class CoordinadorPagos(models.Model):
    coordinador = models.ForeignKey(
        User,
        on_delete=models.PROTECT,                # evita borrar pagos si borran el usuario
        related_name='pagos_coordinador'
    )
    programa = models.ForeignKey(
        ProgramaPosgrado,
        on_delete=models.PROTECT,               # evita borrar pagos si borran el programa
        related_name='pagos_programa'
    )
    contrato = models.ForeignKey(
        ContratoCoordinador,
        on_delete=models.PROTECT,               # evita borrar pagos si borran el contrato
        related_name='pagos_contrato'
    )

    # Mejor como fecha (primer día del mes pagado) para ordenar/filtrar bien
    mes_pago = models.DateField(
        help_text="Usa el primer día del mes pagado (e.g., 2025-10-01)."
    )

    numero_factura = models.CharField(max_length=100)
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
            models.Index(fields=['programa', 'mes_pago']),
            models.Index(fields=['coordinador', 'mes_pago']),
            models.Index(fields=['contrato', 'numero_factura']),
        ]
        constraints = [
            # Evita duplicar misma factura para el mismo contrato y mes
            models.UniqueConstraint(
                fields=['contrato', 'mes_pago', 'numero_factura'],
                name='uniq_contrato_mes_factura'
            )
        ]

    def clean(self):
        errors = {}

        # 1) Valor no negativo
        if self.valor_total is not None and self.valor_total < 0:
            errors['valor_total'] = "El valor no puede ser negativo."

        # 2) Consistencia con el contrato (ContratoCoordinador guarda enteros)
        if self.contrato_id:
            # coordenador debe coincidir con el ID entero en ContratoCoordinador
            if self.coordinador_id and self.contrato.coordinador != self.coordinador_id:
                errors['coordinador'] = "El coordinador no coincide con el contrato seleccionado."
            # programa debe coincidir con el ID entero en ContratoCoordinador
            if self.programa_id and self.contrato.programadeposgrado != self.programa_id:
                errors['programa'] = "El programa no coincide con el contrato seleccionado."

        if errors:
            raise ValidationError(errors)
        


class ContratoDocenteGestion(models.Model):
    """
    Datos adicionales para cada contrato de docente (1 a 1).
    NO modifica tu tabla original; solo la complementa.
    """
    contrato = models.OneToOneField(
        ContratosDocentes,
        on_delete=models.PROTECT,
        related_name='gestion'
    )
    fecha_contratacion = models.DateField(blank=True, null=True)
    pago_realizado = models.BooleanField(default=False)
    numero_factura = models.CharField(max_length=100, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']
        verbose_name = 'Gestión de Contrato Docente'

    def __str__(self):
        return f"Gestión — Contrato {self.contrato.numerocontrato}"

    def clean(self):
        # Si marcas pagado, pide número de factura (ajústalo si no lo necesitas)
        if self.pago_realizado and not self.numero_factura:
            raise ValidationError({'numero_factura': 'Requerido cuando el pago está marcado como realizado.'})
        

class ContratoTutorGestion(models.Model):
    """
    Datos adicionales por cada contrato de tutor.
    Uno a uno con ContratoTutor (no toca tu tabla original).
    """
    contrato = models.OneToOneField(
        ContratoTutor,
        on_delete=models.PROTECT,
        related_name='gestion'
    )
    fecha_contratacion = models.DateField(blank=True, null=True)
    defendido = models.BooleanField(default=False, help_text="Defendido el trabajo de titulación")
    pago_realizado = models.BooleanField(default=False)
    numero_factura = models.CharField(max_length=100, blank=True, null=True)
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
    """
    Datos de pagos y proceso de titulación por estudiante y programa.
    Uno por (usuario, programa).
    """
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gestiones_estudiante')
    programa = models.ForeignKey(ProgramaPosgrado, on_delete=models.PROTECT, related_name='gestiones_estudiantes')

    # Pagos (según ValorProgramaPosgrado del programa)
    pago_inscripcion = models.BooleanField(default=False)
    pago_matricula = models.BooleanField(default=False)
    pago_primera_colegiatura = models.BooleanField(default=False)
    pago_segunda_colegiatura = models.BooleanField(default=False)

    # Proceso titulación
    modalidad = models.ForeignKey(ModalidadDeTitulacion, on_delete=models.SET_NULL, blank=True, null=True)
    fecha_rubrica_aprobada = models.DateField(blank=True, null=True)

    tutor_resolucion = models.CharField(max_length=100, blank=True, null=True)
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

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('usuario', 'programa')]
        ordering = ['-updated', '-created']
        verbose_name = 'Gestión Estudiante en Programa'

    def __str__(self):
        return f"{self.usuario.get_full_name()} — {self.programa}"

    def clean(self):
        # Si marcó tutor_resolucion, pedir fecha (y viceversa) — opcional, descomenta si lo quieres obligatorio en pareja
        # if self.tutor_resolucion and not self.tutor_resolucion_fecha:
        #     raise ValidationError({'tutor_resolucion_fecha': 'Requerido si indicas número de resolución.'})
        pass