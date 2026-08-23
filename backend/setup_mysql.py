"""
Database setup script - Creates database and user for Sleepsia
"""
import pymysql
import sys
from pathlib import Path

# Database configuration
DB_HOST = 'localhost'
DB_PORT = 3306
DB_USER_ADMIN = 'root'
DB_PASSWORD_ADMIN = 'root'  # MySQL root password
DB_USER = 'sleepsia'
DB_PASSWORD = 'sleepsia'
DB_NAME = 'sleepsia_reporting'

print("=" * 60)
print("Sleepsia Database Setup")
print("=" * 60)

# Try to connect to MySQL
try:
    print(f"\n[1/4] Connecting to MySQL as {DB_USER_ADMIN}...")
    connection = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER_ADMIN,
        password=DB_PASSWORD_ADMIN,
    )
    cursor = connection.cursor()
    print("✓ Connected successfully")

    # Create database
    print(f"\n[2/4] Creating database '{DB_NAME}'...")
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}`")
    print(f"✓ Database '{DB_NAME}' created/verified")

    # Create user
    print(f"\n[3/4] Creating user '{DB_USER}'@'localhost'...")
    cursor.execute(f"DROP USER IF EXISTS '{DB_USER}'@'localhost'")
    cursor.execute(f"CREATE USER '{DB_USER}'@'localhost' IDENTIFIED BY '{DB_PASSWORD}'")
    print(f"✓ User '{DB_USER}' created")

    # Grant privileges
    print(f"\n[4/4] Granting privileges...")
    cursor.execute(f"GRANT ALL PRIVILEGES ON `{DB_NAME}`.* TO '{DB_USER}'@'localhost'")
    cursor.execute("FLUSH PRIVILEGES")
    print("✓ Privileges granted")

    connection.commit()
    cursor.close()
    connection.close()

    print("\n" + "=" * 60)
    print("✓ Database setup completed successfully!")
    print("=" * 60)
    print(f"\nConnection details:")
    print(f"  Host:     {DB_HOST}")
    print(f"  Port:     {DB_PORT}")
    print(f"  Database: {DB_NAME}")
    print(f"  User:     {DB_USER}")
    print(f"  Password: {DB_PASSWORD}")
    print("\nNow run: python etl/loader.py")
    print("=" * 60)

except pymysql.err.OperationalError as e:
    print(f"\n✗ Connection failed: {e}")
    print("\nTroubleshooting steps:")
    print("1. Make sure MySQL is running")
    print("2. Check if MySQL is on port 3306")
    print("3. If root has a password, edit this file and set DB_PASSWORD_ADMIN")
    print("\nTo check MySQL status (Windows):")
    print("  Get-Service MySQL* | Select Status")
    print("\nTo start MySQL (Windows):")
    print("  net start MySQL80  (or your MySQL version)")
    sys.exit(1)

except Exception as e:
    print(f"\n✗ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
