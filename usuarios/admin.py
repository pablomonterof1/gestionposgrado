
from django.contrib import admin
from .models import PerfilUsuario

class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'rol', 'telefono')
    search_fields = ('user__username', 'rol')
    list_filter = ('rol',)
    ordering = ('user',)
    fieldsets = (
        (None, {
            'fields': ('user', 'rol', 'telefono')
        }),
    )

admin.site.register(PerfilUsuario, PerfilUsuarioAdmin)

