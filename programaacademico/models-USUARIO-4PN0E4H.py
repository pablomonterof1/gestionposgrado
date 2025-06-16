from django.db import models

# Create your models here.
class Admision(models.Model):
    nombre = models.CharField(max_length=200)
    created = models.DateField(auto_now_add=True)
    descripcion = models.TextField(blank=True)
    informacion = models.TextField(blank=True)
    important = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre + ' - ' + self.descripcion + ' - ' + str(self.important)

        