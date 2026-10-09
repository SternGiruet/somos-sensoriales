"""
Pruebas del módulo clínico: Diagnósticos, Ficha protegida con PIN y solicitudes.
"""
from django.test import TestCase
from django.urls import reverse

from clinica.models import Diagnostico, SolicitudContacto
from usuarios.models import Usuario


class ClinicaTest(TestCase):
    def setUp(self):
        self.paciente = Usuario.objects.create_user(
            username="paciente_cl",
            email="pac_cl@correo.cl",
            password="password123",
            rol=Usuario.PACIENTE,
            rut="12345678-5",
            pin_seguridad="4321"
        )
        self.especialista = Usuario.objects.create_user(
            username="esp_cl",
            email="esp_cl@somossensoriales.cl",
            password="password123",
            rol=Usuario.ESPECIALISTA,
            rut="11222333-4",
            especialidad="Terapia Ocupacional"
        )

    def test_ficha_protegida_con_pin(self):
        """La ficha no muestra diagnósticos hasta que se desbloquea con el PIN correcto."""
        Diagnostico.objects.create(
            paciente=self.paciente,
            especialista=self.especialista,
            tipo="TEA Nivel 1",
            titulo="Informe TEA 2026",
            observaciones="Perfil de integración sensorial",
            visible_para_paciente=True
        )

        self.client.force_login(self.paciente)
        resp1 = self.client.get(reverse("clinica:ficha_paciente"))
        self.assertContains(resp1, "Acceso Protegido por PIN")
        self.assertNotContains(resp1, "Informe TEA 2026")

        # Desbloqueo con PIN erróneo
        resp_err = self.client.post(reverse("clinica:ficha_paciente"), {"accion": "desbloquear", "pin": "9999"})
        self.assertContains(resp_err, "PIN incorrecto")

        # Desbloqueo con PIN correcto
        resp_ok = self.client.post(reverse("clinica:ficha_paciente"), {"accion": "desbloquear", "pin": "4321"}, follow=True)
        self.assertContains(resp_ok, "Informe TEA 2026")
        self.assertContains(resp_ok, "Ficha Desbloqueada")

    def test_crear_diagnostico_especialista(self):
        self.client.force_login(self.especialista)
        diag = Diagnostico.objects.create(
            paciente=self.paciente,
            especialista=self.especialista,
            tipo="Sensibilidad Auditiva",
            titulo="Evaluación Acústica",
            observaciones="Sensibilidad a decibeles altos"
        )
        self.assertEqual(Diagnostico.objects.filter(paciente=self.paciente).count(), 1)
        self.assertEqual(diag.especialista, self.especialista)

    def test_solicitud_contacto_administracion(self):
        self.client.force_login(self.especialista)
        sol = SolicitudContacto.objects.create(
            especialista=self.especialista,
            tipo="VACACIONES",
            asunto="Permiso capacitación",
            mensaje="Asistencia a seminario TEA"
        )
        self.assertEqual(SolicitudContacto.objects.count(), 1)
        self.assertFalse(sol.atendido)
