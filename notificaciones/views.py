from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Notificacion


@login_required
def lista_notificaciones(request):
    """Muestra el buzón de avisos del usuario y marca las no leídas como revisadas."""
    avisos = Notificacion.objects.filter(usuario=request.user)[:50]
    pagina = render(request, "notificaciones/lista.html", {"avisos": avisos})
    Notificacion.objects.filter(usuario=request.user, leida=False).update(leida=True)
    return pagina
