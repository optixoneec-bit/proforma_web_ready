from django.db import models

class Servicio(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=255)
    area = models.CharField(max_length=100, blank=True, null=True)
    costo_base = models.DecimalField(max_digits=10, decimal_places=2)
    pvp_sugerido = models.DecimalField(max_digits=10, decimal_places=2)
    pvp_corporativo = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    porcentaje_ganancia = models.DecimalField(max_digits=5, decimal_places=2, help_text="Ej: 30 para 30%")
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
