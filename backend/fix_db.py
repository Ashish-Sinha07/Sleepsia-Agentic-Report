"""
Alternative database setup using subprocess
"""
import subprocess
import sys

sql_commands = """
DROP USER IF EXISTS 'sleepsia'@'localhost';
CREATE DATABASE IF NOT EXISTS sleepsia_reporting;
CREATE USER 'sleepsia'@'localhost' IDENTIFIED BY 'sleepsia';
GRANT ALL PRIVILEGES ON sleepsia_reporting.* TO 'sleepsia'@'localhost';
FLUSH PRIVILEGES;
"""

print("Setting up database...")
try:
    # Use echo to pipe SQL commands to mysql
    process = subprocess.Popen(
        ['mysql', '-u', 'root', '-proot'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    stdout, stderr = process.communicate(input=sql_commands, timeout=10)

    if process.returncode == 0:
        print("✓ Database and user created successfully!")
        print("\nNow running ETL loader...")
        subprocess.run(
            [sys.executable, 'etl/loader.py'],
            check=False
        )
    else:
        print(f"✗ Failed: {stderr}")

except subprocess.TimeoutExpired:
    process.kill()
    print("✗ Command timed out")
except Exception as e:
    print(f"✗ Error: {e}")
