# PIMCO DataHub LLM Demo - Query Examples

## Example 1: Total Positions by Region for Tax-Exempt Bonds

### Business Question
"Show me total municipal bond positions by region for tax-exempt bonds"

### Expected Result
A table showing:
- Region name
- Total par value (aggregated)
- Total market value (aggregated)
- Position count
- Filtered to only tax-exempt bonds

### Without DataHub Context

**Prompt to Claude Desktop**:
```
I need to query Snowflake for total municipal bond positions by region for tax-exempt bonds. 
The database is PIMCO_DEMO. What SQL query should I use?
```

**Generated SQL** (Incorrect):
```sql
-- Claude may generate something like this without context
SELECT 
    REGION_CD,
    SUM(PAR_VALUE) as total_par,
    SUM(MARKET_VALUE) as total_market
FROM GLD_003.POS_9912
WHERE SEGMENT_CD = 'TAX_EXEMPT'
GROUP BY REGION_CD;
```

**Issues**:
- May not understand that `SEGMENT_CD` contains tax-exempt classification
- May not know to join with `DIM_SEG_4421` for segment names
- May not join with `DIM_REG_003` for region names
- May not understand the relationship between tables

### With DataHub Context

**Prompt to Claude Desktop**:
```
I need to query Snowflake for total municipal bond positions by region for tax-exempt bonds. 
The database is PIMCO_DEMO. 

First, use DataHub to verify that any tables you plan to use have the "Authorized for Reporting" 
structured property set to "Yes". Then use DataHub to understand the schema and generate the correct SQL.
```

**Generated SQL** (Correct):
```sql
-- Claude uses DataHub context to understand:
-- - POS_9912 = Aggregated bond positions table
-- - VERIFIED: POS_9912 has "Authorized for Reporting = Yes" structured property (data governance compliance)
-- - SEGMENT_CD = Segment code (TAX_EXEMPT or TAXABLE)
-- - REGION_CD = Region code
-- - Need to join with DIM_SEG_4421 for segment names
-- - Need to join with DIM_REG_003 for region names

SELECT 
    r.REGION_NAME,
    SUM(p.PAR_VALUE) as TOTAL_PAR_VALUE,
    SUM(p.MARKET_VALUE) as TOTAL_MARKET_VALUE,
    COUNT(DISTINCT p.BOND_ID) as POSITION_COUNT
FROM GLD_003.POS_9912 p
INNER JOIN SLV_009.DIM_SEG_4421 s ON p.SEGMENT_CD = s.SEGMENT_CD
INNER JOIN SLV_009.DIM_REG_003 r ON p.REGION_CD = r.REGION_CD
WHERE s.TAX_EXEMPT_FLAG = 1
  AND p.AS_OF_DATE = CURRENT_DATE()
GROUP BY r.REGION_NAME
ORDER BY TOTAL_PAR_VALUE DESC;
```

**Why This Works**:
- Claude understands `POS_9912` contains aggregated positions
- Claude verifies `POS_9912` has "Authorized for Reporting = Yes" structured property (data governance compliance)
- Claude knows `SEGMENT_CD` links to segment dimension
- Claude knows `TAX_EXEMPT_FLAG = 1` means tax-exempt bonds
- Claude correctly joins dimension tables for readable names
- Claude includes proper filtering and aggregation

---

## Example 2: Position Growth Over Time by Segment

### Business Question
"Show me how bond positions have grown over the last 30 days by segment (tax-exempt vs taxable)"

### Expected Result
A time series showing:
- Date
- Segment name
- Total par value
- Value change from previous period
- Percentage change

### Without DataHub Context

**Prompt to Claude Desktop**:
```
I need to query Snowflake to show bond position growth over the last 30 days by segment. 
The database is PIMCO_DEMO. What SQL should I use?
```

**Generated SQL** (Incorrect):
```sql
-- Claude may generate something like this without context
SELECT 
    METRIC_DATE,
    SEGMENT_CD,
    TOTAL_PAR_VALUE,
    VALUE_CHANGE
FROM GLD_003.GRO_5566
WHERE METRIC_DATE >= DATEADD(day, -30, CURRENT_DATE())
ORDER BY METRIC_DATE;
```

**Issues**:
- May not understand `GRO_5566` contains growth metrics
- May not join with `DIM_SEG_4421` for segment names
- May not understand the time series structure
- May not calculate growth correctly if using wrong table

### With DataHub Context

**Prompt to Claude Desktop**:
```
I need to query Snowflake to show bond position growth over the last 30 days by segment. 
The database is PIMCO_DEMO. Use DataHub to understand the schema and generate the correct SQL.
```

**Generated SQL** (Correct):
```sql
-- Claude uses DataHub context to understand:
-- - GRO_5566 = Growth metrics table with time series data
-- - Contains VALUE_CHANGE and PCT_CHANGE columns
-- - SEGMENT_CD links to DIM_SEG_4421 for segment names

SELECT 
    g.METRIC_DATE,
    s.SEGMENT_NAME,
    g.TOTAL_PAR_VALUE,
    g.TOTAL_MARKET_VALUE,
    g.VALUE_CHANGE,
    g.PCT_CHANGE
FROM GLD_003.GRO_5566 g
INNER JOIN SLV_009.DIM_SEG_4421 s ON g.SEGMENT_CD = s.SEGMENT_CD
WHERE g.METRIC_DATE >= DATEADD(day, -30, CURRENT_DATE())
ORDER BY g.METRIC_DATE DESC, s.SEGMENT_NAME;
```

**Why This Works**:
- Claude understands `GRO_5566` contains growth metrics over time
- Claude knows to join with segment dimension for readable names
- Claude includes all relevant metrics (par value, market value, changes)
- Claude properly filters by date range

---

## Example 3: Top Issuers by Total Position Value

### Business Question
"Show me the top 10 issuers by total position value (par value)"

### Expected Result
A table showing:
- Issuer name
- Total par value
- Total market value
- Position count
- Ranked by par value

### Without DataHub Context

**Prompt to Claude Desktop**:
```
I need to query Snowflake for the top 10 issuers by total position value. 
The database is PIMCO_DEMO. What SQL should I use?
```

**Generated SQL** (Incorrect):
```sql
-- Claude may generate something like this without context
SELECT 
    ISSUER_ID,
    SUM(PAR_VALUE) as total_par
FROM GLD_003.POS_9912
GROUP BY ISSUER_ID
ORDER BY total_par DESC
LIMIT 10;
```

**Issues**:
- Returns issuer IDs instead of names
- May not understand `ISS_8844` contains issuer aggregations
- May not join with `DIM_ISS_002` for issuer names

### With DataHub Context

**Prompt to Claude Desktop**:
```
I need to query Snowflake for the top 10 issuers by total position value. 
The database is PIMCO_DEMO. Use DataHub to understand the schema and generate the correct SQL.
```

**Generated SQL** (Correct):
```sql
-- Claude uses DataHub context to understand:
-- - ISS_8844 = Issuer aggregations table (already aggregated)
-- - Or POS_9912 = Positions table (needs aggregation)
-- - DIM_ISS_002 = Issuer dimension with issuer names

SELECT 
    i.ISSUER_NAME,
    a.TOTAL_PAR_VALUE,
    a.TOTAL_MARKET_VALUE,
    a.POSITION_COUNT
FROM GLD_003.ISS_8844 a
INNER JOIN SLV_009.DIM_ISS_002 i ON a.ISSUER_ID = i.ISS_ID
WHERE a.AS_OF_DATE = CURRENT_DATE()
ORDER BY a.TOTAL_PAR_VALUE DESC
LIMIT 10;
```

**Alternative (if aggregating from positions)**:
```sql
SELECT 
    i.ISSUER_NAME,
    SUM(p.PAR_VALUE) as TOTAL_PAR_VALUE,
    SUM(p.MARKET_VALUE) as TOTAL_MARKET_VALUE,
    COUNT(DISTINCT p.BOND_ID) as POSITION_COUNT
FROM GLD_003.POS_9912 p
INNER JOIN SLV_009.DIM_ISS_002 i ON p.ISSUER_ID = i.ISS_ID
WHERE p.AS_OF_DATE = CURRENT_DATE()
GROUP BY i.ISSUER_NAME
ORDER BY TOTAL_PAR_VALUE DESC
LIMIT 10;
```

**Why This Works**:
- Claude understands there's an aggregated table (`ISS_8844`) for issuer data
- Claude knows to join with issuer dimension for readable names
- Claude includes proper filtering by as-of date
- Claude includes relevant metrics (par value, market value, position count)

---

## Example 4: Bond Positions with Maturity Analysis

### Business Question
"Show me bond positions grouped by years to maturity for tax-exempt bonds"

### Expected Result
A table showing:
- Years to maturity (buckets)
- Total par value
- Total market value
- Number of positions
- Only for tax-exempt bonds

### Without DataHub Context

**Prompt to Claude Desktop**:
```
I need to query Snowflake to show bond positions by years to maturity for tax-exempt bonds. 
The database is PIMCO_DEMO. What SQL should I use?
```

**Generated SQL** (Incorrect):
```sql
-- Claude may generate something like this without context
SELECT 
    MATURITY_DATE,
    SUM(PAR_VALUE) as total_par
FROM GLD_003.POS_9912
GROUP BY MATURITY_DATE;
```

**Issues**:
- May not understand `POS_9912` doesn't have maturity date (need to join with bond dimension)
- May not know to calculate years to maturity
- May not filter for tax-exempt bonds correctly
- May not understand the relationship between position and bond tables

### With DataHub Context

**Prompt to Claude Desktop**:
```
I need to query Snowflake to show bond positions by years to maturity for tax-exempt bonds. 
The database is PIMCO_DEMO. Use DataHub to understand the schema and generate the correct SQL.
```

**Generated SQL** (Correct):
```sql
-- Claude uses DataHub context to understand:
-- - POS_9912 = Positions table (needs bond dimension for maturity)
-- - DIM_BND_001 = Bond dimension with maturity date
-- - DIM_SEG_4421 = Segment dimension for tax-exempt filter
-- - Need to calculate years to maturity from MATURITY_DATE

SELECT 
    CASE 
        WHEN DATEDIFF(year, CURRENT_DATE(), b.MATURITY_DATE) <= 1 THEN '0-1 years'
        WHEN DATEDIFF(year, CURRENT_DATE(), b.MATURITY_DATE) <= 3 THEN '1-3 years'
        WHEN DATEDIFF(year, CURRENT_DATE(), b.MATURITY_DATE) <= 5 THEN '3-5 years'
        WHEN DATEDIFF(year, CURRENT_DATE(), b.MATURITY_DATE) <= 10 THEN '5-10 years'
        WHEN DATEDIFF(year, CURRENT_DATE(), b.MATURITY_DATE) <= 20 THEN '10-20 years'
        ELSE '20+ years'
    END as MATURITY_BUCKET,
    SUM(p.PAR_VALUE) as TOTAL_PAR_VALUE,
    SUM(p.MARKET_VALUE) as TOTAL_MARKET_VALUE,
    COUNT(DISTINCT p.BOND_ID) as POSITION_COUNT
FROM GLD_003.POS_9912 p
INNER JOIN SLV_009.DIM_BND_001 b ON p.BOND_ID = b.BND_ID
INNER JOIN SLV_009.DIM_SEG_4421 s ON p.SEGMENT_CD = s.SEGMENT_CD
WHERE s.TAX_EXEMPT_FLAG = 1
  AND p.AS_OF_DATE = CURRENT_DATE()
GROUP BY MATURITY_BUCKET
ORDER BY 
    CASE MATURITY_BUCKET
        WHEN '0-1 years' THEN 1
        WHEN '1-3 years' THEN 2
        WHEN '3-5 years' THEN 3
        WHEN '5-10 years' THEN 4
        WHEN '10-20 years' THEN 5
        ELSE 6
    END;
```

**Why This Works**:
- Claude understands `POS_9912` needs to join with bond dimension for maturity data
- Claude knows to calculate years to maturity from `MATURITY_DATE`
- Claude creates meaningful maturity buckets
- Claude correctly filters for tax-exempt bonds using segment dimension
- Claude includes proper aggregations and ordering

---

## Key Takeaways

1. **Without DataHub**: LLM sees opaque names and guesses relationships
2. **With DataHub**: LLM retrieves context about tables, columns, and relationships
3. **Data Governance**: LLM can verify "Authorized for Reporting" structured property before using tables
4. **Better SQL**: Context enables correct joins, filters, and aggregations
5. **Business-Friendly**: Context helps generate SQL that returns meaningful business results
6. **Compliance**: DataHub structured properties ensure LLM only uses authorized tables for reporting

