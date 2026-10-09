"""
Patrón Observer (Observador: Auditoría).
Registra en la auditoría inmutable cada cambio en el ciclo de vida de una cita.
"""
from django.dispatch import receiver
from agenda.senales import cita_cambiada
from .models import RegistroAuditoria


@receiver(cita_cambiada)
def auditar_cambio_de_cita(sender, cita, accion, actor, **kwargs):
    RegistroAuditoria.objects.create(
        usuario=actor if actor and getattr(actor, 'is_authenticated', False) else None,
        correo=getattr(actor, 'email', '') if actor else '',
        accion=f"CITA_{accion.upper()}",
        detalle=f"Cita N° {cita.id} con {cita.bloque.especialista.nombre_completo_con_titulo}",
    )
