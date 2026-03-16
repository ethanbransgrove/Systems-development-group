# Student: [Your Name] | Student ID: [Your ID]

from database import get_connection


def create_complaint(tenant_id, desc):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        INSERT INTO complaint (tenant_id, description, status)
        VALUES (%s, %s, 'OPEN')
    """, (tenant_id, desc))

    conn.commit()
    conn.close()


def get_all_complaints():
    """Returns all complaints — used by Front Desk."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT complaint_id, tenant_id, description, status, created_at
        FROM complaint
        ORDER BY created_at DESC
    """)

    complaints = cursor.fetchall()
    conn.close()
    return complaints


def get_tenant_complaints(tenant_id):
    """Returns complaints for a specific tenant — used by Tenant view."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT complaint_id, description, status, created_at
        FROM complaint
        WHERE tenant_id = %s
        ORDER BY created_at DESC
    """, (tenant_id,))

    complaints = cursor.fetchall()
    conn.close()
    return complaints