-- PIMCO Municipal Bond Demo - Schema Setup
-- Opaque schema names to showcase DataHub context value

-- Create Bronze Schema (Raw Data)
CREATE SCHEMA IF NOT EXISTS BRZ_001;

-- Create Silver Schema (Cleaned Data)
CREATE SCHEMA IF NOT EXISTS SLV_009;

-- Create Gold Schema (Reporting Data)
CREATE SCHEMA IF NOT EXISTS GLD_003;

-- Bronze Schema: Raw Transaction Data
-- TX_0421: Raw bond transactions
CREATE TABLE IF NOT EXISTS BRZ_001.TX_0421 (
    TX_ID VARCHAR(50) PRIMARY KEY,
    TD_DATE DATE,
    STL_DATE DATE,
    PRN_AMT DECIMAL(18, 2),
    ISS_ID VARCHAR(50),
    BND_ID VARCHAR(50),
    TRD_TYPE VARCHAR(10),
    CUSIP VARCHAR(9),
    RAW_DATA VARIANT
);

-- REF_7832: Reference data for bonds
CREATE TABLE IF NOT EXISTS BRZ_001.REF_7832 (
    BND_ID VARCHAR(50) PRIMARY KEY,
    CUSIP VARCHAR(9),
    ISIN VARCHAR(12),
    MAT_DATE DATE,
    CPN_RATE DECIMAL(5, 3),
    CR_RT VARCHAR(5),
    ISS_TYPE VARCHAR(50),
    RAW_DESC VARIANT
);

-- ISS_5510: Issuer information
CREATE TABLE IF NOT EXISTS BRZ_001.ISS_5510 (
    ISS_ID VARCHAR(50) PRIMARY KEY,
    ISS_NAME VARCHAR(200),
    ISS_TYPE VARCHAR(50),
    STATE_CD VARCHAR(2),
    MUN_NAME VARCHAR(100),
    RAW_INFO VARIANT
);

-- Silver Schema: Dimension Tables (Cleaned)
-- Note: DIM_BND_001 and DIM_ISS_002 are created as dynamic tables (DT_DIM_BND_001, DT_DIM_ISS_002)
-- Views are created in views.sql pointing to these dynamic tables
-- This shows lineage: Bronze → Dynamic Tables → Views

-- DIM_REG_003: Region dimension
CREATE TABLE IF NOT EXISTS SLV_009.DIM_REG_003 (
    REGION_CD VARCHAR(10) PRIMARY KEY,
    REGION_NAME VARCHAR(100),
    STATE_CODE VARCHAR(2),
    REGION_TYPE VARCHAR(50),
    CREATED_TS TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- DIM_SEG_4421: Segment dimension (taxable vs tax-exempt)
CREATE TABLE IF NOT EXISTS SLV_009.DIM_SEG_4421 (
    SEGMENT_CD VARCHAR(20) PRIMARY KEY,
    SEGMENT_NAME VARCHAR(100),
    SEG_TYPE VARCHAR(50),
    TAX_EXEMPT_FLAG NUMBER(1, 0),
    CREATED_TS TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Silver Schema: Fact Tables (Cleaned)
-- Note: TXN_7821 is created as a dynamic table (DT_TXN_7821) in dynamic_tables.sql
-- The dynamic table automatically populates from BRZ_001.TX_0421

-- Gold Schema: Reporting Tables
-- Note: All Gold tables are created as dynamic tables (DT_*) in dynamic_tables.sql
-- Views are created in views.sql pointing to these dynamic tables
-- This shows lineage: Bronze → Silver Dynamic Tables → Gold Dynamic Tables → Views
-- Architecture: 
--   Bronze Tables (static) → Dynamic Tables (transformations) → Views (clean querying)

