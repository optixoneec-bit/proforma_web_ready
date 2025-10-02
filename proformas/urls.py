from django.urls import path
from . import views

urlpatterns = [
    path("", views.proforma_list, name="proforma_list"),
    path("nueva/", views.proforma_create, name="proforma_create"),
    path("<int:numero>/", views.proforma_detail, name="proforma_detail"),
    path("<int:numero>/pdf/", views.proforma_pdf, name="proforma_pdf"),
    path("<int:numero>/eliminar/", views.proforma_delete, name="proforma_delete"),
    path("buscar-paciente/", views.buscar_paciente, name="buscar_paciente"),  # 👈 nuevo endpoint
]
