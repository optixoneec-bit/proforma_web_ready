from django.urls import path
from . import views

urlpatterns = [
    path("", views.servicio_list, name="servicio_list"),
    path("nuevo/", views.servicio_create, name="servicio_create"),
    path("<int:pk>/editar/", views.servicio_edit, name="servicio_edit"),
    path("<int:pk>/eliminar/", views.servicio_delete, name="servicio_delete"),
    path("eliminar-seleccionados/", views.servicio_bulk_delete, name="servicio_bulk_delete"),
    path("eliminar-todo/", views.servicio_delete_all, name="servicio_delete_all"),
    path("importar/", views.importar_catalogo_view, name="importar_catalogo"),
    path("buscar/", views.servicio_search, name="servicio_search"),
]
