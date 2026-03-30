# Group B3, Rory Foley (23071664), Zuhaib Asif (23039419), Ethan Bransgrove (23079243), Rodrigo Garrabou Socias (23018284)

from database import get_connection

def create_notification(user_id, message, type="GENERAL"):

    """

    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO notification (user_id, message, type)
        VALUES (%s, %s, %s)
    """, (user_id, message, type))

    conn.commit()
    conn.close()


def get_unread_notifications(user_id):

    """
    Fetches all the notifications where the status is unread
    """

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT notification_id, message, type, create_at
        FROM notification
        WHERE user_id = %s
        AND is_read = 0
        ORDER BY create_at DESC
    """, (user_id,))

    notifications = cursor.fetchall()

    conn.close()
    return notifications


def mark_notifications_read(user_id):
    
    """
    Updates read status of the notification in the notifications tab once opened.
    """

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        UPDATE notification
        SET is_read = 1
        WHERE user_id = %s
    """, (user_id,))

    conn.commit()
    conn.close()


def get_all_notifications(user_id):

    """
    Facilitates the viewing of notifications for the tenant user to see.
    """

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT message, type, is_read, create_at
        FROM notification
        WHERE user_id = %s
        ORDER BY create_at DESC
    """, (user_id,))

    notifications = cursor.fetchall()

    conn.close()
    return notifications