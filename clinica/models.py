"""
Modelos del módulo clínico: Diagnósticos, Fichas Sensoriales y Solicitudes Institucionales.
"""
from django.conf import settings
from django.db import models
from django.utils import timezone
from agenda.models import Cita


class Diagnostico(models.Model):
    """
    Informes clínicos y evaluaciones sensoriales asociados al paciente,
    con soporte para descarga de informes PDF (conforme a los mockups de Claude).
    """
    TIPO_CHOICES = [
        ("TEA Nivel 1", "TEA Nivel 1"),
        ("TEA Nivel 2", "TEA Nivel 2"),
        ("Sensibilidad Auditiva", "Sensibilidad Auditiva"),
        ("Integración Sensorial", "Integración Sensorial"),
        ("TDAH", "Evaluación TDAH"),
        ("Evaluación Conductual", "Evaluación Conductual"),
        ("Fonoaudiología", "Fonoaudiología"),
        ("Neurología", "Neurología Pediátrica"),
        ("Primera consulta", "Primera Consulta"),
        ("Otro", "Otro informe clínico"),
    ]

    paciente = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="diagnosticos"
    )
    especialista = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="diagnosticos_emitidos"
    )
    cita = models.ForeignKey(
        Cita, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="diagnosticos_relacionados"
    )
    tipo = models.CharField(max_length=60, choices=TIPO_CHOICES, default="TEA Nivel 1")
    titulo = models.CharField(max_length=150)
    observaciones = models.TextField(
        "observaciones clínicas y recomendaciones", blank=True,
        help_text="Notas clínicas, estímulos sensoriales evaluados y adaptaciones sugeridas"
    )
    archivo_pdf = models.FileField(upload_to="diagnosticos/", blank=True, null=True)
    fecha_emision = models.DateField(default=timezone.now)
    visible_para_paciente = models.BooleanField(
        "visible para el paciente", default=True,
        help_text="Indica si el paciente puede visualizar este informe desde su Ficha"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha_emision", "-id"]
        verbose_name = "diagnóstico sensorial"
        verbose_name_plural = "diagnósticos sensoriales"

    def __str__(self):
        return f"{self.titulo} | {self.paciente.get_full_name()} ({self.tipo})"


class SolicitudContacto(models.Model):
    """Canal de comunicación entre terapeutas y la administración del centro."""
    TIPO_CHOICES = [
        ("VACACIONES", "Solicitud de Vacaciones / Días Libres"),
        ("AGENDA", "Ajuste de Horarios y Disponibilidad"),
        ("ADMINISTRATIVA", "Consulta Administrativa o Insumos Clínicos"),
        ("URGENCIA", "Notificación de Urgencia Clínica"),
    ]

    especialista = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="solicitudes_contacto"
    )
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES, default="VACACIONES")
    asunto = models.CharField(max_length=150)
    mensaje = models.TextField()
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    atendido = models.BooleanField("atendido por administración", default=False)

    class Meta:
        ordering = ["-fecha_solicitud"]
        verbose_name = "solicitud a administración"
        verbose_name_plural = "solicitudes a administración"

    def __str__(self):
        return f"{self.get_tipo_display()} | {self.especialista.nombre_completo_con_titulo} ({self.asunto})"
