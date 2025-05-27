from django.contrib import admin
from .models import ContratosDocentes

# Register your models here.

class ContratosDocentesAdmin(admin.ModelAdmin):
    readonly_fields = ('created',)
    list_display = ('docente', 'programadeposgrado', 'modulo', 'horasacademicas', 'valorxhora', 'certificacionpresupuestaria', 'fechacertificacionpresupuestaria', 'plazo', 'numerocontrato', 'numeromemorandotthh' , 'tipopersonalacademico', 'adenda', 'obsevaciones', 'created')
    search_fields = ('docente__username', 'programadeposgrado__nombre')
    list_per_page = 10
    ordering = ('-created',)


admin.site.register(ContratosDocentes, ContratosDocentesAdmin)