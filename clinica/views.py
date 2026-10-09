"""Vistas clínicas: Ficha Médica Sensorial protegida con PIN, Diagnósticos PDF y Contacto."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from agenda.models import Cita
from usuarios.models import Usuario
from usuarios.permisos import verificar_rol

from .forms import DiagnosticoForm, SolicitudContactoForm
from .models import Diagnostico, SolicitudContacto


@login_required
def ficha_paciente(request):
    """
    Ficha de Salud Sensorial protegida con PIN de 4 dígitos (conforme al Mockup de Claude).
    Exige ingresar el PIN de 4 dígitos antes de revelar diagnósticos o datos confidenciales.
    """
    verificar_rol(request.user, Usuario.PACIENTE)
    usuario = request.user
    pin_error = False

    if request.method == "POST":
        accion = request.POST.get("accion")
        if accion == "bloquear":
            request.session["ficha_desbloqueada"] = False
            messages.info(request, "La ficha médica confidencial ha sido bloqueada.")
            return redirect("clinica:ficha_paciente")
        elif accion == "desbloquear":
            pin_ingresado = request.POST.get("pin", "").strip()
            # Valida contra el PIN del usuario o PIN maestro demo '1234'
            if pin_ingresado == usuario.pin_seguridad or pin_ingresado == "1234":
                request.session["ficha_desbloqueada"] = True
                messages.success(request, "Acceso concedido a la Ficha Clínica Sensorial.")
                return redirect("clinica:ficha_paciente")
            else:
                pin_error = True

    ficha_desbloqueada = request.session.get("ficha_desbloqueada", False)
    diagnosticos = []
    if ficha_desbloqueada:
        diagnosticos = Diagnostico.objects.filter(
            paciente=usuario, visible_para_paciente=True
        ).order_by("-fecha_emision")

    return render(request, "clinica/ficha_paciente.html", {
        "usuario": usuario,
        "ficha_desbloqueada": ficha_desbloqueada,
        "pin_error": pin_error,
        "diagnosticos": diagnosticos,
    })


@login_required
def diagnosticos_especialista(request):
    """Buscador y directorio de pacientes para consultar antecedentes o emitir diagnósticos."""
    verificar_rol(request.user, Usuario.ESPECIALISTA)

    query = request.GET.get("q", "").strip()
    pacientes = Usuario.objects.filter(rol=Usuario.PACIENTE, is_active=True)

    if query:
        pacientes = pacientes.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(rut__icontains=query)
        )

    pacientes = pacientes.order_by("first_name")

    return render(request, "clinica/diagnosticos_especialista.html", {
        "pacientes": pacientes,
        "query": query,
    })


@login_required
def subir_diagnostico(request, paciente_id=None):
    """Emisión y carga de informe diagnóstico sensorial con archivo PDF."""
    verificar_rol(request.user, Usuario.ESPECIALISTA)

    paciente_pre = None
    if paciente_id:
        paciente_pre = get_object_or_404(Usuario, id=paciente_id, rol=Usuario.PACIENTE)

    cita_id = request.GET.get("cita_id")
    cita_rel = None
    if cita_id:
        cita_rel = Cita.objects.filter(
            id=cita_id, bloque__especialista=request.user
        ).first()
        if cita_rel and not paciente_pre:
            paciente_pre = cita_rel.paciente

    if request.method == "POST":
        form = DiagnosticoForm(request.POST, request.FILES)
        if form.is_valid():
            diag = form.save(commit=False)
            diag.especialista = request.user
            if cita_rel:
                diag.cita = cita_rel

            # Si el especialista no adjuntó un archivo PDF, asociamos el PDF modelo de prueba
            if not diag.archivo_pdf:
                diag.archivo_pdf = "diagnosticos/ArchivoDePrueba.pdf"

            diag.save()

            if form.cleaned_data.get("marcar_realizada") and cita_rel:
                cita_rel.marcar_realizada(request.user)

            messages.success(request, f"¡Diagnóstico '{diag.titulo}' guardado exitosamente para {diag.paciente.get_full_name()}!")
            return redirect("clinica:diagnosticos_especialista")
    else:
        initial_data = {}
        if paciente_pre:
            initial_data["paciente"] = paciente_pre
        form = DiagnosticoForm(initial=initial_data)

    return render(request, "clinica/subir_diagnostico.html", {
        "form": form,
        "paciente_pre": paciente_pre,
        "cita_rel": cita_rel,
    })


@login_required
def historial_clinico(request):
    """Historial de sesiones y diagnósticos emitidos con filtros por categoría."""
    verificar_rol(request.user, Usuario.ESPECIALISTA)

    filtro_tipo = request.GET.get("tipo", "TODOS")
    diagnosticos = Diagnostico.objects.filter(especialista=request.user).order_by("-fecha_emision")

    if filtro_tipo != "TODOS":
        diagnosticos = diagnosticos.filter(tipo__icontains=filtro_tipo)

    citas_historicas = Cita.objects.filter(
        bloque__especialista=request.user
    ).order_by("-bloque__inicio")[:25]

    return render(request, "clinica/historial_clinico.html", {
        "diagnosticos": diagnosticos,
        "citas_historicas": citas_historicas,
        "filtro_tipo": filtro_tipo,
    })


@login_required
def contacto_especialista(request):
    """Canal de comunicación entre terapeutas y la administración."""
    verificar_rol(request.user, Usuario.ESPECIALISTA)

    if request.method == "POST":
        form = SolicitudContactoForm(request.POST)
        if form.is_valid():
            sol = form.save(commit=False)
            sol.especialista = request.user
            sol.save()
            messages.success(request, "Tu solicitud ha sido transmitida a la dirección administrativa del centro.")
            return redirect("clinica:contacto")
    else:
        form = SolicitudContactoForm()

    solicitudes = SolicitudContacto.objects.filter(especialista=request.user).order_by("-fecha_solicitud")

    return render(request, "clinica/contacto.html", {
        "form": form,
        "solicitudes": solicitudes,
    })
