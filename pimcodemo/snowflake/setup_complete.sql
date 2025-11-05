-- ============================================================================
-- PIMCO Municipal Bond Demo - Complete Setup Script
-- ============================================================================
-- This script drops all schemas and recreates everything from scratch
-- Architecture: Bronze Tables → Dynamic Tables → Views
-- Warehouse: MSJDEMO
-- ============================================================================

-- ============================================================================
-- STEP 1: DROP ALL SCHEMAS (Clean Slate)
-- ============================================================================
DROP SCHEMA IF EXISTS GLD_003 CASCADE;
DROP SCHEMA IF EXISTS SLV_009 CASCADE;
DROP SCHEMA IF EXISTS BRZ_001 CASCADE;

-- ============================================================================
-- STEP 2: CREATE SCHEMAS
-- ============================================================================
CREATE SCHEMA BRZ_001;
CREATE SCHEMA SLV_009;
CREATE SCHEMA GLD_003;

-- ============================================================================
-- STEP 3: CREATE BRONZE TABLES (Raw Data)
-- ============================================================================

-- TX_0421: Raw bond transactions
CREATE TABLE BRZ_001.TX_0421 (
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
CREATE TABLE BRZ_001.REF_7832 (
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
CREATE TABLE BRZ_001.ISS_5510 (
    ISS_ID VARCHAR(50) PRIMARY KEY,
    ISS_NAME VARCHAR(200),
    ISS_TYPE VARCHAR(50),
    STATE_CD VARCHAR(2),
    MUN_NAME VARCHAR(100),
    RAW_INFO VARIANT
);

-- ============================================================================
-- STEP 4: CREATE SILVER STATIC TABLES (Reference Dimensions)
-- ============================================================================

-- DIM_REG_003: Region dimension (static reference table)
CREATE TABLE SLV_009.DIM_REG_003 (
    REGION_CD VARCHAR(10) PRIMARY KEY,
    REGION_NAME VARCHAR(100),
    STATE_CODE VARCHAR(2),
    REGION_TYPE VARCHAR(50),
    CREATED_TS TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- DIM_SEG_4421: Segment dimension (static reference table)
CREATE TABLE SLV_009.DIM_SEG_4421 (
    SEGMENT_CD VARCHAR(20) PRIMARY KEY,
    SEGMENT_NAME VARCHAR(100),
    SEG_TYPE VARCHAR(50),
    TAX_EXEMPT_FLAG NUMBER(1, 0),
    CREATED_TS TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- ============================================================================
-- STEP 5: INSERT SEED DATA
-- ============================================================================

-- Insert Region Dimension Data
INSERT INTO SLV_009.DIM_REG_003 (REGION_CD, REGION_NAME, STATE_CODE, REGION_TYPE) VALUES
('WEST', 'Western Region', NULL, 'GEOGRAPHIC'),
('NORTHEAST', 'Northeast Region', NULL, 'GEOGRAPHIC'),
('SOUTH', 'Southern Region', NULL, 'GEOGRAPHIC'),
('MIDWEST', 'Midwest Region', NULL, 'GEOGRAPHIC'),
('OTHER', 'Other Region', NULL, 'GEOGRAPHIC');

-- Insert Segment Dimension Data
INSERT INTO SLV_009.DIM_SEG_4421 (SEGMENT_CD, SEGMENT_NAME, SEG_TYPE, TAX_EXEMPT_FLAG) VALUES
('TAX_EXEMPT', 'Tax-Exempt Municipal Bonds', 'TAX_EXEMPT', 1),
('TAXABLE', 'Taxable Municipal Bonds', 'TAXABLE', 0),
('OTHER', 'Other Bonds', 'OTHER', 0);

-- Insert Issuer Dimension Data (Bronze)
INSERT INTO BRZ_001.ISS_5510 (ISS_ID, ISS_NAME, ISS_TYPE, STATE_CD, MUN_NAME, RAW_INFO)
SELECT 'ISS001', 'California State General Obligation', 'MUNICIPAL_TAX_EXEMPT', 'CA', 'State of California', PARSE_JSON('{"type": "state", "full_name": "State of California"}')
UNION ALL
SELECT 'ISS002', 'New York City Municipal Water Authority', 'MUNICIPAL_TAX_EXEMPT', 'NY', 'New York City', PARSE_JSON('{"type": "municipal", "full_name": "NYC Water Authority"}')
UNION ALL
SELECT 'ISS003', 'Texas Transportation Infrastructure', 'MUNICIPAL_TAX_EXEMPT', 'TX', 'State of Texas', PARSE_JSON('{"type": "state", "full_name": "Texas DOT"}')
UNION ALL
SELECT 'ISS004', 'Florida School District Bond', 'MUNICIPAL_TAX_EXEMPT', 'FL', 'Miami-Dade County', PARSE_JSON('{"type": "school", "full_name": "Miami-Dade Schools"}')
UNION ALL
SELECT 'ISS005', 'Illinois State Revenue Bond', 'MUNICIPAL_TAXABLE', 'IL', 'State of Illinois', PARSE_JSON('{"type": "state", "full_name": "Illinois Revenue"}')
UNION ALL
SELECT 'ISS006', 'Massachusetts General Obligation', 'MUNICIPAL_TAX_EXEMPT', 'MA', 'Commonwealth of Massachusetts', PARSE_JSON('{"type": "state", "full_name": "Massachusetts GO"}')
UNION ALL
SELECT 'ISS007', 'Georgia Municipal Utility', 'MUNICIPAL_TAX_EXEMPT', 'GA', 'Atlanta Metro', PARSE_JSON('{"type": "utility", "full_name": "Atlanta Utilities"}')
UNION ALL
SELECT 'ISS008', 'North Carolina Transportation', 'MUNICIPAL_TAX_EXEMPT', 'NC', 'State of North Carolina', PARSE_JSON('{"type": "state", "full_name": "NC DOT"}')
UNION ALL
SELECT 'ISS009', 'Virginia State Authority', 'MUNICIPAL_TAX_EXEMPT', 'VA', 'Commonwealth of Virginia', PARSE_JSON('{"type": "state", "full_name": "Virginia Authority"}')
UNION ALL
SELECT 'ISS010', 'Michigan Infrastructure Bond', 'MUNICIPAL_TAXABLE', 'MI', 'State of Michigan', PARSE_JSON('{"type": "state", "full_name": "Michigan Infrastructure"}');

-- Insert Bond Reference Data (Bronze)
INSERT INTO BRZ_001.REF_7832 (BND_ID, CUSIP, ISIN, MAT_DATE, CPN_RATE, CR_RT, ISS_TYPE, RAW_DESC)
SELECT 'BND001', '123456789', 'US1234567890', DATEADD(year, 5, CURRENT_DATE()), 2.500, 'AAA', 'MUNICIPAL_TAX_EXEMPT', PARSE_JSON('{"description": "5-year California GO"}')
UNION ALL
SELECT 'BND002', '123456790', 'US1234567908', DATEADD(year, 10, CURRENT_DATE()), 3.000, 'AA+', 'MUNICIPAL_TAX_EXEMPT', PARSE_JSON('{"description": "10-year NYC Water"}')
UNION ALL
SELECT 'BND003', '123456791', 'US1234567916', DATEADD(year, 7, CURRENT_DATE()), 2.750, 'AA', 'MUNICIPAL_TAX_EXEMPT', PARSE_JSON('{"description": "7-year Texas Transportation"}')
UNION ALL
SELECT 'BND004', '123456792', 'US1234567924', DATEADD(year, 15, CURRENT_DATE()), 3.250, 'AA-', 'MUNICIPAL_TAX_EXEMPT', PARSE_JSON('{"description": "15-year Florida School"}')
UNION ALL
SELECT 'BND005', '123456793', 'US1234567932', DATEADD(year, 3, CURRENT_DATE()), 3.500, 'A+', 'MUNICIPAL_TAXABLE', PARSE_JSON('{"description": "3-year Illinois Revenue"}')
UNION ALL
SELECT 'BND006', '123456794', 'US1234567940', DATEADD(year, 20, CURRENT_DATE()), 3.750, 'AAA', 'MUNICIPAL_TAX_EXEMPT', PARSE_JSON('{"description": "20-year Massachusetts GO"}')
UNION ALL
SELECT 'BND007', '123456795', 'US1234567958', DATEADD(year, 8, CURRENT_DATE()), 2.875, 'AA', 'MUNICIPAL_TAX_EXEMPT', PARSE_JSON('{"description": "8-year Georgia Utility"}')
UNION ALL
SELECT 'BND008', '123456796', 'US1234567966', DATEADD(year, 12, CURRENT_DATE()), 3.125, 'AA-', 'MUNICIPAL_TAX_EXEMPT', PARSE_JSON('{"description": "12-year NC Transportation"}')
UNION ALL
SELECT 'BND009', '123456797', 'US1234567974', DATEADD(year, 6, CURRENT_DATE()), 2.625, 'AA+', 'MUNICIPAL_TAX_EXEMPT', PARSE_JSON('{"description": "6-year Virginia Authority"}')
UNION ALL
SELECT 'BND010', '123456798', 'US1234567982', DATEADD(year, 4, CURRENT_DATE()), 3.625, 'A', 'MUNICIPAL_TAXABLE', PARSE_JSON('{"description": "4-year Michigan Infrastructure"}');

-- Insert Transaction Data (Bronze) - Last 30 days
INSERT INTO BRZ_001.TX_0421 (TX_ID, TD_DATE, STL_DATE, PRN_AMT, ISS_ID, BND_ID, TRD_TYPE, CUSIP, RAW_DATA)
SELECT 'TX001', DATEADD(day, -30, CURRENT_DATE()), DATEADD(day, -28, CURRENT_DATE()), 1000000.00, 'ISS001', 'BND001', 'BUY', '123456789', PARSE_JSON('{"trade_id": "T001"}')
UNION ALL
SELECT 'TX002', DATEADD(day, -29, CURRENT_DATE()), DATEADD(day, -27, CURRENT_DATE()), 2500000.00, 'ISS002', 'BND002', 'BUY', '123456790', PARSE_JSON('{"trade_id": "T002"}')
UNION ALL
SELECT 'TX003', DATEADD(day, -28, CURRENT_DATE()), DATEADD(day, -26, CURRENT_DATE()), 1500000.00, 'ISS003', 'BND003', 'BUY', '123456791', PARSE_JSON('{"trade_id": "T003"}')
UNION ALL
SELECT 'TX004', DATEADD(day, -27, CURRENT_DATE()), DATEADD(day, -25, CURRENT_DATE()), 5000000.00, 'ISS004', 'BND004', 'BUY', '123456792', PARSE_JSON('{"trade_id": "T004"}')
UNION ALL
SELECT 'TX005', DATEADD(day, -26, CURRENT_DATE()), DATEADD(day, -24, CURRENT_DATE()), 750000.00, 'ISS005', 'BND005', 'BUY', '123456793', PARSE_JSON('{"trade_id": "T005"}')
UNION ALL
SELECT 'TX006', DATEADD(day, -25, CURRENT_DATE()), DATEADD(day, -23, CURRENT_DATE()), 3000000.00, 'ISS006', 'BND006', 'BUY', '123456794', PARSE_JSON('{"trade_id": "T006"}')
UNION ALL
SELECT 'TX007', DATEADD(day, -24, CURRENT_DATE()), DATEADD(day, -22, CURRENT_DATE()), 2000000.00, 'ISS007', 'BND007', 'BUY', '123456795', PARSE_JSON('{"trade_id": "T007"}')
UNION ALL
SELECT 'TX008', DATEADD(day, -23, CURRENT_DATE()), DATEADD(day, -21, CURRENT_DATE()), 1800000.00, 'ISS008', 'BND008', 'BUY', '123456796', PARSE_JSON('{"trade_id": "T008"}')
UNION ALL
SELECT 'TX009', DATEADD(day, -22, CURRENT_DATE()), DATEADD(day, -20, CURRENT_DATE()), 1200000.00, 'ISS009', 'BND009', 'BUY', '123456797', PARSE_JSON('{"trade_id": "T009"}')
UNION ALL
SELECT 'TX010', DATEADD(day, -21, CURRENT_DATE()), DATEADD(day, -19, CURRENT_DATE()), 900000.00, 'ISS010', 'BND010', 'BUY', '123456798', PARSE_JSON('{"trade_id": "T010"}')
UNION ALL
SELECT 'TX011', DATEADD(day, -20, CURRENT_DATE()), DATEADD(day, -18, CURRENT_DATE()), 500000.00, 'ISS001', 'BND001', 'BUY', '123456789', PARSE_JSON('{"trade_id": "T011"}')
UNION ALL
SELECT 'TX012', DATEADD(day, -19, CURRENT_DATE()), DATEADD(day, -17, CURRENT_DATE()), 1750000.00, 'ISS002', 'BND002', 'BUY', '123456790', PARSE_JSON('{"trade_id": "T012"}')
UNION ALL
SELECT 'TX013', DATEADD(day, -18, CURRENT_DATE()), DATEADD(day, -16, CURRENT_DATE()), 2250000.00, 'ISS003', 'BND003', 'BUY', '123456791', PARSE_JSON('{"trade_id": "T013"}')
UNION ALL
SELECT 'TX014', DATEADD(day, -17, CURRENT_DATE()), DATEADD(day, -15, CURRENT_DATE()), 1100000.00, 'ISS004', 'BND004', 'BUY', '123456792', PARSE_JSON('{"trade_id": "T014"}')
UNION ALL
SELECT 'TX015', DATEADD(day, -16, CURRENT_DATE()), DATEADD(day, -14, CURRENT_DATE()), 850000.00, 'ISS005', 'BND005', 'BUY', '123456793', PARSE_JSON('{"trade_id": "T015"}')
UNION ALL
SELECT 'TX016', DATEADD(day, -15, CURRENT_DATE()), DATEADD(day, -13, CURRENT_DATE()), 4000000.00, 'ISS006', 'BND006', 'BUY', '123456794', PARSE_JSON('{"trade_id": "T016"}')
UNION ALL
SELECT 'TX017', DATEADD(day, -14, CURRENT_DATE()), DATEADD(day, -12, CURRENT_DATE()), 1600000.00, 'ISS007', 'BND007', 'BUY', '123456795', PARSE_JSON('{"trade_id": "T017"}')
UNION ALL
SELECT 'TX018', DATEADD(day, -13, CURRENT_DATE()), DATEADD(day, -11, CURRENT_DATE()), 1900000.00, 'ISS008', 'BND008', 'BUY', '123456796', PARSE_JSON('{"trade_id": "T018"}')
UNION ALL
SELECT 'TX019', DATEADD(day, -12, CURRENT_DATE()), DATEADD(day, -10, CURRENT_DATE()), 1300000.00, 'ISS009', 'BND009', 'BUY', '123456797', PARSE_JSON('{"trade_id": "T019"}')
UNION ALL
SELECT 'TX020', DATEADD(day, -11, CURRENT_DATE()), DATEADD(day, -9, CURRENT_DATE()), 950000.00, 'ISS010', 'BND010', 'BUY', '123456798', PARSE_JSON('{"trade_id": "T020"}')
UNION ALL
SELECT 'TX021', DATEADD(day, -10, CURRENT_DATE()), DATEADD(day, -8, CURRENT_DATE()), 600000.00, 'ISS001', 'BND001', 'BUY', '123456789', PARSE_JSON('{"trade_id": "T021"}')
UNION ALL
SELECT 'TX022', DATEADD(day, -9, CURRENT_DATE()), DATEADD(day, -7, CURRENT_DATE()), 2000000.00, 'ISS002', 'BND002', 'BUY', '123456790', PARSE_JSON('{"trade_id": "T022"}')
UNION ALL
SELECT 'TX023', DATEADD(day, -8, CURRENT_DATE()), DATEADD(day, -6, CURRENT_DATE()), 2750000.00, 'ISS003', 'BND003', 'BUY', '123456791', PARSE_JSON('{"trade_id": "T023"}')
UNION ALL
SELECT 'TX024', DATEADD(day, -7, CURRENT_DATE()), DATEADD(day, -5, CURRENT_DATE()), 1250000.00, 'ISS004', 'BND004', 'BUY', '123456792', PARSE_JSON('{"trade_id": "T024"}')
UNION ALL
SELECT 'TX025', DATEADD(day, -6, CURRENT_DATE()), DATEADD(day, -4, CURRENT_DATE()), 920000.00, 'ISS005', 'BND005', 'BUY', '123456793', PARSE_JSON('{"trade_id": "T025"}')
UNION ALL
SELECT 'TX026', DATEADD(day, -5, CURRENT_DATE()), DATEADD(day, -3, CURRENT_DATE()), 3500000.00, 'ISS006', 'BND006', 'BUY', '123456794', PARSE_JSON('{"trade_id": "T026"}')
UNION ALL
SELECT 'TX027', DATEADD(day, -4, CURRENT_DATE()), DATEADD(day, -2, CURRENT_DATE()), 1400000.00, 'ISS007', 'BND007', 'BUY', '123456795', PARSE_JSON('{"trade_id": "T027"}')
UNION ALL
SELECT 'TX028', DATEADD(day, -3, CURRENT_DATE()), DATEADD(day, -1, CURRENT_DATE()), 2100000.00, 'ISS008', 'BND008', 'BUY', '123456796', PARSE_JSON('{"trade_id": "T028"}')
UNION ALL
SELECT 'TX029', DATEADD(day, -2, CURRENT_DATE()), CURRENT_DATE(), 1350000.00, 'ISS009', 'BND009', 'BUY', '123456797', PARSE_JSON('{"trade_id": "T029"}')
UNION ALL
SELECT 'TX030', DATEADD(day, -1, CURRENT_DATE()), DATEADD(day, 1, CURRENT_DATE()), 980000.00, 'ISS010', 'BND010', 'BUY', '123456798', PARSE_JSON('{"trade_id": "T030"}');

-- ============================================================================
-- STEP 6: CREATE DYNAMIC TABLES (Transformations)
-- ============================================================================

-- Bronze to Silver: Clean and Standardize Transactions
CREATE OR REPLACE DYNAMIC TABLE SLV_009.DT_TXN_7821
TARGET_LAG = '1 minute'
WAREHOUSE = 'MSJDEMO'
AS
SELECT 
    TX_ID as TX_ID,
    TD_DATE as TRADE_DATE,
    STL_DATE as SETTLEMENT_DATE,
    PRN_AMT as PRINCIPAL_AMOUNT,
    ISS_ID as ISSUER_ID,
    BND_ID as BOND_ID,
    TRD_TYPE as TRADE_TYPE,
    CUSIP as CUSIP,
    CURRENT_TIMESTAMP() as CREATED_TS
FROM BRZ_001.TX_0421
WHERE TD_DATE IS NOT NULL
  AND PRN_AMT IS NOT NULL
  AND BND_ID IS NOT NULL;

-- Bronze to Silver: Clean and Standardize Bond Dimension
CREATE OR REPLACE DYNAMIC TABLE SLV_009.DT_DIM_BND_001
TARGET_LAG = '1 minute'
WAREHOUSE = 'MSJDEMO'
AS
SELECT 
    r.BND_ID as BND_ID,
    r.CUSIP as CUSIP,
    r.ISIN as ISIN,
    r.MAT_DATE as MATURITY_DATE,
    r.CPN_RATE as COUPON_RATE,
    r.CR_RT as CREDIT_RATING,
    r.ISS_TYPE as ISSUER_TYPE,
    CASE 
        WHEN r.ISS_TYPE LIKE '%TAX%EXEMPT%' OR r.ISS_TYPE LIKE '%MUNICIPAL%' THEN 'TAX_EXEMPT'
        WHEN r.ISS_TYPE LIKE '%TAXABLE%' THEN 'TAXABLE'
        ELSE 'OTHER'
    END as SEGMENT_CD,
    i.ISS_ID as ISSUER_ID,
    CURRENT_TIMESTAMP() as CREATED_TS,
    CURRENT_TIMESTAMP() as UPDATED_TS
FROM BRZ_001.REF_7832 r
LEFT JOIN BRZ_001.ISS_5510 i ON r.ISS_TYPE = i.ISS_TYPE
WHERE r.BND_ID IS NOT NULL;

-- Bronze to Silver: Clean and Standardize Issuer Dimension
CREATE OR REPLACE DYNAMIC TABLE SLV_009.DT_DIM_ISS_002
TARGET_LAG = '1 minute'
WAREHOUSE = 'MSJDEMO'
AS
SELECT 
    ISS_ID as ISS_ID,
    ISS_NAME as ISSUER_NAME,
    ISS_TYPE as ISSUER_TYPE,
    STATE_CD as STATE_CODE,
    MUN_NAME as MUNICIPALITY_NAME,
    CASE 
        WHEN STATE_CD IN ('CA', 'NY', 'TX', 'FL', 'IL') THEN 'WEST'
        WHEN STATE_CD IN ('NY', 'NJ', 'CT', 'MA', 'PA') THEN 'NORTHEAST'
        WHEN STATE_CD IN ('TX', 'FL', 'GA', 'NC', 'VA') THEN 'SOUTH'
        WHEN STATE_CD IN ('IL', 'MI', 'OH', 'WI', 'MN') THEN 'MIDWEST'
        ELSE 'OTHER'
    END as REGION_CD,
    CURRENT_TIMESTAMP() as CREATED_TS,
    CURRENT_TIMESTAMP() as UPDATED_TS
FROM BRZ_001.ISS_5510
WHERE ISS_ID IS NOT NULL;

-- Bronze to Silver: Create Region Dimension
CREATE OR REPLACE DYNAMIC TABLE SLV_009.DT_DIM_REG_003
TARGET_LAG = '1 minute'
WAREHOUSE = 'MSJDEMO'
AS
SELECT DISTINCT
    REGION_CD as REGION_CD,
    CASE 
        WHEN REGION_CD = 'WEST' THEN 'Western Region'
        WHEN REGION_CD = 'NORTHEAST' THEN 'Northeast Region'
        WHEN REGION_CD = 'SOUTH' THEN 'Southern Region'
        WHEN REGION_CD = 'MIDWEST' THEN 'Midwest Region'
        ELSE 'Other Region'
    END as REGION_NAME,
    NULL as STATE_CODE,
    'GEOGRAPHIC' as REGION_TYPE,
    CURRENT_TIMESTAMP() as CREATED_TS
FROM SLV_009.DT_DIM_ISS_002
WHERE REGION_CD IS NOT NULL;

-- Bronze to Silver: Create Segment Dimension
CREATE OR REPLACE DYNAMIC TABLE SLV_009.DT_DIM_SEG_4421
TARGET_LAG = '1 minute'
WAREHOUSE = 'MSJDEMO'
AS
SELECT DISTINCT
    SEGMENT_CD as SEGMENT_CD,
    CASE 
        WHEN SEGMENT_CD = 'TAX_EXEMPT' THEN 'Tax-Exempt Municipal Bonds'
        WHEN SEGMENT_CD = 'TAXABLE' THEN 'Taxable Municipal Bonds'
        ELSE 'Other Bonds'
    END as SEGMENT_NAME,
    SEGMENT_CD as SEG_TYPE,
    CASE WHEN SEGMENT_CD = 'TAX_EXEMPT' THEN 1 ELSE 0 END as TAX_EXEMPT_FLAG,
    CURRENT_TIMESTAMP() as CREATED_TS
FROM SLV_009.DT_DIM_BND_001
WHERE SEGMENT_CD IS NOT NULL;

-- Silver to Gold: Aggregate Positions by Bond, Issuer, Region, Segment
CREATE OR REPLACE DYNAMIC TABLE GLD_003.DT_POS_9912
TARGET_LAG = '5 minutes'
WAREHOUSE = 'MSJDEMO'
AS
SELECT 
    CONCAT('POS_', b.BND_ID, '_', CURRENT_DATE()) as POS_ID,
    b.BND_ID as BOND_ID,
    b.ISSUER_ID as ISSUER_ID,
    i.REGION_CD as REGION_CD,
    b.SEGMENT_CD as SEGMENT_CD,
    COALESCE(SUM(t.PRINCIPAL_AMOUNT), 0) as PAR_VALUE,
    COALESCE(SUM(t.PRINCIPAL_AMOUNT * (1 + b.COUPON_RATE / 100)), 0) as MARKET_VALUE,
    CURRENT_DATE() as POSITION_DATE,
    CURRENT_DATE() as AS_OF_DATE,
    CURRENT_TIMESTAMP() as CREATED_TS
FROM SLV_009.DT_DIM_BND_001 b
LEFT JOIN SLV_009.DT_TXN_7821 t ON b.BND_ID = t.BOND_ID
LEFT JOIN SLV_009.DT_DIM_ISS_002 i ON b.ISSUER_ID = i.ISS_ID
WHERE t.TRADE_DATE >= DATEADD(day, -30, CURRENT_DATE())
GROUP BY b.BND_ID, b.ISSUER_ID, i.REGION_CD, b.SEGMENT_CD;

-- Silver to Gold: Segment Aggregations
CREATE OR REPLACE DYNAMIC TABLE GLD_003.DT_SEG_4421
TARGET_LAG = '5 minutes'
WAREHOUSE = 'MSJDEMO'
AS
SELECT 
    SEGMENT_CD,
    CURRENT_DATE() as AS_OF_DATE,
    SUM(PAR_VALUE) as TOTAL_PAR_VALUE,
    SUM(MARKET_VALUE) as TOTAL_MARKET_VALUE,
    COUNT(DISTINCT BOND_ID) as POSITION_COUNT
FROM GLD_003.DT_POS_9912
GROUP BY SEGMENT_CD;

-- Silver to Gold: Region Aggregations
CREATE OR REPLACE DYNAMIC TABLE GLD_003.DT_REG_7733
TARGET_LAG = '5 minutes'
WAREHOUSE = 'MSJDEMO'
AS
SELECT 
    REGION_CD,
    CURRENT_DATE() as AS_OF_DATE,
    SUM(PAR_VALUE) as TOTAL_PAR_VALUE,
    SUM(MARKET_VALUE) as TOTAL_MARKET_VALUE,
    COUNT(DISTINCT BOND_ID) as POSITION_COUNT
FROM GLD_003.DT_POS_9912
WHERE REGION_CD IS NOT NULL
GROUP BY REGION_CD;

-- Silver to Gold: Issuer Aggregations
CREATE OR REPLACE DYNAMIC TABLE GLD_003.DT_ISS_8844
TARGET_LAG = '5 minutes'
WAREHOUSE = 'MSJDEMO'
AS
SELECT 
    ISSUER_ID,
    CURRENT_DATE() as AS_OF_DATE,
    SUM(PAR_VALUE) as TOTAL_PAR_VALUE,
    SUM(MARKET_VALUE) as TOTAL_MARKET_VALUE,
    COUNT(DISTINCT BOND_ID) as POSITION_COUNT
FROM GLD_003.DT_POS_9912
WHERE ISSUER_ID IS NOT NULL
GROUP BY ISSUER_ID;

-- Silver to Gold: Growth Metrics Over Time
CREATE OR REPLACE DYNAMIC TABLE GLD_003.DT_GRO_5566
TARGET_LAG = '1 hour'
WAREHOUSE = 'MSJDEMO'
AS
SELECT 
    CURRENT_DATE() as METRIC_DATE,
    SEGMENT_CD,
    REGION_CD,
    SUM(PAR_VALUE) as TOTAL_PAR_VALUE,
    SUM(MARKET_VALUE) as TOTAL_MARKET_VALUE,
    SUM(PAR_VALUE) - LAG(SUM(PAR_VALUE)) OVER (
        PARTITION BY SEGMENT_CD, REGION_CD 
        ORDER BY CURRENT_DATE()
    ) as VALUE_CHANGE,
    CASE 
        WHEN LAG(SUM(PAR_VALUE)) OVER (
            PARTITION BY SEGMENT_CD, REGION_CD 
            ORDER BY CURRENT_DATE()
        ) > 0
        THEN ((SUM(PAR_VALUE) - LAG(SUM(PAR_VALUE)) OVER (
            PARTITION BY SEGMENT_CD, REGION_CD 
            ORDER BY CURRENT_DATE()
        )) / LAG(SUM(PAR_VALUE)) OVER (
            PARTITION BY SEGMENT_CD, REGION_CD 
            ORDER BY CURRENT_DATE()
        )) * 100
        ELSE 0
    END as PCT_CHANGE
FROM GLD_003.DT_POS_9912
WHERE REGION_CD IS NOT NULL AND SEGMENT_CD IS NOT NULL
GROUP BY SEGMENT_CD, REGION_CD;

-- ============================================================================
-- STEP 7: CREATE VIEWS (Clean Querying Interface)
-- ============================================================================

-- Silver Schema: Views on Dynamic Tables
-- View on cleaned transactions (points to DT_TXN_7821)
CREATE OR REPLACE VIEW SLV_009.TXN_7821 AS
SELECT * FROM SLV_009.DT_TXN_7821;

-- View on bond dimension (points to DT_DIM_BND_001)
CREATE OR REPLACE VIEW SLV_009.DIM_BND_001 AS
SELECT * FROM SLV_009.DT_DIM_BND_001;

-- View on issuer dimension (points to DT_DIM_ISS_002)
CREATE OR REPLACE VIEW SLV_009.DIM_ISS_002 AS
SELECT * FROM SLV_009.DT_DIM_ISS_002;

-- Gold Schema: Views on Dynamic Tables
-- View on aggregated positions (points to DT_POS_9912)
CREATE OR REPLACE VIEW GLD_003.POS_9912 AS
SELECT * FROM GLD_003.DT_POS_9912;

-- View on segment aggregations (points to DT_SEG_4421)
CREATE OR REPLACE VIEW GLD_003.SEG_4421 AS
SELECT * FROM GLD_003.DT_SEG_4421;

-- View on region aggregations (points to DT_REG_7733)
CREATE OR REPLACE VIEW GLD_003.REG_7733 AS
SELECT * FROM GLD_003.DT_REG_7733;

-- View on issuer aggregations (points to DT_ISS_8844)
CREATE OR REPLACE VIEW GLD_003.ISS_8844 AS
SELECT * FROM GLD_003.DT_ISS_8844;

-- View on growth metrics (points to DT_GRO_5566)
CREATE OR REPLACE VIEW GLD_003.GRO_5566 AS
SELECT * FROM GLD_003.DT_GRO_5566;

-- ============================================================================
-- SETUP COMPLETE
-- ============================================================================
-- Architecture:
--   Bronze Tables (static) → Dynamic Tables (transformations) → Views (querying)
--   
-- Lineage:
--   BRZ_001.* → SLV_009.DT_* → GLD_003.DT_* → GLD_003.* (views)
--
-- Next Steps:
--   1. Wait for dynamic tables to refresh (1-5 minutes)
--   2. Verify data: SELECT COUNT(*) FROM GLD_003.POS_9912;
--   3. Run DataHub ingestion
-- ============================================================================

