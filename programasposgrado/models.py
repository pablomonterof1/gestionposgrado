from django.db import models

# Create your models here.



class Maestrias(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    evaluado = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ['-created']
        verbose_name = 'Maestria'


class Modulos(models.Model):
    maestria = models.ForeignKey(Maestrias, on_delete=models.CASCADE, related_name='modulos')
    nombre = models.CharField(max_length=100)
    codificacion = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ['-created']
        verbose_name = 'Modulo'


class PeriodosAcademicos(models.Model):
    nombre = models.CharField(max_length=100)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ['fecha_inicio']
        verbose_name = 'PeriodosAcademicos'



class PerfildeIngreso(models.Model):
    perfil = models.TextField()
    descripcion = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.perfil

    class Meta:
        ordering = ['-created']
        verbose_name = 'Perfil de Ingreso'


class Modalidad(models.Model):
    modalidad = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.modalidad

    class Meta:
        ordering = ['-created']
        verbose_name = 'Modalidad'


class CampoAmplio(models.Model):
    nombre = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre
    
    class Meta:
        ordering = ['-created']
        verbose_name = 'Campo Amplio'


class ProgramaPosgrado(models.Model):
    maestria = models.BigIntegerField()
    campoamplio = models.BigIntegerField()
    periodoacademico = models.BigIntegerField() 
    modalidad = models.BigIntegerField()
    cohorte = models.IntegerField(choices=[
        (1, 'Primera'),
        (2, 'Segunda'),
        (3, 'Tercera'),
        (4, 'Cuarta'),
        (5, 'Quinta'),
        (6, 'Sexta'),
        (7, 'Septima'),
        (8, 'Octava'),
        (9, 'Novena'),
        (10, 'Decima')
    ])
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        try:
            maestria_nombre = Maestrias.objects.get(id=self.maestria).nombre
        except Maestrias.DoesNotExist:
            maestria_nombre = f'ID {self.maestria}'
        
        try:
            campoamplio_nombre = CampoAmplio.objects.get(id=self.campoamplio).nombre
        except CampoAmplio.DoesNotExist:
            campoamplio_nombre = f'ID {self.campoamplio}'

        try:
            periodo_nombre = PeriodosAcademicos.objects.get(id=self.periodoacademico).nombre
        except PeriodosAcademicos.DoesNotExist:
            periodo_nombre = f'ID {self.periodoacademico}'

        try:
            modalidad_nombre = Modalidad.objects.get(id=self.modalidad).modalidad
        except Modalidad.DoesNotExist:
            modalidad_nombre = f'ID {self.modalidad}'

        return f'{periodo_nombre} - {maestria_nombre} - {modalidad_nombre} - {campoamplio_nombre} - {self.get_cohorte_display()}' 

    class Meta:
        ordering = ['-created']
        verbose_name = 'Programa de Posgrado'


class EspecialidadesMedicas(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ['-created']
        verbose_name = 'Especialidad Medica'


class ModulosEM(models.Model):
    especialidad = models.ForeignKey(EspecialidadesMedicas, on_delete=models.CASCADE, related_name='modulos_especialidad')
    nombre = models.CharField(max_length=100)
    codificacion = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ['-created']
        verbose_name = 'Modulo Especialidad Médica'


class ProgramaPosgradoEM(models.Model):
    especialidad = models.BigIntegerField()
    campoamplio = models.BigIntegerField()
    periodoacademico = models.BigIntegerField() 
    modalidad = models.BigIntegerField()
    cohorte = models.IntegerField(choices=[
        (1, 'Primera'),
        (2, 'Segunda'),
        (3, 'Tercera'),
        (4, 'Cuarta'),
        (5, 'Quinta'),
        (6, 'Sexta'),
        (7, 'Septima'),
        (8, 'Octava'),
        (9, 'Novena'),
        (10, 'Decima')
    ])
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        try:
            especialidad_nombre = EspecialidadesMedicas.objects.get(id=self.especialidad).nombre
        except EspecialidadesMedicas.DoesNotExist:
            especialidad_nombre = f'ID {self.especialidad}'

        try:
            campoamplio_nombre = CampoAmplio.objects.get(id=self.campoamplio).nombre
        except CampoAmplio.DoesNotExist:
            campoamplio_nombre = f'ID {self.campoamplio}'

        try:
            periodo_nombre = PeriodosAcademicos.objects.get(id=self.periodoacademico).nombre
        except PeriodosAcademicos.DoesNotExist:
            periodo_nombre = f'ID {self.periodoacademico}'
        
        try:
            modalidad_nombre = Modalidad.objects.get(id=self.modalidad).modalidad
        except Modalidad.DoesNotExist:
            modalidad_nombre = f'ID {self.modalidad}'

        return f'{periodo_nombre} - {especialidad_nombre} - {modalidad_nombre} - {campoamplio_nombre} - {self.get_cohorte_display()} '

    class Meta:
        ordering = ['-created']
        verbose_name = 'Programa de Posgrado EM'