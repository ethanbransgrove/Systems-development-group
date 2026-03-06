from database import get_connection
from datetime import date

def get_tenant_details(tenant_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM tenant WHERE tenant_id = %s", (tenant_id,))
    tenant = cursor.fetchone()

    conn.close()
    return tenant


def update_late_invoices(tenant_id):

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