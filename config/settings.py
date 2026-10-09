"""
Configuración unificada del proyecto Gestión Sensorial ("Aquí Somos Sensoriales").

Combina la arquitectura de backend robusta de 'somos-sensoriales' (Singleton,
Observer con señales, Factory, auditoría inmutable, protección contra fuerza bruta)
con la riqueza clínica y frontend de 'GestionSensorial' (Ficha clínica con PIN de 4 dígitos,
diagnósticos sensoriales con PDFs, interfaz responsiva tipo dashboard con sidebar y tiles).
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------------------------------------------------------------
# Entorno
# --------------------------------------------------------------------------
PRODUCCION = os.environ.get("PRODUCCION") == "True" or os.environ.get("RENDER") == "true"
DEBUG = not PRODUCCION

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-gs-definitivo-2026-super-secret-key-prod-dev")

ALLOWED_HOSTS = ["*"]

# --------------------------------------------------------------------------
# Aplicaciones instaladas
# --------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Módulos del Sistema
    "usuarios.apps.UsuariosConfig",
    "agenda.apps.AgendaConfig",
    "clinica.apps.ClinicaConfig",
    "notificaciones.apps.NotificacionesConfig",
]

# --------------------------------------------------------------------------
# Middleware
# --------------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "usuarios.context_processors.sensorial_context",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# --------------------------------------------------------------------------
# Base de datos: SQLite por defecto, o PostgreSQL si DATABASE_URL está definida
# --------------------------------------------------------------------------
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL:
    try:
        import dj_database_url
        DATABASES = {
            "default": dj_database_url.config(default=DATABASE_URL, conn_max_age=600)
        }
    except ImportError:
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": BASE_DIR / "db.sqlite3",
            }
        }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# --------------------------------------------------------------------------
# Modelo de Usuario personalizado
# --------------------------------------------------------------------------
AUTH_USER_MODEL = "usuarios.Usuario"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 6}},
]

LOGIN_URL = "usuarios:login"
LOGIN_REDIRECT_URL = "inicio"
LOGOUT_REDIRECT_URL = "usuarios:login"

# Sesión segura (expiración tras 30 min sin actividad)
SESSION_COOKIE_AGE = 30 * 60
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

CSRF_COOKIE_HTTPONLY = True

# --------------------------------------------------------------------------
# Internacionalización y Localización
# --------------------------------------------------------------------------
LANGUAGE_CODE = "es-cl"
TIME_ZONE = "America/Santiago"
USE_I18N = True
USE_TZ = True

# --------------------------------------------------------------------------
# Archivos Estáticos y Media
# --------------------------------------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Correo (consola para desarrollo y auditoría)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "no-responder@somossensoriales.cl"
