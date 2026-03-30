# Group B3, Rory Foley (23071664), Zuhaib Asif (23039419), Ethan Bransgrove (23079243), Rodrigo Garrabou Socias (23018284)

import re
from database import get_connection
from utils.auth import hash_password


def _valid_email(email: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))


# ── BRANCH / PROPERTY ─────────────────────────────────────────────────────────

def get_all_branches():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT branch_id, name FROM branch ORDER BY name")
    branches = cursor.fetchall()
    conn.close()
    return branches


def get_all_properties():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.property_id, p.name, p.address, b.name AS branch_name
        FROM property p
        JOIN branch b ON b.branch_id = p.branch_id
        ORDER BY p.name
    """)
    properties = cursor.fetchall()
    conn.close()
    return properties


# ── STAFF USER MANAGEMENT ─────────────────────────────────────────────────────

def create_staff_user(name, email, password, role, branch_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "INSERT INTO user (branch_id, name, email, password_hash, role) VALUES (%s, %s, %s, %s, %s)",
            (branch_id, name, email, hash_password(password), role)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.rollback()
        conn.close()
        print("User create failed:", e)
        return False


def get_all_staff_users():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT u.user_id, u.name, u.email, u.role, b.name AS branch_name
        FROM user u
        JOIN branch b ON b.branch_id = u.branch_id
        WHERE u.role != 'TENANT'
        ORDER BY u.role, u.name
    """)
    users = cursor.fetchall()
    conn.close()
    return users


def update_staff_user(user_id, name, email, role, branch_id, new_password=""):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if new_password:
            cursor.execute(
                "UPDATE user SET name=%s, email=%s, role=%s, branch_id=%s, password_hash=%s WHERE user_id=%s",
                (name, email, role, branch_id, hash_password(new_password), user_id)
            )
        else:
            cursor.execute(
                "UPDATE user SET name=%s, email=%s, role=%s, branch_id=%s WHERE user_id=%s",
                (name, email, role, branch_id, user_id)
            )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.rollback()
        conn.close()
        print("User update failed:", e)
        return False


def delete_staff_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM user WHERE user_id = %s AND role != 'TENANT'",
            (user_id,)
        )
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        return deleted
    except Exception as e:
        conn.rollback()
        conn.close()
        print("User delete failed:", e)
        return False


# ── APARTMENT MANAGEMENT ──────────────────────────────────────────────────────

def get_all_apartments():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT a.apartment_id, a.apartment_number, a.type, a.rooms,
               a.monthly_rent, a.status,
               p.name AS property_name, p.property_id,
               b.name AS branch_name
        FROM apartment a
        JOIN property p ON p.property_id = a.property_id
        JOIN branch   b ON b.branch_id   = p.branch_id
        ORDER BY p.name, a.apartment_number
    """)
    apartments = cursor.fetchall()
    conn.close()
    return apartments


def apartment_number_exists(property_id, apartment_number, exclude_id=None):
    """
    Returns True if the apartment_number already exists in the given property.
    Pass exclude_id when editing so the apartment doesn't flag itself.
    """
    conn = get_connection()
    cursor = conn.cursor()
    if exclude_id:
        cursor.execute(
            "SELECT 1 FROM apartment WHERE property_id=%s AND apartment_number=%s AND apartment_id != %s",
            (property_id, apartment_number, exclude_id)
        )
    else:
        cursor.execute(
            "SELECT 1 FROM apartment WHERE property_id=%s AND apartment_number=%s",
            (property_id, apartment_number)
        )
    exists = cursor.fetchone() is not None
    conn.close()
    return exists


def update_apartment(apartment_id, apartment_number, apt_type, rooms, monthly_rent, status):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE apartment
            SET apartment_number=%s, type=%s, rooms=%s, monthly_rent=%s, status=%s
            WHERE apartment_id=%s
            """,
            (apartment_number, apt_type, rooms, monthly_rent, status, apartment_id)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.rollback()
        conn.close()
        print("Apartment update failed:", e)
        return False


def add_apartment(property_id, apartment_number, apt_type, rooms, monthly_rent):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO apartment (property_id, apartment_number, type, rooms, monthly_rent, status)
            VALUES (%s, %s, %s, %s, %s, 'AVAILABLE')
            """,
            (property_id, apartment_number, apt_type, rooms, monthly_rent)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.rollback()
        conn.close()
        print("Apartment add failed:", e)
        return False


def delete_apartment(apartment_id):
    """
    Delete an apartment by ID.
    Returns (True, "") on success.
    Returns (False, "occupied") if the apartment is OCCUPIED.
    Returns (False, "error") on failure.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT status FROM apartment WHERE apartment_id = %s", (apartment_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return False, "error"

        if row["status"] == "OCCUPIED":
            conn.close()
            return False, "occupied"

        cursor.execute("DELETE FROM apartment WHERE apartment_id = %s", (apartment_id,))
        conn.commit()
        conn.close()
        return True, ""

    except Exception as e:
        conn.rollback()
        conn.close()
        print("Apartment delete failed:", e)
        return False, "error"