# PIMCO DataHub LLM Demo - Testing Guide

This guide provides comprehensive testing instructions, query examples with expected results, and step-by-step procedures for testing with and without DataHub context.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Query Examples with Expected Results](#query-examples-with-expected-results)
3. [Testing Without DataHub Context](#testing-without-datahub-context)
4. [Testing With DataHub Context](#testing-with-datahub-context)
5. [Verification Steps](#verification-steps)

---

## Prerequisites

Before testing, ensure you have:

1. ✅ Snowflake database `PIMCO_DEMO` set up with all schemas and data
2. ✅ DataHub Cloud ingestion completed (all tables visible in DataHub)
3. ✅ Glossary terms, tags, and domains created in DataHub
4. ✅ Terms and tags applied to tables/columns (run `scripts/apply_terms_and_tags.py`)
5. ✅ Claude Desktop configured with Snowflake MCP server
6. ✅ DataHub MCP server configured (if available)

---

## Query Examples with Expected Results

### Example 1: Total Positions by Region for Tax-Exempt Bonds

#### Business Question
"Show me total municipal bond positions by region for tax-exempt bonds"

#### Expected SQL (Correct)
```sql
SELECT 
    r.REGION_NAME,
    SUM(p.PAR_VALUE) as TOTAL_PAR_VALUE,
    SUM(p.MARKET_VALUE) as TOTAL_MARKET_VALUE,
    COUNT(DISTINCT p.BOND_ID) as POSITION_COUNT
FROM GLD_003.POS_9912 p
INNER JOIN SLV_009.DIM_REG_003 r ON p.REGION_CD = r.REGION_CD
INNER JOIN SLV_009.DIM_SEG_4421 s ON p.SEGMENT_CD = s.SEGMENT_CD
WHERE s.SEGMENT_CD = '001'  -- Tax-exempt segment code
  AND p.AS_OF_DATE = (SELECT MAX(AS_OF_DATE) FROM GLD_003.POS_9912)
GROUP BY r.REGION_NAME
ORDER BY TOTAL_PAR_VALUE DESC;
```

#### Expected Results Structure
```
REGION_NAME        | TOTAL_PAR_VALUE | TOTAL_MARKET_VALUE | POSITION_COUNT
------------------|-----------------|-------------------|----------------
West              | 150000000.00    | 152500000.00      | 45
Northeast         | 120000000.00    | 122000000.00      | 38
South             | 95000000.00     | 97000000.00       | 32
Midwest           | 75000000.00     | 76500000.00       | 28
Other             | 25000000.00     | 25500000.00       | 12
```

#### Key Points to Verify
- ✅ Uses correct table `GLD_003.POS_9912` for positions
- ✅ Joins with `DIM_REG_003` for region names (not just codes)
- ✅ Joins with `DIM_SEG_4421` for segment filtering
- ✅ Filters by segment code `'001'` (tax-exempt)
- ✅ Uses latest `AS_OF_DATE` for current positions
- ✅ Aggregates `PAR_VALUE` and `MARKET_VALUE` correctly
- ✅ Returns readable region names, not codes

---

### Example 2: Position Growth Over Time by Segment

#### Business Question
"Show me how bond positions have grown over the last 30 days by segment"

#### Expected SQL (Correct)
```sql
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

#### Expected Results Structure
```
METRIC_DATE | SEGMENT_NAME    | TOTAL_PAR_VALUE | TOTAL_MARKET_VALUE | VALUE_CHANGE | PCT_CHANGE
------------|-----------------|-----------------|-------------------|--------------|------------
2024-11-15  | Tax-Exempt      | 465000000.00    | 473500000.00      | 5000000.00   | 1.09
2024-11-15  | Taxable         | 285000000.00    | 290500000.00      | 3000000.00   | 1.06
2024-11-14  | Tax-Exempt      | 460000000.00    | 468500000.00      | 4000000.00   | 0.88
2024-11-14  | Taxable         | 282000000.00    | 287500000.00      | 2500000.00   | 0.90
...
```

#### Key Points to Verify
- ✅ Uses `GLD_003.GRO_5566` growth metrics table
- ✅ Joins with `DIM_SEG_4421` for segment names
- ✅ Filters by date range (last 30 days)
- ✅ Includes growth metrics (`VALUE_CHANGE`, `PCT_CHANGE`)
- ✅ Orders by date descending (most recent first)

---

### Example 3: Top 10 Issuers by Total Position Value

#### Business Question
"Show me the top 10 issuers by total position value"

#### Expected SQL (Correct)
```sql
SELECT 
    i.ISSUER_NAME,
    a.TOTAL_PAR_VALUE,
    a.TOTAL_MARKET_VALUE,
    a.POSITION_COUNT
FROM GLD_003.ISS_8844 a
INNER JOIN SLV_009.DIM_ISS_002 i ON a.ISSUER_ID = i.ISS_ID
WHERE a.AS_OF_DATE = (SELECT MAX(AS_OF_DATE) FROM GLD_003.ISS_8844)
ORDER BY a.TOTAL_PAR_VALUE DESC
LIMIT 10;
```

#### Expected Results Structure
```
ISSUER_NAME           | TOTAL_PAR_VALUE | TOTAL_MARKET_VALUE | POSITION_COUNT
---------------------|-----------------|-------------------|----------------
Issuer 1 CA          | 25000000.00     | 25500000.00       | 8
Issuer 2 NY          | 22000000.00     | 22400000.00       | 7
Issuer 3 TX          | 20000000.00     | 20400000.00       | 6
...
```

#### Key Points to Verify
- ✅ Uses aggregated table `GLD_003.ISS_8844` (not raw positions)
- ✅ Joins with `DIM_ISS_002` for issuer names
- ✅ Filters by latest `AS_OF_DATE`
- ✅ Orders by `TOTAL_PAR_VALUE` descending
- ✅ Limits to top 10 results
- ✅ Returns readable issuer names, not IDs

---

### Example 4: Bond Positions by Maturity Buckets for Tax-Exempt Bonds

#### Business Question
"Show me bond positions grouped by years to maturity for tax-exempt bonds"

#### Expected SQL (Correct)
```sql
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
WHERE s.SEGMENT_CD = '001'  -- Tax-exempt
  AND p.AS_OF_DATE = (SELECT MAX(AS_OF_DATE) FROM GLD_003.POS_9912)
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

#### Expected Results Structure
```
MATURITY_BUCKET | TOTAL_PAR_VALUE | TOTAL_MARKET_VALUE | POSITION_COUNT
----------------|----------------|-------------------|----------------
0-1 years       | 15000000.00    | 15200000.00      | 8
1-3 years       | 35000000.00    | 35600000.00      | 15
3-5 years       | 45000000.00    | 45800000.00      | 18
5-10 years      | 60000000.00    | 61100000.00      | 22
10-20 years     | 40000000.00    | 40700000.00      | 16
20+ years       | 25000000.00    | 25400000.00      | 10
```

#### Key Points to Verify
- ✅ Joins with `DIM_BND_001` for maturity date
- ✅ Calculates years to maturity correctly
- ✅ Creates meaningful maturity buckets
- ✅ Filters for tax-exempt bonds (`SEGMENT_CD = '001'`)
- ✅ Aggregates by maturity bucket
- ✅ Orders buckets logically (shortest to longest)

---

### Example 5: Total Positions by Segment (Tax-Exempt vs Taxable)

#### Business Question
"Show me total positions by segment (tax-exempt vs taxable)"

#### Expected SQL (Correct)
```sql
SELECT 
    s.SEGMENT_NAME,
    seg.TOTAL_PAR_VALUE,
    seg.TOTAL_MARKET_VALUE,
    seg.POSITION_COUNT
FROM GLD_003.SEG_4421 seg
INNER JOIN SLV_009.DIM_SEG_4421 s ON seg.SEGMENT_CD = s.SEGMENT_CD
WHERE seg.AS_OF_DATE = (SELECT MAX(AS_OF_DATE) FROM GLD_003.SEG_4421)
ORDER BY seg.TOTAL_PAR_VALUE DESC;
```

#### Expected Results Structure
```
SEGMENT_NAME | TOTAL_PAR_VALUE | TOTAL_MARKET_VALUE | POSITION_COUNT
-------------|-----------------|-------------------|----------------
Tax-Exempt   | 465000000.00    | 473500000.00      | 155
Taxable      | 285000000.00    | 290500000.00      | 95
```

#### Key Points to Verify
- ✅ Uses aggregated segment table `GLD_003.SEG_4421`
- ✅ Joins with dimension for segment names
- ✅ Filters by latest date
- ✅ Returns readable segment names

---

## Testing Without DataHub Context

### Step 1: Open Claude Desktop

1. Open Claude Desktop application
2. Ensure Snowflake MCP server is connected (check MCP status)

### Step 2: Ask Without DataHub Context

**Prompt to Claude:**
```
I need to query Snowflake for total municipal bond positions by region for tax-exempt bonds. 
The database is PIMCO_DEMO. What SQL query should I use?
```

### Step 3: Common Issues Without DataHub

Claude may generate SQL with these problems:

- ❌ Uses wrong table names (guessing based on opaque names)
- ❌ Doesn't join dimension tables for readable names
- ❌ Uses wrong segment codes (e.g., `'TAX_EXEMPT'` instead of `'001'`)
- ❌ Misses date filtering (uses wrong or no `AS_OF_DATE`)
- ❌ Doesn't understand relationships between tables
- ❌ Returns codes instead of readable names

### Step 4: Note the Issues

Document what Claude got wrong:
- What table did it use?
- What joins did it miss?
- What filters were incorrect?
- What values were wrong?

### Step 5: Run the Incorrect SQL

1. Copy the SQL Claude generated
2. Run it in Snowflake
3. Note the results (may be empty, wrong, or error)

---

## Testing With DataHub Context

### Step 1: Configure DataHub MCP (if available)

If you have DataHub MCP server configured:
1. Ensure it's connected in Claude Desktop
2. Test with: "Search DataHub for municipal bond positions"

### Step 2: Ask With DataHub Context

**Prompt to Claude:**
```
I need to query Snowflake for total municipal bond positions by region for tax-exempt bonds. 
The database is PIMCO_DEMO. 
Use DataHub to understand the schema, tables, columns, and relationships. 
Generate the correct SQL query.
```

**Alternative Prompt (if DataHub MCP not available):**
```
I need to query Snowflake for total municipal bond positions by region for tax-exempt bonds. 
The database is PIMCO_DEMO. 

Here's what I know from DataHub:
- Table GLD_003.POS_9912 contains aggregated bond positions
- Column SEGMENT_CD links to segment dimension (value '001' = tax-exempt)
- Column REGION_CD links to region dimension (DIM_REG_003)
- Need to join with DIM_REG_003 for region names
- Need to join with DIM_SEG_4421 for segment filtering
- Use latest AS_OF_DATE for current positions

Generate the correct SQL query.
```

### Step 3: Verify the Generated SQL

Check that Claude's SQL:
- ✅ Uses correct table `GLD_003.POS_9912`
- ✅ Joins with `DIM_REG_003` for region names
- ✅ Joins with `DIM_SEG_4421` for segment filtering
- ✅ Filters by segment code `'001'` (tax-exempt)
- ✅ Uses latest `AS_OF_DATE`
- ✅ Includes proper aggregations

### Step 4: Run the Correct SQL

1. Copy the SQL Claude generated
2. Run it in Snowflake
3. Verify results match expected structure
4. Check that values are reasonable

---

## Verification Steps

### 1. Verify Data in Snowflake

Run these queries to verify data exists:

```sql
-- Check positions exist
SELECT COUNT(*) as position_count FROM GLD_003.POS_9912;

-- Check segment codes
SELECT DISTINCT SEGMENT_CD FROM GLD_003.SEG_4421;

-- Check regions exist
SELECT COUNT(*) as region_count FROM SLV_009.DIM_REG_003;

-- Check latest date
SELECT MAX(AS_OF_DATE) as latest_date FROM GLD_003.POS_9912;
```

### 2. Verify DataHub Metadata

In DataHub UI:
1. Search for `POS_9912`
2. Verify table has:
   - ✅ Description
   - ✅ Tags (Gold Schema, Reporting, Position Data, etc.)
   - ✅ Glossary terms (Municipal Bond Position)
   - ✅ Domain (Reporting & Analytics)
3. Check columns:
   - ✅ `PAR_VALUE` has glossary term "Par Value"
   - ✅ `SEGMENT_CD` has glossary terms "Bond Segment", etc.
   - ✅ `REGION_CD` has glossary term "Geographic Region"

### 3. Verify Claude Can Access DataHub

If DataHub MCP is configured:
1. Ask Claude: "Search DataHub for municipal bond positions"
2. Verify Claude can retrieve table metadata
3. Check that Claude understands relationships

### 4. Compare Results

Create a comparison table:

| Aspect | Without DataHub | With DataHub |
|--------|----------------|--------------|
| Table Used | ? | `GLD_003.POS_9912` ✅ |
| Joins | ? | Correct joins ✅ |
| Segment Filter | ? | `'001'` ✅ |
| Region Names | ? | Readable names ✅ |
| Date Filter | ? | Latest date ✅ |
| Results | ? | Correct results ✅ |

---

## Next Steps

1. Test all 5 example queries
2. Document results for each
3. Create a demo script highlighting the differences
4. Prepare visualizations comparing before/after

---

## Troubleshooting

### Issue: Claude generates wrong SQL even with DataHub

**Solution:**
- Verify DataHub MCP is connected
- Check that metadata is ingested in DataHub
- Try providing more explicit context in prompt

### Issue: SQL returns empty results

**Solution:**
- Verify `AS_OF_DATE` filter uses correct date
- Check that segment codes match (`'001'` not `'TAX_EXEMPT'`)
- Verify data exists in Snowflake

### Issue: Wrong column names

**Solution:**
- Verify column names match actual schema
- Check if using views vs. dynamic tables
- Verify DataHub has correct column metadata

---

## Quick Reference

### Correct Segment Codes
- `'001'` = Tax-Exempt
- `'002'` = Taxable
- `'X'` = Other

### Key Tables
- `GLD_003.POS_9912` = Positions
- `GLD_003.SEG_4421` = Segment aggregations
- `GLD_003.REG_7733` = Region aggregations
- `GLD_003.ISS_8844` = Issuer aggregations
- `GLD_003.GRO_5566` = Growth metrics
- `SLV_009.DIM_BND_001` = Bond dimension
- `SLV_009.DIM_ISS_002` = Issuer dimension
- `SLV_009.DIM_REG_003` = Region dimension
- `SLV_009.DIM_SEG_4421` = Segment dimension

### Key Views
- `SLV_009.TXN_7821` = View of transaction dynamic table
- `SLV_009.DIM_BND_001` = View of bond dimension dynamic table
- `SLV_009.DIM_ISS_002` = View of issuer dimension dynamic table

