from django.contrib import admin
from .models import Paciente, Proforma, ProformaItem

class ProformaItemInline(admin.TabularInline):
    model = ProformaItem
    extra = 0

@admin.register(Proforma)
class ProformaAdmin(admin.ModelAdmin):
    list_display = ("numero", "paciente", "fecha", "total")
    inlines = [ProformaItemInline]

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    search_fields = ("cedula", "nombre", "email")

admin.site.register(ProformaItem)
