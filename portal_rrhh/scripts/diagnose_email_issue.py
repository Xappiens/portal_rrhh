"""
Script de diagnóstico para problemas de envío de correo a direcciones @burgosatu.es
"""
import frappe
import smtplib
from frappe.email.doctype.email_account.email_account import EmailAccount


def diagnose_email_issue():
    """Diagnostica el problema de envío de correos a direcciones @burgosatu.es"""
    
    frappe.init(site=frappe.local.site)
    frappe.connect()
    
    print("=" * 80)
    print("DIAGNÓSTICO DE PROBLEMA DE ENVÍO DE CORREO")
    print("=" * 80)
    
    # 1. Verificar cuentas de correo configuradas
    print("\n1. CUENTAS DE CORREO CONFIGURADAS:")
    print("-" * 80)
    email_accounts = frappe.get_all("Email Account", 
                                   filters={"enable_outgoing": 1},
                                   fields=["name", "email_id", "smtp_server", "smtp_port", "use_tls", "use_ssl"])
    
    if not email_accounts:
        print("❌ No se encontraron cuentas de correo saliente configuradas")
        return
    
    for account in email_accounts:
        print(f"  • {account.name}:")
        print(f"    - Email: {account.email_id}")
        print(f"    - SMTP Server: {account.smtp_server}")
        print(f"    - SMTP Port: {account.smtp_port}")
        print(f"    - TLS: {account.use_tls}, SSL: {account.use_ssl}")
    
    # 2. Verificar Email Queue con errores para @burgosatu.es
    print("\n2. EMAIL QUEUE CON ERRORES PARA @burgosatu.es:")
    print("-" * 80)
    failed_emails = frappe.db.sql("""
        SELECT eq.name, eq.sender, eq.status, eq.error, eq.retry, eq.creation
        FROM `tabEmail Queue` eq
        INNER JOIN `tabEmail Queue Recipient` eqr ON eq.name = eqr.parent
        WHERE eqr.recipient LIKE '%@burgosatu.es'
        AND eq.status = 'Error'
        ORDER BY eq.creation DESC
        LIMIT 10
    """, as_dict=True)
    
    if failed_emails:
        print(f"  Se encontraron {len(failed_emails)} emails con errores:")
        for email in failed_emails:
            print(f"  • Queue: {email.name}")
            print(f"    - Sender: {email.sender}")
            print(f"    - Status: {email.status}")
            print(f"    - Retry: {email.retry}")
            print(f"    - Creation: {email.creation}")
            if email.error:
                error_lines = email.error.split('\n')[:3]
                print(f"    - Error: {' '.join(error_lines)}")
    else:
        print("  ✓ No se encontraron emails con errores recientes")
    
    # 3. Verificar destinatarios problemáticos
    print("\n3. DESTINATARIOS PROBLEMÁTICOS:")
    print("-" * 80)
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
    
    if problematic_recipients:
        print(f"  Se encontraron {len(problematic_recipients)} destinatarios con errores:")
        for recipient in problematic_recipients:
            print(f"  • {recipient.recipient}: {recipient.error_count} errores")
    else:
        print("  ✓ No se encontraron destinatarios problemáticos")
    
    # 4. Probar conexión SMTP
    print("\n4. PRUEBA DE CONEXIÓN SMTP:")
    print("-" * 80)
    if email_accounts:
        account_name = email_accounts[0]['name']
        try:
            email_account = frappe.get_doc("Email Account", account_name)
            smtp_server = email_account.get_smtp_server()
            
            print(f"  ✓ Conexión SMTP exitosa a {email_account.smtp_server}:{email_account.smtp_port}")
            print(f"    - Servidor activo: {smtp_server.is_session_active()}")
            
            # Intentar verificar un destinatario (si el servidor lo permite)
            print(f"\n  ⚠️  PROBLEMA IDENTIFICADO:")
            print(f"    El error 'User unknown in virtual mailbox table' indica que:")
            print(f"    - El servidor SMTP está tratando @burgosatu.es como dominio LOCAL")
            print(f"    - Está intentando entregar el correo localmente en lugar de enviarlo externamente")
            print(f"    - El servidor necesita configurarse para tratar @burgosatu.es como dominio EXTERNO")
            print(f"    - Esto es un problema de configuración del servidor SMTP, no de Frappe")
            
        except Exception as e:
            print(f"  ❌ Error al conectar con SMTP: {str(e)}")
    
    # 5. Recomendaciones
    print("\n5. RECOMENDACIONES:")
    print("-" * 80)
    print("  ⚠️  PROBLEMA: El servidor SMTP está tratando @burgosatu.es como dominio LOCAL")
    print("")
    print("  • Contactar al administrador del servidor SMTP (grupoatu.es) para:")
    print("    - Verificar si burgosatu.es está en la lista de dominios locales")
    print("    - Si está, ELIMINARLO para que se trate como dominio externo")
    print("    - Si usan Plesk/cPanel: Deshabilitar servicio de correo para burgosatu.es")
    print("    - Verificar que el servidor pueda enviar correos a dominios externos (relay SMTP)")
    print("")
    print("  • Las direcciones @burgosatu.es NO necesitan existir en grupoatu.es")
    print("    - Solo necesitan que el servidor sepa que es un dominio externo")
    print("")
    print("  • Si el problema persiste, considerar usar un servidor SMTP diferente")
    
    print("\n" + "=" * 80)
    
    frappe.destroy()


if __name__ == "__main__":
    import sys
    site = sys.argv[1] if len(sys.argv) > 1 else None
    frappe.init(site=site)
    diagnose_email_issue()

