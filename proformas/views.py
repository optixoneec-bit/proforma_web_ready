from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse, JsonResponse
from django.db import transaction
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.utils import simpleSplit

from .models import Paciente, Proforma, ProformaItem
from .forms import PacienteInlineForm, ProformaObservForm


def proforma_list(request):
    query = request.GET.get("q", "")
    proformas = Proforma.objects.select_related("paciente")

    if query:
        proformas = (proformas.filter(numero__icontains=query) |
                     proformas.filter(paciente__nombre__icontains=query) |
                     proformas.filter(paciente__cedula__icontains=query))

    proformas = proformas.order_by("-numero")[:200]

    return render(request, "proformas/proforma_list.html", {
        "proformas": proformas,
        "query": query,
    })


def _get_or_create_paciente_from_post(request):
    cedula = (request.POST.get("cedula") or "").strip()
    if not cedula:
        return None

    nombre = (request.POST.get("nombre") or "").strip()
    email = (request.POST.get("email") or "").strip()
    celular = (request.POST.get("celular") or "").strip()
    direccion = (request.POST.get("direccion") or "").strip()

    paciente, created = Paciente.objects.get_or_create(
        cedula=cedula,
        defaults={
            "nombre": nombre,
            "email": email,
            "celular": celular,
            "direccion": direccion,
        },
    )
    if not created:
        if nombre:
            paciente.nombre = nombre
        if email:
            paciente.email = email
        if celular:
            paciente.celular = celular
        if direccion:
            paciente.direccion = direccion
        paciente.save()

    return paciente


@transaction.atomic
def proforma_create(request):
    if request.method == "POST":
        paciente = _get_or_create_paciente_from_post(request)
        if paciente is None:
            return render(request, "proformas/proforma_form.html", {
                "p_form": PacienteInlineForm(data=request.POST),
                "o_form": ProformaObservForm(data=request.POST),
                "error": "Debe ingresar una cédula para guardar la proforma."
            })

        obs_form = ProformaObservForm(request.POST)
        obs_form.is_valid()
        observaciones = obs_form.cleaned_data.get("observaciones", "")

        mostrar_precios = bool(request.POST.get("mostrar_precios"))

        prof = Proforma.objects.create(
            paciente=paciente,
            observaciones=observaciones,
        )
        request.session[f"mostrar_precios_{prof.numero}"] = mostrar_precios

        descs = request.POST.getlist("item_descripcion[]")
        precios = request.POST.getlist("item_precio[]")
        cants = request.POST.getlist("item_cantidad[]")

        for d, pu, c in zip(descs, precios, cants):
            if not (d or "").strip():
                continue
            try:
                pu_val = float(pu)
                c_val = int(float(c))
            except Exception:
                continue
            ProformaItem.objects.create(
                proforma=prof,
                descripcion=d.strip(),
                precio_unitario=pu_val,
                cantidad=c_val
            )

        prof.recomputar()
        return redirect("proforma_detail", numero=prof.numero)

    return render(request, "proformas/proforma_form.html", {
        "p_form": PacienteInlineForm(),
        "o_form": ProformaObservForm(),
    })


def proforma_detail(request, numero):
    prof = get_object_or_404(Proforma.objects.select_related("paciente"), pk=numero)
    items = prof.items.all()
    mostrar_precios = request.session.get(f"mostrar_precios_{prof.numero}", True)
    return render(request, "proformas/proforma_detail.html", {
        "prof": prof,
        "items": items,
        "mostrar_precios": mostrar_precios,
    })


def proforma_pdf(request, numero):
    prof = get_object_or_404(Proforma.objects.select_related("paciente"), pk=numero)
    items = prof.items.all()

    if request.GET.get("ocultar") == "1":
        mostrar_precios = False
    elif request.GET.get("ocultar") == "0":
        mostrar_precios = True
    else:
        mostrar_precios = request.session.get(f"mostrar_precios_{prof.numero}", True)

    request.session[f"mostrar_precios_{prof.numero}"] = mostrar_precios

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    page_width, page_height = letter

    logo_path = "static/img/logo.png"
    try:
        p.drawImage(ImageReader(logo_path), (page_width - 220) / 2, page_height - 120,
                    width=220, height=90, mask='auto')
    except Exception:
        pass

    title_y = page_height - 150
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(page_width / 2, title_y, "Proforma")

    p.setFont("Helvetica", 10)
    p.drawString(100, title_y - 20, f"Número: {prof.numero}")
    p.drawString(100, title_y - 35, f"Paciente: {prof.paciente.nombre}")
    p.drawString(100, title_y - 50, f"Fecha: {prof.fecha.strftime('%d/%m/%Y')}")

    # 👉 Línea divisoria debajo del encabezado
    y_line = title_y - 65
    p.setLineWidth(0.8)
    p.line(80, y_line, page_width - 80, y_line)

    # Cabecera de ítems
    y = y_line - 20
    p.setFont("Helvetica-Bold", 10)
    p.drawString(100, y, "Descripción")
    p.drawString(300, y, "Cant.")
    if mostrar_precios:
        p.drawString(350, y, "P.Unit")
        p.drawString(420, y, "Subtotal")

    # Cuerpo
    p.setFont("Helvetica", 10)
    for item in items:
        y -= 20
        if y < 150:  # margen para no pisar el bloque inferior
            p.showPage()
            y = 750
            p.setFont("Helvetica-Bold", 10)
            p.drawString(100, y, "Descripción")
            p.drawString(300, y, "Cant.")
            if mostrar_precios:
                p.drawString(350, y, "P.Unit")
                p.drawString(420, y, "Subtotal")
            p.setFont("Helvetica", 10)
            y -= 20

        p.drawString(100, y, item.descripcion)
        p.drawString(300, y, str(item.cantidad))
        if mostrar_precios:
            p.drawString(350, y, f"{item.precio_unitario:.2f}")
            p.drawString(420, y, f"{item.subtotal:.2f}")

    # Total (arriba del bloque observaciones)
    y -= 40
    p.setFont("Helvetica-Bold", 12)
    p.drawString(350, y, "Total:")
    p.drawString(420, y, f"{prof.total:.2f}")

    # 👉 Línea divisoria para observaciones
    obs_y = 120  # altura fija del bloque inferior
    p.setLineWidth(0.8)
    p.line(80, obs_y + 20, page_width - 80, obs_y + 20)

    # Observaciones al pie
    p.setFont("Helvetica-Bold", 10)
    p.drawString(100, obs_y, "Observaciones:")
    p.setFont("Helvetica", 10)

    obs_text = prof.observaciones or ""
    max_width = page_width - 200
    lines = simpleSplit(obs_text, "Helvetica", 10, max_width) if obs_text else [""]

    offset = 14
    for i, line in enumerate(lines):
        p.drawString(200, obs_y - offset * i, line)

    p.showPage()
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f"proforma_{prof.numero}.pdf")


def proforma_delete(request, numero):
    prof = get_object_or_404(Proforma, pk=numero)
    prof.delete()
    return redirect("proforma_list")


def buscar_paciente(request):
    cedula = request.GET.get("cedula")
    try:
        paciente = Paciente.objects.get(cedula=cedula)
        data = {
            "existe": True,
            "nombre": paciente.nombre,
            "email": paciente.email,
            "celular": paciente.celular,
            "direccion": paciente.direccion,
        }
    except Paciente.DoesNotExist:
        data = {"existe": False}
    return JsonResponse(data)


# ====== FORMULARIOS ======
from django import forms


class PacienteInlineForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ["cedula", "nombre", "email", "celular", "direccion"]
        widgets = {
            "cedula": forms.TextInput(attrs={"class": "form-control", "placeholder": "Cédula"}),
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre completo"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Correo electrónico"}),
            "celular": forms.TextInput(attrs={"class": "form-control", "placeholder": "Celular"}),
            "direccion": forms.TextInput(attrs={"class": "form-control", "placeholder": "Dirección"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.required = False


class ProformaObservForm(forms.ModelForm):
    class Meta:
        model = Proforma
        fields = ["observaciones"]
        widgets = {
            "observaciones": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Observaciones adicionales"
            }),
        }
