# Update DT_POS_9912 with Opaque Business Logic - Instructions

## Overview

This update adds opaque business logic to the `GLD_003.DT_POS_9912` dynamic table to demonstrate how DataHub provides context for complex business rules that aren't obvious from SQL.

## What This Update Does

The update adds three new columns and complex business logic to `DT_POS_9912`:

1. **STATUS_CD**: Opaque status code ('A'/'1'/'Y' = active, 'I'/'0'/'N' = inactive)
2. **MATURITY_MULTIPLIER**: Opaque calculation based on years to maturity (< 5 years = 1.05, 5-10 years = 1.02, > 10 years = 1.0)
3. **RISK_FACTOR**: Opaque calculation based on credit rating (AAA/AA/A = 0.98, BBB/BB/B = 1.0, others = 1.05)
4. **MARKET_VALUE**: Updated to use complex adjusted calculation: `PAR_VALUE * (1 + COUPON_RATE/100) * MATURITY_MULTIPLIER * RISK_FACTOR`

## SQL Scripts to Run

### Option 1: Update Only DT_POS_9912 (Recommended)

**File**: `snowflake/update_dt_pos_9912_opaque_logic.sql`

**What it does**:
- Updates the existing `GLD_003.DT_POS_9912` dynamic table with opaque business logic
- Adds new columns: STATUS_CD, MATURITY_MULTIPLIER, RISK_FACTOR
- Updates MARKET_VALUE calculation to use the complex formula
- Includes verification queries

**How to run**:
1. Open Snowflake UI
2. Select database: `PIMCO_DEMO`
3. Select warehouse: `MSJDEMO`
4. Copy and paste the entire contents of `update_dt_pos_9912_opaque_logic.sql`
5. Run the script
6. Wait for dynamic table to refresh (5 minutes)

**Note**: The view `GLD_003.POS_9912` will automatically pick up the new columns since it's `SELECT * FROM DT_POS_9912`.

### Option 2: Full Rebuild (If Needed)

**File**: `snowflake/setup_complete.sql`

**What it does**:
- Drops and recreates all schemas, tables, dynamic tables, and views
- Includes the updated DT_POS_9912 with opaque business logic
- **WARNING**: This will delete all existing data and recreate everything

**How to run**:
1. Open Snowflake UI
2. Select database: `PIMCO_DEMO`
3. Select warehouse: `MSJDEMO`
4. Copy and paste the entire contents of `setup_complete.sql`
5. Run the script
6. Wait for dynamic tables to refresh (1-5 minutes)

## Verification

After running the update script, verify the changes:

```sql
-- Check that new columns exist
SELECT 
    STATUS_CD,
    MATURITY_MULTIPLIER,
    RISK_FACTOR,
    PAR_VALUE,
    MARKET_VALUE
FROM GLD_003.POS_9912
LIMIT 10;

-- Check status code distribution
SELECT 
    STATUS_CD,
    COUNT(*) as POSITION_COUNT
FROM GLD_003.POS_9912
GROUP BY STATUS_CD;

-- Check maturity multiplier distribution
SELECT 
    MATURITY_MULTIPLIER,
    COUNT(*) as POSITION_COUNT
FROM GLD_003.POS_9912
GROUP BY MATURITY_MULTIPLIER
ORDER BY MATURITY_MULTIPLIER DESC;

-- Check risk factor distribution
SELECT 
    RISK_FACTOR,
    COUNT(*) as POSITION_COUNT
FROM GLD_003.POS_9912
GROUP BY RISK_FACTOR
ORDER BY RISK_FACTOR DESC;

-- Verify adjusted market value calculation
SELECT 
    PAR_VALUE,
    MARKET_VALUE,
    CASE 
        WHEN PAR_VALUE > 0 
        THEN (MARKET_VALUE / PAR_VALUE) 
        ELSE 0 
    END as ADJUSTMENT_FACTOR
FROM GLD_003.POS_9912
WHERE PAR_VALUE > 0
LIMIT 10;
```

## Expected Results

After the update:

1. **STATUS_CD column**: Should show 'A' for active positions (from BUY transactions)
2. **MATURITY_MULTIPLIER column**: Should show 1.05, 1.02, or 1.0 based on years to maturity
3. **RISK_FACTOR column**: Should show 0.98, 1.0, or 1.05 based on credit rating
4. **MARKET_VALUE column**: Should be adjusted (not simple par + interest)

## Next Steps

After updating the dynamic table in Snowflake:

1. **Wait for dynamic table refresh** (5 minutes)
2. **Run DataHub metadata scripts** to add new glossary terms and documentation:
   ```bash
   python3 scripts/create_metadata.py
   python3 scripts/apply_documentation.py
   ```
3. **Verify in DataHub UI** that:
   - New glossary terms are visible (Position Status, Maturity Multiplier, Risk Factor, Adjusted Market Value)
   - Table documentation explains the opaque business logic
   - Column documentation explains the opaque calculations
4. **Test with Claude Desktop** using the prompts in `demo/CLAUDE_PROMPTS.md`

## Troubleshooting

### Issue: Dynamic table not refreshing

**Solution**: Manually refresh the dynamic table:
```sql
ALTER DYNAMIC TABLE GLD_003.DT_POS_9912 REFRESH;
```

### Issue: View doesn't show new columns

**Solution**: The view should automatically pick up new columns. If not, recreate the view:
```sql
CREATE OR REPLACE VIEW GLD_003.POS_9912 AS
SELECT * FROM GLD_003.DT_POS_9912;
```

### Issue: Downstream tables (DT_SEG_4421, etc.) not updating

**Solution**: These tables reference DT_POS_9912 and should automatically refresh. If not, manually refresh:
```sql
ALTER DYNAMIC TABLE GLD_003.DT_SEG_4421 REFRESH;
ALTER DYNAMIC TABLE GLD_003.DT_REG_7733 REFRESH;
ALTER DYNAMIC TABLE GLD_003.DT_ISS_8844 REFRESH;
ALTER DYNAMIC TABLE GLD_003.DT_GRO_5566 REFRESH;
```

## Files Modified

1. `snowflake/dynamic_tables.sql` - Updated DT_POS_9912 definition
2. `snowflake/setup_complete.sql` - Updated DT_POS_9912 definition
3. `snowflake/update_dt_pos_9912_opaque_logic.sql` - **NEW** SQL script to run in Snowflake

## Files to Run in Snowflake

**Primary script** (recommended):
- `snowflake/update_dt_pos_9912_opaque_logic.sql`

**Alternative** (full rebuild):
- `snowflake/setup_complete.sql`

