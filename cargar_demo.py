"""
Script de población de datos de prueba para la Versión Definitiva de Gestión Sensorial.
Ejecuta: python cargar_demo.py
"""
import os
import django
from datetime import timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.utils import timezone
from usuarios.models import Usuario
from agenda.models import CentroTerapeutico, BloqueHorario, Cita
from clinica.models import Diagnostico, SolicitudContacto
from notificaciones.models import Notificacion


def run():
    print("Iniciando carga de datos demo para la Versión Definitiva de Gestión Sensorial...")

    # 1. Configuración Centralizada (Singleton)
    centro = CentroTerapeutico.obtener()
    centro.nombre = "Aquí Somos Sensoriales"
    centro.duracion_bloque = 45
    centro.horas_minimas_cancelacion = 24
    centro.save()
    print(f"[OK] CentroTerapeutico configurado: '{centro.nombre}' (Bloques: {centro.duracion_bloque} min, Cancelacion: {centro.horas_minimas_cancelacion} hrs).")

    # 2. Superusuario Administrador
    if not Usuario.objects.filter(username="admin").exists():
        admin_u = Usuario.objects.create_superuser(
            username="admin",
            email="admin@somossensoriales.cl",
            password="admin123",
            first_name="Administrador",
            last_name="General",
            rol=Usuario.ADMINISTRADOR,
            rut="11111111-1",
            color_avatar="#0d3f7a",
            iniciales="AD"
        )
        print("[OK] Administrador 'admin' (clave: admin123) creado.")

    # 3. Especialistas Clínicos
    especialistas_data = [
        {
            "username": "andrea_soto",
            "email": "andrea.soto@somossensoriales.cl",
            "first_name": "Andrea",
            "last_name": "Soto",
            "prefijo": "Dra.",
            "especialidad": "Terapia Ocupacional",
            "biografia": "Especialista en integración sensorial y desarrollo funcional en niños y adultos con TEA. 12 años de experiencia clínica.",
            "telefono": "+56 9 1234 5678",
            "rut": "15345678-9",
            "iniciales": "AS",
            "color": "#d6e8f8",
        },
        {
            "username": "tomas_vega",
            "email": "tomas.vega@somossensoriales.cl",
            "first_name": "Tomás",
            "last_name": "Vega",
            "prefijo": "Dr.",
            "especialidad": "Neurología Pediátrica",
            "biografia": "Neurólogo con foco en trastornos del neurodesarrollo. Diagnóstico y seguimiento de TEA, TDAH y epilepsia infantil.",
            "telefono": "+56 9 8765 4321",
            "rut": "14987654-3",
            "iniciales": "TV",
            "color": "#e8f0fb",
        },
        {
            "username": "valeria_munoz",
            "email": "valeria.munoz@somossensoriales.cl",
            "first_name": "Valeria",
            "last_name": "Muñoz",
            "prefijo": "Ps.",
            "especialidad": "Psicología Clínica",
            "biografia": "Psicóloga infantojuvenil con enfoque cognitivo-conductual. Intervención en ansiedad, conducta y habilidades sociales.",
            "telefono": "+56 9 5555 1122",
            "rut": "16789123-4",
            "iniciales": "VM",
            "color": "#f0e8fb",
        },
        {
            "username": "javiera_lagos",
            "email": "javiera.lagos@somossensoriales.cl",
            "first_name": "Javiera",
            "last_name": "Lagos",
            "prefijo": "Flga.",
            "especialidad": "Fonoaudiología",
            "biografia": "Especializada en comunicación aumentativa y alternativa (CAA) para personas con TEA no verbal y baja comunicación.",
            "telefono": "+56 9 3344 5566",
            "rut": "17456789-0",
            "iniciales": "JL",
            "color": "#e8fbf0",
        },
    ]

    especialistas = {}
    for data in especialistas_data:
        u, creado = Usuario.objects.get_or_create(
            username=data["username"],
            defaults={
                "email": data["email"],
                "first_name": data["first_name"],
                "last_name": data["last_name"],
                "rol": Usuario.ESPECIALISTA,
                "prefijo": data["prefijo"],
                "especialidad": data["especialidad"],
                "biografia": data["biografia"],
                "telefono": data["telefono"],
                "rut": data["rut"],
                "color_avatar": data["color"],
                "iniciales": data["iniciales"],
                "dias_atencion": "Lunes a Viernes (09:00 - 18:00)",
                "registro_minsal": "REG-83921",
            }
        )
        if creado:
            u.set_password("password123")
            u.save()
        especialistas[data["username"]] = u
        print(f"[OK] Especialista '{u.nombre_completo_con_titulo}' verificado.")

    # 4. Pacientes y Tutores
    pacientes_data = [
        {
            "username": "camila_rojas",
            "email": "camila.rojas@correo.cl",
            "first_name": "Camila",
            "last_name": "Rojas Pérez",
            "telefono": "+56 9 9876 5432",
            "rut": "19876543-2",
            "nombre_tutor": "María Pérez",
            "telefono_tutor": "+56 9 1111 2222",
            "direccion": "Av. Providencia 1240, Santiago",
            "edad": 24,
            "pin": "1234",
            "color": "#d6e8f8",
            "iniciales": "CR",
        },
        {
            "username": "martin_perez",
            "email": "martin.perez@correo.cl",
            "first_name": "Martín",
            "last_name": "Pérez Torres",
            "telefono": "+56 9 3344 5566",
            "rut": "21345678-9",
            "nombre_tutor": "Ana Torres",
            "telefono_tutor": "+56 9 3333 4444",
            "direccion": "Los Leones 540, Providencia",
            "edad": 17,
            "pin": "1234",
            "color": "#f0e8fb",
            "iniciales": "MP",
        },
        {
            "username": "valentina_ortiz",
            "email": "valentina.ortiz@correo.cl",
            "first_name": "Valentina",
            "last_name": "Ortiz Silva",
            "telefono": "+56 9 7788 9900",
            "rut": "17654321-K",
            "nombre_tutor": "Pedro Ortiz",
            "telefono_tutor": "+56 9 5566 7788",
            "direccion": "Alonso de Córdova 280, Las Condes",
            "edad": 31,
            "pin": "1234",
            "color": "#e8fbf0",
            "iniciales": "VO",
        },
        {
            "username": "lucas_gonzalez",
            "email": "lucas.gonzalez@correo.cl",
            "first_name": "Lucas",
            "last_name": "González Mora",
            "telefono": "+56 9 2233 4455",
            "rut": "23456789-1",
            "nombre_tutor": "Claudia Mora",
            "telefono_tutor": "+56 9 8899 0011",
            "direccion": "Gran Avenida 4320, San Miguel",
            "edad": 9,
            "pin": "1234",
            "color": "#fdf0e0",
            "iniciales": "LG",
        },
    ]

    pacientes = {}
    for data in pacientes_data:
        u, creado = Usuario.objects.get_or_create(
            username=data["username"],
            defaults={
                "email": data["email"],
                "first_name": data["first_name"],
                "last_name": data["last_name"],
                "rol": Usuario.PACIENTE,
                "telefono": data["telefono"],
                "rut": data["rut"],
                "nombre_tutor": data["nombre_tutor"],
                "telefono_tutor": data["telefono_tutor"],
                "direccion": data["direccion"],
                "edad": data["edad"],
                "pin_seguridad": data["pin"],
                "color_avatar": data["color"],
                "iniciales": data["iniciales"],
                "fecha_consentimiento": timezone.now(),
            }
        )
        if creado:
            u.set_password("password123")
            u.save()
        pacientes[data["username"]] = u
        print(f"[OK] Paciente '{u.nombre_completo_con_titulo}' verificado.")

    # 5. Bloques Horarios (de 45 min) para la Dra. Andrea Soto
    dra = especialistas["andrea_soto"]
    ahora = timezone.localtime()
    hoy_base = ahora.replace(hour=9, minute=0, second=0, microsecond=0)

    # Bloques de hoy
    b_hoy1, _ = BloqueHorario.objects.get_or_create(
        especialista=dra,
        inicio=hoy_base + timedelta(hours=1, minutes=30),  # 10:30
        defaults={"fin": hoy_base + timedelta(hours=2, minutes=15), "disponible": False}
    )
    b_hoy2, _ = BloqueHorario.objects.get_or_create(
        especialista=dra,
        inicio=hoy_base + timedelta(hours=3),  # 12:00
        defaults={"fin": hoy_base + timedelta(hours=3, minutes=45), "disponible": False}
    )
    b_hoy3, _ = BloqueHorario.objects.get_or_create(
        especialista=dra,
        inicio=hoy_base + timedelta(hours=6),  # 15:00
        defaults={"fin": hoy_base + timedelta(hours=6, minutes=45), "disponible": True}
    )

    # Bloques de días futuros libres
    for dia in range(1, 4):
        fecha_d = hoy_base + timedelta(days=dia)
        for h in [9, 10, 11, 15, 16]:
            BloqueHorario.objects.get_or_create(
                especialista=dra,
                inicio=fecha_d.replace(hour=h, minute=0),
                defaults={
                    "fin": fecha_d.replace(hour=h, minute=45),
                    "disponible": True,
                }
            )

    # 6. Citas Médicas con perfil sensorial
    # Cita 1: Camila Rojas hoy 10:30 con Dra. Andrea Soto (Confirmada - Alarm Card)
    c1, _ = Cita.objects.get_or_create(
        paciente=pacientes["camila_rojas"],
        bloque=b_hoy1,
        defaults={
            "motivo_consulta": "Terapia Ocupacional - Integracion Sensorial",
            "mensaje_sensorial": "Paciente con diagnostico TEA nivel 1. Presenta sensibilidad auditiva moderada y dificultad en regulacion emocional. Se recomienda ambiente controlado y sesion de max. 45 min.",
            "estado": Cita.CONFIRMADA,
        }
    )

    # Cita 2: Martín Pérez hoy 12:00 (Solicitada)
    c2, _ = Cita.objects.get_or_create(
        paciente=pacientes["martin_perez"],
        bloque=b_hoy2,
        defaults={
            "motivo_consulta": "Evaluacion de respuesta sensorial a estimulos tactiles",
            "mensaje_sensorial": "Adolescente con hipersensibilidad tactil y desregulacion postural.",
            "estado": Cita.SOLICITADA,
        }
    )

    print("[OK] Bloques horarios y Citas de la jornada cargados.")

    # 7. Diagnósticos Sensoriales con PDF
    pdf_path = "diagnosticos/ArchivoDePrueba.pdf"
    diags_seed = [
        {
            "paciente": pacientes["camila_rojas"],
            "especialista": dra,
            "tipo": "TEA Nivel 1",
            "titulo": "TEA Nivel 1 -- Evaluacion Inicial",
            "obs": "Evaluacion multidimensional de procesamiento sensorial. Se evidencia respuesta atipica a frecuencias sonoras intermedias y altas.",
            "fecha": timezone.now().date() - timedelta(days=360),
        },
        {
            "paciente": pacientes["camila_rojas"],
            "especialista": dra,
            "tipo": "Sensibilidad Auditiva",
            "titulo": "Sensibilidad Auditiva Moderada",
            "obs": "Recomendacion de uso de protectores auditivos pasivos en entornos con aglomeraciones y pausas reguladas en aula.",
            "fecha": timezone.now().date() - timedelta(days=180),
        },
        {
            "paciente": pacientes["camila_rojas"],
            "especialista": especialistas["valeria_munoz"],
            "tipo": "Evaluación Conductual",
            "titulo": "Evaluacion Conductual y Regulacion Emocional",
            "obs": "Plan de intervencion con estrategias de autorregulacion y semaforo emocional.",
            "fecha": timezone.now().date() - timedelta(days=60),
        },
        {
            "paciente": pacientes["martin_perez"],
            "especialista": especialistas["tomas_vega"],
            "tipo": "TDAH",
            "titulo": "TDAH Tipo Combinado",
            "obs": "Informe neurologico con indicacion de pausas activas motoras.",
            "fecha": timezone.now().date() - timedelta(days=90),
        },
    ]

    for d in diags_seed:
        Diagnostico.objects.get_or_create(
            paciente=d["paciente"],
            titulo=d["titulo"],
            defaults={
                "especialista": d["especialista"],
                "tipo": d["tipo"],
                "observaciones": d["obs"],
                "archivo_pdf": pdf_path,
                "fecha_emision": d["fecha"],
                "visible_para_paciente": True,
            }
        )

    print("[OK] Diagnosticos clinicos con PDF asociados a la Ficha Sensorial.")

    # 8. Solicitud a Administración
    SolicitudContacto.objects.get_or_create(
        especialista=dra,
        asunto="Solicitud de permisos de capacitacion clinica",
        defaults={
            "tipo": "VACACIONES",
            "mensaje": "Solicito autorizacion para asistir a las Jornadas Internacionales de Integracion Sensorial los dias 14 y 15 del proximo mes.",
            "atendido": True,
        }
    )

    # 9. Notificación de bienvenida
    Notificacion.objects.get_or_create(
        usuario=pacientes["camila_rojas"],
        mensaje="Bienvenida a Gestion Sensorial. Recuerda que tu cita de integracion sensorial esta confirmada.",
    )

    print("\n=======================================================")
    print("Base de datos demo de la Version Definitiva cargada con exito!")
    print("=======================================================")
    print("Credenciales disponibles (clave estandar: password123):")
    print("  - Paciente: camila.rojas@correo.cl | Clave: password123 | PIN Ficha: 1234")
    print("  - Especialista: andrea.soto@somossensoriales.cl | Clave: password123")
    print("  - Administrador: admin | Clave: admin123")
    print("=======================================================")


if __name__ == "__main__":
    run()
