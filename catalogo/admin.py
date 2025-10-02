from django.contrib import admin
from .models import Servicio

@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'area', 'pvp_sugerido', 'activo')
    search_fields = ('codigo', 'nombre', 'area')
    list_filter = ('area', 'activo')
