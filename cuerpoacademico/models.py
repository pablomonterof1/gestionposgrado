
from django.db import models
from programasposgrado.models import ProgramaPosgrado

# Create your models here.
class ComposicionCA(models.Model):
    nombre = models.CharField(max_length=200, blank=True, null=True)
    tipodedato = models.IntegerField(choices=[(
        1, 'Composición 1'), (2, 'Composición 2'), (3, 'Composición 3'),])
    descripcion = models.TextField(blank=True, null=True)
    valor = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    created = models.DateField(auto_now_add=True)
    programadeposgrado= models.ForeignKey(
        ProgramaPosgrado, on_delete=models.CASCADE, related_name='programadeposgrado_composicionca')
    
    def __str__(self):
        return f"{self.nombre or ''} - {self.tipodedato or ''} - {self.descripcion or ''} - {self.valor or ''} - {self.created or ''} - {self.programadeposgrado or ''}"

    # Create your models here.
class GestionAcademicaCA(models.Model):
    nombre = models.CharField(max_length=200, blank=True, null=True)
    tipodedato = models.IntegerField(choices=[(
        1, 'Gestion Academica 1'), (2, 'Gestion Academica 2'), (3, 'Gestion Academica 3'),])
    descripcion = models.TextField(blank=True, null=True)
    valor = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    created = models.DateField(auto_now_add=True)
    programadeposgrado = models.ForeignKey(
        ProgramaPosgrado, on_delete=models.CASCADE, related_name='programadeposgrado_gestionacademicaca')

    def __str__(self):
        return f"{self.nombre or ''} - {self.tipodedato or ''} - {self.descripcion or ''} - {self.valor or ''} - {self.created or ''} - {self.programadeposgrado or ''}"
