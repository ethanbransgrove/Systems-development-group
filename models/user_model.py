from database import get_connection

def login_user(email, password):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT * FROM user
        WHERE email = %s AND password_hash = %s
    """

    cursor.execute(query, (email, password))
    user = cursor.fetchone()

    conn.close()
    return user