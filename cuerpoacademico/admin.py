from django.contrib import admin

# Register your models here.

from .models import ComposicionCA, GestionAcademicaCA


class ComposicionCAAdmin(admin.ModelAdmin):
    readonly_fields = ('created',)
    list_display = ('nombre', 'tipodedato', 'descripcion',
                    'valor', 'created', 'programadeposgrado')


admin.site.register(ComposicionCA, ComposicionCAAdmin)

class GestionAcademicaCAAdmin(admin.ModelAdmin):
    readonly_fields = ('created',)
    list_display = ('nombre', 'tipodedato', 'descripcion',
                    'valor', 'created', 'programadeposgrado')


admin.site.register(GestionAcademicaCA, GestionAcademicaCAAdmin)
