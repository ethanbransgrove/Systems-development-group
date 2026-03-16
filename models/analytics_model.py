from database import get_connection

def get_late_payments_per_property():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT pr.name, COUNT(i.invoice_id) AS late_count
        FROM invoice i
        JOIN lease l ON i.lease_id = l.lease_id
        JOIN apartment a ON l.apartment_id = a.apartment_id
        JOIN property pr ON a.property_id = pr.property_id
        WHERE i.status = 'LATE'
        GROUP BY pr.name
        ORDER BY late_count DESC
    """

    cursor.execute(query)
    data = cursor.fetchall()

    conn.close()
    return data
