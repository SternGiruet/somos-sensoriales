# Bitácora de Decisiones Arquitectónicas — Versión Definitiva
**Proyecto:** Gestión Sensorial ("Aquí Somos Sensoriales")  
**Fecha:** Octubre 2026  
**Responsable:** Esteban Morales & Equipo  

---

## 1. Unificación del Modelo de Usuario y Roles
- **Decisión:** Se adoptó un modelo único `Usuario(AbstractUser)` en la aplicación `usuarios`, combinando la simplicidad del rol como selector (`PACIENTE`, `ESPECIALISTA`, `ADMINISTRADOR`) con los atributos clínicos necesarios para ambos perfiles.
- **Campos del Paciente:** `rut` (con validación de módulo 11), `nombre_tutor`, `telefono_tutor`, `edad`, `direccion` y `pin_seguridad` (PIN de 4 dígitos).
- **Campos del Especialista:** `prefijo` ("Dra.", "Dr.", "Ps.", "Flga."), `especialidad`, `biografia`, `dias_atencion` y `registro_minsal`.
- **Identidad Gráfica:** `color_avatar` e `iniciales` calculadas dinámicamente en el método `save()`.

---

## 2. Implementación de Patrones de Diseño (GoF)
1. **Patrón Singleton (`agenda.models.CentroTerapeutico`):**
   - Garantiza que la configuración del centro (nombre, duración estándar de 45 minutos y mínimo de 24 horas para cancelación) sea única y persistente en la clave primaria `pk=1`.
2. **Patrón Factory (`notificaciones.avisos.crear_aviso`):**
   - Fabrica instancias de notificación según el canal solicitado (`AvisoApp`, `AvisoCorreo`). Permite incorporar nuevos canales (como WhatsApp mediante API de Twilio o SMS) sin alterar la lógica de negocio existente.
3. **Patrón Observer (`agenda.senales.cita_cambiada`):**
   - Desacopla la entidad `Cita` de los subsistemas de auditoría y notificaciones. Dos receptores escuchan el evento:
     - `notificaciones.receptores.avisar_cambio_de_cita`: notifica a la contraparte respetando la privacidad (RNF-05).
     - `usuarios.receptores.auditar_cambio_de_cita`: registra la transacción en el modelo inmutable `RegistroAuditoria`.

---

## 3. Concurrencia Atómica y Reglas de Negocio
- **Prevención de Doble Reserva:** El método `Cita.solicitar()` ejecuta una transacción atómica con actualización condicional `BloqueHorario.objects.filter(id=bloque_id, disponible=True, inicio__gt=timezone.now()).update(disponible=False)`. Si el número de filas afectadas es 0, se arroja la excepción de dominio `ErrorCita`.
- **Regla de 24 Horas:** Para el paciente, la cancelación está condicionada a tener al menos 24 horas de antelación respecto a la hora de inicio de la sesión. Los especialistas y administradores pueden cancelar en cualquier momento por razones de fuerza mayor.

---

## 4. Seguridad y Cumplimiento Normativo Chileno
- **Protección contra Fuerza Bruta (RF-01, DEF-05):** Si un correo o usuario acumula 5 intentos fallidos en un lapso de 15 minutos, el sistema bloquea temporalmente el acceso e inserta el evento `LOGIN_BLOQUEADO` en la tabla de auditoría.
- **Auditoría Inmutable (Ley 21.459):** El modelo `RegistroAuditoria` registra IP, usuario, acción y detalle. En el panel de Django Admin se deshabilitaron los permisos de agregar, editar o eliminar registros (`has_add_permission`, `has_change_permission`, `has_delete_permission` retornan `False`).
- **Derecho de Supresión (Ley 21.719, RF-13):** La función `eliminar_cuenta` cancela citas futuras, libera los horarios asociados, elimina el motivo de consulta de las citas pasadas y anonimiza la cuenta del usuario.
- **Ficha Confidencial Protegida por PIN:** La visualización de antecedentes médicos y diagnósticos requiere la validación del PIN de 4 dígitos en la sesión activa (`session['ficha_desbloqueada']`).

---

## 5. Pruebas y Verificación
- **14 Pruebas Unitarias** cubriendo patrones de diseño, seguridad OWASP A01, ciclo de vida de la agenda y módulo clínico.
- **Script de Verificación de Endpoints (`tests/verificar_todo.py`)**: Valida que todas las rutas HTTP del paciente y del especialista respondan con código 200 y que los modales y desbloqueos operen correctamente.
