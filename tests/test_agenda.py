"""
Pruebas de la agenda clínica: Concurrencia atómica, regla de 24 horas y reagendación.
"""
from datetime import timedelta
from django.test import TestCase
from django.utils import timezone

from agenda.models import BloqueHorario, CentroTerapeutico, Cita, ErrorCita
from usuarios.models import Usuario


class AgendaTest(TestCase):
    def setUp(self):
        CentroTerapeutico.obtener()
        self.paciente = Usuario.objects.create_user(
            username="paciente_ag",
            email="pac_ag@correo.cl",
            password="password123",
            rol=Usuario.PACIENTE,
            rut="12345678-5"
        )
        self.especialista = Usuario.objects.create_user(
            username="esp_ag",
            email="esp_ag@somossensoriales.cl",
            password="password123",
            rol=Usuario.ESPECIALISTA,
            rut="11222333-4"
        )
        self.bloque = BloqueHorario.objects.create(
            especialista=self.especialista,
            inicio=timezone.now() + timedelta(days=3),
            fin=timezone.now() + timedelta(days=3, minutes=45),
            disponible=True
        )

    def test_solicitar_cita_marca_bloque_no_disponible(self):
        """Concurrencia atómica: La reserva del bloque lo inhabilita para otros."""
        cita = Cita.solicitar(self.paciente, self.bloque.id, "Evaluación Sensorial", "Sensibilidad acústica")
        self.assertEqual(cita.estado, Cita.SOLICITADA)
        self.bloque.refresh_from_db()
        self.assertFalse(self.bloque.disponible)

    def test_doble_reserva_falla(self):
        """Previene double-booking cuando el bloque ya no está libre."""
        Cita.solicitar(self.paciente, self.bloque.id, "Primera reserva")
        otro_paciente = Usuario.objects.create_user(
            username="otro_pac", email="otro@correo.cl", password="password123",
            rol=Usuario.PACIENTE, rut="19999888-7"
        )
        with self.assertRaises(ErrorCita):
            Cita.solicitar(otro_paciente, self.bloque.id, "Intento de segunda reserva")

    def test_regla_24_horas_cancelacion_paciente(self):
        """El paciente solo puede cancelar si restan 24 horas o más."""
        # Cita a 48 horas (válida para cancelar)
        cita_lejana = Cita.solicitar(self.paciente, self.bloque.id, "Motivo")
        cita_lejana.cancelar(self.paciente, "Motivo razonable")
        self.assertEqual(cita_lejana.estado, Cita.CANCELADA)
        self.bloque.refresh_from_db()
        self.assertTrue(self.bloque.disponible)

        # Cita a 2 horas (debe fallar la cancelación)
        bloque_cercano = BloqueHorario.objects.create(
            especialista=self.especialista,
            inicio=timezone.now() + timedelta(hours=2),
            fin=timezone.now() + timedelta(hours=2, minutes=45),
            disponible=True
        )
        cita_cercana = Cita.solicitar(self.paciente, bloque_cercano.id, "Urgente")
        with self.assertRaises(ErrorCita):
            cita_cercana.cancelar(self.paciente, "Cancelación tardía")

    def test_reagendar_libera_bloque_antiguo_y_toma_nuevo(self):
        cita = Cita.solicitar(self.paciente, self.bloque.id, "Reagendar")
        nuevo_bloque = BloqueHorario.objects.create(
            especialista=self.especialista,
            inicio=timezone.now() + timedelta(days=5),
            fin=timezone.now() + timedelta(days=5, minutes=45),
            disponible=True
        )
        cita.reagendar(self.especialista, nuevo_bloque.id)
        self.bloque.refresh_from_db()
        nuevo_bloque.refresh_from_db()
        self.assertTrue(self.bloque.disponible)
        self.assertFalse(nuevo_bloque.disponible)
        self.assertEqual(cita.bloque, nuevo_bloque)
