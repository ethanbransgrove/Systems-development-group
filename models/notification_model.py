from database import get_connection

def create_notification(user_id, message, type="GENERAL"):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO notification (user_id, message, type)
        VALUES (%s, %s, %s)
    """, (user_id, message, type))

    conn.commit()
    conn.close()


def get_unread_notifications(user_id):

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