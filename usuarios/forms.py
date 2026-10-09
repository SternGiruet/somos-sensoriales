import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario


def rut_valido(rut):
    """
    Revisa formato de RUT chileno 12345678-5 y dígito verificador módulo 11.
    """
    if not re.fullmatch(r"\d{7,8}-[\dkK]", rut):
        return False
    numero, dv = rut.split("-")
    suma = 0
    multiplicador = 2
    for digito in reversed(numero):
        suma += int(digito) * multiplicador
        multiplicador = 2 if multiplicador == 7 else multiplicador + 1
    resultado = 11 - (suma % 11)
    if resultado == 11:
        esperado = "0"
    elif resultado == 10:
        esperado = "K"
    else:
        esperado = str(resultado)
    return dv.upper() == esperado


def aplicar_estilos_form(form):
    for field in form.fields.values():
        if isinstance(field.widget, forms.CheckboxInput):
            field.widget.attrs["class"] = "form-check-input"
        else:
            field.widget.attrs["class"] = "form-control"


class LoginForm(forms.Form):
    email = forms.CharField(
        label="Correo electrónico o Usuario",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "tu@correo.cl o usuario", "autofocus": True})
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "••••••••"})
    )


class RegistroPacienteForm(UserCreationForm):
    first_name = forms.CharField(label="Nombre", max_length=60)
    last_name = forms.CharField(label="Apellido", max_length=60)
    email = forms.EmailField(label="Correo electrónico")
    rut = forms.CharField(label="RUT (ej: 12345678-5)", max_length=12)
    telefono = forms.CharField(label="Teléfono del paciente", max_length=20, required=False)
    nombre_tutor = forms.CharField(label="Nombre del tutor / responsable (opcional)", max_length=120, required=False)
    telefono_tutor = forms.CharField(label="Teléfono del tutor (opcional)", max_length=20, required=False)
    direccion = forms.CharField(label="Dirección", max_length=255, required=False)
    edad = forms.IntegerField(label="Edad", min_value=0, max_value=120, initial=18)
    pin_seguridad = forms.CharField(
        label="PIN de 4 dígitos para Ficha Sensorial (Confidencial)",
        max_length=4,
        min_length=4,
        initial="1234",
        widget=forms.TextInput(attrs={"class": "form-control text-center letter-spacing-1", "maxlength": "4"})
    )
    acepta_datos = forms.BooleanField(
        label="Acepto el uso de mis datos personales para la atención y seguimiento sensorial (Leyes 19.628 y 21.719).",
        required=True
    )

    class Meta:
        model = Usuario
        fields = [
            "first_name", "last_name", "email", "rut", "telefono",
            "nombre_tutor", "telefono_tutor", "direccion", "edad", "pin_seguridad"
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        aplicar_estilos_form(self)

    def clean_email(self):
        email = self.cleaned_data["email"].lower().strip()
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("Ya existe una cuenta con ese correo electrónico.")
        return email

    def clean_rut(self):
        rut = self.cleaned_data["rut"].replace(".", "").strip().upper()
        if not rut_valido(rut):
            raise forms.ValidationError("RUT inválido. Ingrésalo sin puntos y con guion (ej: 12345678-5).")
        return rut

    def clean_pin_seguridad(self):
        pin = self.cleaned_data.get("pin_seguridad", "").strip()
        if not re.fullmatch(r"\d{4}", pin):
            raise forms.ValidationError("El PIN debe consistir exactamente en 4 números.")
        return pin
