from django.db import models
from programasposgrado.models import ProgramaPosgrado, Modulos
from tinymce.models import HTMLField
from django.contrib.auth.models import User

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
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.enunciado or ''} - {self.contribucion or ''} - {self.opciona or ''} - {self.opcionb or ''} - {self.opcionc or ''} - {self.opciond or ''} - {self.correcta or ''} - {self.justificacion or ''} - {self.bibliografia or ''} - {self.palabras_clave or ''} - {self.tiempo_estimado or ''} - {self.estado or ''} - {self.created or ''} - {self.programadeposgrado or ''} - {self.modulo or ''} - {self.usuario or ''} - {self.observaciones or ''}"

    class Meta:
        ordering = ['-created']
        verbose_name = 'Reactivo'


class ReactivosModuloRAE(models.Model):
    programadeposgrado = models.ForeignKey(ProgramaPosgrado, on_delete=models.CASCADE, related_name='programa_reactivosmodulorae')
    modulo = models.IntegerField()
    numero_reactivos_modulo = models.IntegerField()
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.programadeposgrado or ''} - {self.modulo or ''} - {self.numero_reactivos_modulo or ''} - {self.observaciones or ''}"

    class Meta:
        verbose_name = 'ReactivosModuloRAE'
        verbose_name_plural = 'ReactivosModuloRAE'


class EvaluacionPrograma(models.Model):
    TIPOS_EVALUACION = [
        ('simulacro', 'Simulacro'),
        ('final', 'Final')
    ]
    programa = models.ForeignKey(ProgramaPosgrado, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10, choices=TIPOS_EVALUACION)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    activa = models.BooleanField(default=False)

    class Meta:
        unique_together = ('programa', 'tipo')


class EvaluacionEstudiante(models.Model):
    evaluacion = models.ForeignKey(EvaluacionPrograma, on_delete=models.CASCADE)
    estudiante = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    calificacion = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    respondido = models.BooleanField(default=False)

    


class ReactivoEvaluacion(models.Model):
    evaluacion_estudiante = models.ForeignKey(EvaluacionEstudiante, on_delete=models.CASCADE)
    reactivo = models.ForeignKey(ReactivosMultipleChoice, on_delete=models.CASCADE)
    respuesta_estudiante = models.CharField(max_length=1, blank=True, null=True)
    correcta = models.BooleanField(default=False)
