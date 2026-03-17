from database import get_connection


def create_maintenance_request(tenant_id, description):

    """
    Handles maintenance request creation by the tenant. The status and priority of request are set to defaults
    to be changed by staff.
    """

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            INSERT INTO maintenance_request
            (tenant_id, description, priority, status)
            VALUES (%s, %s, 'LOW', 'REPORTED')
        """, (tenant_id, description))

        conn.commit()
        conn.close()

        return True

    except Exception as e:
        conn.rollback()
        conn.close()
        print("Maintenance request error:", e)
        return False
    

def get_tenant_maintenance_requests(tenant_id):

    """
    Supports tenants being able to see a log of their previous request they have made and allows them to see the
    progress of each request.
    """

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT request_id, description, priority, status, reported_date
        FROM maintenance_request
        WHERE tenant_id = %s
        ORDER BY reported_date DESC
    """

    cursor.execute(query, (tenant_id,))
    requests = cursor.fetchall()

    conn.close()
    return requests
