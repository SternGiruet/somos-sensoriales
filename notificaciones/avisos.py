"""
Patrón Factory para el despacho multicanal de notificaciones.
Permite extender fácilmente el sistema agregando nuevos canales (WhatsApp, SMS, etc.).
"""
from django.core.mail import send_mail
from .models import Notificacion


class AvisoApp:
    def enviar(self, usuario, texto):
        Notificacion.objects.create(usuario=usuario, mensaje=texto)


class AvisoCorreo:
    def enviar(self, usuario, texto):
        if getattr(usuario, "email", None):
            send_mail(
                subject="Gestión Sensorial: Actualización en tu cita",
                message=texto,
                from_email=None,
                recipient_list=[usuario.email],
                fail_silently=True,
            )


CANALES = {
    "app": AvisoApp,
    "correo": AvisoCorreo,
}


def crear_aviso(canal):
    """Fábrica que instancia el despachador según el canal solicitado."""
    if canal not in CANALES:
        raise ValueError(f"Canal de aviso desconocido: {canal}")
    return CANALES[canal]()
