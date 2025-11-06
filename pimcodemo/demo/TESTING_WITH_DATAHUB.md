# Testing with DataHub Context - Comprehensive Guide

This guide explains how to test the demo with DataHub context, including how to verify metadata is applied correctly and how DataHub improves LLM SQL generation.

## Prerequisites

1. ✅ DataHub Cloud account set up
2. ✅ Snowflake ingestion completed
3. ✅ Glossary terms created in DataHub
4. ✅ Tags created in DataHub
5. ✅ Domains created in DataHub
6. ✅ Terms and tags applied to tables/columns (run `scripts/apply_terms_and_tags.py`)
7. ✅ DataHub MCP server configured (optional, for direct Claude access)

---

## Part 1: Verify DataHub Metadata

### Step 1: Verify Table Ingestion

1. Log into DataHub Cloud
2. Search for `POS_9912`
3. Click on the table `PIMCO_DEMO.GLD_003.POS_9912`

**Verify:**
- ✅ Table name appears correctly
- ✅ Schema shows `GLD_003`
- ✅ Database shows `PIMCO_DEMO`
- ✅ Columns are listed (PAR_VALUE, MARKET_VALUE, SEGMENT_CD, etc.)

### Step 2: Verify Table Documentation

In the table view, check:

**Description:**
- ✅ Should say: "Aggregated bond positions table. Contains total positions by bond, issuer, region, and segment with par value and market value."

**Tags:**
- ✅ "Gold Schema"
- ✅ "Reporting"
- ✅ "Position Data"
- ✅ "Financial Metrics"
- ✅ "Core Data"

**Glossary Terms:**
- ✅ "Municipal Bond Position"

**Domain:**
- ✅ "Reporting & Analytics"

### Step 3: Verify Column Metadata

Click on a column (e.g., `PAR_VALUE`):

**Should show:**
- ✅ Glossary term: "Par Value"
- ✅ Tags: "Financial Metrics"
- ✅ Description (if available)

### Step 4: Verify Relationships

In the table view, check:

**Lineage:**
- ✅ Shows upstream sources (dynamic tables, views)
- ✅ Shows downstream usage

**Schema:**
- ✅ All columns listed
- ✅ Column types shown
- ✅ Nullability shown

---

## Part 2: Verify Glossary Terms

### Step 1: Check Glossary Terms Exist

1. Go to **Glossary** in DataHub
2. Search for "Municipal Bond Position"
3. Verify it appears

**Check:**
- ✅ Term name: "Municipal Bond Position"
- ✅ Description is present
- ✅ Domain: "Municipal Bonds"
- ✅ Term Group: "Municipal Bonds"

### Step 2: Verify Term Group

1. In Glossary, find "Municipal Bonds" term group
2. Click on it
3. Verify all terms are listed:
   - ✅ Municipal Bond Position
   - ✅ Tax-Exempt Municipal Bond
   - ✅ Taxable Municipal Bond
   - ✅ Bond Segment
   - ✅ Par Value
   - ✅ Market Value
   - ✅ Position Growth
   - ✅ Geographic Region
   - ✅ Bond Issuer
   - ✅ Bond Transaction
   - ✅ Coupon Rate
   - ✅ Maturity Date
   - ✅ Credit Rating

### Step 3: Verify Term Links to Tables

1. Click on a term (e.g., "Par Value")
2. Check **Assets** tab
3. Verify columns are listed:
   - ✅ `GLD_003.POS_9912.PAR_VALUE`
   - ✅ `GLD_003.SEG_4421.TOTAL_PAR_VALUE`
   - ✅ Other columns with PAR_VALUE

---

## Part 3: Verify Tags and Domains

### Step 1: Check Tags

1. Go to **Tags** in DataHub
2. Verify tags exist:
   - ✅ "Municipal Bonds"
   - ✅ "Gold Schema"
   - ✅ "Silver Schema"
   - ✅ "Bronze Schema"
   - ✅ "Reporting"
   - ✅ "Position Data"
   - ✅ "Transaction Data"
   - ✅ "Financial Metrics"
   - ✅ "Dimension Data"
   - ✅ "Aggregated"

### Step 2: Verify Tags Applied to Tables

1. Search for `POS_9912`
2. Check tags on the table:
   - ✅ "Gold Schema"
   - ✅ "Reporting"
   - ✅ "Position Data"
   - ✅ "Financial Metrics"

3. Check tags on columns:
   - ✅ `PAR_VALUE` has "Financial Metrics"
   - ✅ `MARKET_VALUE` has "Financial Metrics"

### Step 3: Verify Domains

1. Go to **Domains** in DataHub
2. Verify domains exist:
   - ✅ "Municipal Bonds"
   - ✅ "Trading Operations"
   - ✅ "Reporting & Analytics"

3. Check domain assignments:
   - ✅ `GLD_003.*` tables → "Reporting & Analytics"
   - ✅ `SLV_009.*` tables → "Municipal Bonds"
   - ✅ `BRZ_001.*` tables → "Trading Operations"

---

## Part 4: Testing with DataHub MCP (if configured)

### Step 1: Verify DataHub MCP Connection

1. Open Claude Desktop
2. Check MCP status
3. Verify DataHub MCP server is connected

### Step 2: Test DataHub Search

**Prompt to Claude:**
```
Search DataHub for municipal bond positions table.
```

**Expected Response:**
- Claude should find `POS_9912`
- Should describe what the table contains
- Should mention related tables

### Step 3: Test with Context Retrieval

**Prompt to Claude:**
```
I need to query Snowflake for total municipal bond positions by region for tax-exempt bonds.
Database: PIMCO_DEMO.

First, search DataHub to understand:
1. Which table contains bond positions?
2. What columns represent region and segment?
3. How are tax-exempt bonds identified?
4. What dimension tables provide readable names?

Then generate the correct SQL query.
```

**Expected Behavior:**
- Claude searches DataHub
- Retrieves table metadata
- Understands relationships
- Generates correct SQL with proper joins

---

## Part 5: Manual Context Testing

If DataHub MCP is not available, manually provide context:

### Step 1: Gather Context from DataHub

For each query, gather:

1. **Table Information:**
   - Table name
   - Description
   - Columns
   - Tags
   - Glossary terms

2. **Relationship Information:**
   - Which dimension tables link to this table?
   - What columns are used for joins?
   - What do the codes mean?

3. **Business Context:**
   - What glossary terms apply?
   - What do the segment codes mean?
   - What filters are needed?

### Step 2: Provide Context to Claude

**Example Prompt:**
```
I need to query Snowflake for total municipal bond positions by region for tax-exempt bonds.
Database: PIMCO_DEMO.

From DataHub, I know:

Table: GLD_003.POS_9912
- Description: Aggregated bond positions table
- Tags: Gold Schema, Reporting, Position Data
- Glossary Term: Municipal Bond Position

Columns:
- PAR_VALUE: Par Value (glossary term)
- MARKET_VALUE: Market Value (glossary term)
- SEGMENT_CD: Segment code (links to DIM_SEG_4421)
- REGION_CD: Region code (links to DIM_REG_003)
- AS_OF_DATE: Date filter (use latest)

Relationships:
- SEGMENT_CD joins to SLV_009.DIM_SEG_4421.SEGMENT_CD
- REGION_CD joins to SLV_009.DIM_REG_003.REGION_CD

Segment Codes:
- '001' = Tax-Exempt (from DIM_SEG_4421)
- '002' = Taxable

Generate the correct SQL query.
```

### Step 3: Verify Generated SQL

Check that Claude's SQL:
- ✅ Uses correct table
- ✅ Joins with dimension tables
- ✅ Uses correct segment code ('001')
- ✅ Filters by latest AS_OF_DATE
- ✅ Returns readable names

---

## Part 6: Comparison Testing

### Test 1: Without DataHub Context

1. Ask Claude a query without any context
2. Document the SQL generated
3. Run it in Snowflake
4. Note the issues

### Test 2: With DataHub Context

1. Provide DataHub context (or use MCP)
2. Ask Claude the same query
3. Document the SQL generated
4. Run it in Snowflake
5. Verify it's correct

### Test 3: Create Comparison

| Aspect | Without DataHub | With DataHub |
|--------|----------------|--------------|
| Table Selection | Guessed | Correct ✅ |
| Joins | Missing | Correct ✅ |
| Segment Codes | Wrong | Correct ✅ |
| Column Names | Guessed | Correct ✅ |
| Date Filters | Missing | Correct ✅ |
| Results | Wrong/Empty | Correct ✅ |

---

## Part 7: Advanced Testing

### Test 1: Complex Queries

Test queries that require:
- Multiple joins
- Complex filters
- Aggregations
- Subqueries

### Test 2: Edge Cases

Test:
- What if table doesn't exist?
- What if column name is wrong?
- What if relationship is unclear?
- What if code values are opaque?

### Test 3: Follow-up Questions

After generating SQL, ask:
- "Is this correct?"
- "Can you verify the joins?"
- "What does segment code '001' mean?"
- "How do I filter for latest data?"

---

## Troubleshooting

### Issue: Metadata not appearing in DataHub

**Solutions:**
1. Verify ingestion completed successfully
2. Check ingestion recipe is correct
3. Re-run ingestion if needed
4. Wait a few minutes for indexing

### Issue: Terms/Tags not applied

**Solutions:**
1. Run `scripts/apply_terms_and_tags.py`
2. Check for errors in script output
3. Verify URNs match ingested tables
4. Check DataHub UI for applied metadata

### Issue: DataHub MCP not working

**Solutions:**
1. Verify MCP server is running
2. Check configuration in Claude Desktop
3. Test connection manually
4. Fall back to manual context provision

---

## Verification Checklist

- [ ] All tables ingested in DataHub
- [ ] All tables have descriptions
- [ ] All tables have tags
- [ ] All tables have glossary terms
- [ ] All tables have domains
- [ ] Key columns have glossary terms
- [ ] Key columns have tags
- [ ] Glossary terms are in term group
- [ ] Term group has all terms
- [ ] Domains are assigned correctly
- [ ] Relationships/lineage visible
- [ ] DataHub MCP working (if configured)

---

## Next Steps

1. Complete all verification steps
2. Test all example queries
3. Document results
4. Create comparison materials
5. Prepare demo presentation

