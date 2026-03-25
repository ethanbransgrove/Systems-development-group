from database import get_connection
from datetime import datetime, timedelta

def get_active_leases(branch_id):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT l.lease_id,
        t.name AS tenant_name,
        a.apartment_number,
        l.monthly_rent
    FROM lease l
    JOIN tenant t ON l.tenant_id = t.tenant_id
    JOIN apartment a ON l.apartment_id = a.apartment_id
    JOIN property p ON a.property_id = p.property_id
    WHERE l.status = 'ACTIVE'
    AND p.branch_id = %s
    """

    cursor.execute(query, (branch_id,))
    leases = cursor.fetchall()
    conn.close()

    return leases


def add_one_month(date_obj):
    
    """
    When sending out an invoice to a tenant the date must be handled automatically which this helps to do.
    """

    month = date_obj.month + 1
    year = date_obj.year

    if month > 12:
        month = 1
        year += 1

    # Handle month length differences
    day = min(date_obj.day, [31,
                             29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
                             31, 30, 31, 30,
                             31, 31, 30, 31,
                             30, 31][month - 1])

    return date_obj.replace(year=year, month=month, day=day)


def generate_next_invoice(lease_id):

    """
    Finance staff send out invoices to their assigned tenants and buildings.
    """

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Get lease details
        cursor.execute("""
            SELECT start_date, monthly_rent
            FROM lease
            WHERE lease_id = %s
        """, (lease_id,))

        lease = cursor.fetchone()

        if not lease:
            raise Exception("Lease not found")

        lease_start = lease["start_date"]
        rent = lease["monthly_rent"]

        # Check last invoice
        cursor.execute("""
            SELECT period_end
            FROM invoice
            WHERE lease_id = %s
            ORDER BY period_end DESC
            LIMIT 1
        """, (lease_id,))

        last_invoice = cursor.fetchone()

        if last_invoice:
            period_start = last_invoice["period_end"] + timedelta(days=1)
        else:
            period_start = lease_start

        # Calculate end date (1 month - 1 day)
        next_month = add_one_month(period_start)
        period_end = next_month - timedelta(days=1)

        # Due date (5 days after start)
        due_date = period_start + timedelta(days=5)

        # Insert invoice
        cursor.execute("""
            INSERT INTO invoice
            (lease_id, period_start, period_end, amount_due, due_date)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            lease_id,
            period_start,
            period_end,
            rent,
            due_date
        ))

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        conn.rollback()
        conn.close()
        print("Invoice generation error:", e)
        return False
    

def get_all_payments():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT p.payment_id, p.amount, payment_date, t.name AS tenant_name
        FROM payment p
        JOIN lease l ON p.lease_id = l.lease_id
        JOIN tenant t ON l.tenant_id = t.tenant_id
        ORDER BY p.payment_date DESC
    """

    cursor.execute(query)
    data = cursor.fetchall()

    conn.close()
    return data


def get_all_invoices():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT i.invoice_id, i.amount_due, i.due_date, i.status, t.name AS tenant_name
        FROM invoice i
        JOIN lease l ON i.lease_id = l.lease_id
        JOIN tenant t ON l.tenant_id = t.tenant_id
        ORDER BY i.due_date DESC
    """

    cursor.execute(query)
    data = cursor.fetchall()

    conn.close()
    return data


def get_outstanding_balance():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT SUM(amount_due)
        FROM invoice
        WHERE status != 'PAID'
    """)

    result = cursor.fetchone()[0]

    conn.close()
    return result if result else 0


def get_late_payment_count():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM invoice
        WHERE status = 'LATE'
    """)

    count = cursor.fetchone()[0]

    conn.close()
    return count


def get_monthly_revenue():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DATE_FORMAT(payment_date, '%Y-%m') AS month, SUM(amount)
        FROM payment
        GROUP BY month
        ORDER BY month
    """)

    data = cursor.fetchall()

    conn.close()
    return data

