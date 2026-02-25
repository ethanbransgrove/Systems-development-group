from database import get_connection

def create_maintenance_request(tenant_id, desc, priority):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(""" 
        SELECT apartment_id 
        FROM lease
        WHERE tenant_id = %s 
    """, (tenant_id,))

    lease = cursor.fetchone()

    if not lease:
        conn.close()
        return False
    
    apartment_id = lease[0]

    query = """
        INSERT INTO maintenance_request (tenant_id, apartment_id, priority, description)
        VALUES (%s, %s, %s, %s)
    """

    cursor.execute(query, (tenant_id, apartment_id, priority, desc))
    conn.commit()
    conn.close()
    
    return True