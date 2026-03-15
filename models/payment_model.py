from database import get_connection

def get_tenant_payments(tenant_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT p.amount, p.payment_date
        FROM payment p
        JOIN lease l ON p.lease_id = l.lease_id
        WHERE l.tenant_id = %s
        ORDER BY p.payment_date DESC
    """

    cursor.execute(query, (tenant_id,))
    payments = cursor.fetchall()
    conn.close()
    return payments


def create_payment(invoice_id, lease_id, amount, card_number):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        last4 = card_number[-4:]

        # Insert payment
        cursor.execute("""
            INSERT INTO payment
            (invoice_id, lease_id, amount, payment_method, card_last4)
            VALUES (%s, %s, %s, 'CARD', %s)
        """, (invoice_id, lease_id, amount, last4))

        # Update invoice status
        cursor.execute("""
            UPDATE invoice
            SET status = 'PAID'
            WHERE invoice_id = %s
        """, (invoice_id,))

        conn.commit()
        conn.close()

        return True

    except Exception as e:
        conn.rollback()
        conn.close()
        print("Payment error:", e)
        return False
    

def get_monthly_payments(tenant_id):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT DATE_FORMAT(payment_date, '%Y-%m') AS month,
            SUM(amount) AS total
        FROM payment p
        JOIN lease l ON p.lease_id = l.lease_id
        WHERE l.tenant_id = %s
        GROUP BY month
        ORDER BY month
    """

    cursor.execute(query, (tenant_id,))
    data = cursor.fetchall()

    conn.close()
    
    return data




def get_neighbour_payment_totals(tenant_id):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT t.name, SUM(p.amount) AS total
        FROM payment p
        JOIN lease l ON p.lease_id = l.lease_id
        JOIN tenant t ON l.tenant_id = t.tenant_id
        JOIN apartment a ON l.apartment_id = a.apartment_id
        JOIN property pr ON a.property_id = pr.property_id
        WHERE pr.property_id = (
            SELECT pr2.property_id
            FROM lease l2
            JOIN apartment a2 ON l2.apartment_id = a2.apartment_id
            JOIN property pr2 ON a2.property_id = pr2.property_id
            WHERE l2.tenant_id = %s
            LIMIT 1
        )
        GROUP BY t.name
    """

    cursor.execute(query, (tenant_id,))
    data = cursor.fetchall()

    conn.close()
    return data