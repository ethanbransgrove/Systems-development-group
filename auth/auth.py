from app.session import login, logout
from db.database import get_connection

# Fake users for now 
USERS = {
    "admin": {
        "password": "admin123",
        "role": "admin",
        "city": "London",
        "user_id": 1
    },
    "frontdesk": {
        "password": "front123",
        "role": "frontdesk",
        "city": "Bristol",
        "user_id": 2
    },
    "finance": {
        "password": "finance123",
        "role": "finance",
        "city": "Manchester",
        "user_id": 3
    }
}


def authenticate(username, password):
    user = USERS.get(username)

    if not user:
        return None
    
    if user["password"] != password:
        return None
    
    return user


def login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(""" 
        SELECT user_id, name, role, city
        FROM users
        WHERE name = ? AND password = ? 
    """, (username, password))

    user = cursor.fetchone()
    conn.close()

    if not user:
        return None

    login(
        user["user_id"],
        user["name"],
        user["role"],
        user["city"],
    )

    return user["role"]


def logout_user():
    logout()