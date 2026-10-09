"""
Modelos de la Agenda Clínica: CentroTerapeutico (Singleton), BloqueHorario y Cita.

Incorpora:
- Patrón Singleton para configuración centralizada.
- Control de concurrencia atómica (select/update) para prevenir doble reserva de horas.
- Regla de 24 horas mínimas de cancelación.
- Registro del perfil y sensibilidades sensoriales del paciente.
- Notificación automática mediante el patrón Observer (señal cita_cambiada).
"""
from datetime import timedelta
from django.conf import settings
from django.db import models, transaction
from django.utils import timezone

from .senales import cita_cambiada


class ErrorCita(Exception):
    """Excepción de regla de negocio cuyo mensaje se presenta al usuario."""
    pass


class CentroTerapeutico(models.Model):
    """
    Patrón Singleton: El centro clínico tiene una única configuración.
    save() fuerza pk=1 para garantizar unicidad.
    """
    nombre = models.CharField(max_length=120, default="Aquí Somos Sensoriales")
    horas_minimas_cancelacion = models.PositiveSmallIntegerField(
        "horas mínimas de anticipación para cancelar", default=24
    )
    duracion_bloque = models.PositiveSmallIntegerField(
        "duración estándar del bloque (minutos)", default=45
    )

    class Meta:
        verbose_name = "centro terapéutico"
        verbose_name_plural = "centro terapéutico"

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def obtener(cls):
        centro, _ = cls.objects.get_or_create(pk=1)
        return centro


class BloqueHorario(models.Model):
    """Bloque de atención clínica publicado por un especialista."""
    especialista = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bloques"
    )
    inicio = models.DateTimeField()
    fin = models.DateTimeField()
    disponible = models.BooleanField(default=True)

    class Meta:
        ordering = ["inicio"]
        verbose_name = "bloque horario"
        verbose_name_plural = "bloques horarios"

    def __str__(self):
        return f"{timezone.localtime(self.inicio):%d-%m-%Y %H:%M} | {self.especialista.nombre_completo_con_titulo}"


class Cita(models.Model):
    """Ciclo de vida y reglas de negocio de una sesión terapéutica."""
    SOLICITADA = "SOLICITADA"
    CONFIRMADA = "CONFIRMADA"
    REALIZADA = "REALIZADA"
    RECHAZADA = "RECHAZADA"
    CANCELADA = "CANCELADA"

    ESTADOS = [
        (SOLICITADA, "Solicitada"),
        (CONFIRMADA, "Confirmada"),
        (REALIZADA, "Realizada"),
        (RECHAZADA, "Rechazada"),
        (CANCELADA, "Cancelada"),
    ]

    paciente = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="citas_paciente"
    )
    bloque = models.ForeignKey(
        BloqueHorario, on_delete=models.PROTECT, related_name="citas"
    )
    estado = models.CharField(max_length=15, choices=ESTADOS, default=SOLICITADA)
    motivo_consulta = models.CharField(
        "motivo de consulta", max_length=300,
        help_text="Ej: Terapia Ocupacional, Integración Sensorial, Evaluación TEA, Primera Consulta"
    )
    mensaje_sensorial = models.TextField(
        "mensaje de introducción y perfil sensorial", blank=True,
        help_text="Indica hipersensibilidad (auditiva, táctil), requerimientos de luz, límites de tiempo o adaptaciones"
    )
    motivo_respuesta = models.CharField(
        "motivo de respuesta o cancelación", max_length=300, blank=True
    )
    creada = models.DateTimeField(auto_now_add=True)
    actualizada = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["bloque__inicio"]
        verbose_name = "cita"
        verbose_name_plural = "citas"

    def __str__(self):
        return f"Cita #{self.id} | {self.paciente.get_full_name()} con {self.bloque.especialista.nombre_completo_con_titulo} ({self.get_estado_display()})"

    # --- Métodos de Ayuda ---
    def esta_activa(self):
        return self.estado in [self.SOLICITADA, self.CONFIRMADA]

    def horas_que_faltan(self):
        return (self.bloque.inicio - timezone.now()) / timedelta(hours=1)

    @property
    def es_hoy(self):
        return timezone.localtime(self.bloque.inicio).date() == timezone.localdate()

    def _guardar_y_notificar(self, accion, actor):
        self.save()
        cita_cambiada.send(sender=Cita, cita=self, accion=accion, actor=actor)

    def _liberar_bloque(self):
        self.bloque.disponible = True
        self.bloque.save()

    # --- Reglas de Negocio con Concurrencia Atómica ---
    @classmethod
    def solicitar(cls, paciente, bloque_id, motivo="", mensaje_sensorial=""):
        """
        Reserva atómica que previene que dos usuarios reserven el mismo bloque simultáneamente.
        """
        with transaction.atomic():
            filas_actualizadas = BloqueHorario.objects.filter(
                id=bloque_id, disponible=True, inicio__gt=timezone.now()
            ).update(disponible=False)

            if filas_actualizadas == 0:
                raise ErrorCita("Ese horario ya no se encuentra disponible. Por favor selecciona otro.")

            cita = cls.objects.create(
                paciente=paciente,
                bloque_id=bloque_id,
                motivo_consulta=motivo or "Evaluación e Integración Sensorial",
                mensaje_sensorial=mensaje_sensorial,
                estado=cls.SOLICITADA,
            )

        cita_cambiada.send(sender=Cita, cita=cita, accion="solicitada", actor=paciente)
        return cita

    def confirmar(self, especialista):
        if self.estado != self.SOLICITADA:
            raise ErrorCita("Solo se pueden confirmar citas en estado 'Solicitada'.")
        self.estado = self.CONFIRMADA
        self._guardar_y_notificar("confirmada", especialista)

    def rechazar(self, especialista, motivo):
        if self.estado != self.SOLICITADA:
            raise ErrorCita("Solo se pueden rechazar citas en estado 'Solicitada'.")
        self.estado = self.RECHAZADA
        self.motivo_respuesta = motivo
        self._liberar_bloque()
        self._guardar_y_notificar("rechazada", especialista)

    def cancelar(self, actor, motivo, revisar_24_horas=True):
        if not self.esta_activa():
            raise ErrorCita("Esta cita ya no se encuentra activa para ser cancelada.")

        es_paciente = (actor == self.paciente)
        minimo = CentroTerapeutico.obtener().horas_minimas_cancelacion

        if es_paciente and revisar_24_horas and self.horas_que_faltan() < minimo:
            raise ErrorCita(
                f"Las cancelaciones deben realizarse con al menos {minimo} horas de anticipación. "
                "Para situaciones de fuerza mayor, por favor contacta a tu especialista."
            )

        self.estado = self.CANCELADA
        self.motivo_respuesta = motivo
        self._liberar_bloque()
        self._guardar_y_notificar("cancelada", actor)

    def reagendar(self, especialista, nuevo_bloque_id):
        if not self.esta_activa():
            raise ErrorCita("Solo se pueden reagendar citas que se encuentren activas.")

        with transaction.atomic():
            filas_actualizadas = BloqueHorario.objects.filter(
                id=nuevo_bloque_id,
                especialista=especialista,
                disponible=True,
                inicio__gt=timezone.now(),
            ).update(disponible=False)

            if filas_actualizadas == 0:
                raise ErrorCita("El nuevo horario seleccionado ya no está disponible.")

            self._liberar_bloque()
            self.bloque = BloqueHorario.objects.get(id=nuevo_bloque_id)
            self.save()

        cita_cambiada.send(sender=Cita, cita=self, accion="reagendada", actor=especialista)

    def marcar_realizada(self, especialista):
        self.estado = self.REALIZADA
        self.save()
        cita_cambiada.send(sender=Cita, cita=self, accion="realizada", actor=especialista)
