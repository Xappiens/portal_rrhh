"""
Manejador personalizado de errores de correo para direcciones @burgosatu.es
"""
import frappe
import smtplib
from frappe import _


def handle_email_send_error(email_queue, sender, recipient, message):
    """
    Hook personalizado para manejar errores de envío de correo.
    Este hook se ejecuta cuando hay un error al enviar un correo.
    """
    # Solo manejar errores para direcciones @burgosatu.es
    if "@burgosatu.es" not in recipient:
        return
    
    # Intentar enviar el correo normalmente
    try:
        email_account = email_queue.get_email_account(raise_error=True)
        smtp_server = email_account.get_smtp_server()
        
        smtp_server.session.sendmail(
            from_addr=sender,
            to_addrs=recipient,
            msg=message.decode("utf-8").encode() if isinstance(message, bytes) else message.encode(),
        )
        
        # Si el envío fue exitoso, actualizar el estado del destinatario
        for rec in email_queue.recipients:
            if rec.recipient == recipient:
                rec.update_db(status="Sent", commit=True)
                break
        
    except smtplib.SMTPRecipientsRefused as e:
        # Manejar específicamente el error SMTPRecipientsRefused
        error_msg = str(e)
        refused_recipients = e.recipients if hasattr(e, 'recipients') else {}
        
        # Registrar el error de manera más detallada
        frappe.log_error(
            title=f"Error al enviar correo a {recipient}",
            message=f"""
            Error SMTPRecipientsRefused para {recipient}
            
            Detalles del error:
            {error_msg}
            
            Destinatarios rechazados: {refused_recipients}
            
            Este error indica que el servidor SMTP está rechazando la dirección de correo
            porque no existe en su tabla de buzones virtuales.
            
            Acciones recomendadas:
            1. Verificar que la dirección {recipient} exista en el servidor de correo
            2. Contactar al administrador del servidor SMTP para verificar la configuración
            3. Verificar que el dominio @burgosatu.es esté configurado correctamente
            """,
            reference_doctype=email_queue.doctype,
            reference_name=email_queue.name,
        )
        
        # Marcar el destinatario como error pero no fallar todo el proceso
        for rec in email_queue.recipients:
            if rec.recipient == recipient:
                rec.update_db(status="Error", commit=True)
                break
        
        # Lanzar el error para que Frappe lo maneje normalmente
        raise
        
    except Exception as e:
        # Para otros errores, registrar y relanzar
        frappe.log_error(
            title=f"Error inesperado al enviar correo a {recipient}",
            message=f"Error: {str(e)}",
            reference_doctype=email_queue.doctype,
            reference_name=email_queue.name,
        )
        raise


def get_email_diagnosis_info():
    """
    Obtiene información de diagnóstico sobre problemas de correo con @burgosatu.es
    """
    info = {
        "failed_emails": [],
        "problematic_recipients": [],
        "email_accounts": [],
    }
    
    # Obtener emails fallidos
    failed_emails = frappe.db.sql("""
        SELECT DISTINCT eq.name, eq.sender, eq.status, eq.error, eq.retry, eq.creation
        FROM `tabEmail Queue` eq
        INNER JOIN `tabEmail Queue Recipient` eqr ON eq.name = eqr.parent
        WHERE eqr.recipient LIKE '%@burgosatu.es'
        AND eq.status = 'Error'
        ORDER BY eq.creation DESC
        LIMIT 20
    """, as_dict=True)
    
    info["failed_emails"] = failed_emails
    
    # Obtener destinatarios problemáticos
    problematic_recipients = frappe.db.sql("""
        SELECT DISTINCT eqr.recipient, COUNT(*) as error_count
        FROM `tabEmail Queue Recipient` eqr
        INNER JOIN `tabEmail Queue` eq ON eqr.parent = eq.name
        WHERE eqr.recipient LIKE '%@burgosatu.es'
        AND eq.status = 'Error'
        GROUP BY eqr.recipient
        ORDER BY error_count DESC
        LIMIT 10
    """, as_dict=True)
    
    info["problematic_recipients"] = problematic_recipients
    
    # Obtener cuentas de correo configuradas
    email_accounts = frappe.get_all("Email Account",
                                   filters={"enable_outgoing": 1},
                                   fields=["name", "email_id", "smtp_server", "smtp_port"])
    
    info["email_accounts"] = email_accounts
    
    return info

