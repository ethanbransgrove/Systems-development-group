from db.database import get_connection
from app.permissions import has_permission

def register_tenant(session, tenant_data):
    if not has_permission(session["role"], "register_tenant"):
        raise PermissionError("You're not allowed to register tenants")
    
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(""" 
    INSERT INTO tenants (
        ni_number, name, phone, email, 
        occupation, lease_start, lease_end, city
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        tenant_data["ni_number"],
        tenant_data["name"],
        tenant_data["phone"],
        tenant_data["email"],
        tenant_data["occupation"],
        tenant_data["lease_start"],
        tenant_data["lease_end"],
        session["city"]
    ))

    conn.commit()
    conn.close()


def get_tenants_for_city(session):
    if not has_permission(session["role"], "view_tenant"):
        raise PermissionError("You are not allowed to view tenants")
    
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        ni_number,
        name,
        phone,
        email,
        occupation,
        lease_start,
        lease_end,
        city
    FROM tenants
        WHERE city = ?
        ORDER BY name
    """, (session["city"],))

    rows = cursor.fetchall()
    conn.close()

    return rows