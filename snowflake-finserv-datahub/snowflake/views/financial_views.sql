-- File: snowflake/views/financial_views.sql
-- Purpose: Create views for the Financial Services Asset Management demo
-- These views will establish lineage that DataHub can discover and display

USE DATABASE FINSERV_DEMO;
USE WAREHOUSE FINSERV_WH;

-- Create view for current positions by trader and symbol
CREATE OR REPLACE VIEW TRADING.CURRENT_POSITIONS AS
SELECT 
    TR.TRADER_ID,
    TR.TRADER_NAME,
    TR.DESK,
    TR.REGION,
    T.SYMBOL,
    SUM(CASE WHEN T.BUY_SELL = 'BUY' THEN T.QUANTITY ELSE -T.QUANTITY END) AS POSITION,
    MAX(T.TRADE_DATE) AS LAST_TRADE_DATE
FROM 
    TRADING.TRADES T
JOIN 
    TRADING.TRADERS TR ON T.TRADER_ID = TR.TRADER_ID
WHERE 
    T.STATUS = 'SETTLED'
GROUP BY 
    TR.TRADER_ID, TR.TRADER_NAME, TR.DESK, TR.REGION, T.SYMBOL
HAVING 
    POSITION <> 0;
