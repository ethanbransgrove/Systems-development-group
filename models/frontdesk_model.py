# Group B3, Rory Foley (23071664), Zuhaib Asif (23039419), Ethan Bransgrove (23079243), Rodrigo Garrabou Socias (23018284)

from database import get_connection
from utils.auth import hash_password

def get_available_apartments(branch_id):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT a.apartment_id, a.apartment_number, a.monthly_rent
        FROM apartment a
        JOIN property p ON a.property_id = p.property_id
        WHERE p.branch_id = %s
        AND a.status = 'AVAILABLE'
    """

    cursor.execute(query, (branch_id,))
    apartments = cursor.fetchall()

    conn.close()
    return apartments


def register_new_tenant(tenant_data, start_date, end_date, apartment_id, branch_id):
    
    """
    New tenant generation by front desk staff.

    Staff need to input the required fields for a tenant.

    Handles apartment assignment, lease creation and login details for new tenant. Also makes sure the
    assigned room is now marked as occupied in the database.
    """


    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Insert new tenant
        cursor.execute("""
            INSERT INTO tenant
            (ni_number, name, email, phone, occupation, reference)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, tenant_data)

        tenant_id = cursor.lastrowid

        # Get monthly rent 
        cursor.execute("""
            SELECT monthly_rent
            FROM apartment
            WHERE apartment_id = %s
        """, (apartment_id,))

        result = cursor.fetchone()

        if not result:
            raise Exception("Apartment not found.")
        
        monthly_rent = result[0]

        # Create lease
        cursor.execute(""" 
            INSERT INTO lease
            (tenant_id, apartment_id, start_date, end_date, monthly_rent)
            VALUES (%s, %s, %s, %s, %s)
        """, (tenant_id, apartment_id, start_date, end_date, monthly_rent))

        # Update apartment status
        cursor.execute("""
            UPDATE apartment
            SET status = 'OCCUPIED'
            WHERE apartment_id = %s
        """, (apartment_id,))

        # Create new tenant login (temp password = 123)

        temp_password = hash_password("123")
        
        cursor.execute("""
            INSERT INTO user
            (branch_id, name, email, password_hash, role, tenant_id)
            VALUES (%s, %s, %s, %s, 'TENANT', %s)
        """, (branch_id, tenant_data[1], tenant_data[2], temp_password, tenant_id))

        conn.commit()
        conn.close()
        return True
    
    except Exception as e:
        conn.rollback()
        conn.close()
        print("Registration Error:", e)
        return False
    
def get_tenants_by_branch(branch_id):
    """
    Fetch all tenants associated with a given branch (through apartments/properties).
    Returns a list of tenant dictionaries with id, name, email, phone, occupation, ni_number.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT DISTINCT t.tenant_id, t.name, t.email, t.phone, t.occupation, t.ni_number
        FROM tenant t
        JOIN lease l ON t.tenant_id = l.tenant_id
        JOIN apartment a ON l.apartment_id = a.apartment_id
        JOIN property p ON a.property_id = p.property_id
        WHERE p.branch_id = %s
        ORDER BY t.name
    """
    cursor.execute(query, (branch_id,))
    tenants = cursor.fetchall()
    conn.close()
    return tenants

def get_tenant_details_with_lease(tenant_id):
    """
    Fetch detailed tenant information including current lease and apartment.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT t.*, 
               l.lease_id, l.start_date, l.end_date, l.monthly_rent, l.status AS lease_status,
               a.apartment_number, a.type, a.rooms,
               p.name AS property_name, p.address AS property_address
        FROM tenant t
        LEFT JOIN lease l ON t.tenant_id = l.tenant_id AND l.status = 'ACTIVE'
        LEFT JOIN apartment a ON l.apartment_id = a.apartment_id
        LEFT JOIN property p ON a.property_id = p.property_id
        WHERE t.tenant_id = %s
    """
    cursor.execute(query, (tenant_id,))
    tenant = cursor.fetchone()
    conn.close()
    return tenant