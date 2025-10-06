-- Snowflake DMF Demo Setup
-- This script creates sample data and a DMF for the DataHub demo

-- Create demo database and schema
CREATE DATABASE IF NOT EXISTS DEMO_DB;
USE DATABASE DEMO_DB;

CREATE SCHEMA IF NOT EXISTS DEMO_SCHEMA;
USE SCHEMA DEMO_SCHEMA;

-- Create sample customers table
CREATE OR REPLACE TABLE CUSTOMERS (
    CUSTOMER_ID NUMBER,
    FIRST_NAME VARCHAR(50),
    LAST_NAME VARCHAR(50),
    EMAIL VARCHAR(100),
    PHONE VARCHAR(20),
    CREATED_DATE DATE,
    STATUS VARCHAR(20)
);

-- Insert sample data with some intentional nulls for testing
INSERT INTO CUSTOMERS VALUES
(1, 'John', 'Doe', 'john.doe@email.com', '555-0101', '2024-01-15', 'ACTIVE'),
(2, 'Jane', 'Smith', 'jane.smith@email.com', '555-0102', '2024-01-16', 'ACTIVE'),
(3, 'Bob', 'Johnson', NULL, '555-0103', '2024-01-17', 'ACTIVE'),  -- NULL email
(4, 'Alice', 'Brown', 'alice.brown@email.com', NULL, '2024-01-18', 'ACTIVE'),  -- NULL phone
(5, 'Charlie', 'Wilson', 'charlie.wilson@email.com', '555-0105', '2024-01-19', 'INACTIVE'),
(6, 'Diana', 'Davis', NULL, '555-0106', '2024-01-20', 'ACTIVE'),  -- NULL email
(7, 'Eve', 'Miller', 'eve.miller@email.com', '555-0107', '2024-01-21', 'ACTIVE'),
(8, 'Frank', 'Garcia', 'frank.garcia@email.com', '555-0108', '2024-01-22', 'ACTIVE'),
(9, 'Grace', 'Martinez', NULL, '555-0109', '2024-01-23', 'ACTIVE'),  -- NULL email
(10, 'Henry', 'Anderson', 'henry.anderson@email.com', '555-0110', '2024-01-24', 'ACTIVE');

-- Verify the data
SELECT 
    COUNT(*) as total_customers,
    COUNT(EMAIL) as customers_with_email,
    COUNT(*) - COUNT(EMAIL) as customers_without_email
FROM CUSTOMERS;

-- Create a DMF to monitor null values in the EMAIL column
-- This will create an expectation that no more than 2 customers should have null emails
ALTER TABLE CUSTOMERS
    MODIFY DATA METRIC FUNCTION SNOWFLAKE.CORE.NULL_COUNT ON (EMAIL)
    ADD EXPECTATION email_null_check CHECK (VALUE <= 2);

-- Create another DMF to monitor data freshness
-- This will create an expectation that the data should be fresh (less than 7 days old)
ALTER TABLE CUSTOMERS
    MODIFY DATA METRIC FUNCTION SNOWFLAKE.CORE.FRESHNESS ON (CREATED_DATE)
    ADD EXPECTATION data_freshness_check CHECK (VALUE <= 7);

-- Evaluate the expectations to see current status
SELECT *
FROM TABLE(SYSTEM$EVALUATE_DATA_QUALITY_EXPECTATIONS(
    REF_ENTITY_NAME => 'DEMO_DB.DEMO_SCHEMA.CUSTOMERS'));

-- Show the DMF associations
SELECT 
    TABLE_NAME,
    COLUMN_NAME,
    METRIC_FUNCTION_NAME,
    EXPECTATION_NAME,
    EXPECTATION_EXPRESSION
FROM SNOWFLAKE.LOCAL.DATA_QUALITY_MONITORING_RESULTS_RAW
WHERE TABLE_NAME = 'CUSTOMERS'
ORDER BY CREATED_ON DESC;

-- Display success message
SELECT 'Snowflake DMF Demo Setup Complete!' as STATUS,
       'Run the Python script to extract DMFs and ingest into DataHub' as NEXT_STEP;
