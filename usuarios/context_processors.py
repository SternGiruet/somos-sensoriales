"""
Context processor global para la plataforma Gestión Sensorial.
Inyecta datos de navegación, badges, contadores y roles a todas las plantillas.
"""
from agenda.models import Cita
from notificaciones.models import Notificacion


def sensorial_context(request):
    ctx = {
        "app_nombre": "Gestión Sensorial",
        "app_eslogan": "Recordando mi espectro",
        "usuario_actual": None,
        "es_paciente": False,
        "es_especialista": False,
        "es_admin": False,
        "citas_pendientes_count": 0,
        "notificaciones_no_leidas_count": 0,
    }

    if request.user.is_authenticated:
        user = request.user
        ctx["usuario_actual"] = user
        ctx["es_paciente"] = (user.rol == user.PACIENTE)
        ctx["es_especialista"] = (user.rol == user.ESPECIALISTA)
        ctx["es_admin"] = (user.rol == user.ADMINISTRADOR or user.is_staff)

        # Contador de notificaciones no leídas
        try:
            ctx["notificaciones_no_leidas_count"] = Notificacion.objects.filter(usuario=user, leida=False).count()
        except Exception:
            pass

        # Contador de citas pendientes según rol
        try:
            if ctx["es_especialista"]:
                ctx["citas_pendientes_count"] = Cita.objects.filter(
                    bloque__especialista=user,
                    estado__in=[Cita.SOLICITADA, Cita.CONFIRMADA]
                ).count()
            elif ctx["es_paciente"]:
                ctx["citas_pendientes_count"] = Cita.objects.filter(
                    paciente=user,
                    estado__in=[Cita.SOLICITADA, Cita.CONFIRMADA]
                ).count()
        except Exception:
            pass

    return ctx
