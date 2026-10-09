"""Vistas de autenticación, perfil de cuenta, auditoría y atajos demo."""
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from agenda.models import Cita
from .auditoria import demasiados_intentos, registrar
from .forms import LoginForm, RegistroPacienteForm
from .models import Usuario
from .permisos import verificar_rol


def login_view(request):
    """Inicio de sesión seguro con protección contra ataques de fuerza bruta."""
    if request.user.is_authenticated:
        return redirect("inicio")

    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        identificador = form.cleaned_data["email"].strip().lower()
        password = form.cleaned_data["password"]

        # Protección contra ataques de fuerza bruta
        if demasiados_intentos(identificador):
            registrar("LOGIN_BLOQUEADO", request, correo=identificador)
            messages.error(request, "Demasiados intentos fallidos. Por seguridad, espera 15 minutos.")
            return render(request, "usuarios/login.html", {"form": form})

        # Búsqueda por email o por username
        usuario_obj = Usuario.objects.filter(email=identificador).first()
        if not usuario_obj:
            usuario_obj = Usuario.objects.filter(username=identificador).first()

        usuario = None
        if usuario_obj:
            usuario = authenticate(request, username=usuario_obj.username, password=password)

        if usuario is None:
            registrar("LOGIN_FALLIDO", request, correo=identificador)
            messages.error(request, "Correo o contraseña incorrectos.")
        else:
            login(request, usuario)
            registrar("LOGIN_OK", request, usuario=usuario)
            messages.success(request, f"¡Bienvenido/a, {usuario.first_name or usuario.username}!")
            return redirect("inicio")

    return render(request, "usuarios/login.html", {"form": form})


def logout_view(request):
    if request.user.is_authenticated:
        registrar("LOGOUT", request)
    logout(request)
    request.session.flush()
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect("usuarios:login")


def demo_paciente(request):
    """Atajo para pruebas inmediatas como paciente (Camila Rojas)."""
    user = Usuario.objects.filter(rol=Usuario.PACIENTE).first()
    if user:
        login(request, user)
        registrar("LOGIN_DEMO_PACIENTE", request, usuario=user)
        messages.success(request, f"Modo Demo: Sesión iniciada como {user.nombre_completo_con_titulo} (Paciente)")
    return redirect("inicio")


def demo_especialista(request):
    """Atajo para pruebas inmediatas como especialista (Dra. Andrea Soto)."""
    user = Usuario.objects.filter(rol=Usuario.ESPECIALISTA).first()
    if user:
        login(request, user)
        registrar("LOGIN_DEMO_ESPECIALISTA", request, usuario=user)
        messages.success(request, f"Modo Demo: Sesión iniciada como {user.nombre_completo_con_titulo} (Especialista)")
    return redirect("inicio")


def registro_view(request):
    """Registro de pacientes con consentimiento informado (Leyes 19.628 y 21.719)."""
    if request.user.is_authenticated:
        return redirect("inicio")

    form = RegistroPacienteForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        usuario = form.save(commit=False)
        usuario.username = usuario.email
        usuario.rol = Usuario.PACIENTE
        usuario.fecha_consentimiento = timezone.now()
        usuario.save()

        registrar("CUENTA_CREADA", request, usuario=usuario)
        login(request, usuario)
        messages.success(request, "¡Tu cuenta ha sido creada con éxito! Ya puedes gestionar tus atenciones.")
        return redirect("inicio")

    return render(request, "usuarios/registro.html", {"form": form})


@login_required
def mi_cuenta(request):
    """Perfil y configuración del usuario activo."""
    return render(request, "usuarios/mi_cuenta.html", {"usuario": request.user})


@require_POST
@login_required
def eliminar_cuenta(request):
    """Ejercicio del Derecho de Supresión de datos personales (Ley 21.719, RF-13)."""
    verificar_rol(request.user, Usuario.PACIENTE)
    if request.POST.get("confirmacion") != "ELIMINAR":
        messages.error(request, "Debes escribir exactamente la palabra ELIMINAR para confirmar la supresión de tus datos.")
        return redirect("usuarios:mi_cuenta")

    usuario = request.user
    # Cancelación de citas futuras para liberar los horarios
    citas_futuras = Cita.objects.filter(
        paciente=usuario,
        estado__in=[Cita.SOLICITADA, Cita.CONFIRMADA],
        bloque__inicio__gt=timezone.now(),
    )
    for c in citas_futuras:
        c.cancelar(usuario, "El paciente ejerció su derecho de supresión de cuenta", revisar_24_horas=False)

    # Las citas históricas anonimizan su motivo clínico
    Cita.objects.filter(paciente=usuario).update(motivo_consulta="", mensaje_sensorial="")

    registrar("DATOS_ELIMINADOS", request, usuario=usuario)
    usuario.eliminar_datos_personales()
    logout(request)
    messages.success(request, "Tus datos personales han sido suprimidos conforme a la Ley N° 21.719.")
    return redirect("usuarios:login")


def acceso_denegado(request, exception=None):
    """Manejador de error 403 con auditoría de seguridad."""
    registrar("ACCESO_DENEGADO", request, detalle=request.path)
    return render(request, "403.html", status=403)
