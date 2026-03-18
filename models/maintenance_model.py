from database import get_connection

# ================== TENANT FUNCTIONS ==================

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


# ================== STAFF FUNCTIONS ==================

def get_branch_maintenance_requests(branch_id):
    """
    Fetch all maintenance requests for apartments belonging to a given branch.
    Returns a list of dictionaries with request details.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT mr.request_id, mr.description, mr.priority, mr.status, 
               mr.reported_date, mr.assigned_staff_id,
               CONCAT(COALESCE(t.name, 'Unknown'), ' (Apt ', COALESCE(a.apartment_number, '?'), ')') AS tenant_apartment,
               u.name AS assigned_staff_name
        FROM maintenance_request mr
        LEFT JOIN tenant t ON mr.tenant_id = t.tenant_id
        LEFT JOIN apartment a ON mr.apartment_id = a.apartment_id
        LEFT JOIN property p ON a.property_id = p.property_id
        LEFT JOIN user u ON mr.assigned_staff_id = u.user_id
        WHERE p.branch_id = %s OR mr.apartment_id IS NULL
        ORDER BY mr.reported_date DESC
    """
    cursor.execute(query, (branch_id,))
    requests = cursor.fetchall()
    conn.close()
    return requests


def get_request_details(request_id):
    """
    Retrieve full details of a single maintenance request, including tenant,
    apartment, property, and assigned staff information.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT mr.*, t.name AS tenant_name, t.phone, t.email,
               a.apartment_number, a.type, a.rooms, a.monthly_rent,
               p.name AS property_name, p.address AS property_address,
               u.name AS assigned_staff_name
        FROM maintenance_request mr
        LEFT JOIN tenant t ON mr.tenant_id = t.tenant_id
        LEFT JOIN apartment a ON mr.apartment_id = a.apartment_id
        LEFT JOIN property p ON a.property_id = p.property_id
        LEFT JOIN user u ON mr.assigned_staff_id = u.user_id
        WHERE mr.request_id = %s
    """
    cursor.execute(query, (request_id,))
    request = cursor.fetchone()
    conn.close()
    return request


def assign_request(request_id, staff_user_id):
    """
    Assign a maintenance request to a specific staff member.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE maintenance_request
            SET assigned_staff_id = %s
            WHERE request_id = %s
        """, (staff_user_id, request_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.rollback()
        conn.close()
        print("Assign error:", e)
        return False


def update_request_status(request_id, status, priority=None):
    """
    Update the status (and optionally priority) of a maintenance request.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if priority:
            cursor.execute("""
                UPDATE maintenance_request
                SET status = %s, priority = %s
                WHERE request_id = %s
            """, (status, priority, request_id))
        else:
            cursor.execute("""
                UPDATE maintenance_request
                SET status = %s
                WHERE request_id = %s
            """, (status, request_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.rollback()
        conn.close()
        print("Update error:", e)
        return False


def create_maintenance_log(request_id, start_time, end_time, hours_spent, cost, resolution_notes):
    """
    Insert a maintenance log entry and mark the request as RESOLVED.
    Datetime parameters can be None or datetime objects.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO maintenance_log
            (request_id, start_time, end_time, hours_spent, cost, resolution_notes)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (request_id, start_time, end_time, hours_spent, cost, resolution_notes))

        cursor.execute("""
            UPDATE maintenance_request
            SET status = 'RESOLVED'
            WHERE request_id = %s
        """, (request_id,))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.rollback()
        conn.close()
        print("Log error:", e)
        return False