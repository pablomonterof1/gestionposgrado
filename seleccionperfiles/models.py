from django.db import models
from usuarios.models import PerfilUsuario, User
from programasposgrado.models import ProgramaPosgrado, Modulos

class TernaModuloPM(models.Model):
    programa_posgrado = models.ForeignKey(ProgramaPosgrado, on_delete=models.CASCADE, related_name='terna_modulopm')
    modulo = models.ForeignKey(Modulos, on_delete=models.CASCADE, related_name='terna_modulopm')
    docente1_idoneo = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='ternas_idoneo')
    docente2 = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='ternas_docente2')
    docente3 = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='ternas_docente3')
    responsable = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='ternas_responsable')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Terna de Módulo Maestría'
        verbose_name_plural = 'Ternas de Módulo Maestría'

    def _str_(self):
        return f"{self.programa_posgrado} - {self.modulo}"
    

class DocenteContratadoPM(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='docente_contratadopm')
    terna_modulo_maestria = models.ForeignKey(TernaModuloPM, on_delete=models.CASCADE, related_name='docente_contratadopm')
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    

    class Meta:
        verbose_name = 'Docente Contratado'
        verbose_name_plural = 'Docentes Contratados'

    def __str__(self):
        return f"{self.perfil_usuario} - {self.terna_modulo_maestria}"