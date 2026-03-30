# Group B3, Rory Foley (23071664), Zuhaib Asif (23039419), Ethan Bransgrove (23079243), Rodrigo Garrabou Socias (23018284)

from database import get_connection
from datetime import date

def get_tenant_details(tenant_id):

    """
    Allows the tenant dashboard to only show information related the tenant that logged in.
    """

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM tenant WHERE tenant_id = %s", (tenant_id,))
    tenant = cursor.fetchone()

    conn.close()
    return tenant


def update_late_invoices(tenant_id):

    """
    When a tenant logs in the system needs to check if the tenant has a late payment due. Checks the status of the 
    tenant's invoice.
    """

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        UPDATE invoice i
        JOIN lease l ON i.lease_id = l.lease_id
        SET i.status = 'LATE'
        WHERE l.tenant_id = %s
        AND i.status = 'PENDING'
        AND i.due_date < CURDATE()
    """, (tenant_id,))

    conn.commit()
    conn.close()


def get_tenant_invoices(tenant_id):

    """
    Facilitates the viewing of the logged-in tenant's invoices.
    """

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT  i.invoice_id,
                i.lease_id,
                i.period_start,
                i.period_end,
                i.amount_due,
                i.due_date,
                i.status
        FROM invoice i
        JOIN lease l ON i.lease_id = l.lease_id
        WHERE l.tenant_id = %s
        ORDER BY i.period_start DESC
    """

    cursor.execute(query, (tenant_id,))
    invoices = cursor.fetchall()

    conn.close()
    return invoices


def create_late_payment_notification(user_id, tenant_id):

    """
    This function is ran after the update_late_invoices() function to add a notification to the system to then be
    shown to the user in the notifications tab.
    """

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """ 
        SELECT i.invoice_id, i.amount_due, i.due_date
        FROM invoice i
        JOIN lease l ON i.lease_id = l.lease_id
        WHERE l.tenant_id = %s
        AND i.status = 'LATE'
    """

    cursor.execute(query, (tenant_id,))
    late_invoices = cursor.fetchall()

    for invoice in late_invoices:

        message = f"Invoice #{invoice['invoice_id']} (£{invoice['amount_due']}) was due on {invoice['due_date']} and is now late."

        cursor.execute("""
            INSERT INTO notification (user_id, message, type)
            SELECT %s, %s, 'LATE_PAYMENT'
            WHERE NOT EXISTS (
                SELECT 1 FROM notification
                WHERE user_id = %s
                AND message = %s           
            )
        """, (user_id, message, user_id, message))

    conn.commit()
    conn.close()


def get_late_invoice_count(tenant_id):
    
    """
    Helps to implement the late payment banner in the tenant dashboard.
    Finds how many LATE payments a tenant has from the database.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM invoice i
        JOIN lease l ON i.lease_id = l.lease_id
        WHERE l.tenant_id = %s
        AND i.status = 'LATE'
    """, (tenant_id,))

    count = cursor.fetchone()[0]

    conn.close()
    return count