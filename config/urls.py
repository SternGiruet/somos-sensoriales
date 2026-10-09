"""Rutas principales del sistema unificado Gestión Sensorial."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from agenda import views as agenda_views

urlpatterns = [
    path("", agenda_views.inicio, name="inicio"),
    path("salud/", agenda_views.salud, name="salud"),
    path("admin/", admin.site.urls),
    path("cuentas/", include("usuarios.urls")),
    path("agenda/", include("agenda.urls")),
    path("clinica/", include("clinica.urls")),
    path("avisos/", include("notificaciones.urls")),
]

# Manejador propio de error 403 con auditoría de seguridad
handler403 = "usuarios.views.acceso_denegado"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
