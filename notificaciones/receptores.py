"""
Patrón Observer (Observador: Avisos y Notificaciones).
Escucha la señal 'cita_cambiada' y notifica a la otra parte involucrada sin exponer
información sensible de salud en el cuerpo del mensaje (RNF-05).
"""
from django.dispatch import receiver
from django.utils import timezone
from agenda.senales import cita_cambiada
from .avisos import CANALES, crear_aviso


@receiver(cita_cambiada)
def avisar_cambio_de_cita(sender, cita, accion, actor, **kwargs):
    especialista = cita.bloque.especialista
    paciente = cita.paciente

    # Notificar a la contraparte
    if actor == paciente:
        destinatario = especialista
    else:
        destinatario = paciente

    fecha_str = timezone.localtime(cita.bloque.inicio).strftime("%d-%m-%Y a las %H:%M")
    texto = f"La cita médica del {fecha_str} con {especialista.nombre_completo_con_titulo} fue {accion}."

    for canal in CANALES:
        try:
            crear_aviso(canal).enviar(destinatario, texto)
        except Exception:
            pass
