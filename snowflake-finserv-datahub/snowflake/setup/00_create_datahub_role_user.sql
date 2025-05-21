-- File: snowflake/setup/00_create_datahub_role_user.sql
-- Purpose: Create a DataHub-specific role and user in Snowflake for metadata ingestion

-- Use ACCOUNTADMIN to ensure sufficient privileges
USE ROLE ACCOUNTADMIN;

-- Create a dedicated warehouse for DataHub operations
CREATE WAREHOUSE IF NOT EXISTS DATAHUB_WH 
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    COMMENT = 'Warehouse for DataHub metadata ingestion from Snowflake';

-- Create a DataHub-specific role
CREATE ROLE IF NOT EXISTS DATAHUB_ROLE;
GRANT USAGE ON WAREHOUSE DATAHUB_WH TO ROLE DATAHUB_ROLE;

-- Create a DataHub-specific user
-- Note: Replace '<your-secure-password>' with a strong password
CREATE USER IF NOT EXISTS DATAHUB_USER
    PASSWORD = '<your-secure-password>'
    DEFAULT_ROLE = DATAHUB_ROLE
    DEFAULT_WAREHOUSE = DATAHUB_WH
    COMMENT = 'User for DataHub metadata ingestion';

-- Grant the DataHub role to the DataHub user
GRANT ROLE DATAHUB_ROLE TO USER DATAHUB_USER;

-- Grant ACCOUNTADMIN to DATAHUB_ROLE for initial setup
-- Note: This is temporary and will be revoked after setup is complete
GRANT ROLE ACCOUNTADMIN TO ROLE DATAHUB_ROLE;

-- Output the created objects
SELECT 'DataHub role and user created successfully' AS STATUS;
