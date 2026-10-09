from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import RegistroAuditoria, Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ["email", "first_name", "last_name", "rol", "especialidad", "rut", "pin_seguridad", "is_active"]
    list_filter = ["rol", "is_active"]
    search_fields = ["email", "first_name", "last_name", "rut"]
    fieldsets = UserAdmin.fieldsets + (
        ("Datos Clínicos y Sensoriales", {
            "fields": [
                "rol", "rut", "telefono", "direccion", "nombre_tutor", "telefono_tutor",
                "edad", "pin_seguridad", "prefijo", "especialidad", "biografia",
                "dias_atencion", "registro_minsal", "color_avatar", "iniciales",
                "fecha_consentimiento"
            ]
        }),
    )


@admin.register(RegistroAuditoria)
class RegistroAuditoriaAdmin(admin.ModelAdmin):
    list_display = ["fecha", "accion", "correo", "detalle", "ip"]
    list_filter = ["accion", "fecha"]
    search_fields = ["correo", "accion", "detalle", "ip"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
