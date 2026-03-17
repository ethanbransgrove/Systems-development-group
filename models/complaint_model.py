from database import get_connection


def create_complaint(tenant_id, description):

    """
    Logs a new complaint by a tenant and sets the status to submitted to later be changed by staff.
    """

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT apartment_id
            FROM lease
            WHERE tenant_id = %s
            AND status = 'ACTIVE'
            LIMIT 1
        """, (tenant_id,))

        result = cursor.fetchone()

        if not result:
            conn.close()
            return False

        apartment_id = result[0]

        # Insert complaint
        cursor.execute("""
            INSERT INTO complaint
            (tenant_id, apartment_id, description, status)
            VALUES (%s, %s, %s, 'SUBMITTED')
        """, (tenant_id, apartment_id, description))

        conn.commit()
        conn.close()

        return True

    except Exception as e:
        conn.rollback()
        conn.close()
        print("Complaint error:", e)
        return False
    

def get_tenant_complaints(tenant_id):

    """
    Used in the tenant dashboard to display a table of previous complaints made by current tenant.
    """

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT complaint_id, description, status, created_date
        FROM complaint
        WHERE tenant_id = %s
        ORDER BY created_date DESC
    """

    cursor.execute(query, (tenant_id,))
    complaints = cursor.fetchall()

    conn.close()
    return complaints
