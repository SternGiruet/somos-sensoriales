from django.contrib import admin
from .models import BloqueHorario, CentroTerapeutico, Cita


@admin.register(CentroTerapeutico)
class CentroTerapeuticoAdmin(admin.ModelAdmin):
    list_display = ["nombre", "horas_minimas_cancelacion", "duracion_bloque"]

    def has_add_permission(self, request):
        return not CentroTerapeutico.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(BloqueHorario)
class BloqueHorarioAdmin(admin.ModelAdmin):
    list_display = ["inicio", "fin", "especialista", "disponible"]
    list_filter = ["especialista", "disponible"]
    date_hierarchy = "inicio"


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ["id", "paciente", "bloque", "motivo_consulta", "estado", "creada"]
    list_filter = ["estado", "creada"]
    search_fields = ["paciente__first_name", "paciente__last_name", "motivo_consulta"]
