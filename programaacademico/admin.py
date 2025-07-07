from django.contrib import admin
from .models import Admision, DisenoCurricular, Titulacion

# Register your models here.

class admisionAdmin(admin.ModelAdmin):
    readonly_fields = ('created',)   
    list_display = ('tipodedato', 'descripcion', 'valor', 'created', 'programadeposgrado')

admin.site.register(Admision, admisionAdmin)

class DisenoCurricularAdmin(admin.ModelAdmin):
    readonly_fields = ('created',)   
    list_display = ('nombre', 'tipodedato', 'descripcion', 'valor', 'created', 'programadeposgrado')

admin.site.register(DisenoCurricular, DisenoCurricularAdmin)

class TitulacionAdmin(admin.ModelAdmin):
    readonly_fields = ('created',)   
    list_display = ('nombre', 'tipodedato', 'descripcion', 'valor', 'created', 'programadeposgrado')

admin.site.register(Titulacion, TitulacionAdmin)

    