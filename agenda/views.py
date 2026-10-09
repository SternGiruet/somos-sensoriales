"""Vistas y controladores del flujo de agenda, reserva y gestión de citas."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from usuarios.models import Usuario
from usuarios.permisos import verificar_rol

from .forms import BloqueForm, MotivoForm, SolicitudCitaForm
from .models import BloqueHorario, Cita, ErrorCita


@login_required
def inicio(request):
    """Enrutador de inicio según el rol del usuario conectado."""
    if request.user.rol == Usuario.ESPECIALISTA:
        return redirect("agenda:mi_agenda")
    if request.user.rol == Usuario.ADMINISTRADOR or request.user.is_staff:
        return redirect("admin:index")
    return redirect("agenda:dashboard_paciente")


def salud(request):
    """Endpoint de comprobación de salud del servicio (Health Check)."""
    return JsonResponse({"estado": "ok", "app": "Gestion Sensorial Definitivo"})


# ====================================================================
# PACIENTE
# ====================================================================
@login_required
def dashboard_paciente(request):
    """Dashboard principal del paciente con tarjeta de alarma y widgets interactivos."""
    verificar_rol(request.user, Usuario.PACIENTE)

    proxima_cita = Cita.objects.filter(
        paciente=request.user,
        estado__in=[Cita.SOLICITADA, Cita.CONFIRMADA],
        bloque__inicio__gte=timezone.now()
    ).order_by("bloque__inicio").first()

    total_citas = Cita.objects.filter(paciente=request.user).count()

    context = {
        "proxima_cita": proxima_cita,
        "total_citas": total_citas,
    }
    return render(request, "agenda/dashboard_paciente.html", context)


@login_required
def especialistas(request):
    """Directorio de terapeutas y especialistas disponibles."""
    verificar_rol(request.user, Usuario.PACIENTE)
    lista = Usuario.objects.filter(rol=Usuario.ESPECIALISTA, is_active=True).order_by("first_name")
    return render(request, "agenda/especialistas.html", {"especialistas": lista})


@login_required
def horarios(request, especialista_id):
    """Muestra los bloques libres de un especialista y permite reservar ingresando perfil sensorial."""
    verificar_rol(request.user, Usuario.PACIENTE)
    especialista = get_object_or_404(
        Usuario, id=especialista_id, rol=Usuario.ESPECIALISTA, is_active=True
    )

    if request.method == "POST":
        form = SolicitudCitaForm(request.POST)
        if form.is_valid():
            try:
                Cita.solicitar(
                    paciente=request.user,
                    bloque_id=form.cleaned_data["bloque_id"],
                    motivo=form.cleaned_data["motivo"],
                    mensaje_sensorial=form.cleaned_data["mensaje_sensorial"],
                )
                messages.success(request, f"¡Solicitud de cita enviada a {especialista.nombre_completo_con_titulo}! Te notificaremos una vez confirmada.")
                return redirect("agenda:mis_citas")
            except ErrorCita as error:
                messages.error(request, str(error))
    else:
        form = SolicitudCitaForm()

    bloques = BloqueHorario.objects.filter(
        especialista=especialista, disponible=True, inicio__gt=timezone.now()
    ).order_by("inicio")

    return render(
        request,
        "agenda/horarios.html",
        {"especialista": especialista, "bloques": bloques, "form": form},
    )


@login_required
def mis_citas(request):
    """Historial de citas del paciente (próximas y pasadas)."""
    verificar_rol(request.user, Usuario.PACIENTE)

    citas_proximas = Cita.objects.filter(
        paciente=request.user,
        estado__in=[Cita.SOLICITADA, Cita.CONFIRMADA],
        bloque__inicio__gte=timezone.now()
    ).order_by("bloque__inicio")

    citas_pasadas = Cita.objects.filter(
        paciente=request.user
    ).exclude(
        id__in=citas_proximas.values_list("id", flat=True)
    ).order_by("-bloque__inicio")

    return render(request, "agenda/mis_citas.html", {
        "citas_proximas": citas_proximas,
        "citas_pasadas": citas_pasadas,
    })


# ====================================================================
# ESPECIALISTA
# ====================================================================
@login_required
def mi_agenda(request):
    """Panel de gestión del especialista con citas de la jornada y solicitudes pendientes."""
    verificar_rol(request.user, Usuario.ESPECIALISTA)
    hoy_inicio = timezone.localtime().replace(hour=0, minute=0, second=0, microsecond=0)

    citas_hoy = Cita.objects.filter(
        bloque__especialista=request.user,
        bloque__inicio__gte=hoy_inicio,
        bloque__inicio__lt=hoy_inicio + timezone.timedelta(days=1),
        estado__in=[Cita.SOLICITADA, Cita.CONFIRMADA]
    ).order_by("bloque__inicio")

    citas_pendientes = Cita.objects.filter(
        bloque__especialista=request.user,
        estado=Cita.SOLICITADA
    ).order_by("bloque__inicio")

    todas_citas = Cita.objects.filter(
        bloque__especialista=request.user
    ).order_by("-bloque__inicio")[:20]

    return render(request, "agenda/mi_agenda.html", {
        "citas_hoy": citas_hoy,
        "citas_pendientes": citas_pendientes,
        "todas_citas": todas_citas,
    })


@login_required
def disponibilidad(request):
    """Publicación y administración de bloques de 45 minutos."""
    verificar_rol(request.user, Usuario.ESPECIALISTA)
    form = BloqueForm(request.POST or None)
    form.instance.especialista = request.user

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Nuevo bloque horario publicado con éxito.")
        return redirect("agenda:disponibilidad")

    bloques = BloqueHorario.objects.filter(
        especialista=request.user, inicio__gte=timezone.now()
    ).order_by("inicio")

    return render(request, "agenda/disponibilidad.html", {"form": form, "bloques": bloques})


@require_POST
@login_required
def eliminar_bloque(request, bloque_id):
    verificar_rol(request.user, Usuario.ESPECIALISTA)
    bloque = get_object_or_404(BloqueHorario, id=bloque_id, especialista=request.user)
    if bloque.citas.exists():
        messages.error(request, "No puedes eliminar un bloque que ya tiene solicitudes o citas asociadas.")
    else:
        bloque.delete()
        messages.success(request, "Bloque horario eliminado correctamente.")
    return redirect("agenda:disponibilidad")


@require_POST
@login_required
def confirmar(request, cita_id):
    verificar_rol(request.user, Usuario.ESPECIALISTA)
    cita = get_object_or_404(Cita, id=cita_id, bloque__especialista=request.user)
    try:
        cita.confirmar(request.user)
        messages.success(request, f"Cita N° {cita.id} confirmada con éxito.")
    except ErrorCita as error:
        messages.error(request, str(error))
    return redirect("agenda:mi_agenda")


@require_POST
@login_required
def rechazar(request, cita_id):
    verificar_rol(request.user, Usuario.ESPECIALISTA)
    cita = get_object_or_404(Cita, id=cita_id, bloque__especialista=request.user)
    motivo = request.POST.get("motivo", "").strip()
    if not motivo:
        messages.error(request, "Debes ingresar el motivo del rechazo.")
        return redirect("agenda:mi_agenda")
    try:
        cita.rechazar(request.user, motivo)
        messages.success(request, f"Solicitud N° {cita.id} rechazada. El bloque horario ha sido liberado.")
    except ErrorCita as error:
        messages.error(request, str(error))
    return redirect("agenda:mi_agenda")


@login_required
def reagendar(request, cita_id):
    """Reagendación de cita hacia otro bloque libre del mismo especialista."""
    verificar_rol(request.user, Usuario.ESPECIALISTA)
    cita = get_object_or_404(Cita, id=cita_id, bloque__especialista=request.user)

    if request.method == "POST":
        bloque_id = request.POST.get("bloque_id", "").strip()
        if not bloque_id.isdigit():
            messages.error(request, "Por favor selecciona un horario válido.")
            return redirect("agenda:reagendar", cita_id=cita.id)
        try:
            cita.reagendar(request.user, int(bloque_id))
            messages.success(request, f"Cita N° {cita.id} reagendada exitosamente. Se ha notificado al paciente.")
            return redirect("agenda:mi_agenda")
        except ErrorCita as error:
            messages.error(request, str(error))

    libres = BloqueHorario.objects.filter(
        especialista=request.user, disponible=True, inicio__gt=timezone.now()
    ).order_by("inicio")

    return render(request, "agenda/reagendar.html", {"cita": cita, "bloques": libres})


# ====================================================================
# PACIENTE O ESPECIALISTA
# ====================================================================
@require_POST
@login_required
def cancelar(request, cita_id):
    """Cancelación de cita con verificación de 24 horas para pacientes."""
    if request.user.rol == Usuario.PACIENTE:
        cita = get_object_or_404(Cita, id=cita_id, paciente=request.user)
        volver_a = "agenda:mis_citas"
    else:
        verificar_rol(request.user, Usuario.ESPECIALISTA)
        cita = get_object_or_404(Cita, id=cita_id, bloque__especialista=request.user)
        volver_a = "agenda:mi_agenda"

    motivo = request.POST.get("motivo", "").strip()
    if not motivo:
        messages.error(request, "Debes indicar el motivo de la cancelación.")
        return redirect(volver_a)

    try:
        cita.cancelar(request.user, motivo)
        messages.success(request, f"La cita N° {cita.id} ha sido cancelada y el bloque quedó liberado.")
    except ErrorCita as error:
        messages.error(request, str(error))

    return redirect(volver_a)
