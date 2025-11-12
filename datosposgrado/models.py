from django.db import models

# Create your models here.
class ContratosDocentes(models.Model):
    docente = models.IntegerField()
    programadeposgrado = models.IntegerField()
    modulo = models.IntegerField()
    horasacademicas = models.IntegerField()
    valorxhora = models.DecimalField(max_digits=10, decimal_places=2)
    certificacionpresupuestaria = models.CharField(max_length=100)
    fechacertificacionpresupuestaria = models.DateField()
    plazo = models.CharField(max_length=100)
    numerocontrato = models.CharField(max_length=100)
    numeromemorandotthh = models.CharField(max_length=100)
    tipopersonalacademico = models.IntegerField(choices=[
        (1, 'Servicios profesionales'),
    ], default=1)
    adenda = models.CharField(max_length=100, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    urldocumento = models.URLField(max_length=500, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.docente} {self.programadeposgrado} {self.horasacademicas}"

    class Meta:
        ordering = ['-created']
        verbose_name = 'Contrato Docente'
        verbose_name_plural = 'Contratos Docentes'


class ContratoTutor(models.Model):
    tutor = models.IntegerField()
    programadeposgrado = models.IntegerField()
    maestrante = models.IntegerField()
    plazo = models.CharField(max_length=100)
    certificacionpresupuestaria = models.CharField(max_length=100)
    fechacertificacionpresupuestaria = models.DateField()
    valorcontrato = models.DecimalField(max_digits=10, decimal_places=2)
    numerocontrato = models.CharField(max_length=100)
    numeromemorandotthh = models.CharField(max_length=100)
    tipopersonalacademico = models.IntegerField(choices=[
        (1, 'Servicios profesionales'),
    ], default=1)
    adenda = models.CharField(max_length=100, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    urldocumento = models.URLField(max_length=500, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tutor} {self.programadeposgrado}"

    class Meta:
        ordering = ['-created']
        verbose_name = 'Contrato de Tutor'
        verbose_name_plural = 'Contratos de Tutor'


class ContratoCoordinador(models.Model):
    coordinador = models.IntegerField()
    programadeposgrado = models.IntegerField()
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

    def __str__(self):
        return f"{self.coordinador} {self.programadeposgrado}"

    class Meta:
        ordering = ['-created']
        verbose_name = 'Contrato de Coordinador'
        verbose_name_plural = 'Contratos de Coordinador'
