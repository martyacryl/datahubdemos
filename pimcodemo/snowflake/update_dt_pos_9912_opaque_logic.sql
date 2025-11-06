-- ============================================================================
-- PIMCO Municipal Bond Demo - Update DT_POS_9912 with Opaque Business Logic
-- ============================================================================
-- This script updates the DT_POS_9912 dynamic table to include opaque business logic:
-- - Status code filtering (A/1/Y = active, I/0/N = inactive)
-- - Maturity multipliers based on years to maturity
-- - Risk factors based on credit ratings
-- - Complex market value calculation using all factors
--
-- Run this script in Snowflake to update the existing dynamic table.
-- ============================================================================

USE DATABASE PIMCO_DEMO;
USE WAREHOUSE MSJDEMO;

-- Drop and recreate DT_POS_9912 with opaque business logic
-- Note: CREATE OR REPLACE DYNAMIC TABLE will update the existing table
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
    -- Opaque status code: A/1/Y = active, I/0/N = inactive, U = unknown
    -- Since we're aggregating transactions, use 'A' for active positions (BUY transactions)
    'A' as STATUS_CD,
    -- Opaque maturity multiplier: < 5 years = 1.05, 5-10 years = 1.02, > 10 years = 1.0
    CASE 
        WHEN DATEDIFF(year, CURRENT_DATE(), b.MATURITY_DATE) < 5 THEN 1.05
        WHEN DATEDIFF(year, CURRENT_DATE(), b.MATURITY_DATE) <= 10 THEN 1.02
        ELSE 1.0
    END as MATURITY_MULTIPLIER,
    -- Opaque risk factor: AAA/AA/A = 0.98, BBB/BB/B = 1.0, others = 1.05
    CASE 
        WHEN b.CREDIT_RATING IN ('AAA', 'AA', 'A') THEN 0.98
        WHEN b.CREDIT_RATING IN ('BBB', 'BB', 'B') THEN 1.0
        ELSE 1.05
    END as RISK_FACTOR,
    COALESCE(SUM(t.PRINCIPAL_AMOUNT), 0) as PAR_VALUE,
    -- Complex market value calculation: PAR_VALUE * (1 + COUPON_RATE/100) * MATURITY_MULTIPLIER * RISK_FACTOR
    COALESCE(
        SUM(t.PRINCIPAL_AMOUNT * (1 + b.COUPON_RATE / 100) * 
            CASE 
                WHEN DATEDIFF(year, CURRENT_DATE(), b.MATURITY_DATE) < 5 THEN 1.05
                WHEN DATEDIFF(year, CURRENT_DATE(), b.MATURITY_DATE) <= 10 THEN 1.02
                ELSE 1.0
            END * 
            CASE 
                WHEN b.CREDIT_RATING IN ('AAA', 'AA', 'A') THEN 0.98
                WHEN b.CREDIT_RATING IN ('BBB', 'BB', 'B') THEN 1.0
                ELSE 1.05
            END
        ), 0
    ) as MARKET_VALUE,
    CURRENT_DATE() as POSITION_DATE,
    CURRENT_DATE() as AS_OF_DATE,
    CURRENT_TIMESTAMP() as CREATED_TS
FROM SLV_009.DT_DIM_BND_001 b
LEFT JOIN SLV_009.DT_TXN_7821 t ON b.BND_ID = t.BOND_ID
LEFT JOIN SLV_009.DT_DIM_ISS_002 i ON b.ISSUER_ID = i.ISS_ID
WHERE t.TRADE_DATE >= DATEADD(day, -30, CURRENT_DATE())
  -- Opaque status filter: Only include active positions (A/1/Y)
  AND (
    t.TRADE_TYPE = 'BUY' OR 
    t.TRADE_TYPE IN ('A', '1', 'Y')
  )
GROUP BY b.BND_ID, b.ISSUER_ID, i.REGION_CD, b.SEGMENT_CD, 
         b.MATURITY_DATE, b.CREDIT_RATING;

-- Verify the dynamic table was updated
SELECT 
    'DT_POS_9912 updated with opaque business logic' as STATUS,
    COUNT(*) as ROW_COUNT,
    COUNT(DISTINCT STATUS_CD) as STATUS_CODES,
    COUNT(DISTINCT MATURITY_MULTIPLIER) as MATURITY_MULTIPLIERS,
    COUNT(DISTINCT RISK_FACTOR) as RISK_FACTORS
FROM GLD_003.DT_POS_9912;

-- Show sample of new columns
SELECT 
    STATUS_CD,
    MATURITY_MULTIPLIER,
    RISK_FACTOR,
    PAR_VALUE,
    MARKET_VALUE,
    COUNT(*) as POSITION_COUNT
FROM GLD_003.DT_POS_9912
GROUP BY STATUS_CD, MATURITY_MULTIPLIER, RISK_FACTOR, PAR_VALUE, MARKET_VALUE
ORDER BY POSITION_COUNT DESC
LIMIT 10;

-- Recreate the view to pick up the new columns from the dynamic table
CREATE OR REPLACE VIEW GLD_003.POS_9912 AS
SELECT * FROM GLD_003.DT_POS_9912;

-- Verify the view has the new columns
SELECT 
    COLUMN_NAME,
    DATA_TYPE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'GLD_003' 
  AND TABLE_NAME = 'POS_9912'
ORDER BY ORDINAL_POSITION;

-- ============================================================================
-- Update Complete
-- ============================================================================
-- The DT_POS_9912 dynamic table now includes:
-- 1. STATUS_CD column with opaque codes (A/1/Y = active, I/0/N = inactive)
-- 2. MATURITY_MULTIPLIER column with opaque calculation (< 5 years = 1.05, etc.)
-- 3. RISK_FACTOR column with opaque calculation (AAA/AA/A = 0.98, etc.)
-- 4. MARKET_VALUE column with complex adjusted calculation
--
-- The view GLD_003.POS_9912 has been recreated to include all new columns.
--
-- Next Steps:
-- 1. Wait for dynamic table to refresh (5 minutes) or run refresh_dynamic_table.sql
-- 2. Re-run DataHub ingestion to pick up the new columns
-- 3. Run metadata scripts to update DataHub with new glossary terms and documentation
-- 4. Verify in DataHub that the opaque business logic is documented
-- ============================================================================

