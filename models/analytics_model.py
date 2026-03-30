# Group B3, Rory Foley (23071664), Zuhaib Asif (23039419), Ethan Bransgrove (23079243), Rodrigo Garrabou Socias (23018284)

from database import get_connection

def get_late_payments_per_property():

    """
    Gathers data from the DB which is used in the tenant function "view_late_payments_graph()".
    """

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
