-- ==============================================
-- DataHub Snowflake Permissions Setup
-- ==============================================
-- Execute these commands as ACCOUNTADMIN or user with MANAGE GRANTS privilege
-- Based on: https://docs.datahub.com/docs/generated/ingestion/sources/snowflake

-- Step 1: Create DataHub Role
CREATE OR REPLACE ROLE DATAHUB_ROLE;

-- Step 2: Grant Warehouse Access
-- Replace <YOUR_WAREHOUSE> with your actual warehouse name
GRANT OPERATE, USAGE ON WAREHOUSE "<YOUR_WAREHOUSE>" TO ROLE DATAHUB_ROLE;

-- Step 3: Grant Database Access
-- Replace <YOUR_DATABASE> with your actual database names
-- Repeat for each database you want to ingest
GRANT USAGE ON DATABASE "<YOUR_DATABASE>" TO ROLE DATAHUB_ROLE;
GRANT USAGE ON ALL SCHEMAS IN DATABASE "<YOUR_DATABASE>" TO ROLE DATAHUB_ROLE;
GRANT USAGE ON FUTURE SCHEMAS IN DATABASE "<YOUR_DATABASE>" TO ROLE DATAHUB_ROLE;

-- Step 4: Grant Table and View Access
-- For basic metadata extraction (without profiling)
GRANT REFERENCES ON ALL TABLES IN DATABASE "<YOUR_DATABASE>" TO ROLE DATAHUB_ROLE;
GRANT REFERENCES ON FUTURE TABLES IN DATABASE "<YOUR_DATABASE>" TO ROLE DATAHUB_ROLE;
GRANT REFERENCES ON ALL EXTERNAL TABLES IN DATABASE "<YOUR_DATABASE>" TO ROLE DATAHUB_ROLE;
GRANT REFERENCES ON FUTURE EXTERNAL TABLES IN DATABASE "<YOUR_DATABASE>" TO ROLE DATAHUB_ROLE;
GRANT REFERENCES ON ALL VIEWS IN DATABASE "<YOUR_DATABASE>" TO ROLE DATAHUB_ROLE;
GRANT REFERENCES ON FUTURE VIEWS IN DATABASE "<YOUR_DATABASE>" TO ROLE DATAHUB_ROLE;

-- For profiling (optional - more permissive but enables column statistics)
-- Uncomment if you want to enable profiling in the configuration
-- GRANT SELECT ON ALL TABLES IN DATABASE "<YOUR_DATABASE>" TO ROLE DATAHUB_ROLE;
-- GRANT SELECT ON FUTURE TABLES IN DATABASE "<YOUR_DATABASE>" TO ROLE DATAHUB_ROLE;
-- GRANT SELECT ON ALL EXTERNAL TABLES IN DATABASE "<YOUR_DATABASE>" TO ROLE DATAHUB_ROLE;
-- GRANT SELECT ON FUTURE EXTERNAL TABLES IN DATABASE "<YOUR_DATABASE>" TO ROLE DATAHUB_ROLE;
-- GRANT SELECT ON ALL VIEWS IN DATABASE "<YOUR_DATABASE>" TO ROLE DATAHUB_ROLE;
-- GRANT SELECT ON FUTURE VIEWS IN DATABASE "<YOUR_DATABASE>" TO ROLE DATAHUB_ROLE;

-- Step 5: Grant Stream Access (if using Snowflake Streams)
GRANT SELECT ON ALL STREAMS IN DATABASE "<YOUR_DATABASE>" TO ROLE DATAHUB_ROLE;
GRANT SELECT ON FUTURE STREAMS IN DATABASE "<YOUR_DATABASE>" TO ROLE DATAHUB_ROLE;

-- Step 6: Grant Access to Account Usage (for lineage and usage statistics)
-- This is required for table lineage and usage statistics (Snowflake Enterprise+ only)
GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE TO ROLE DATAHUB_ROLE;

-- Step 7: Create DataHub User
CREATE OR REPLACE USER DATAHUB_USER
    PASSWORD = '<STRONG_PASSWORD>'  -- Replace with a strong password
    DEFAULT_ROLE = DATAHUB_ROLE
    DEFAULT_WAREHOUSE = '<YOUR_WAREHOUSE>'
    COMMENT = 'DataHub service user for metadata ingestion';

-- Step 8: Grant Role to User
GRANT ROLE DATAHUB_ROLE TO USER DATAHUB_USER;

-- ==============================================
-- Verification Queries
-- ==============================================
-- Run these to verify the setup

-- Check role grants
SHOW GRANTS TO ROLE DATAHUB_ROLE;

-- Check user details
DESCRIBE USER DATAHUB_USER;

-- Test queries (run as DATAHUB_USER to verify access)
-- USE ROLE DATAHUB_ROLE;
-- USE WAREHOUSE <YOUR_WAREHOUSE>;
-- SHOW DATABASES;
-- SHOW SCHEMAS IN DATABASE "<YOUR_DATABASE>";
-- SHOW TABLES IN DATABASE "<YOUR_DATABASE>";
