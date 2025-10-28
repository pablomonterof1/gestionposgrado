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
    modulo = models.ForeignKey(Modulos, on_delete=models.CASCADE, null=True, blank=True)
    usuario = models.IntegerField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

    def get_opciones(self):
        return [
            ('A', self.opciona),
            ('B', self.opcionb),
            ('C', self.opcionc),
            ('D', self.opciond)
        ]

    def __str__(self):
        return f"{self.enunciado or ''} - {self.contribucion or ''} - {self.opciona or ''} - {self.opcionb or ''} - {self.opcionc or ''} - {self.opciond or ''} - {self.correcta or ''} - {self.justificacion or ''} - {self.bibliografia or ''} - {self.palabras_clave or ''} - {self.tiempo_estimado or ''} - {self.estado or ''} - {self.created or ''} - {self.programadeposgrado or ''} - {self.modulo or ''} - {self.usuario or ''} - {self.observaciones or ''}"

    class Meta:
        ordering = ['-created']
        verbose_name = 'Reactivo'


class ReactivosModuloRAE(models.Model):
    programadeposgrado = models.ForeignKey(ProgramaPosgrado, on_delete=models.CASCADE, related_name='programa_reactivosmodulorae')
    modulo = models.ForeignKey(Modulos, on_delete=models.CASCADE)
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
    duracion_minutos = models.PositiveIntegerField(default=90)
    valorpregunta = models.DecimalField(max_digits=5, decimal_places=3, default=2.000)

    def __str__(self):
        return f"{self.programa} - {self.get_tipo_display()}"
    

class ReactivoPorEvaluacion(models.Model):
    evaluacion = models.ForeignKey(EvaluacionPrograma, on_delete=models.CASCADE)
    reactivo = models.ForeignKey(ReactivosMultipleChoice, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('evaluacion', 'reactivo')


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


class ComponenteRAE(models.Model):
    programa = models.ForeignKey(
        ProgramaPosgrado, on_delete=models.CASCADE,
        related_name='componentes_rae'
    )
    nombre = models.CharField(max_length=255)
    orden = models.PositiveIntegerField(default=1)
    peso = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    preguntas_sugeridas = models.PositiveIntegerField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['programa', 'orden', 'id']
        unique_together = [('programa', 'nombre')]
        verbose_name = 'Componente RAE'
        verbose_name_plural = 'Componentes RAE'

    def __str__(self):
        return f'{self.programa} — {self.nombre}'


class SubcomponenteRAE(models.Model):
    componente = models.ForeignKey(
        ComponenteRAE, on_delete=models.CASCADE,
        related_name='subcomponentes'
    )
    nombre = models.CharField(max_length=255)
    orden = models.PositiveIntegerField(default=1)
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['componente', 'orden', 'id']
        unique_together = [('componente', 'nombre')]
        verbose_name = 'Subcomponente RAE'
        verbose_name_plural = 'Subcomponentes RAE'

    def __str__(self):
        return f'{self.componente.nombre} — {self.nombre}'


class SubcomponenteModuloRAE(models.Model):
    """
    Asigna MÓDULOS (de la maestría del programa) a un SUBCOMPONENTE.
    Un módulo debe pertenecer a un único subcomponente dentro del mismo programa.
    Si un componente “no tiene subcomponentes”, crea uno único (p. ej. “Único”),
    así mantenemos una sola ruta jerárquica: Componente > Subcomponente > Módulo.
    """
    subcomponente = models.ForeignKey(
        SubcomponenteRAE, on_delete=models.CASCADE,
        related_name='modulos_asignados'
    )
    modulo = models.ForeignKey(
        Modulos, on_delete=models.CASCADE,
        related_name='asignaciones_rae'
    )

    class Meta:
        unique_together = [('subcomponente', 'modulo')]
        verbose_name = 'Asignación de módulo a subcomponente'
        verbose_name_plural = 'Asignaciones de módulos a subcomponentes'

    def __str__(self):
        return f'{self.subcomponente} — {self.modulo.nombre}'

    def clean(self):
        """
        Garantiza coherencia: el módulo debe pertenecer a la misma maestría del programa
        del componente padre.
        """
        from django.core.exceptions import ValidationError
        comp = self.subcomponente.componente
        # comp.programa.maestria es un ID; modulo.maestria puede ser ID o FK según tu modelo.
        if str(self.modulo.maestria) != str(comp.programa.maestria):
            raise ValidationError(
                'El módulo no pertenece a la maestría del programa de este componente.'
            )
        # Evitar que el mismo módulo quede asignado a dos subcomponentes del mismo programa.
        ya = SubcomponenteModuloRAE.objects.filter(
            modulo=self.modulo,
            subcomponente__componente__programa=comp.programa
        ).exclude(pk=self.pk).exists()
        if ya:
            raise ValidationError('Este módulo ya está asignado a otro subcomponente del mismo programa.')