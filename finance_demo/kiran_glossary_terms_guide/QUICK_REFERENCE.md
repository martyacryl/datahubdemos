# Quick Reference: Glossary Terms Workflow

## The 5-Step Process

1. **In DataHub**: Create glossary terms (CLI or UI)
2. **In dbt**: Add meta properties to models/columns
3. **In DataHub recipe**: Configure meta mappings
4. **In Terminal**: Run dbt ingestion
5. **In DataHub UI**: Verify terms are applied

## Step 1: Create Terms in DataHub

### Option A: CLI Import
```bash
export DATAHUB_PAT=your_token
cd examples/
python import_glossary_terms.py
```

### Option B: UI Manual Creation
- Go to DataHub → Glossary
- Create term groups first
- Create terms within groups
- **Key**: Term names must match dbt meta values exactly (case-sensitive)

## Step 2: Add Meta to dbt Models

**In `schema.yml`**:
```yaml
models:
  - name: silver_revenue
    config:
      meta:
        data_tier: Silver
        domain: Revenue
        terms_list: "Revenue,Product Revenue"
    columns:
      - name: amount
        meta:
          term: Transaction Amount
```

## Step 3: Configure Meta Mappings

**In ingestion recipe**:
```yaml
source:
  type: dbt-cloud
  config:
    enable_meta_mapping: true
    enable_column_meta_mapping: true
    write_semantics: PATCH
    
    meta_mapping:
      data_tier:
        match: "Silver|Gold"
        operation: "add_term"
        config:
          term: "{{ $match }}"
      terms_list:
        match: ".*"
        operation: "add_terms"
        config:
          separator: ","
    
    column_meta_mapping:
      term:
        match: ".*"
        operation: "add_term"
        config:
          term: "{{ $match }}"
```

## Step 4: Run Ingestion

```bash
export DBT_CLOUD_TOKEN=your_token
export DATAHUB_PAT=your_pat
datahub ingest -c dbt_cloud_ingestion_recipe.yml
```

## Step 5: Verify in DataHub UI

1. Search for your dbt model
2. Check **Glossary Terms** section
3. Check **Columns** for column-level terms

## Common Patterns

### Single Term
```yaml
# dbt
meta:
  domain: Revenue

# recipe
domain:
  match: "Revenue"
  operation: "add_term"
  config:
    term: "Revenue"
```

### Dynamic Term
```yaml
# dbt
meta:
  data_tier: Silver

# recipe
data_tier:
  match: "Silver|Gold"
  operation: "add_term"
  config:
    term: "{{ $match }}"
```

### Multiple Terms
```yaml
# dbt
meta:
  terms_list: "Revenue,Product Revenue"

# recipe
terms_list:
  match: ".*"
  operation: "add_terms"
  config:
    separator: ","
```

## Troubleshooting

- **Terms not appearing?**
  - Verify terms exist in DataHub (check Glossary section)
  - Check term names match exactly (case-sensitive)
  - Verify meta properties in dbt schema.yml
  - Check meta mapping config matches meta property names

- **Column terms not appearing?**
  - Ensure `enable_column_meta_mapping: true`
  - Verify column meta properties exist
  - Check `column_meta_mapping` section exists

## Key Files

- `examples/glossary_terms.yaml` - Term definitions
- `examples/import_glossary_terms.py` - CLI import script
- `examples/dbt_schema_example.yml` - Example dbt meta
- `examples/dbt_ingestion_recipe_example.yml` - Example recipe

