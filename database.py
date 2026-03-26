import mysql.connector
from mysql.connector import Error
from config import *

"""
Connects the app to the database to facilitate SQL queries and updating the database
Ensures safe database connections
"""

def get_connection():
    try:
        return mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
    except Error as e:
        raise Exception("Database connection failed")