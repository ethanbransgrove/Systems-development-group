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

def get_branch_complaints(branch_id):
    """
    Fetch all complaints for apartments belonging to a given branch.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT c.complaint_id, c.description, c.status, c.created_date, c.resolved_date,
               t.name AS tenant_name, a.apartment_number, p.name AS property_name
        FROM complaint c
        JOIN tenant t ON c.tenant_id = t.tenant_id
        JOIN apartment a ON c.apartment_id = a.apartment_id
        JOIN property p ON a.property_id = p.property_id
        WHERE p.branch_id = %s
        ORDER BY c.created_date DESC
    """
    cursor.execute(query, (branch_id,))
    complaints = cursor.fetchall()
    conn.close()
    return complaints

def create_complaint_by_staff(tenant_id, description):
    """
    Create a complaint on behalf of a tenant. Assumes tenant has an active lease.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Get active apartment for tenant
        cursor.execute("""
            SELECT apartment_id
            FROM lease
            WHERE tenant_id = %s AND status = 'ACTIVE'
            LIMIT 1
        """, (tenant_id,))
        result = cursor.fetchone()
        if not result:
            conn.close()
            return False
        apartment_id = result[0]
        cursor.execute("""
            INSERT INTO complaint (tenant_id, apartment_id, description, status)
            VALUES (%s, %s, %s, 'SUBMITTED')
        """, (tenant_id, apartment_id, description))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.rollback()
        conn.close()
        print("Complaint creation error:", e)
        return False