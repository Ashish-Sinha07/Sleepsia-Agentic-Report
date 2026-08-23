DROP USER IF EXISTS 'sleepsia'@'localhost';
CREATE DATABASE IF NOT EXISTS sleepsia_reporting;
CREATE USER 'sleepsia'@'localhost' IDENTIFIED BY 'sleepsia';
GRANT ALL PRIVILEGES ON sleepsia_reporting.* TO 'sleepsia'@'localhost';
FLUSH PRIVILEGES;
SELECT 'Database and user created successfully' as Status;
