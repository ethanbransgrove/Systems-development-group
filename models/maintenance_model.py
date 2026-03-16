# Student: [Your Name] | Student ID: [Your ID]

from database import get_connection


def create_maintenance_request(tenant_id, desc, priority):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT apartment_id
        FROM lease
        WHERE tenant_id = %s AND status = 'ACTIVE'
    """, (tenant_id,))

    lease = cursor.fetchone()

    if not lease:
        conn.close()
        return False

    apartment_id = lease["apartment_id"]  # FIX: was lease[0] which breaks with dictionary cursor

    cursor.execute("""
        INSERT INTO maintenance_request (tenant_id, apartment_id, priority, description, status)
        VALUES (%s, %s, %s, %s, 'PENDING')
    """, (tenant_id, apartment_id, priority, desc))

    conn.commit()
    conn.close()
    return True


def get_all_maintenance_requests():
    """Returns all maintenance requests — used by Front Desk."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT request_id, tenant_id, apartment_id, priority, status, description, created_at
        FROM maintenance_request
        ORDER BY created_at DESC
    """)

    requests = cursor.fetchall()
    conn.close()
    return requests


def get_tenant_maintenance_requests(tenant_id):
    """Returns maintenance requests for a specific tenant — used by Tenant view."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT request_id, priority, status, description, created_at
        FROM maintenance_request
        WHERE tenant_id = %s
        ORDER BY created_at DESC
    """, (tenant_id,))

    requests = cursor.fetchall()
    conn.close()
    return requests