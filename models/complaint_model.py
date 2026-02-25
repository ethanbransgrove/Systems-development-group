from database import get_connection

def create_complaint(tenant_id, desc):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        INSERT INTO complaint (tenant_id, description)
        VALUES (%s, %s)
    """

    cursor.execute(query, (tenant_id, desc))
    conn.commit()
    conn.close()