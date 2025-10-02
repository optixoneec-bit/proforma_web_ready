from django.db import models
from django.utils import timezone
from decimal import Decimal


class Paciente(models.Model):
    cedula = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    celular = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} ({self.cedula})"


class Proforma(models.Model):
    numero = models.AutoField(primary_key=True)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    fecha = models.DateTimeField(default=timezone.now)
    observaciones = models.TextField(blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # ✅ Nuevo campo para controlar visibilidad de precios en PDF
    mostrar_precios = models.BooleanField(default=True)

    def recomputar(self):
        total = Decimal("0.00")
        for item in self.items.all():
            item.subtotal = Decimal(item.precio_unitario) * Decimal(item.cantidad)
            item.save()
            total += item.subtotal
        self.total = total
        self.save()

    def __str__(self):
        return f"Proforma {self.numero} - {self.paciente.nombre}"


class ProformaItem(models.Model):
    proforma = models.ForeignKey(Proforma, related_name="items", on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=200)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.subtotal = Decimal(self.precio_unitario) * Decimal(self.cantidad)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.descripcion} x{self.cantidad}"
