
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from programasposgrado.models import Modulos, ModulosEM



ESTADO_CHOICES = [
    ('enviado', 'Enviado'),
    ('aprobado', 'Aprobado'),
    ('rechazado', 'Rechazado'),
]

class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ci = models.CharField(max_length=20, blank=True, null=True)
    rol = models.IntegerField( choices=[
        (1, 'Estudiante'),
        (2, 'Docente'),
        (3, 'Coordinador'),
        (4, 'Editor'),
    ], blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    nacionalidad = models.CharField(max_length=20, blank=True, null=True)
    sexo = models.CharField(max_length=10, choices=[
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ], blank=True, null=True)
    titulotercernivel = models.CharField(max_length=100, blank=True, null=True)
    provincia = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.user.get_full_name} - {self.rol} - {self.telefono} - {self.ci}"
    

class MatriculaUsuario(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    programa = GenericForeignKey('content_type', 'object_id')
    rol_en_programa = models.CharField(max_length=20, choices=[('estudiante', 'Estudiante')])
    fecha_matricula = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Matrícula usuario'
        verbose_name_plural = 'Matrículas usuarios'

    def __str__(self):
        return f"{self.usuario.get_full_name()} en {self.programa}"


class MatriculaDocenteModulo(models.Model):
    docente = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'perfilusuario__rol': 2}
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    modulo = GenericForeignKey('content_type', 'object_id')
    fecha_matricula = models.DateTimeField(auto_now_add=True)
    programa = models.BigIntegerField()

    class Meta:
        verbose_name = 'Matricula docente a módulo'
        verbose_name_plural = 'Matriculas docentes a módulos'
        unique_together = ('docente', 'content_type', 'object_id')

    def __str__(self):
        return f"{self.docente.get_full_name()} asignado al módulo {self.modulo}"


class DocumentosUsuarioPEM(models.Model):
    
    usuario = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE)

    especialidadmedica = models.BigIntegerField()
    
    docidentificacion = models.FileField(upload_to='documentospem/', blank=True, null=True)
    observaciondocidentificacion = models.TextField(blank=True, null=True)
    estado_docidentificacion = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Pendiente')

    titulosenescyt = models.FileField(upload_to='documentospem/', blank=True, null=True)
    observaciontitulosenescyt = models.TextField(blank=True, null=True)
    estado_titulosenescyt = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Pendiente')

    descripcion = models.TextField(blank=True, null=True)


    fecha_subida = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.usuario.user.get_full_name()} - Documentos"


