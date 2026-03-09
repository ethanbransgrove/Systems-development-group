from database import get_connection
from utils.auth import hash_password

def create_staff_user(name, email, password, role, branch_id):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        hashed_password = hash_password(password)

        query = """
            INSERT INTO user
            (branch_id, name, email, password_hash, role)
            VALUES (%s, %s, %s, %s, %s)
        """

        cursor.execute(query, (branch_id, name, email, hashed_password, role))

        conn.commit()
        conn.close()

        return True
    
    except Exception as e:
        conn.rollback()
        conn.close()
        print("User create failed:", e)
        return False
    

def get_all_branches():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""  
        SELECT branch_id, name
        FROM  branch
        ORDER BY name
    """)

    branches = cursor.fetchall()

    conn.close()
    return branches