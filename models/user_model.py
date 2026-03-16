from database import get_connection
from utils.auth import hash_password
import bcrypt


def login_user(email, password):

    """
    Checks the inputted password hash matches the database then allows for successful login.
    """

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM user WHERE email = %s"
    cursor.execute(query, (email,))
    user = cursor.fetchone()

    conn.close()

    if not user:
        return None

    stored_hash = user["password_hash"]

    if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
        return user
    
    return None


def update_user_password(user_id, new_password):

    """
    Once a new password is checked for its strength this function hashes the password and updates the database
    so that the tenant now has a new password.
    """

    conn = get_connection()
    cursor = conn.cursor()

    try:

        hashed = hash_password(new_password)

        cursor.execute("""
            UPDATE user
            SET password_hash = %s
            WHERE user_id = %s
        """, (hashed, user_id))

        conn.commit()
        conn.close()

        return True
    
    except Exception as e:
        conn.rollback()
        conn.close()
        print("Password update error:", e)
        return False