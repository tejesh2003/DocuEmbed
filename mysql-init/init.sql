-- Create the Temporal database if it doesn't exist
CREATE DATABASE IF NOT EXISTS temporal;
CREATE DATABASE IF NOT EXISTS temporal_visibility;

-- Grant privileges to the Temporal user
GRANT ALL PRIVILEGES ON temporal.* TO 'temporal'@'%';
GRANT ALL PRIVILEGES ON temporal_visibility.* TO 'temporal'@'%';

-- Apply changes
FLUSH PRIVILEGES;