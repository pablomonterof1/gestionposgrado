from django.contrib import admin
from .models import Admision

# Register your models here.

class admisionAdmin(admin.ModelAdmin):
    readonly_fields = ('created',)   

admin.site.register(Admision, admisionAdmin)