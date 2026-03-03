from django.contrib import admin
from .models import ContratosDocentes

@admin.register(ContratosDocentes)
class ContratosDocentesAdmin(admin.ModelAdmin):
    readonly_fields = ('created',)
    list_display = (
        'docente', 'horasacademicas', 'valorxhora',
        'certificacionpresupuestaria', 'fechacertificacionpresupuestaria',
        'plazo', 'numerocontrato', 'numeromemorandotthh',
        'tipopersonalacademico', 'adenda', 'created'
    )

    # ✅ si tenías list_filter con programa_tipo, bórralo
    list_filter = ()  # o elimina esta línea

    search_fields = ('docente', 'numerocontrato', 'numeromemorandotthh')
    list_per_page = 10
    ordering = ('-created',)