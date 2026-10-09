"""
Pruebas de los patrones de diseño GoF: Singleton, Factory y Observer.
"""
from datetime import timedelta
from django.core import mail
from django.test import TestCase
from django.utils import timezone

from agenda.models import BloqueHorario, CentroTerapeutico, Cita
from notificaciones.avisos import AvisoApp, AvisoCorreo, crear_aviso
from notificaciones.models import Notificacion
from usuarios.models import RegistroAuditoria, Usuario


class PatronesTest(TestCase):
    def setUp(self):
        self.centro = CentroTerapeutico.obtener()
        self.paciente = Usuario.objects.create_user(
            username="paciente_test",
            email="paciente@test.cl",
            password="password123",
            rol=Usuario.PACIENTE,
            rut="12345678-5",
            first_name="Paciente",
            last_name="Test"
        )
        self.especialista = Usuario.objects.create_user(
            username="esp_test",
            email="esp@test.cl",
            password="password123",
            rol=Usuario.ESPECIALISTA,
            rut="11222333-4",
            first_name="Dra.",
            last_name="Especialista",
            especialidad="Terapia Ocupacional"
        )
        self.bloque = BloqueHorario.objects.create(
            especialista=self.especialista,
            inicio=timezone.now() + timedelta(days=2),
            fin=timezone.now() + timedelta(days=2, minutes=45),
            disponible=True
        )

    def test_singleton_centro_terapeutico(self):
        """Patrón Singleton: Siempre existe una sola instancia con id=1."""
        primero = CentroTerapeutico.obtener()
        segundo = CentroTerapeutico(nombre="Otro Centro Terapéutico")
        segundo.save()
        self.assertEqual(CentroTerapeutico.objects.count(), 1)
        self.assertEqual(CentroTerapeutico.obtener().pk, 1)

    def test_factory_crear_aviso(self):
        """Patrón Factory: Fabrica la clase correcta según el canal."""
        self.assertIsInstance(crear_aviso("app"), AvisoApp)
        self.assertIsInstance(crear_aviso("correo"), AvisoCorreo)
        with self.assertRaises(ValueError):
            crear_aviso("canal_inexistente")

    def test_observer_notificaciones_y_auditoria(self):
        """
        Patrón Observer: Al cambiar una cita, la señal 'cita_cambiada'
        despacha notificaciones y crea un registro inmutable de auditoría.
        """
        cita = Cita.solicitar(
            paciente=self.paciente,
            bloque_id=self.bloque.id,
            motivo="Integración Sensorial",
            mensaje_sensorial="Sensibilidad auditiva moderada"
        )

        # 1. El especialista debe recibir notificación en la app
        self.assertTrue(Notificacion.objects.filter(usuario=self.especialista).exists())

        # 2. Debe generarse registro de auditoría
        self.assertTrue(RegistroAuditoria.objects.filter(accion="CITA_SOLICITADA").exists())

        # 3. Confirmar la cita notifica al paciente
        cita.confirmar(self.especialista)
        aviso_paciente = Notificacion.objects.filter(usuario=self.paciente).first()
        self.assertIsNotNone(aviso_paciente)
        self.assertIn("confirmada", aviso_paciente.mensaje)
        self.assertTrue(RegistroAuditoria.objects.filter(accion="CITA_CONFIRMADA").exists())
