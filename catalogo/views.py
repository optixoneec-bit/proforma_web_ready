from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.db.models import Q
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.core.paginator import Paginator  # 👈 agregado

import os
import openpyxl

from .models import Servicio


def servicio_list(request):
    """Listado con buscador, opciones masivas y paginación."""
    query = request.GET.get("q", "")
    if query:
        servicios = Servicio.objects.filter(
            Q(nombre__icontains=query) |
            Q(codigo__icontains=query) |
            Q(area__icontains=query)
        )
    else:
        servicios = Servicio.objects.all()

    # 👇 Paginación: máximo 50 registros por página
    paginator = Paginator(servicios.order_by("codigo"), 50)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "catalogo/servicio_list.html", {
        "servicios": page_obj.object_list,
        "page_obj": page_obj,
        "query": query,
    })


@require_http_methods(["POST"])
def servicio_create(request):
    """Crear un nuevo servicio."""
    codigo = request.POST.get("codigo")
    nombre = request.POST.get("nombre")
    area = request.POST.get("area")
    pvp_sugerido = request.POST.get("pvp_sugerido")

    if codigo and nombre and pvp_sugerido:
        Servicio.objects.create(
            codigo=codigo,
            nombre=nombre,
            area=area,
            costo_base=0,
            pvp_sugerido=pvp_sugerido,
            porcentaje_ganancia=0,
        )
        messages.success(request, f"✅ Servicio '{nombre}' creado correctamente.")
    else:
        messages.error(request, "❌ Todos los campos obligatorios deben completarse.")

    return redirect("servicio_list")


@require_http_methods(["POST"])
def servicio_edit(request, pk):
    """Editar un servicio existente."""
    servicio = get_object_or_404(Servicio, pk=pk)

    codigo = request.POST.get("codigo")
    nombre = request.POST.get("nombre")
    area = request.POST.get("area")
    pvp_sugerido = request.POST.get("pvp_sugerido")

    if codigo and nombre and pvp_sugerido:
        servicio.codigo = codigo
        servicio.nombre = nombre
        servicio.area = area
        servicio.pvp_sugerido = pvp_sugerido
        servicio.save()
        messages.success(request, f"✏️ Servicio '{nombre}' actualizado correctamente.")
    else:
        messages.error(request, "❌ Todos los campos obligatorios deben completarse.")

    return redirect("servicio_list")


def servicio_delete(request, pk):
    """Eliminar un servicio individual."""
    servicio = get_object_or_404(Servicio, pk=pk)
    servicio.delete()
    messages.success(request, f"🗑 Servicio '{servicio.nombre}' eliminado.")
    return redirect("servicio_list")


@require_http_methods(["POST"])
def servicio_bulk_delete(request):
    """Eliminar varios servicios seleccionados."""
    ids = request.POST.getlist("seleccionados")
    if ids:
        Servicio.objects.filter(id__in=ids).delete()
        messages.success(request, f"🗑 {len(ids)} servicios eliminados.")
    else:
        messages.warning(request, "⚠️ No seleccionaste servicios.")
    return redirect("servicio_list")


def servicio_delete_all(request):
    """Eliminar toda la base de servicios."""
    Servicio.objects.all().delete()
    messages.success(request, "🗑 Se eliminaron todos los servicios del catálogo.")
    return redirect("servicio_list")


def importar_catalogo_view(request):
    """Importar un archivo Excel .xlsx y reemplazar el catálogo."""
    if request.method == "POST" and request.FILES.get("archivo"):
        archivo = request.FILES["archivo"]
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, "uploads"))
        filename = fs.save(archivo.name, archivo)
        filepath = fs.path(filename)

        try:
            wb = openpyxl.load_workbook(filepath)
            sheet = wb.active
            count = 0
            Servicio.objects.all().delete()  # 🔥 borra la base antes de cargar nueva

            for row in sheet.iter_rows(min_row=2, values_only=True):
                codigo, nombre, area, precio = row[:4]
                if not codigo or not nombre:
                    continue
                Servicio.objects.create(
                    codigo=str(codigo).strip(),
                    nombre=str(nombre).strip(),
                    area=(str(area).strip() if area else None),
                    costo_base=float(precio or 0),
                    pvp_sugerido=float(precio or 0),
                    pvp_corporativo=float(precio or 0),
                    porcentaje_ganancia=0,
                    activo=True,
                )
                count += 1

            messages.success(request, f"✅ Se cargaron {count} servicios desde el archivo.")
        except Exception as e:
            messages.error(request, f"❌ Error procesando archivo: {e}")

        os.remove(filepath)  # limpiar archivo temporal
        return redirect("servicio_list")

    return redirect("servicio_list")


def servicio_search(request):
    """Endpoint JSON para autocompletar ítems en proforma."""
    q = request.GET.get("q", "").strip()
    if not q:
        return JsonResponse([], safe=False)

    servicios = Servicio.objects.filter(
        Q(nombre__icontains=q) | Q(codigo__icontains=q)
    ).filter(activo=True)[:15]

    data = [{
        "id": s.id,
        "codigo": s.codigo,
        "nombre": s.nombre,
        "precio": float(s.pvp_sugerido or 0),
    } for s in servicios]

    return JsonResponse(data, safe=False)
