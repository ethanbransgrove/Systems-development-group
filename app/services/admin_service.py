# app/services/admin_service.py

import bcrypt
import mysql.connector
from config import DB_CONFIG


def _get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


# ── BRANCH / PROPERTY ─────────────────────────────────────────────────────────

def get_all_branches() -> list:
    conn = None
    try:
        conn = _get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT branch_id, name FROM branch ORDER BY name")
        return cursor.fetchall()
    except mysql.connector.Error as exc:
        print(f"[admin_service] get_all_branches error: {exc}")
        return []
    finally:
        if conn and conn.is_connected():
            conn.close()


def get_all_properties() -> list:
    conn = None
    try:
        conn = _get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT p.property_id, p.name, p.address, b.name AS branch_name
            FROM property p
            JOIN branch b ON b.branch_id = p.branch_id
            ORDER BY p.name
        """)
        return cursor.fetchall()
    except mysql.connector.Error as exc:
        print(f"[admin_service] get_all_properties error: {exc}")
        return []
    finally:
        if conn and conn.is_connected():
            conn.close()


# ── STAFF USER MANAGEMENT ─────────────────────────────────────────────────────

def create_staff_user(name, email, password, role, branch_id) -> bool:
    conn = None
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO user (branch_id, name, email, password_hash, role) VALUES (%s, %s, %s, %s, %s)",
            (branch_id, name, email, hash_password(password), role)
        )
        conn.commit()
        return True
    except mysql.connector.Error as exc:
        print(f"[admin_service] create_staff_user error: {exc}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn and conn.is_connected():
            conn.close()


def get_all_staff_users() -> list:
    conn = None
    try:
        conn = _get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT u.user_id, u.name, u.email, u.role, b.name AS branch_name
            FROM user u
            JOIN branch b ON b.branch_id = u.branch_id
            WHERE u.role != 'TENANT'
            ORDER BY u.role, u.name
        """)
        return cursor.fetchall()
    except mysql.connector.Error as exc:
        print(f"[admin_service] get_all_staff_users error: {exc}")
        return []
    finally:
        if conn and conn.is_connected():
            conn.close()


def update_staff_user(user_id, name, email, role, branch_id, new_password="") -> bool:
    conn = None
    try:
        conn = _get_connection()
        cursor = conn.cursor()
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
        return True
    except mysql.connector.Error as exc:
        print(f"[admin_service] update_staff_user error: {exc}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn and conn.is_connected():
            conn.close()


def delete_staff_user(user_id) -> bool:
    conn = None
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM user WHERE user_id = %s AND role != 'TENANT'",
            (user_id,)
        )
        conn.commit()
        return cursor.rowcount > 0
    except mysql.connector.Error as exc:
        print(f"[admin_service] delete_staff_user error: {exc}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn and conn.is_connected():
            conn.close()


# ── APARTMENT MANAGEMENT ──────────────────────────────────────────────────────

def get_all_apartments() -> list:
    conn = None
    try:
        conn = _get_connection()
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
        return cursor.fetchall()
    except mysql.connector.Error as exc:
        print(f"[admin_service] get_all_apartments error: {exc}")
        return []
    finally:
        if conn and conn.is_connected():
            conn.close()


def apartment_number_exists(property_id, apartment_number, exclude_id=None) -> bool:
    """
    Returns True if the apartment_number already exists in the given property.
    Pass exclude_id when editing an existing apartment so it doesn't flag itself.
    """
    conn = None
    try:
        conn = _get_connection()
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
        return cursor.fetchone() is not None
    except mysql.connector.Error as exc:
        print(f"[admin_service] apartment_number_exists error: {exc}")
        return False
    finally:
        if conn and conn.is_connected():
            conn.close()


def update_apartment(apartment_id, apartment_number, apt_type, rooms, monthly_rent, status) -> bool:
    conn = None
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE apartment
            SET apartment_number=%s, type=%s, rooms=%s, monthly_rent=%s, status=%s
            WHERE apartment_id=%s
            """,
            (apartment_number, apt_type, rooms, monthly_rent, status, apartment_id)
        )
        conn.commit()
        return True
    except mysql.connector.Error as exc:
        print(f"[admin_service] update_apartment error: {exc}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn and conn.is_connected():
            conn.close()


def add_apartment(property_id, apartment_number, apt_type, rooms, monthly_rent) -> bool:
    conn = None
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO apartment (property_id, apartment_number, type, rooms, monthly_rent, status)
            VALUES (%s, %s, %s, %s, %s, 'AVAILABLE')
            """,
            (property_id, apartment_number, apt_type, rooms, monthly_rent)
        )
        conn.commit()
        return True
    except mysql.connector.Error as exc:
        print(f"[admin_service] add_apartment error: {exc}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn and conn.is_connected():
            conn.close()


def delete_apartment(apartment_id) -> tuple:
    """
    Delete an apartment by ID.
    Returns (True, "") on success.
    Returns (False, "occupied") if the apartment is currently OCCUPIED.
    Returns (False, "error") on DB failure.
    """
    conn = None
    try:
        conn = _get_connection()
        cursor = conn.cursor(dictionary=True)

        # Check status before deleting
        cursor.execute("SELECT status FROM apartment WHERE apartment_id = %s", (apartment_id,))
        row = cursor.fetchone()

        if not row:
            return False, "error"

        if row["status"] == "OCCUPIED":
            return False, "occupied"

        cursor.execute("DELETE FROM apartment WHERE apartment_id = %s", (apartment_id,))
        conn.commit()
        return True, ""

    except mysql.connector.Error as exc:
        print(f"[admin_service] delete_apartment error: {exc}")
        if conn:
            conn.rollback()
        return False, "error"
    finally:
        if conn and conn.is_connected():
            conn.close()