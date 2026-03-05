from database import get_connection
from utils.auth import hash_password

def login_user(email, password):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    hashed_password = hash_password(password)

    query = """
        SELECT * FROM user
        WHERE email = %s AND password_hash = %s
    """

    cursor.execute(query, (email, hashed_password))
    user = cursor.fetchone()

    conn.close()
    return user