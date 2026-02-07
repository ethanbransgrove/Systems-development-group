# Creating Tables Here

from db.database import get_connection


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()


    # Passwords are not hashed yet
    cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        city TEXT NOT NULL 
    )
    """)

    conn.commit()
    conn.close()

# Creates the tenants table
def create_tenants_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS tenants (
        tenant_id INTEGER PRIMARY KEY AUTOINCREMENT,
        ni_number TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT NOT NULL,
        occupation TEXT,
        lease_start DATE,
        lease_end DATE,
        city TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()


# Testing the database and login works together
def seed_users():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR IGNORE INTO users (name, password, role, city)
    VALUES ('bob', 'front123', 'frontdesk', 'London')
    """)

    conn.commit()
    conn.close()