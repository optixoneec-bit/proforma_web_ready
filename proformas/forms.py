from django import forms
from .models import Paciente, Proforma


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
