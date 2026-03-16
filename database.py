import mysql.connector
from config import *

"""
Connects the app to the database to facilitate SQL queries and updating the database
"""

def get_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )