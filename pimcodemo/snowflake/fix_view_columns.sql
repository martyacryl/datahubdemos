-- ============================================================================
-- PIMCO Municipal Bond Demo - Fix View Column Mismatch
-- ============================================================================
-- This script recreates the GLD_003.POS_9912 view to pick up the new columns
-- (STATUS_CD, MATURITY_MULTIPLIER, RISK_FACTOR) from the updated dynamic table
-- ============================================================================

USE DATABASE PIMCO_DEMO;
USE WAREHOUSE MSJDEMO;

-- Recreate the view to pick up all columns from the dynamic table
CREATE OR REPLACE VIEW GLD_003.POS_9912 AS
SELECT * FROM GLD_003.DT_POS_9912;

-- Verify the view has the correct number of columns (should be 13 now)
SELECT 
    COUNT(*) as COLUMN_COUNT,
    LISTAGG(COLUMN_NAME, ', ') WITHIN GROUP (ORDER BY ORDINAL_POSITION) as COLUMNS
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'GLD_003' 
  AND TABLE_NAME = 'POS_9912'
GROUP BY TABLE_NAME;

-- Show all columns in the view
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    ORDINAL_POSITION
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'GLD_003' 
  AND TABLE_NAME = 'POS_9912'
ORDER BY ORDINAL_POSITION;

-- Test query to verify the new columns are accessible
SELECT 
    STATUS_CD,
    MATURITY_MULTIPLIER,
    RISK_FACTOR,
    PAR_VALUE,
    MARKET_VALUE
FROM GLD_003.POS_9912
LIMIT 5;

-- ============================================================================
-- View Fixed
-- ============================================================================
-- The view GLD_003.POS_9912 now includes all 13 columns:
-- 1. POS_ID
-- 2. BOND_ID
-- 3. ISSUER_ID
-- 4. REGION_CD
-- 5. SEGMENT_CD
-- 6. STATUS_CD (NEW)
-- 7. MATURITY_MULTIPLIER (NEW)
-- 8. RISK_FACTOR (NEW)
-- 9. PAR_VALUE
-- 10. MARKET_VALUE
-- 11. POSITION_DATE
-- 12. AS_OF_DATE
-- 13. CREATED_TS
--
-- Next Steps:
-- 1. Re-run DataHub ingestion to pick up the new columns
-- 2. Run: python3 scripts/apply_documentation.py to apply column descriptions
-- ============================================================================

