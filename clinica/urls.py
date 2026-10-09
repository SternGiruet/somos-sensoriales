from django.urls import path
from . import views

app_name = "clinica"

urlpatterns = [
    # Ficha del paciente protegida con PIN
    path("ficha/", views.ficha_paciente, name="ficha_paciente"),
    # Diagnósticos y atenciones para especialistas
    path("diagnosticos/", views.diagnosticos_especialista, name="diagnosticos_especialista"),
    path("diagnosticos/subir/", views.subir_diagnostico, name="subir_diagnostico"),
    path("diagnosticos/subir/<int:paciente_id>/", views.subir_diagnostico, name="subir_diagnostico_paciente"),
    path("historial/", views.historial_clinico, name="historial_clinico"),
    # Contacto institucional
    path("contacto/", views.contacto_especialista, name="contacto"),
]
