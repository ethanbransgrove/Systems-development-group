from database import get_connection

def get_tenant_details(tenant_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM tenant WHERE tenant_id = %s", (tenant_id,))
    tenant = cursor.fetchone()

    conn.close()
    return tenant