"""
Patrón Observer: Señal publicada cada vez que el estado de una cita médica cambia.
"""
from django.dispatch import Signal

cita_cambiada = Signal()
