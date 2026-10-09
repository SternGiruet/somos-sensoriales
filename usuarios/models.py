"""
Modelos de la app usuarios: Usuario unificado y RegistroAuditoria.

Unifica la herencia de AbstractUser con los campos clínicos del perfil sensorial
(PIN de 4 dígitos, avatar, tutor, especialidad médica y derecho de supresión Ley 21.719).
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class Usuario(AbstractUser):
    """
    Modelo de usuario único con discriminación por rol, conforme a los principios
    de diseño de software y requerimientos clínicos de Gestión Sensorial.
    """
    PACIENTE = "PACIENTE"
    ESPECIALISTA = "ESPECIALISTA"
    ADMINISTRADOR = "ADMINISTRADOR"

    ROLES = [
        (PACIENTE, "Paciente / Tutor"),
        (ESPECIALISTA, "Especialista Clínico"),
        (ADMINISTRADOR, "Administrador"),
    ]

    email = models.EmailField("correo electrónico", unique=True)
    rol = models.CharField(max_length=15, choices=ROLES, default=PACIENTE)
    telefono = models.CharField("teléfono", max_length=20, blank=True)
    direccion = models.CharField("dirección", max_length=255, blank=True)

    # Datos exclusivos del Paciente
    rut = models.CharField("RUT", max_length=12, blank=True)
    nombre_tutor = models.CharField("nombre del tutor", max_length=120, blank=True)
    telefono_tutor = models.CharField("teléfono del tutor", max_length=20, blank=True)
    edad = models.PositiveIntegerField("edad", default=18, blank=True, null=True)
    fecha_consentimiento = models.DateTimeField(
        "fecha consentimiento ley 19.628 / 21.719", null=True, blank=True
    )
    # PIN de 4 dígitos para resguardo de la Ficha Clínica Sensorial (Mockup)
    pin_seguridad = models.CharField(
        "PIN de seguridad de ficha", max_length=4, default="1234",
        help_text="PIN de 4 dígitos para desbloquear la ficha clínica y diagnósticos"
    )

    # Datos exclusivos del Especialista
    prefijo = models.CharField("título / prefijo", max_length=15, default="Dra.", blank=True)
    especialidad = models.CharField("especialidad", max_length=120, blank=True)
    biografia = models.TextField("biografía clínica", blank=True)
    dias_atencion = models.CharField("días de atención", max_length=120, default="Lunes a Viernes", blank=True)
    registro_minsal = models.CharField("registro prestador de salud", max_length=50, blank=True)

    # Identidad visual de la UI (Mockups)
    color_avatar = models.CharField("color de avatar", max_length=10, default="#d6e8f8")
    iniciales = models.CharField("iniciales", max_length=5, blank=True)

    def save(self, *args, **kwargs):
        if not self.iniciales:
            nom = self.first_name or self.username
            ape = self.last_name or ""
            ini1 = nom[0].upper() if nom else "U"
            ini2 = ape[0].upper() if ape else (nom[1].upper() if len(nom) > 1 else "")
            self.iniciales = f"{ini1}{ini2}"
        super().save(*args, **kwargs)

    @property
    def nombre_completo_con_titulo(self):
        full = self.get_full_name() or self.username
        if self.rol == self.ESPECIALISTA and self.prefijo:
            return f"{self.prefijo} {full}".strip()
        return full

    def __str__(self):
        return self.nombre_completo_con_titulo or self.email

    def eliminar_datos_personales(self):
        """
        Derecho de supresión (Ley 21.719, RF-13).
        Anonimiza los datos personales manteniendo la integridad de las citas pasadas.
        """
        self.first_name = "Usuario"
        self.last_name = "eliminado"
        self.username = f"eliminado-{self.id}"
        self.email = f"eliminado-{self.id}@correo.invalid"
        self.telefono = ""
        self.telefono_tutor = ""
        self.rut = ""
        self.nombre_tutor = ""
        self.direccion = ""
        self.is_active = False
        self.set_unusable_password()
        self.save()


class RegistroAuditoria(models.Model):
    """
    Registro inmutable de auditoría para seguridad y cumplimiento legal (Ley 21.459).
    Nadie en el panel administrativo puede modificar ni eliminar registros de esta tabla.
    """
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(Usuario, null=True, blank=True, on_delete=models.SET_NULL)
    correo = models.CharField(max_length=254, blank=True)
    accion = models.CharField(max_length=60)
    detalle = models.CharField(max_length=300, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ["-fecha"]
        verbose_name = "registro de auditoría"
        verbose_name_plural = "registros de auditoría"

    def __str__(self):
        return f"{self.fecha:%d-%m-%Y %H:%M} | {self.accion} | {self.correo or self.usuario}"
