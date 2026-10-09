from django.apps import AppConfig


class NotificacionesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "notificaciones"
    verbose_name = "Notificaciones y Alertas"

    def ready(self):
        # Conecta el receptor a la señal de cambio de citas
        import notificaciones.receptores  # noqa: F401
