from django.db import models
from programasposgrado.models import ProgramaPosgrado

# Create your models here.


class Admision(models.Model):
    tipodedato = models.IntegerField(choices=[(1, 'Incritos'), (
        2, 'Matriculados'),])
    descripcion = models.TextField(blank=True, null=True)
    valor = models.IntegerField( blank=True, null=True)
    created = models.DateField(auto_now_add=True)
    programadeposgrado = models.ForeignKey(
        ProgramaPosgrado, on_delete=models.CASCADE, related_name='programadeposgrado')

    def __str__(self):
        return self.get_tipodedato_display() + ' - ' + self.descripcion + ' - ' + str(self.valor) + ' - ' + str(self.created) + ' - ' + str(self.programadeposgrado)


class DisenoCurricular(models.Model):
    nombre = models.CharField(max_length=200)
    tipodedato = models.IntegerField(choices=[(1, 'Perfil de egreso'), (
        2, 'Plan de estudios'), (3, 'Sillabus'), (4, 'Sillabus aprobados')])
    descripcion = models.TextField(blank=True, null=True)
    valor = models.IntegerField(blank=True, null=True)
    created = models.DateField(auto_now_add=True)
    programadeposgrado = models.ForeignKey(
        ProgramaPosgrado, on_delete=models.CASCADE, related_name='programadeposgrado_disenocurricular')

    def __str__(self):
        return self.nombre + ' - ' + str(self.tipodedato) + ' - ' + self.descripcion + ' - ' + str(self.valor) + ' - ' + str(self.created) + ' - ' + str(self.programadeposgrado)


class Titulacion(models.Model):
    nombre = models.CharField(max_length=200)
    tipodedato = models.IntegerField(choices=[(
        1, 'Proyecto de titulación con componente de investigación aplicada y/o desarrollo'), (2, 'Artículos científicos o profesionales de alto nivel'), (3, 'Examen Complexivo teórico – práctico'),])
    descripcion = models.TextField(blank=True, null=True)
    valor = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    created = models.DateField(auto_now_add=True)
    programadeposgrado = models.ForeignKey(
        ProgramaPosgrado, on_delete=models.CASCADE, related_name='programadeposgrado_titulacion')

    def __str__(self):
        return self.nombre + ' - ' + str(self.tipodedato) + ' - ' + self.descripcion + ' - ' + str(self.valor) + ' - ' + str(self.created) + ' - ' + str(self.programadeposgrado)
