Group B3, Rory Foley (23071664), Zuhaib Asif (23039419), Ethan Bransgrove (23079243), Rodrigo Garrabou Socias (23018284)

Prerequisites:
Python 3.7 or higher
MySQL Server

Libraries:
bcrypt 
mysql-connector-python 
matplotlib

pip install bcrypt mysql-connector-python matplotlib

To run:
python main.py

Database setup:
SQL dump found in project folder "ParagonDatabaseDump.sql"

DB_HOST = "127.0.0.1"
DB_USER = "your_username"
DB_PASSWORD = "your_password"
DB_NAME = "pams"

Logins:

Admins create new staff & front desk staff create new tenants

===================================================================
STAFF LOGINS:
===================================================================

ADMIN:
Name: admin1
Email: admin1@test.com
PWD: 123
ROLE: ADMIN


FRONT DESK GUY:
NAME: front1
Email: front1@test.com
PWD: 123
ROLE: FRONT_DESK


MAINTENANCE STAFF
Name: maintenance1
Email: maintenance1@test.com
PWD: 123
ROLE: MAINTENANCE_STAFF


FINANCE MANAGER
Name: finance1
Email: finance1@test.com
PWD: 123
ROLE: FINANCE_MANAGER


MANAGER
Name: manager1
Email: manager1@test.com
PWD: 123
ROLE: MANAGER


===================================================================
TENANTS LOGINS:
===================================================================

Name: Will
Email: will@test.com
PWD: 123

Name: John Smith
Email: smithy@test.com
PWD: 123

Name: Sophie
Email: sophie@test.com
PWD: 123

Name: Bobby
Email: bobby@test.com
PWD: 123

Name: Greg
Email: greg@test.com
PWD: 123
