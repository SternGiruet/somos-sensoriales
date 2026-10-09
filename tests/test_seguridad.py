"""
Pruebas de seguridad: OWASP Top 10 (A01: Broken Access Control),
cumplimiento de Ley 21.459 (auditoría) y Ley 21.719 (derecho de supresión).
"""
from django.test import TestCase
from django.urls import reverse
from usuarios.models import RegistroAuditoria, Usuario


class SeguridadTest(TestCase):
    def setUp(self):
        self.paciente = Usuario.objects.create_user(
            username="paciente_seg",
            email="paciente_seg@correo.cl",
            password="password123",
            rol=Usuario.PACIENTE,
            rut="12345678-5",
            pin_seguridad="1234"
        )
        self.especialista = Usuario.objects.create_user(
            username="esp_seg",
            email="esp_seg@somossensoriales.cl",
            password="password123",
            rol=Usuario.ESPECIALISTA,
            rut="11222333-4",
            especialidad="Neurología"
        )

    def test_paciente_no_accede_a_panel_especialista(self):
        """OWASP A01: Un paciente no puede acceder a las vistas del especialista (403 auditado)."""
        self.client.force_login(self.paciente)
        resp = self.client.get(reverse("agenda:mi_agenda"))
        self.assertEqual(resp.status_code, 403)
        self.assertTrue(RegistroAuditoria.objects.filter(accion="ACCESO_DENEGADO").exists())

    def test_especialista_no_accede_a_dashboard_paciente(self):
        """Un especialista no puede acceder a vistas exclusivas del paciente."""
        self.client.force_login(self.especialista)
        resp = self.client.get(reverse("agenda:dashboard_paciente"))
        self.assertEqual(resp.status_code, 403)

    def test_sin_sesion_redirige_a_login(self):
        resp = self.client.get(reverse("agenda:mis_citas"))
        self.assertRedirects(resp, reverse("usuarios:login") + "?next=/agenda/mis-citas/")

    def test_derecho_supresion_datos_personales(self):
        """Cumplimiento Ley 21.719: Derecho a supresión y anonimización."""
        self.client.force_login(self.paciente)
        resp = self.client.post(reverse("usuarios:eliminar_cuenta"), {"confirmacion": "ELIMINAR"})
        self.assertRedirects(resp, reverse("usuarios:login"))

        self.paciente.refresh_from_db()
        self.assertFalse(self.paciente.is_active)
        self.assertEqual(self.paciente.first_name, "Usuario")
        self.assertEqual(self.paciente.last_name, "eliminado")
        self.assertTrue(RegistroAuditoria.objects.filter(accion="DATOS_ELIMINADOS").exists())
