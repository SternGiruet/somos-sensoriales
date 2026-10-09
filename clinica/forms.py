from django import forms
from usuarios.models import Usuario
from .models import Diagnostico, SolicitudContacto


class DiagnosticoForm(forms.ModelForm):
    """Formulario para que el especialista cargue un diagnóstico o informe con PDF."""
    marcar_realizada = forms.BooleanField(
        required=False,
        initial=True,
        label="Marcar la cita asociada como 'Realizada' automáticamente",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )

    class Meta:
        model = Diagnostico
        fields = [
            "paciente", "tipo", "titulo", "observaciones", "archivo_pdf",
            "visible_para_paciente"
        ]
        widgets = {
            "paciente": forms.Select(attrs={"class": "form-select"}),
            "tipo": forms.Select(attrs={"class": "form-select"}),
            "titulo": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ej: TEA Nivel 1 — Evaluación Inicial 2026"
            }),
            "observaciones": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Detalla estímulos sensoriales evaluados, nivel de alerta, hipersensibilidad o pautas para el hogar/escuela..."
            }),
            "archivo_pdf": forms.FileInput(attrs={"class": "form-control", "accept": ".pdf"}),
            "visible_para_paciente": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo mostrar usuarios pacientes en el select
        self.fields["paciente"].queryset = Usuario.objects.filter(
            rol=Usuario.PACIENTE, is_active=True
        ).order_by("first_name")


class SolicitudContactoForm(forms.ModelForm):
    class Meta:
        model = SolicitudContacto
        fields = ["tipo", "asunto", "mensaje"]
        widgets = {
            "tipo": forms.Select(attrs={"class": "form-select"}),
            "asunto": forms.TextInput(attrs={"class": "form-control", "placeholder": "Asunto de la solicitud"}),
            "mensaje": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Detalla tu requerimiento..."}),
        }
