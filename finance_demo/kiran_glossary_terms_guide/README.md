# Guide: Automatically Apply Glossary Terms from dbt to DataHub

## Overview

This guide shows how to automatically apply glossary terms to dbt models and columns in DataHub using meta mappings. The workflow is:

1. **Create glossary terms in DataHub** (one-time setup) - via CLI or UI
2. **Add meta properties to dbt models/columns** (in your dbt project)
3. **Configure meta mappings in ingestion recipe** (maps meta → terms)
4. **Run dbt ingestion** (terms automatically applied)
5. **Verify terms are applied** (in DataHub UI)

## What DataHub Supports

### Meta Mapping Operations

DataHub's dbt source supports these operations in `meta_mapping` and `column_meta_mapping`:

- **`add_term`**: Add a single glossary term
- **`add_terms`**: Add multiple glossary terms (comma-separated)

### Match Patterns

- **Exact match**: `match: "Revenue"` → matches exactly "Revenue"
- **Regex match**: `match: "Silver|Gold"` → matches "Silver" OR "Gold"
- **Wildcard**: `match: ".*"` → matches any value

### Dynamic Term Names

- **`{{ $match }}`**: Uses the matched value from meta property
- **Static**: `term: "Revenue"` → always uses "Revenue"

---

## Step 1: Create Glossary Terms in DataHub

**IMPORTANT**: Terms must exist in DataHub BEFORE running ingestion. The meta mapping will look for terms by name (case-sensitive).

### Option A: Import via CLI (Recommended)

1. **Create a `glossary_terms.yaml` file** with your terms (see `examples/glossary_terms.yaml` for format)

2. **Set your DataHub token**:
   ```bash
   export DATAHUB_PAT=your_datahub_pat_token
   ```

3. **Run the import script**:
   ```bash
   python import_glossary_terms.py
   ```

4. **Verify in DataHub UI**:
   - Go to DataHub → Glossary
   - You should see your term groups and terms

**See `examples/import_glossary_terms.py` for the complete CLI script.**

### Option B: Create Manually in DataHub UI

1. **Go to DataHub UI** → Navigate to **Glossary** section

2. **Create Term Groups (Glossary Nodes) first**:
   - Click "Create Term Group" or "+" button
   - Enter name (e.g., "Data Tier")
   - Enter description (optional)
   - Click "Create"

3. **Create Terms within each group**:
   - Click on the term group
   - Click "Create Term" or "+" button
   - Enter term name (e.g., "Silver") - **must match exactly what you'll use in dbt meta**
   - Enter description (optional)
   - Click "Create"

4. **Repeat for all terms**:
   - Create all term groups first
   - Then create all terms within their respective groups

**Key Point**: Term names must match exactly (case-sensitive) what you'll use in your dbt meta properties. For example, if your dbt model has `data_tier: Silver`, the term must be named exactly "Silver" in DataHub.

---

## Step 2: Add Meta Properties to dbt Models

**IN DBT PROJECT**: Add meta properties to your dbt models and columns.

### Model-Level Meta

Add meta properties at the model level in your `schema.yml` file:

```yaml
models:
  - name: silver_revenue
    description: Cleaned and enriched revenue transaction data
    config:
      meta:
        data_tier: Silver          # Will map to "Silver" glossary term
        domain: Revenue             # Will map to "Revenue" glossary term
        terms_list: "Revenue,Product Revenue,Financial Metrics"  # Multiple terms
```

**Where to add**: In your dbt project, in the `models/` directory, create or edit `schema.yml` files.

### Column-Level Meta

Add meta properties at the column level:

```yaml
columns:
  - name: amount
    description: Transaction amount in the specified currency
    meta:
      term: Transaction Amount      # Will map to "Transaction Amount" term
  - name: total_revenue
    description: Total revenue amount
    meta:
      term: Revenue                 # Will map to "Revenue" term
```

**See `examples/dbt_schema_example.yml` for a complete example.**

---

## Step 3: Configure Meta Mappings in Ingestion Recipe

**IN DATAHUB INGESTION RECIPE**: Configure how dbt meta properties map to glossary terms.

### Model-Level Meta Mapping

Add `meta_mapping` section to your dbt ingestion recipe:

```yaml
source:
  type: dbt-cloud  # or dbt
  config:
    enable_meta_mapping: true
    write_semantics: PATCH  # PATCH adds without overwriting existing terms
    
    meta_mapping:
      # Map data_tier meta to glossary terms
      data_tier:
        match: "Silver|Gold"        # Regex: matches "Silver" OR "Gold"
        operation: "add_term"
        config:
          term: "{{ $match }}"      # Uses matched value ("Silver" or "Gold")
      
      # Map domain meta to Revenue term
      domain:
        match: "Revenue"
        operation: "add_term"
        config:
          term: "Revenue"           # Static term name
      
      # Map multiple terms from comma-separated list
      terms_list:
        match: ".*"                 # Matches any value
        operation: "add_terms"
        config:
          separator: ","            # Splits by comma
```

### Column-Level Meta Mapping

Add `column_meta_mapping` section:

```yaml
    column_meta_mapping:
      # Map term meta to glossary term
      term:
        match: ".*"
        operation: "add_term"
        config:
          term: "{{ $match }}"      # Uses the term name from meta
```

**See `examples/dbt_ingestion_recipe_example.yml` for a complete example.**

---

## Step 4: Run dbt Ingestion

**IN TERMINAL**: Run the DataHub ingestion command.

1. **Set environment variables**:
   ```bash
   export DBT_CLOUD_TOKEN=your_dbt_cloud_token
   export DATAHUB_PAT=your_datahub_pat_token
   ```

2. **Run ingestion**:
   ```bash
   datahub ingest -c dbt_cloud_ingestion_recipe.yml
   ```

**What Happens**:
1. DataHub ingests dbt models from dbt Cloud (or local artifacts)
2. For each model/column, checks meta properties
3. Applies meta mappings: adds glossary terms based on meta values
4. Terms appear in DataHub UI automatically

---

## Step 5: Verify Terms Are Applied

**IN DATAHUB UI**: Verify that terms were automatically applied.

1. **Search for your dbt model** (e.g., `silver_revenue`)

2. **Check Glossary Terms section**:
   - Should show terms like: Silver, Revenue, Product Revenue, Financial Metrics
   - Terms should match what you configured in meta mappings

3. **Check Columns**:
   - Click on a column (e.g., `amount`)
   - Should show column-level terms (e.g., "Transaction Amount")
   - Terms should match what you configured in column meta mappings

4. **Verify term associations**:
   - Terms should be clickable links to the glossary term definitions
   - You can click through to see term details

**If terms are missing**: See Troubleshooting section below.

---

## Common Patterns

### Pattern 1: Single Term from Meta Value

**In dbt** (`schema.yml`):
```yaml
models:
  - name: revenue_model
    config:
      meta:
        domain: Revenue
```

**In ingestion recipe**:
```yaml
meta_mapping:
  domain:
    match: "Revenue"
    operation: "add_term"
    config:
      term: "Revenue"
```

**Result**: Model gets "Revenue" glossary term applied.

### Pattern 2: Dynamic Term Name from Meta

**In dbt** (`schema.yml`):
```yaml
models:
  - name: silver_revenue
    config:
      meta:
        data_tier: Silver
```

**In ingestion recipe**:
```yaml
meta_mapping:
  data_tier:
    match: "Silver|Gold"
    operation: "add_term"
    config:
      term: "{{ $match }}"  # Becomes "Silver" or "Gold" based on meta value
```

**Result**: Model gets "Silver" glossary term applied (matches the meta value).

### Pattern 3: Multiple Terms from Comma-Separated List

**In dbt** (`schema.yml`):
```yaml
models:
  - name: gold_revenue_summary
    config:
      meta:
        terms_list: "Revenue,Product Revenue,Financial Metrics"
```

**In ingestion recipe**:
```yaml
meta_mapping:
  terms_list:
    match: ".*"
    operation: "add_terms"
    config:
      separator: ","
```

**Result**: Model gets all three terms applied: "Revenue", "Product Revenue", "Financial Metrics".

### Pattern 4: Column-Level Term

**In dbt** (`schema.yml`):
```yaml
columns:
  - name: amount
    meta:
      term: Transaction Amount
```

**In ingestion recipe**:
```yaml
column_meta_mapping:
  term:
    match: ".*"
    operation: "add_term"
    config:
      term: "{{ $match }}"
```

**Result**: Column gets "Transaction Amount" glossary term applied.

---

## Troubleshooting

### Terms Not Appearing After Ingestion

**Checklist**:

1. **Verify terms exist in DataHub**:
   - Go to DataHub UI → Glossary
   - Confirm all terms exist with exact names (case-sensitive)
   - If missing, create them first (Step 1)

2. **Check term names match exactly**:
   - Term name in DataHub must match meta property value exactly
   - Example: If meta is `data_tier: Silver`, term must be named "Silver" (not "silver" or "SILVER")

3. **Check meta properties in dbt**:
   - Verify dbt models have correct meta in `schema.yml`
   - Run `dbt compile` or `dbt parse` to validate
   - Check that meta properties are under `config.meta` for models

4. **Check meta mapping configuration**:
   - Verify `meta_mapping` section matches your meta property names
   - Example: If meta is `data_tier`, mapping must have `data_tier:` key
   - Verify `enable_meta_mapping: true` is set

5. **Check ingestion logs**:
   - Look for errors about missing terms
   - Look for warnings about meta mapping failures
   - Verify ingestion completed successfully

6. **Verify write_semantics**:
   - Use `write_semantics: PATCH` to add terms without overwriting
   - `OVERWRITE` will replace existing terms

### Column-Level Terms Not Appearing

**Checklist**:

1. **Enable column meta mapping**:
   - Ensure `enable_column_meta_mapping: true` in recipe
   - Verify `column_meta_mapping` section exists

2. **Check column meta properties**:
   - Verify columns have meta properties in `schema.yml`
   - Meta should be at column level, not model level

3. **Check column_meta_mapping config**:
   - Verify mapping config matches column meta property names
   - Example: If column meta is `term:`, mapping must have `term:` key

### Ingestion Fails

**Checklist**:

1. **Check environment variables**:
   - `DBT_CLOUD_TOKEN` is set correctly
   - `DATAHUB_PAT` is set correctly

2. **Check dbt Cloud credentials**:
   - Account ID, Project ID, Job ID are correct
   - dbt Cloud job has run successfully (generates manifest.json)

3. **Check file paths**:
   - If using local dbt, verify `DBT_PROJECT_ROOT` points to correct directory
   - Verify manifest.json and catalog.json exist in target/

---

## Summary

**The Complete Workflow**:

1. ✅ **In DataHub**: Create glossary terms (CLI or UI)
2. ✅ **In dbt**: Add meta properties to models/columns
3. ✅ **In DataHub recipe**: Configure meta mappings
4. ✅ **In Terminal**: Run dbt ingestion
5. ✅ **In DataHub UI**: Verify terms are applied

**Key Files**:

- `examples/glossary_terms.yaml` - Term definitions for CLI import
- `examples/import_glossary_terms.py` - CLI import script
- `examples/dbt_schema_example.yml` - Example dbt model with meta properties
- `examples/dbt_ingestion_recipe_example.yml` - Example ingestion recipe with meta mappings

**Key Concepts**:

- Terms must exist in DataHub before ingestion
- Meta mapping matches meta property names to operations
- `{{ $match }}` uses the meta property value dynamically
- `write_semantics: PATCH` adds terms without overwriting existing ones
- Term names are case-sensitive - must match exactly

