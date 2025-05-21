-- File: snowflake/setup/01_grant_privileges.sql
-- Purpose: Grant necessary privileges to the DataHub role for metadata ingestion

-- Use ACCOUNTADMIN for granting privileges
USE ROLE ACCOUNTADMIN;

-- Grant privileges for metadata access
-- These grants allow DataHub to read schema information 
-- and extract lineage and usage statistics

-- Grant access to account usage to enable lineage and usage stats collection
GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE TO ROLE DATAHUB_ROLE;

-- Create a database for the Financial Services demo
CREATE DATABASE IF NOT EXISTS FINSERV_DEMO;
GRANT USAGE ON DATABASE FINSERV_DEMO TO ROLE DATAHUB_ROLE;

-- Grant schema access permissions
GRANT USAGE ON ALL SCHEMAS IN DATABASE FINSERV_DEMO TO ROLE DATAHUB_ROLE;
GRANT USAGE ON FUTURE SCHEMAS IN DATABASE FINSERV_DEMO TO ROLE DATAHUB_ROLE;

-- Grant table access permissions for metadata extraction
GRANT SELECT ON ALL TABLES IN DATABASE FINSERV_DEMO TO ROLE DATAHUB_ROLE;
GRANT SELECT ON FUTURE TABLES IN DATABASE FINSERV_DEMO TO ROLE DATAHUB_ROLE;

-- Grant view access permissions for metadata extraction
GRANT SELECT ON ALL VIEWS IN DATABASE FINSERV_DEMO TO ROLE DATAHUB_ROLE;
GRANT SELECT ON FUTURE VIEWS IN DATABASE FINSERV_DEMO TO ROLE DATAHUB_ROLE;

-- Grant access to dynamic tables if available
GRANT SELECT ON ALL DYNAMIC TABLES IN DATABASE FINSERV_DEMO TO ROLE DATAHUB_ROLE;
GRANT SELECT ON FUTURE DYNAMIC TABLES IN DATABASE FINSERV_DEMO TO ROLE DATAHUB_ROLE;

-- Grant access to external tables if available
GRANT SELECT ON ALL EXTERNAL TABLES IN DATABASE FINSERV_DEMO TO ROLE DATAHUB_ROLE;
GRANT SELECT ON FUTURE EXTERNAL TABLES IN DATABASE FINSERV_DEMO TO ROLE DATAHUB_ROLE;

-- Revoke the temporary accountadmin access
REVOKE ROLE ACCOUNTADMIN FROM ROLE DATAHUB_ROLE;

-- Output status
SELECT 'DataHub privileges granted successfully' AS STATUS;
