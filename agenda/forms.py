from datetime import timedelta
from django import forms
from django.utils import timezone
from .models import BloqueHorario, CentroTerapeutico


class BloqueForm(forms.ModelForm):
    """El especialista publica un bloque indicando su fecha y hora de inicio."""
    class Meta:
        model = BloqueHorario
        fields = ["inicio"]
        labels = {"inicio": "Fecha y hora de inicio"}
        widgets = {
            "inicio": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"},
                format="%Y-%m-%dT%H:%M",
            )
        }

    def clean_inicio(self):
        inicio = self.cleaned_data["inicio"]
        if inicio <= timezone.now():
            raise forms.ValidationError("No puedes publicar horarios en fechas u horas pasadas.")

        duracion = CentroTerapeutico.obtener().duracion_bloque
        fin = inicio + timedelta(minutes=duracion)

        se_cruza = BloqueHorario.objects.filter(
            especialista_id=self.instance.especialista_id,
            inicio__lt=fin,
            fin__gt=inicio,
        ).exists()
        if se_cruza:
            raise forms.ValidationError("Este horario colisiona con otro bloque ya publicado en tu agenda.")

        self.instance.fin = fin
        return inicio


class SolicitudCitaForm(forms.Form):
    """Formulario de reserva de cita con motivo y perfil sensorial."""
    bloque_id = forms.IntegerField(widget=forms.HiddenInput)
    motivo = forms.CharField(
        label="Motivo de la atención",
        max_length=300,
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Ej: Integración Sensorial, Evaluación TEA, Primera Consulta..."
        })
    )
    mensaje_sensorial = forms.CharField(
        label="Mensaje de introducción y Perfil Sensorial",
        max_length=1000,
        required=False,
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 3,
            "placeholder": "Indica si el paciente presenta hipersensibilidad sonora/táctil, sobrecarga de estímulos, adaptaciones necesarias o límites recomendados de sesión (máx 45 min)..."
        })
    )


class MotivoForm(forms.Form):
    """Motivo obligatorio para rechazar o cancelar una cita."""
    motivo = forms.CharField(
        max_length=300,
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 3,
            "placeholder": "Indica claramente el motivo..."
        })
    )
