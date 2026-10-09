"""Funciones de ayuda para auditoría y protección contra ataques de fuerza bruta."""
from datetime import timedelta
from django.utils import timezone
from .models import RegistroAuditoria

MAX_INTENTOS = 5
MINUTOS_BLOQUEO = 15


def registrar(accion, request=None, usuario=None, correo="", detalle=""):
    """Registra una acción inmutable en el log de auditoría."""
    ip = None
    if request is not None:
        ip = request.META.get("REMOTE_ADDR")
        if usuario is None and request.user.is_authenticated:
            usuario = request.user
    RegistroAuditoria.objects.create(
        usuario=usuario,
        correo=correo or (usuario.email if usuario else ""),
        accion=accion,
        detalle=detalle[:300],
        ip=ip,
    )


def demasiados_intentos(correo):
    """
    True si hubo 5 o más intentos fallidos con ese correo en los últimos 15 minutos.
    Previene enumeración de usuarios (DEF-05).
    """
    hace_15_minutos = timezone.now() - timedelta(minutes=MINUTOS_BLOQUEO)
    fallidos = RegistroAuditoria.objects.filter(
        accion="LOGIN_FALLIDO", correo=correo, fecha__gte=hace_15_minutos
    ).count()
    return fallidos >= MAX_INTENTOS
