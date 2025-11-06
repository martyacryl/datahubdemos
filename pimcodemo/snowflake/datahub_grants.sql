-- ============================================================================
-- DataHub Snowflake Ingestion - Required Grants for PIMCO Demo
-- ============================================================================
-- This script grants all necessary permissions for DataHub to ingest metadata
-- from the PIMCO_DEMO database.
-- 
-- Database: PIMCO_DEMO
-- Warehouse: MSJDEMO
-- Run this as ACCOUNTADMIN
-- ============================================================================

USE ROLE ACCOUNTADMIN;
USE DATABASE PIMCO_DEMO;
USE WAREHOUSE MSJDEMO;

-- ============================================================================
-- Step 1: Create DataHub Role (if it doesn't exist)
-- ============================================================================
CREATE ROLE IF NOT EXISTS PIMCO_DATAHUB_ROLE;
COMMENT ON ROLE PIMCO_DATAHUB_ROLE IS 'Role for DataHub metadata ingestion - PIMCO Demo';

-- ============================================================================
-- Step 2: Grant Warehouse Privileges
-- ============================================================================
-- Replace 'MSJDEMO' with your actual warehouse name
GRANT OPERATE, USAGE ON WAREHOUSE "MSJDEMO" TO ROLE PIMCO_DATAHUB_ROLE;

-- ============================================================================
-- Step 3: Grant Database and Schema Privileges
-- ============================================================================
-- Replace 'PIMCO_DEMO' with your actual database name
GRANT USAGE ON DATABASE "PIMCO_DEMO" TO ROLE PIMCO_DATAHUB_ROLE;

-- Grant usage on existing schemas
GRANT USAGE ON ALL SCHEMAS IN DATABASE "PIMCO_DEMO" TO ROLE PIMCO_DATAHUB_ROLE;

-- Grant usage on future schemas (for any new schemas created later)
GRANT USAGE ON FUTURE SCHEMAS IN DATABASE "PIMCO_DEMO" TO ROLE PIMCO_DATAHUB_ROLE;

-- ============================================================================
-- Step 4: Grant Object-Level Privileges - Tables
-- ============================================================================
-- Grant SELECT on all existing tables
GRANT SELECT ON ALL TABLES IN DATABASE "PIMCO_DEMO" TO ROLE PIMCO_DATAHUB_ROLE;

-- Grant SELECT on future tables
GRANT SELECT ON FUTURE TABLES IN DATABASE "PIMCO_DEMO" TO ROLE PIMCO_DATAHUB_ROLE;

-- Grant REFERENCES on all existing tables
GRANT REFERENCES ON ALL TABLES IN DATABASE "PIMCO_DEMO" TO ROLE PIMCO_DATAHUB_ROLE;

-- Grant REFERENCES on future tables
GRANT REFERENCES ON FUTURE TABLES IN DATABASE "PIMCO_DEMO" TO ROLE PIMCO_DATAHUB_ROLE;

-- ============================================================================
-- Step 5: Grant Object-Level Privileges - Views
-- ============================================================================
-- Grant SELECT on all existing views
GRANT SELECT ON ALL VIEWS IN DATABASE "PIMCO_DEMO" TO ROLE PIMCO_DATAHUB_ROLE;

-- Grant SELECT on future views
GRANT SELECT ON FUTURE VIEWS IN DATABASE "PIMCO_DEMO" TO ROLE PIMCO_DATAHUB_ROLE;

-- Grant REFERENCES on all existing views
GRANT REFERENCES ON ALL VIEWS IN DATABASE "PIMCO_DEMO" TO ROLE PIMCO_DATAHUB_ROLE;

-- Grant REFERENCES on future views
GRANT REFERENCES ON FUTURE VIEWS IN DATABASE "PIMCO_DEMO" TO ROLE PIMCO_DATAHUB_ROLE;

-- ============================================================================
-- Step 6: Grant Object-Level Privileges - External Tables
-- ============================================================================
-- Grant SELECT on all existing external tables
GRANT SELECT ON ALL EXTERNAL TABLES IN DATABASE "PIMCO_DEMO" TO ROLE PIMCO_DATAHUB_ROLE;

-- Grant SELECT on future external tables
GRANT SELECT ON FUTURE EXTERNAL TABLES IN DATABASE "PIMCO_DEMO" TO ROLE PIMCO_DATAHUB_ROLE;

-- Grant REFERENCES on all existing external tables
GRANT REFERENCES ON ALL EXTERNAL TABLES IN DATABASE "PIMCO_DEMO" TO ROLE PIMCO_DATAHUB_ROLE;

-- Grant REFERENCES on future external tables
GRANT REFERENCES ON FUTURE EXTERNAL TABLES IN DATABASE "PIMCO_DEMO" TO ROLE PIMCO_DATAHUB_ROLE;

-- ============================================================================
-- Step 7: Grant Object-Level Privileges - Dynamic Tables
-- ============================================================================
-- Grant SELECT on all existing dynamic tables
GRANT SELECT ON ALL DYNAMIC TABLES IN DATABASE "PIMCO_DEMO" TO ROLE PIMCO_DATAHUB_ROLE;

-- Grant SELECT on future dynamic tables
GRANT SELECT ON FUTURE DYNAMIC TABLES IN DATABASE "PIMCO_DEMO" TO ROLE PIMCO_DATAHUB_ROLE;

-- Grant MONITOR on all existing dynamic tables (for lineage)
GRANT MONITOR ON ALL DYNAMIC TABLES IN DATABASE "PIMCO_DEMO" TO ROLE PIMCO_DATAHUB_ROLE;

-- Grant MONITOR on future dynamic tables
GRANT MONITOR ON FUTURE DYNAMIC TABLES IN DATABASE "PIMCO_DEMO" TO ROLE PIMCO_DATAHUB_ROLE;

-- ============================================================================
-- Step 8: Grant Access to Snowflake Account Usage Data
-- ============================================================================
-- This is required for DataHub to extract lineage and usage statistics
GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE TO ROLE PIMCO_DATAHUB_ROLE;

-- ============================================================================
-- Step 9: Grant Role to Your User (mstjohn)
-- ============================================================================
-- Grant PIMCO_DATAHUB_ROLE to your existing user for DataHub ingestion
GRANT ROLE PIMCO_DATAHUB_ROLE TO USER mstjohn;

-- ============================================================================
-- Step 10: Create DataHub User (Optional - Alternative to Step 9)
-- ============================================================================
-- If you prefer a dedicated DataHub user instead, uncomment below:
-- Replace '<your-password>' with a strong password

-- CREATE USER IF NOT EXISTS DATAHUB_USER
--   DISPLAY_NAME = 'DataHub'
--   PASSWORD = '<your-password>'
--   DEFAULT_ROLE = PIMCO_DATAHUB_ROLE
--   DEFAULT_WAREHOUSE = 'MSJDEMO';

-- GRANT ROLE PIMCO_DATAHUB_ROLE TO USER DATAHUB_USER;

-- ============================================================================
-- Verification Queries
-- ============================================================================
-- Run these to verify grants were applied correctly:

-- Show all grants for PIMCO_DATAHUB_ROLE
SHOW GRANTS TO ROLE PIMCO_DATAHUB_ROLE;

-- Show grants on database
SHOW GRANTS ON DATABASE "PIMCO_DEMO";

-- Show grants on warehouse
SHOW GRANTS ON WAREHOUSE "MSJDEMO";

-- Show roles granted to user
SHOW GRANTS TO USER mstjohn;

-- Verify role has access to schemas
SHOW GRANTS ON SCHEMA "PIMCO_DEMO"."BRZ_001";
SHOW GRANTS ON SCHEMA "PIMCO_DEMO"."SLV_009";
SHOW GRANTS ON SCHEMA "PIMCO_DEMO"."GLD_003";

-- ============================================================================
-- Usage Instructions:
-- ============================================================================
-- 1. Run this entire script as ACCOUNTADMIN in Snowflake
-- 2. After running, use PIMCO_DATAHUB_ROLE in your DataHub ingestion config:
--    role: PIMCO_DATAHUB_ROLE
--    username: mstjohn (or DATAHUB_USER if you created a dedicated user)
--    password: your password
--    warehouse: MSJDEMO
--    database: PIMCO_DEMO
--
-- 3. These grants allow DataHub to:
--    - Read metadata from tables, views, and dynamic tables
--    - Extract schema information
--    - Build lineage relationships
--    - Access usage statistics from SNOWFLAKE database
--
-- ============================================================================
-- Cleanup (if needed):
-- ============================================================================
-- If you need to revoke these grants later:
-- 
-- REVOKE ALL PRIVILEGES ON DATABASE "PIMCO_DEMO" FROM ROLE PIMCO_DATAHUB_ROLE;
-- REVOKE OPERATE, USAGE ON WAREHOUSE "MSJDEMO" FROM ROLE PIMCO_DATAHUB_ROLE;
-- REVOKE IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE FROM ROLE PIMCO_DATAHUB_ROLE;
-- REVOKE ROLE PIMCO_DATAHUB_ROLE FROM USER mstjohn;
-- DROP ROLE PIMCO_DATAHUB_ROLE;
--
-- ============================================================================
-- Setup Complete!
-- ============================================================================
-- You can now use PIMCO_DATAHUB_ROLE in your DataHub ingestion recipe.
-- Make sure to use role: PIMCO_DATAHUB_ROLE in your ingestion config.
-- ============================================================================

