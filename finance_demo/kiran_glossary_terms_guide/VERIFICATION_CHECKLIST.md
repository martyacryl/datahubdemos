# Verification Checklist

Use this checklist to verify each step of the glossary terms workflow.

## Step 1: Terms Created in DataHub ✅

### CLI Import Verification
- [ ] Ran `python import_glossary_terms.py` successfully
- [ ] Script output shows "✅ SUCCESS: Glossary Terms Imported!"
- [ ] No errors in script output

### UI Manual Creation Verification
- [ ] Navigated to DataHub → Glossary
- [ ] Created all required term groups (e.g., "Data Tier", "Revenue")
- [ ] Created all required terms within each group
- [ ] Verified term names match exactly what will be used in dbt meta (case-sensitive)

### Final Verification
- [ ] Can see all term groups in Glossary section
- [ ] Can see all terms within their groups
- [ ] Terms are clickable and show descriptions
- [ ] Term names are exactly as needed (e.g., "Silver", "Revenue", "Transaction Amount")

## Step 2: Meta Properties Added to dbt ✅

### Model-Level Meta
- [ ] Added `config.meta` section to models in `schema.yml`
- [ ] Meta properties match what's configured in ingestion recipe
- [ ] Examples:
  - [ ] `data_tier: Silver` or `data_tier: Gold`
  - [ ] `domain: Revenue` (if using)
  - [ ] `terms_list: "Revenue,Product Revenue"` (if using)

### Column-Level Meta
- [ ] Added `meta` section to columns that need terms
- [ ] Column meta properties match what's configured in `column_meta_mapping`
- [ ] Example: `term: Transaction Amount`

### dbt Validation
- [ ] Ran `dbt parse` or `dbt compile` - no errors
- [ ] Meta properties are valid YAML
- [ ] Meta properties are under correct model/column

## Step 3: Meta Mappings Configured ✅

### Recipe Configuration
- [ ] `enable_meta_mapping: true` is set
- [ ] `enable_column_meta_mapping: true` is set (if using column terms)
- [ ] `write_semantics: PATCH` is set

### Model-Level Mappings
- [ ] `meta_mapping` section exists
- [ ] Each meta property has a corresponding mapping
- [ ] `operation: "add_term"` or `operation: "add_terms"` is correct
- [ ] `match` pattern matches your meta values
- [ ] `term` or `{{ $match }}` is configured correctly

### Column-Level Mappings
- [ ] `column_meta_mapping` section exists (if using column terms)
- [ ] Column meta properties have corresponding mappings
- [ ] `operation: "add_term"` is correct
- [ ] `term: "{{ $match }}"` is configured

### Recipe Validation
- [ ] YAML syntax is valid
- [ ] All placeholders replaced (account_id, project_id, etc.)
- [ ] Environment variables set (DBT_CLOUD_TOKEN, DATAHUB_PAT)

## Step 4: Ingestion Run Successfully ✅

### Pre-Ingestion
- [ ] Environment variables set:
  - [ ] `DBT_CLOUD_TOKEN` (or dbt Cloud credentials)
  - [ ] `DATAHUB_PAT`
- [ ] dbt Cloud job has run successfully (if using dbt-cloud source)
- [ ] Recipe file path is correct

### During Ingestion
- [ ] Ran `datahub ingest -c dbt_cloud_ingestion_recipe.yml`
- [ ] Ingestion completed without errors
- [ ] No warnings about missing terms
- [ ] Logs show meta mapping operations

### Post-Ingestion
- [ ] Ingestion output shows success
- [ ] No errors in ingestion logs
- [ ] Models appear in DataHub

## Step 5: Terms Applied in DataHub UI ✅

### Model-Level Terms
- [ ] Searched for dbt model in DataHub UI
- [ ] Model page shows **Glossary Terms** section
- [ ] Terms appear in the Glossary Terms section
- [ ] Terms match what was configured:
  - [ ] "Silver" or "Gold" (from `data_tier`)
  - [ ] "Revenue" (from `domain` or `terms_list`)
  - [ ] Other terms from `terms_list`

### Column-Level Terms
- [ ] Clicked on a column in the model
- [ ] Column page shows **Glossary Terms** section
- [ ] Terms appear for columns with meta properties
- [ ] Terms match column meta values (e.g., "Transaction Amount")

### Term Verification
- [ ] Terms are clickable links
- [ ] Clicking a term shows term definition
- [ ] Term definitions match what was created in Step 1

## Troubleshooting Checklist

If terms are not appearing:

- [ ] **Terms exist?** Check DataHub → Glossary → Terms exist
- [ ] **Names match?** Term names match meta values exactly (case-sensitive)
- [ ] **Meta exists?** dbt models have correct meta in schema.yml
- [ ] **Mapping correct?** Recipe meta_mapping matches meta property names
- [ ] **Ingestion success?** Ingestion completed without errors
- [ ] **Logs checked?** Review ingestion logs for warnings/errors

## Success Criteria

✅ All checklist items completed
✅ Terms appear on models in DataHub UI
✅ Terms appear on columns (if configured)
✅ Terms are clickable and show definitions
✅ Workflow is repeatable for new models

