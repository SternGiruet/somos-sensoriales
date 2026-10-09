from django.urls import path
from . import views

app_name = "agenda"

urlpatterns = [
    # Navegación y Dashboard
    path("dashboard/", views.dashboard_paciente, name="dashboard_paciente"),
    # Paciente
    path("especialistas/", views.especialistas, name="especialistas"),
    path("especialistas/<int:especialista_id>/", views.horarios, name="horarios"),
    path("mis-citas/", views.mis_citas, name="mis_citas"),
    # Especialista
    path("mi-agenda/", views.mi_agenda, name="mi_agenda"),
    path("disponibilidad/", views.disponibilidad, name="disponibilidad"),
    path("bloques/<int:bloque_id>/eliminar/", views.eliminar_bloque, name="eliminar_bloque"),
    path("citas/<int:cita_id>/confirmar/", views.confirmar, name="confirmar"),
    path("citas/<int:cita_id>/rechazar/", views.rechazar, name="rechazar"),
    path("citas/<int:cita_id>/reagendar/", views.reagendar, name="reagendar"),
    # Común
    path("citas/<int:cita_id>/cancelar/", views.cancelar, name="cancelar"),
]
