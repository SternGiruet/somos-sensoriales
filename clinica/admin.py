from django.contrib import admin
from .models import Diagnostico, SolicitudContacto


@admin.register(Diagnostico)
class DiagnosticoAdmin(admin.ModelAdmin):
    list_display = ["titulo", "paciente", "especialista", "tipo", "fecha_emision", "visible_para_paciente"]
    list_filter = ["tipo", "visible_para_paciente", "fecha_emision"]
    search_fields = ["titulo", "paciente__first_name", "paciente__last_name", "observaciones"]


@admin.register(SolicitudContacto)
class SolicitudContactoAdmin(admin.ModelAdmin):
    list_display = ["asunto", "especialista", "tipo", "fecha_solicitud", "atendido"]
    list_filter = ["tipo", "atendido"]
    search_fields = ["asunto", "mensaje", "especialista__first_name", "especialista__last_name"]
