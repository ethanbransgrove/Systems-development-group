# Student: [Your Name] | Student ID: [Your ID]

from database import get_connection


def register_tenant(data):
    """
    Registers a new tenant and creates their lease record.
    Returns True on success, False if NI number already exists.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Check NI number is unique
    cursor.execute("SELECT tenant_id FROM tenant WHERE ni_number = %s", (data["ni_number"],))
    if cursor.fetchone():
        conn.close()
        return False

    # Insert tenant
    cursor.execute("""
        INSERT INTO tenant (ni_number, name, phone, email, occupation, references, emergency_contact)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        data["ni_number"],
        data["name"],
        data["phone"],
        data["email"],
        data.get("occupation", ""),
        data.get("references", ""),
        data.get("emergency", "")
    ))

    tenant_id = cursor.lastrowid

    # Insert lease if lease info provided
    if data.get("start_date") and data.get("lease_period") and data.get("monthly_rent"):
        cursor.execute("""
            INSERT INTO lease (tenant_id, start_date, lease_period_months, monthly_rent, deposit, status)
            VALUES (%s, %s, %s, %s, %s, 'ACTIVE')
        """, (
            tenant_id,
            data["start_date"],
            data["lease_period"],
            data["monthly_rent"],
            data.get("deposit", 0)
        ))

    conn.commit()
    conn.close()
    return True


def search_tenant(term):
    """
    Search tenants by name or email (partial match).
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT tenant_id, name, email, phone
        FROM tenant
        WHERE name LIKE %s OR email LIKE %s
    """, (f"%{term}%", f"%{term}%"))

    results = cursor.fetchall()
    conn.close()
    return results