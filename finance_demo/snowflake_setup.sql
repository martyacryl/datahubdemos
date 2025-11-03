-- Finance Analytics Demo - Snowflake Database Setup
-- This script creates the database, schema, and tables for the finance analytics demo

-- Create database
CREATE DATABASE IF NOT EXISTS FINANCE_ANALYTICS;

-- Use the database
USE DATABASE FINANCE_ANALYTICS;

-- Create BRONZE schema for raw data
CREATE SCHEMA IF NOT EXISTS BRONZE;

-- Create revenue_transactions table (raw transaction data)
CREATE TABLE IF NOT EXISTS FINANCE_ANALYTICS.BRONZE.revenue_transactions (
    transaction_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    amount DECIMAL(18, 2) NOT NULL,
    transaction_date DATE NOT NULL,
    region VARCHAR(50),
    currency VARCHAR(10) DEFAULT 'USD',
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Create customer_info table (customer master data with PII)
CREATE TABLE IF NOT EXISTS FINANCE_ANALYTICS.BRONZE.customer_info (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_name VARCHAR(200) NOT NULL,
    email VARCHAR(200),
    phone VARCHAR(50),
    address VARCHAR(500),
    country VARCHAR(100),
    customer_segment VARCHAR(50),
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Insert sample revenue transaction data
INSERT INTO FINANCE_ANALYTICS.BRONZE.revenue_transactions 
(transaction_id, customer_id, product_id, amount, transaction_date, region, currency)
VALUES
('TXN001', 'CUST001', 'PROD001', 1500.00, '2024-01-15', 'North America', 'USD'),
('TXN002', 'CUST002', 'PROD002', 2500.00, '2024-01-16', 'Europe', 'EUR'),
('TXN003', 'CUST001', 'PROD003', 3200.00, '2024-01-17', 'North America', 'USD'),
('TXN004', 'CUST003', 'PROD001', 1800.00, '2024-01-18', 'Asia Pacific', 'USD'),
('TXN005', 'CUST002', 'PROD002', 2750.00, '2024-01-19', 'Europe', 'EUR'),
('TXN006', 'CUST004', 'PROD003', 4100.00, '2024-01-20', 'North America', 'USD'),
('TXN007', 'CUST001', 'PROD001', 1200.00, '2024-01-21', 'North America', 'USD'),
('TXN008', 'CUST005', 'PROD002', 3000.00, '2024-01-22', 'Europe', 'EUR'),
('TXN009', 'CUST003', 'PROD003', 2800.00, '2024-01-23', 'Asia Pacific', 'USD'),
('TXN010', 'CUST002', 'PROD001', 1900.00, '2024-01-24', 'Europe', 'EUR');

-- Insert sample customer data (with PII)
INSERT INTO FINANCE_ANALYTICS.BRONZE.customer_info
(customer_id, customer_name, email, phone, address, country, customer_segment)
VALUES
('CUST001', 'John Smith', 'john.smith@example.com', '+1-555-0101', '123 Main St, New York, NY 10001', 'United States', 'Enterprise'),
('CUST002', 'Maria Garcia', 'maria.garcia@example.com', '+34-555-0202', 'Calle Gran Via 45, Madrid 28013', 'Spain', 'Mid-Market'),
('CUST003', 'David Chen', 'david.chen@example.com', '+86-555-0303', '123 Business District, Shanghai 200000', 'China', 'Enterprise'),
('CUST004', 'Sarah Johnson', 'sarah.johnson@example.com', '+1-555-0404', '456 Oak Ave, Los Angeles, CA 90001', 'United States', 'SMB'),
('CUST005', 'Pierre Dubois', 'pierre.dubois@example.com', '+33-555-0505', '78 Rue de Rivoli, Paris 75001', 'France', 'Mid-Market');

-- Verify data
SELECT COUNT(*) as transaction_count FROM FINANCE_ANALYTICS.BRONZE.revenue_transactions;
SELECT COUNT(*) as customer_count FROM FINANCE_ANALYTICS.BRONZE.customer_info;

