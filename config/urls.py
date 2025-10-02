from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Proformas (pantalla principal)
    path('', include('proformas.urls')),

    # Catálogo (servicios)
    path('catalogo/', include('catalogo.urls')),
]
