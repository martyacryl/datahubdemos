-- ============================================================================
-- PIMCO Municipal Bond Demo - Refresh Dynamic Table
-- ============================================================================
-- This script manually refreshes the DT_POS_9912 dynamic table to ensure
-- the new columns (STATUS_CD, MATURITY_MULTIPLIER, RISK_FACTOR) are available
-- ============================================================================

USE DATABASE PIMCO_DEMO;
USE WAREHOUSE MSJDEMO;

-- Manually refresh the dynamic table
ALTER DYNAMIC TABLE GLD_003.DT_POS_9912 REFRESH;

-- Verify the new columns exist
SELECT 
    STATUS_CD,
    MATURITY_MULTIPLIER,
    RISK_FACTOR,
    PAR_VALUE,
    MARKET_VALUE
FROM GLD_003.DT_POS_9912
LIMIT 10;

-- Check column count
SELECT 
    COUNT(*) as COLUMN_COUNT,
    LISTAGG(COLUMN_NAME, ', ') WITHIN GROUP (ORDER BY ORDINAL_POSITION) as COLUMNS
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'GLD_003' 
  AND TABLE_NAME = 'DT_POS_9912'
GROUP BY TABLE_NAME;

-- ============================================================================
-- After running this script:
-- 1. Wait a few minutes for the refresh to complete
-- 2. Re-run the DataHub ingestion recipe to pick up the new columns
-- 3. Re-run the apply_documentation.py script to apply column descriptions
-- ============================================================================

