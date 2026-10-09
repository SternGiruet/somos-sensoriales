# Gestión Sensorial — Versión Definitiva
> **"Recordando mi espectro"** · Plataforma Web Clínica y de Integración Sensorial

---

## 🎯 Descripción del Proyecto
Esta es la **versión definitiva y unificada** del proyecto **Gestión Sensorial**, resultado de fusionar e integrar armónicamente las fortalezas de las dos versiones preexistentes:

1. **La solidez arquitectónica, de seguridad y patrones de software de `somos-sensoriales`:**
   - **Patrón Singleton:** Modelo `CentroTerapeutico` centralizado para parámetros clínicos (bloques de 45 min, 24 hrs de cancelación).
   - **Patrón Observer:** Señal Django `cita_cambiada` con observadores automáticos para notificaciones y registro inmutable de auditoría.
   - **Patrón Factory:** Módulo `crear_aviso(canal)` para despacho multicanal (`AvisoApp`, `AvisoCorreo`, ampliable a WhatsApp/SMS).
   - **Control de Concurrencia Atómica:** Bloqueo y actualización atómica en base de datos (`transaction.atomic()` + `update(disponible=False)`) que previene doble reserva simultánea (*double-booking*).
   - **Seguridad Normativa y Ciberseguridad:** Protección contra ataques de fuerza bruta en login (5 intentos en 15 min), auditoría inmutable de accesos según Ley 21.459, y cumplimiento del derecho de supresión de datos personales (Ley 21.719).

2. **La riqueza clínica, UI responsiva y experiencia de usuario de los Mockups y `GestionSensorial`:**
   - **Ficha Médica Sensorial Protegida por PIN:** Acceso confidencial de 4 dígitos (predeterminado `1234`) para resguardar diagnósticos y antecedentes médicos.
   - **Gestión de Diagnósticos con PDF:** Emisión, visualización y descarga de informes diagnósticos (TEA Nivel 1, Sensibilidad Auditiva, Evaluaciones Conductuales, TDAH, Fonoaudiología) asociados a documentos PDF reales.
   - **Perfil Sensorial en Reservas:** Campo especializado para notas de hipersensibilidad (auditiva, táctil), requerimientos de luz y límites de tiempo en cada cita.
   - **Interfaz Gráfica Responsiva Completa:** Barra lateral (*sidebar*) contextual según rol, topbar con atajos demo, tarjeta destacada *"Próxima Cita"* (con alarma e indicador de urgencia), *action tiles* interactivos y modales Bootstrap 5 para cancelación y reagendación.
   - **Canal de Contacto con Administración:** Comunicación directa para solicitudes de permisos, ajustes de agenda o incidencias clínicas.

---

## 🏛️ Estructura del Proyecto

```text
GestionSensorial_Definitivo/
├── config/                  # Configuración central del proyecto (settings, urls, wsgi)
├── usuarios/                # Modelo Usuario unificado (AbstractUser), roles, auditoría y seguridad
├── agenda/                  # CentroTerapeutico (Singleton), BloqueHorario, Cita y control atómico
├── clinica/                 # Diagnostico con PDF, Ficha protegida con PIN y solicitudes administrativas
├── notificaciones/          # Patrón Factory (avisos) y Observer (receptores de señal)
├── templates/               # Plantillas HTML5 responsivas con Bootstrap 5 y Tabler Icons
│   ├── base.html            # Layout maestro con sidebar y topbar
│   ├── base_auth.html       # Layout de autenticación con identidad visual
│   ├── usuarios/            # Login, registro y mi cuenta (supresión Ley 21.719)
│   ├── agenda/              # Dashboard paciente, directorio especialistas, horarios, mis citas, mi agenda
│   ├── clinica/             # Ficha con PIN gate, listado de pacientes, subida de diagnóstico, historial
│   └── notificaciones/      # Buzón de avisos
├── static/                  # CSS personalizado, Bootstrap local, iconos y assets gráficos
├── media/                   # Informes diagnósticos y archivos PDF
├── tests/                   # Suite automatizada de pruebas unitarias y de integración
├── docs/                    # Diagramas de arquitectura UML, casos de uso y estados
├── manage.py                # CLI de Django
├── cargar_demo.py           # Script para poblar la base de datos con casos de prueba
└── requirements.txt         # Dependencias del proyecto
```

---

## 🚀 Puesta en Marcha Rápida

### 1. Requisitos Previos
- Python 3.10+ (probado con Python 3.14 y Django 6.1 / 5.2).

### 2. Instalación de Dependencias
```bash
pip install -r requirements.txt
```

### 3. Migraciones y Base de Datos
```bash
python manage.py makemigrations usuarios agenda clinica notificaciones
python manage.py migrate
```

### 4. Cargar Datos de Demostración
```bash
python cargar_demo.py
```

### 5. Iniciar el Servidor de Desarrollo
```bash
python manage.py runserver
```
Accede en tu navegador a: **`http://127.0.0.1:8000/`**

---

## 🔑 Credenciales de Acceso Demo

| Rol | Correo / Usuario | Contraseña | PIN Ficha |
| :--- | :--- | :--- | :--- |
| **Paciente** | `camila.rojas@correo.cl` (*o `camila_rojas`*) | `password123` | `1234` |
| **Especialista** | `andrea.soto@somossensoriales.cl` (*o `andrea_soto`*) | `password123` | N/A |
| **Administrador** | `admin` | `admin123` | N/A |

> 💡 *En el encabezado superior de la plataforma tienes un menú desplegable de **"Atajos Demo"** para iniciar sesión instantáneamente con un solo clic.*

---

## 🧪 Ejecución de Pruebas Automatizadas

El proyecto incluye 14 pruebas que cubren concurrencia, patrones de diseño, seguridad y funcionalidades clínicas:

```bash
# Ejecutar todas las pruebas unitarias:
python manage.py test tests

# Ejecutar verificación funcional exhaustiva de rutas HTTP:
python tests/verificar_todo.py
```

---

## 📤 Instrucciones para Git Push

Para inicializar y subir este proyecto definitivo a tu repositorio:

```bash
cd C:\Users\Esteban\Downloads\GestionSensorial_Definitivo
git init
git add .
git commit -m "feat: Version definitiva unificada de Gestion Sensorial"
git branch -M main
git remote add origin <URL_DE_TU_REPOSITORIO_GITHUB>
git push -u origin main
```
