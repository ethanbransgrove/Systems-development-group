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