# Testing with LLM (Claude Desktop) - Step-by-Step Guide

This guide walks you through testing the demo with Claude Desktop, both with and without DataHub context.

## Prerequisites

1. ✅ Claude Desktop installed and running
2. ✅ Snowflake MCP server configured in Claude Desktop
3. ✅ Snowflake credentials working
4. ✅ DataHub ingestion completed
5. ✅ Glossary terms and tags applied to tables

---

## Part 1: Testing WITHOUT DataHub Context

### Step 1: Open Claude Desktop

1. Launch Claude Desktop
2. Check that Snowflake MCP server is connected (you should see it in the MCP status)
3. Start a new conversation

### Step 2: Test Query 1 - Total Positions by Region for Tax-Exempt Bonds

**Prompt to Claude:**
```
I need to query Snowflake for total municipal bond positions by region for tax-exempt bonds. 
The database is PIMCO_DEMO. What SQL query should I use?
```

### Step 3: Analyze Claude's Response

Claude may generate SQL like this:

```sql
-- Likely incorrect without context
SELECT 
    REGION_CD,
    SUM(PAR_VALUE) as total_par,
    SUM(MARKET_VALUE) as total_market
FROM GLD_003.POS_9912
WHERE SEGMENT_CD = 'TAX_EXEMPT'
GROUP BY REGION_CD;
```

**Issues to note:**
- ❌ Returns region codes, not names
- ❌ Wrong segment code (`'TAX_EXEMPT'` instead of `'001'`)
- ❌ Missing date filter
- ❌ No joins with dimension tables

### Step 4: Run the SQL

1. Copy the SQL Claude generated
2. Open Snowflake UI
3. Run the SQL
4. Note the results (may be empty or wrong)

### Step 5: Document the Issues

Create a note like this:

```
Query 1 WITHOUT DataHub:
- Generated SQL: [paste SQL]
- Issues: [list issues]
- Results: [describe results]
- Correct approach: [what should have been done]
```

---

## Part 2: Testing WITH DataHub Context

### Step 1: Provide DataHub Context

**Option A: If DataHub MCP is configured**

```
I need to query Snowflake for total municipal bond positions by region for tax-exempt bonds. 
The database is PIMCO_DEMO. 
Use DataHub to search for and understand:
- The table containing bond positions
- The columns for region and segment
- The relationships between tables
- The correct segment codes for tax-exempt bonds
Generate the correct SQL query.
```

**Option B: Provide context manually**

```
I need to query Snowflake for total municipal bond positions by region for tax-exempt bonds. 
The database is PIMCO_DEMO.

From DataHub, I know:
- Table GLD_003.POS_9912 contains aggregated bond positions
- Column SEGMENT_CD uses code '001' for tax-exempt bonds
- Column REGION_CD links to SLV_009.DIM_REG_003 for region names
- Need to filter by latest AS_OF_DATE
- Need to join with DIM_REG_003 to get REGION_NAME

Generate the correct SQL query.
```

### Step 2: Analyze Claude's Response

Claude should generate SQL like this:

```sql
-- Correct with context
SELECT 
    r.REGION_NAME,
    SUM(p.PAR_VALUE) as TOTAL_PAR_VALUE,
    SUM(p.MARKET_VALUE) as TOTAL_MARKET_VALUE,
    COUNT(DISTINCT p.BOND_ID) as POSITION_COUNT
FROM GLD_003.POS_9912 p
INNER JOIN SLV_009.DIM_REG_003 r ON p.REGION_CD = r.REGION_CD
INNER JOIN SLV_009.DIM_SEG_4421 s ON p.SEGMENT_CD = s.SEGMENT_CD
WHERE s.SEGMENT_CD = '001'  -- Tax-exempt
  AND p.AS_OF_DATE = (SELECT MAX(AS_OF_DATE) FROM GLD_003.POS_9912)
GROUP BY r.REGION_NAME
ORDER BY TOTAL_PAR_VALUE DESC;
```

**Verify it's correct:**
- ✅ Joins with DIM_REG_003 for region names
- ✅ Uses segment code '001' (tax-exempt)
- ✅ Filters by latest AS_OF_DATE
- ✅ Returns readable region names

### Step 3: Run the SQL

1. Copy the SQL
2. Run in Snowflake
3. Verify results are correct

### Step 4: Compare Results

| Aspect | Without DataHub | With DataHub |
|--------|----------------|--------------|
| Table | `GLD_003.POS_9912` | `GLD_003.POS_9912` ✅ |
| Region | Codes only ❌ | Names ✅ |
| Segment Filter | `'TAX_EXEMPT'` ❌ | `'001'` ✅ |
| Date Filter | Missing ❌ | Latest date ✅ |
| Results | Wrong/Empty ❌ | Correct ✅ |

---

## Part 3: Testing All Example Queries

### Query 2: Position Growth Over Time

**Without DataHub:**
```
Show me how bond positions have grown over the last 30 days by segment.
Database: PIMCO_DEMO
```

**With DataHub:**
```
Show me how bond positions have grown over the last 30 days by segment.
Database: PIMCO_DEMO
Use DataHub to understand the growth metrics table and segment relationships.
```

### Query 3: Top Issuers

**Without DataHub:**
```
Show me the top 10 issuers by total position value.
Database: PIMCO_DEMO
```

**With DataHub:**
```
Show me the top 10 issuers by total position value.
Database: PIMCO_DEMO
Use DataHub to find the issuer aggregations table and dimension.
```

### Query 4: Maturity Analysis

**Without DataHub:**
```
Show me bond positions by years to maturity for tax-exempt bonds.
Database: PIMCO_DEMO
```

**With DataHub:**
```
Show me bond positions by years to maturity for tax-exempt bonds.
Database: PIMCO_DEMO
Use DataHub to understand how to join positions with bond dimension for maturity dates.
```

---

## Part 4: Interactive Testing

### Test 1: Ask Follow-up Questions

After Claude generates SQL, ask:

```
Is this query correct? Can you verify:
1. The table names are correct?
2. The joins are necessary?
3. The segment code is correct?
4. The date filter uses the latest date?
```

### Test 2: Ask for Explanations

```
Can you explain:
1. Why you chose this table?
2. Why you joined with these dimension tables?
3. What the segment code '001' means?
4. How to filter for the latest positions?
```

### Test 3: Ask for Alternatives

```
Can you show me an alternative query that:
1. Uses the aggregated segment table instead?
2. Filters by region as well?
3. Includes additional metrics?
```

---

## Part 5: Documenting Results

Create a document with:

### For Each Query:

1. **Query Description**
   - Business question
   - Expected result type

2. **Without DataHub**
   - Generated SQL
   - Issues found
   - Results (if any)
   - What went wrong

3. **With DataHub**
   - Generated SQL
   - Why it's correct
   - Results (verified)
   - What DataHub context helped

4. **Comparison**
   - Side-by-side SQL
   - Side-by-side results
   - Key differences

---

## Troubleshooting

### Issue: Claude generates wrong SQL even with context

**Solutions:**
1. Be more explicit in the prompt
2. Provide table names directly
3. Show example of correct segment code
4. Reference specific DataHub metadata

### Issue: SQL runs but returns empty results

**Solutions:**
1. Check AS_OF_DATE filter
2. Verify segment codes (use '001' not 'TAX_EXEMPT')
3. Check data exists in Snowflake
4. Verify joins are correct

### Issue: Claude doesn't understand DataHub context

**Solutions:**
1. Manually provide key metadata
2. Show example queries
3. Explain the schema structure
4. Reference glossary terms

---

## Quick Reference Prompts

### Good Prompt Template

```
I need to query Snowflake for [business question].
Database: PIMCO_DEMO

From DataHub, I know:
- [Table] contains [what data]
- [Column] represents [business concept]
- [Relationship] links to [other table]
- [Code] means [business meaning]

Generate the correct SQL query.
```

### Bad Prompt (too vague)

```
Query Snowflake for bond positions.
```

### Good Prompt (specific)

```
I need to query Snowflake for total municipal bond positions by region for tax-exempt bonds.
Database: PIMCO_DEMO

From DataHub:
- Table GLD_003.POS_9912 contains aggregated bond positions
- Column SEGMENT_CD uses code '001' for tax-exempt, '002' for taxable
- Column REGION_CD links to SLV_009.DIM_REG_003 for region names
- Filter by latest AS_OF_DATE for current positions

Generate SQL that joins with dimension tables and returns readable region names.
```

---

## Next Steps

1. Test all 5 example queries
2. Document results
3. Create comparison slides
4. Prepare demo script
5. Practice the demo flow

