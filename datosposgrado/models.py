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
    obsevaciones = models.TextField(blank=True, null=True)    
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.docente} {self.programadeposgrado} {self.horasacademicas}"

    class Meta:
        ordering = ['-created']
        verbose_name = 'Contratos Docentes'