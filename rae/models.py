from django.db import models
from programasposgrado.models import ProgramaPosgrado, Modulos
from tinymce.models import HTMLField


# Create your models here.


class ReactivosMultipleChoice(models.Model):

    enunciado = HTMLField(unique=True)
    contribucion = models.IntegerField(
        choices=[(1, 'Alto'), (2, 'Medio'), (3, 'Bajo')])
    opciona = models.TextField()
    opcionb = models.TextField()
    opcionc = models.TextField()
    opciond = models.TextField()
    correcta = models.CharField(max_length=1, choices=[('A', 'Opción A'), ('B', 'Opción B'), ('C', 'Opción C'), ('D', 'Opción D')])
    justificacion = models.TextField()
    bibliografia = models.TextField()
    palabras_clave = models.TextField()
    tiempo_estimado = models.IntegerField()
    estado = models.IntegerField(
        choices=[(1, 'Enviado'), (2, 'Validado'), (3, 'Rechazado')], default=1)
    created = models.DateTimeField(auto_now_add=True)
    programadeposgrado = models.ForeignKey(
        ProgramaPosgrado, on_delete=models.CASCADE, related_name='programa_reactivos')
    modulo = models.IntegerField(blank=True, null=True)
    usuario = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.enunciado or ''} - {self.contribucion or ''} - {self.opciona or ''} - {self.opcionb or ''} - {self.opcionc or ''} - {self.opciond or ''} - {self.correcta or ''} - {self.justificacion or ''} - {self.bibliografia or ''} - {self.palabras_clave or ''} - {self.tiempo_estimado or ''} - {self.estado or ''} - {self.created or ''} - {self.programadeposgrado or ''} - {self.modulo or ''} - {self.usuario or ''}"

    class Meta:
        ordering = ['-created']
        verbose_name = 'Reactivo'
