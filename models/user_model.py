from database import get_connection
import bcrypt


def login_user(email, password):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM user WHERE email = %s"
    cursor.execute(query, (email,))
    user = cursor.fetchone()

    conn.close()

    if not user:
        return None

    stored_hash = user["password"]

    if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
        return user
    
    return None