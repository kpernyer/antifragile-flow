-- PostgreSQL initialization script for antifragile-flow application
-- This script sets up the initial database structure for inbox and user data

-- Create additional databases if they don't exist
SELECT 'CREATE DATABASE inbox' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'inbox')\gexec
SELECT 'CREATE DATABASE users' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'users')\gexec

-- Connect to the main antifragile database
\c antifragile;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS inbox;
CREATE SCHEMA IF NOT EXISTS users;
CREATE SCHEMA IF NOT EXISTS audit;

-- Grant permissions
GRANT USAGE ON SCHEMA inbox TO app_user;
GRANT USAGE ON SCHEMA users TO app_user;
GRANT USAGE ON SCHEMA audit TO app_user;

GRANT CREATE ON SCHEMA inbox TO app_user;
GRANT CREATE ON SCHEMA users TO app_user;
GRANT CREATE ON SCHEMA audit TO app_user;

-- Set search path
ALTER USER app_user SET search_path = public, inbox, users, audit;

-- Basic audit log table for tracking changes
CREATE TABLE IF NOT EXISTS audit.change_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name VARCHAR(100) NOT NULL,
    operation VARCHAR(10) NOT NULL,
    old_data JSONB,
    new_data JSONB,
    changed_by VARCHAR(100),
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Grant permissions on audit table
GRANT SELECT, INSERT ON audit.change_log TO app_user;

-- Create index for performance
CREATE INDEX IF NOT EXISTS idx_change_log_table_time ON audit.change_log(table_name, changed_at);
CREATE INDEX IF NOT EXISTS idx_change_log_operation ON audit.change_log(operation);
