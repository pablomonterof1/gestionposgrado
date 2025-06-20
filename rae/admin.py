from django.contrib import admin
from .models import ReactivosMultipleChoice
from django.utils.html import format_html

# Register your models here.

class ReactivosMultipleChoiceAdmin(admin.ModelAdmin):
    list_display = ('enunciado_html', 'contribucion', 'opciona', 'opcionb', 'opcionc', 'opciond', 'correcta', 'justificacion', 'bibliografia' , 'palabras_clave', 'tiempo_estimado', 'estado' , 'created', 'programadeposgrado', 'modulo',  'usuario')
    search_fields = ('enunciado',)
    ordering = ('-created',)
    list_per_page = 10

    fieldsets = (
        (None, {
            'fields': ('enunciado', 'contribucion', 'opciona', 'opcionb', 'opcionc', 'opciond', 'correcta', 'justificacion', 'palabras_clave',  'bibliografia' , 'tiempo_estimado',  'estado' , 'programadeposgrado', 'modulo', 'usuario')
        }),
    )
    def enunciado_html(self, obj):
        return format_html(obj.enunciado)

admin.site.register(ReactivosMultipleChoice, ReactivosMultipleChoiceAdmin) 