"""
Script de verificación funcional completa para la Versión Definitiva.
Prueba todas las vistas, respuestas HTTP y lógica de negocio en el servidor real/cliente.
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.test import Client
from django.urls import reverse
from usuarios.models import Usuario

def test_endpoints():
    c = Client()
    print("Iniciando verificación funcional de endpoints...")

    # 1. Health check
    resp = c.get(reverse("salud"))
    assert resp.status_code == 200, f"Error en salud: {resp.status_code}"
    print("[OK] Endpoint de salud (/salud/) OK (200)")

    # 2. Login page
    resp = c.get(reverse("usuarios:login"))
    assert resp.status_code == 200, f"Error en login: {resp.status_code}"
    print("[OK] Pagina de Login (/cuentas/login/) OK (200)")

    # 3. Demo Paciente Shortcut
    resp = c.get(reverse("usuarios:demo_paciente"), follow=True)
    assert resp.status_code == 200
    assert "Camila" in resp.content.decode("utf-8")
    print("[OK] Atajo Demo Paciente y Dashboard de Paciente OK (200)")

    # 4. Vistas del Paciente
    rutas_paciente = [
        reverse("agenda:especialistas"),
        reverse("agenda:mis_citas"),
        reverse("clinica:ficha_paciente"),
        reverse("notificaciones:lista"),
        reverse("usuarios:mi_cuenta"),
    ]
    for r in rutas_paciente:
        resp = c.get(r)
        assert resp.status_code == 200, f"Fallo en ruta {r}: {resp.status_code}"
        print(f"[OK] Ruta paciente '{r}' OK (200)")

    # 5. Desbloqueo de Ficha con PIN 1234
    resp = c.post(reverse("clinica:ficha_paciente"), {"accion": "desbloquear", "pin": "1234"}, follow=True)
    assert resp.status_code == 200
    assert "TEA Nivel 1" in resp.content.decode("utf-8")
    print("[OK] Desbloqueo de Ficha Clinica Sensorial con PIN OK (200)")

    # 6. Logout
    c.post(reverse("usuarios:logout"))

    # 7. Demo Especialista Shortcut
    resp = c.get(reverse("usuarios:demo_especialista"), follow=True)
    assert resp.status_code == 200
    assert "Andrea Soto" in resp.content.decode("utf-8")
    print("[OK] Atajo Demo Especialista y Agenda Terapeutica OK (200)")

    # 8. Vistas del Especialista
    rutas_especialista = [
        reverse("agenda:mi_agenda"),
        reverse("agenda:disponibilidad"),
        reverse("clinica:diagnosticos_especialista"),
        reverse("clinica:subir_diagnostico"),
        reverse("clinica:historial_clinico"),
        reverse("clinica:contacto"),
        reverse("notificaciones:lista"),
        reverse("usuarios:mi_cuenta"),
    ]
    for r in rutas_especialista:
        resp = c.get(r)
        assert resp.status_code == 200, f"Fallo en ruta especialista {r}: {resp.status_code}"
        print(f"[OK] Ruta especialista '{r}' OK (200)")

    print("\n" + "="*60)
    print("TODAS LAS PRUEBAS FUNCIONALES PASARON CON EXITO (100% OPERATIVO)!")
    print("="*60)

if __name__ == "__main__":
    test_endpoints()
