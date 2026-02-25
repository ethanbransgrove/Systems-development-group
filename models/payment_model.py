from database import get_connection

def get_tenant_payments(tenant_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT p.amount, p.payment_date
        FROM payment p
        JOIN lease l ON p.lease_id = l.lease_id
        WHERE l.tenant_id = %s
        ORDER BY p.payment_date DESC
    """

    cursor.execute(query, (tenant_id,))
    payments = cursor.fetchall()
    conn.close()
    return payments