from database import get_connection


def get_occupancy_by_location():

    """
    Returns occupancy statistics grouped by city.
    Joins: apartment -> property -> branch -> city
    Uses apartment.status to determine occupied vs available.
    """

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            c.name AS city,
            COUNT(a.apartment_id) AS total_apartments,
            SUM(CASE WHEN a.status = 'OCCUPIED' THEN 1 ELSE 0 END) AS occupied,
            SUM(CASE WHEN a.status = 'AVAILABLE' THEN 1 ELSE 0 END) AS vacant
        FROM apartment a
        JOIN property p ON a.property_id = p.property_id
        JOIN branch b ON p.branch_id = b.branch_id
        JOIN city c ON b.city_id = c.city_id
        GROUP BY c.name
        ORDER BY c.name
    """)

    data = cursor.fetchall()
    conn.close()
    return data


def get_performance_report_by_location():

    """
    Returns financial performance per city.
    Shows collected rent, pending rent and late payment count.
    Joins: invoice -> lease -> apartment -> property -> branch -> city
    """

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            c.name AS city,
            COALESCE(SUM(CASE WHEN i.status = 'PAID' THEN i.amount_due ELSE 0 END), 0) AS collected,
            COALESCE(SUM(CASE WHEN i.status IN ('PENDING', 'LATE') THEN i.amount_due ELSE 0 END), 0) AS pending,
            COUNT(CASE WHEN i.status = 'LATE' THEN 1 END) AS late_payments
        FROM city c
        JOIN branch b ON c.city_id = b.city_id
        JOIN property p ON b.branch_id = p.branch_id
        JOIN apartment a ON p.property_id = a.property_id
        LEFT JOIN lease l ON a.apartment_id = l.apartment_id
        LEFT JOIN invoice i ON l.lease_id = i.lease_id
        GROUP BY c.name
        ORDER BY c.name
    """)

    data = cursor.fetchall()
    conn.close()
    return data


def get_all_cities():

    """
    Returns all cities from the city table.
    """

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT city_id, name FROM city ORDER BY name")

    cities = cursor.fetchall()
    conn.close()
    return cities


def add_new_city(city_name, branch_name, branch_address):

    """
    Expands the business to a new city by adding a city record and a branch.
    If the city already exists, just adds the branch to it.
    Returns True on success, False if branch name already exists.
    """

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Check branch name is unique
    cursor.execute("SELECT branch_id FROM branch WHERE name = %s", (branch_name,))
    if cursor.fetchone():
        conn.close()
        return False

    # Get or create the city
    cursor.execute("SELECT city_id FROM city WHERE name = %s", (city_name,))
    city = cursor.fetchone()

    if city:
        city_id = city["city_id"]
    else:
        cursor.execute("INSERT INTO city (name) VALUES (%s)", (city_name,))
        city_id = cursor.lastrowid

    # Insert the branch
    cursor.execute("""
        INSERT INTO branch (city_id, name, address)
        VALUES (%s, %s, %s)
    """, (city_id, branch_name, branch_address))

    conn.commit()
    conn.close()
    return True


def get_leases_expiring_soon():

    """
    Returns leases expiring within the next 60 days.
    Joins: lease -> tenant, apartment -> property -> branch -> city
    """

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            t.name AS tenant_name,
            a.apartment_number,
            c.name AS city,
            l.end_date
        FROM lease l
        JOIN tenant t ON l.tenant_id = t.tenant_id
        JOIN apartment a ON l.apartment_id = a.apartment_id
        JOIN property p ON a.property_id = p.property_id
        JOIN branch b ON p.branch_id = b.branch_id
        JOIN city c ON b.city_id = c.city_id
        WHERE l.status = 'ACTIVE'
        AND l.end_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 60 DAY)
        ORDER BY l.end_date ASC
    """)

    data = cursor.fetchall()
    conn.close()
    return data