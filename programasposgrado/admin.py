from django.contrib import admin

# Register your models here.

from .models import Maestrias, PeriodosAcademicos, PerfildeIngreso, Modalidad, ProgramaPosgrado, CampoAmplio, Modulos

class MaestriasAdmin(admin.ModelAdmin):
    readonly_fields = ('created',)
    list_display = ('nombre', 'descripcion', 'evaluado', 'created')

class PeriodosAcademicosAdmin(admin.ModelAdmin):
    readonly_fields = ('created',)
    list_display = ('nombre', 'fecha_inicio', 'fecha_fin', 'created')

class ModalidadAdmin(admin.ModelAdmin):
    readonly_fields = ('created',)
    list_display = ('modalidad', 'descripcion', 'created')





class ProgramaPosgradoAdmin(admin.ModelAdmin):
    readonly_fields = ('created',)
    list_display = ('get_maestria_nombre', 'get_periodo_nombre', 'get_modalidad_nombre','get_campoamplio_nombre', 'cohorte' , 'created')

    def get_maestria_nombre(self, obj):
        from .models import Maestrias
        try:
            return Maestrias.objects.get(id=obj.maestria).nombre
        except Maestrias.DoesNotExist:
            return f'ID {obj.maestria}'
    get_maestria_nombre.short_description = 'Maestría'

    def get_campoamplio_nombre(self, obj):
        from .models import CampoAmplio
        try:
            return CampoAmplio.objects.get(id=obj.campoamplio).nombre
        except CampoAmplio.DoesNotExist:
            return f'ID {obj.campoamplio}'
    get_campoamplio_nombre.short_description = 'Campo amplio'

    def get_periodo_nombre(self, obj):
        from .models import PeriodosAcademicos
        try:
            return PeriodosAcademicos.objects.get(id=obj.periodoacademico).nombre
        except PeriodosAcademicos.DoesNotExist:
            return f'ID {obj.periodoacademico}'
    get_periodo_nombre.short_description = 'Periodo académico'

    def get_modalidad_nombre(self, obj):
        from .models import Modalidad
        try:
            return Modalidad.objects.get(id=obj.modalidad).modalidad
        except Modalidad.DoesNotExist:
            return f'ID {obj.modalidad}'
    get_modalidad_nombre.short_description = 'Modalidad'



class PerfildeIngresoAdmin(admin.ModelAdmin):
    readonly_fields = ('created',)
    list_display = ('perfil', 'descripcion', 'created')

class CampoAmplioAdmin(admin.ModelAdmin):
    readonly_fields = ('created',)
    list_display = ('nombre', 'created')

class ModulosAdmin(admin.ModelAdmin):
    readonly_fields = ('created',)
    list_display = ('maestria', 'nombre', 'codificacion', 'created')



admin.site.register(Maestrias, MaestriasAdmin)
admin.site.register(PeriodosAcademicos, PeriodosAcademicosAdmin)
admin.site.register(PerfildeIngreso, PerfildeIngresoAdmin)
admin.site.register(Modalidad, ModalidadAdmin)
admin.site.register(ProgramaPosgrado, ProgramaPosgradoAdmin)
admin.site.register(CampoAmplio, CampoAmplioAdmin)
admin.site.register(Modulos, ModulosAdmin)

