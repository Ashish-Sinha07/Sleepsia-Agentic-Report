-- Create database
CREATE DATABASE IF NOT EXISTS sleepsia_reporting;

-- Create user
CREATE USER IF NOT EXISTS 'sleepsia'@'localhost' IDENTIFIED BY 'sleepsia';

-- Grant privileges
GRANT ALL PRIVILEGES ON sleepsia_reporting.* TO 'sleepsia'@'localhost';

-- Apply changes
FLUSH PRIVILEGES;

-- Verify
SELECT 'Database and user setup complete' as Status;
