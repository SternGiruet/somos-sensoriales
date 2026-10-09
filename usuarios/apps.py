from django.apps import AppConfig


class UsuariosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "usuarios"
    verbose_name = "Usuarios y Seguridad"

    def ready(self):
        # Conecta el observador de auditoría a la señal cita_cambiada
        import usuarios.receptores  # noqa: F401
