# Análisis del Error de Envío de Correo a @burgosatu.es

## Resumen del Problema

El ERP está fallando al enviar correos electrónicos a direcciones con el dominio `@burgosatu.es`. El error específico es:

```
smtplib.SMTPRecipientsRefused: {'cursos@burgosatu.es': (550, b'5.1.1 : Recipient address rejected: User unknown in virtual mailbox table')}
```

## Análisis Técnico

### 1. Tipo de Error

El error `SMTPRecipientsRefused` con código `550` y mensaje `"User unknown in virtual mailbox table"` indica que:

- **El servidor SMTP está tratando el dominio `@burgosatu.es` como un dominio LOCAL** en lugar de un dominio externo
- El servidor intenta entregar el correo localmente (en su propia tabla de buzones virtuales) en lugar de enviarlo al servidor externo correspondiente
- Como las direcciones `@burgosatu.es` no existen en el servidor de `grupoatu.es`, se genera el error

### 2. Causa Real del Problema

**El servidor SMTP de `grupoatu.es` está mal configurado:**

El servidor SMTP está configurado para tratar `burgosatu.es` como un dominio local, lo que significa que:

1. Cuando intentas enviar un correo a `cursos@burgosatu.es`, el servidor SMTP piensa que debe entregarlo localmente
2. Busca la dirección en su propia tabla de buzones virtuales (donde solo tiene direcciones de `grupoatu.es`)
3. Como no encuentra `cursos@burgosatu.es` en su base de datos local, rechaza el correo con el error "User unknown in virtual mailbox table"
4. **NO intenta enviar el correo al servidor externo de `burgosatu.es`**

**Esto NO debería pasar normalmente:**
- Un servidor SMTP normalmente debería aceptar cualquier dirección de destino y luego intentar entregarla (ya sea localmente o a través de Internet)
- El hecho de que esté rechazando direcciones de otros dominios indica una configuración incorrecta del servidor

### 3. Causas Posibles de la Configuración Incorrecta

1. **El dominio `burgosatu.es` está configurado como dominio local en el servidor**
   - El servidor de correo tiene `burgosatu.es` en su lista de dominios locales
   - Esto hace que intente entregar el correo localmente en lugar de enviarlo externamente

2. **El servidor SMTP no está configurado como relay**
   - El servidor no está configurado para enviar correos a dominios externos
   - Solo puede manejar correos para sus propios dominios locales

3. **Configuración de panel de control (Plesk, cPanel, etc.)**
   - Si el servidor usa un panel de control como Plesk, el dominio `burgosatu.es` puede estar habilitado como servicio de correo local
   - Esto hace que el servidor trate el dominio como local en lugar de externo

### 3. Cómo Funciona el Envío de Correo en Frappe

El proceso de envío de correo en Frappe funciona de la siguiente manera:

1. Se crea un registro en `Email Queue` con los destinatarios
2. El método `EmailQueue.send()` intenta enviar el correo a cada destinatario
3. Si hay un error, se captura en `SendMailContext.__exit__()`
4. El sistema reintenta el envío hasta alcanzar el límite configurado (por defecto 3 intentos)
5. Si todos los intentos fallan, el Email Queue se marca como "Error"

### 4. Problema Identificado en el Código

En el código actual de Frappe (`email_queue.py`, líneas 155-185), hay un problema:

- El código marca el destinatario como "Sent" (línea 178) **antes** de verificar si el envío fue exitoso
- Si hay un error después de marcar como "Sent", el destinatario queda marcado incorrectamente
- Los errores `SMTPRecipientsRefused` se propagan y causan que todo el Email Queue falle

## Soluciones Propuestas

### Solución 1: Corregir la Configuración del Servidor SMTP (RECOMENDADO)

**El problema está en el servidor SMTP de `grupoatu.es`, NO en Frappe.**

**Acción inmediata - Contactar al administrador del servidor SMTP:**

1. **Verificar si el dominio `burgosatu.es` está configurado como dominio local:**
   - El servidor SMTP no debería tener `burgosatu.es` en su lista de dominios locales
   - Si está en la lista, debe eliminarse para que el servidor lo trate como dominio externo

2. **Si usan Plesk o similar:**
   - Deshabilitar el servicio de correo para el dominio `burgosatu.es` en el panel de control
   - Esto indica al servidor que NO debe manejar el correo para ese dominio localmente
   - El servidor entonces enviará los correos al servidor externo correspondiente

3. **Verificar la configuración de relay SMTP:**
   - Asegurarse de que el servidor esté configurado para enviar correos a dominios externos
   - Verificar que no haya restricciones que impidan el envío a `burgosatu.es`

4. **Verificar configuración DNS/MX:**
   - Asegurarse de que el servidor pueda resolver correctamente los registros MX de `burgosatu.es`
   - El servidor debe poder encontrar el servidor de correo externo para `burgosatu.es`

**NOTA IMPORTANTE:** 
- Las direcciones `@burgosatu.es` NO necesitan existir en el servidor de `grupoatu.es`
- El servidor solo necesita saber que `burgosatu.es` es un dominio EXTERNO y debe enviar los correos al servidor correspondiente

### Solución 2: Usar un Servidor SMTP Diferente

Si el servidor SMTP actual no puede manejar correos a `@burgosatu.es`, considerar:

1. Usar un servicio de correo externo (Gmail, SendGrid, etc.)
2. Configurar un servidor SMTP diferente para este dominio específico
3. Usar un servicio de relay SMTP que pueda manejar estos correos

### Solución 3: Mejorar el Manejo de Errores (IMPLEMENTADO)

Se ha creado un módulo personalizado (`portal_rrhh.utils.email_handler`) que:

1. Detecta errores específicos para direcciones `@burgosatu.es`
2. Registra errores más detallados en los logs
3. Proporciona información de diagnóstico más útil

**Para usar este módulo:**

1. Ejecutar el script de diagnóstico usando `bench execute`:
```bash
bench --site erp.grupoatu.com execute portal_rrhh.scripts.diagnose_email_issue.diagnose_email_issue
```

O usando `bench console` (modo interactivo):
```bash
bench --site erp.grupoatu.com console
```
Luego ejecutar:
```python
from portal_rrhh.scripts.diagnose_email_issue import diagnose_email_issue
diagnose_email_issue()
```

2. Usar la API de diagnóstico:
```python
frappe.call("portal_rrhh.api.email_diagnosis.get_email_diagnosis")
```

## Scripts y Herramientas Creadas

### 1. Script de Diagnóstico

**Ubicación:** `portal_rrhh/scripts/diagnose_email_issue.py`

Este script proporciona:
- Lista de cuentas de correo configuradas
- Lista de emails con errores para `@burgosatu.es`
- Lista de destinatarios problemáticos
- Prueba de conexión SMTP
- Recomendaciones específicas

**Uso:**
```bash
bench --site erp.grupoatu.com execute portal_rrhh.scripts.diagnose_email_issue.diagnose_email_issue
```

O en modo interactivo:
```bash
bench --site erp.grupoatu.com console
```
Luego:
```python
from portal_rrhh.scripts.diagnose_email_issue import diagnose_email_issue
diagnose_email_issue()
```

### 2. Módulo de Manejo de Errores

**Ubicación:** `portal_rrhh/utils/email_handler.py`

Este módulo proporciona:
- Manejo mejorado de errores `SMTPRecipientsRefused`
- Registro detallado de errores
- Información de diagnóstico

### 3. API de Diagnóstico

**Ubicación:** `portal_rrhh/api/email_diagnosis.py`

Proporciona una API para obtener información de diagnóstico sobre problemas de correo.

## Pasos Siguientes

1. **Ejecutar el script de diagnóstico** para obtener información detallada del problema:
   ```bash
   bench --site erp.grupoatu.com execute portal_rrhh.scripts.diagnose_email_issue.diagnose_email_issue
   ```

2. **Verificar con el administrador del servidor SMTP** que las direcciones existan:
   - `cursos@burgosatu.es` (81 errores detectados)
   - `atu.petronila@burgosatu.es` (44 errores detectados)
   - `director-atu@burgosatu.es` (16 errores detectados)

3. **Revisar la configuración del servidor SMTP** en Frappe:
   - Settings > Email Account
   - Verificar que el servidor `grupoatu.es:465` esté configurado correctamente

4. **Considerar usar un servidor SMTP diferente** si el problema persiste

5. **Monitorear los logs** para ver si el problema se resuelve

## Información Adicional

- **Código de error SMTP 550**: Indica que el servidor rechazó la solicitud
- **Mensaje "User unknown in virtual mailbox table"**: Indica que la dirección no existe en el servidor
- **Este es un error común** cuando las direcciones de correo no están configuradas correctamente en el servidor

## Contacto

Para más información o ayuda adicional, contactar al equipo de desarrollo o al administrador del servidor SMTP.

