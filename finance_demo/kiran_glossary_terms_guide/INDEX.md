# Guide Index

This folder contains everything you need to automatically apply glossary terms from dbt to DataHub.

## Folder Structure

```
kiran_glossary_terms_guide/
├── README.md                          # Main walkthrough guide (START HERE)
├── INDEX.md                           # This file - overview of all documents
├── QUICK_REFERENCE.md                 # Quick reference for the 5-step process
├── UI_IMPORT_GUIDE.md                 # Step-by-step UI guide for creating terms
├── VERIFICATION_CHECKLIST.md          # Checklist to verify each step
└── examples/                          # Example files and code
    ├── glossary_terms.yaml            # Example glossary terms YAML (for CLI import)
    ├── import_glossary_terms.py       # CLI script to import terms from YAML
    ├── dbt_schema_example.yml          # Example dbt schema with meta properties
    └── dbt_ingestion_recipe_example.yml # Example ingestion recipe with meta mappings
```

## Document Guide

### Main Guide
- **README.md** - Complete walkthrough covering all 5 steps:
  1. Create glossary terms in DataHub (CLI or UI)
  2. Add meta properties to dbt models
  3. Configure meta mappings in ingestion recipe
  4. Run dbt ingestion
  5. Verify terms are applied

### Quick References
- **QUICK_REFERENCE.md** - Quick reference card with common patterns and commands
- **VERIFICATION_CHECKLIST.md** - Step-by-step checklist to verify each step

### Detailed Guides
- **UI_IMPORT_GUIDE.md** - Detailed guide for creating terms manually in DataHub UI
- **INDEX.md** - This file - overview of all documents

## Example Files

### For DataHub (Step 1)
- **examples/glossary_terms.yaml** - YAML file with term definitions for CLI import
- **examples/import_glossary_terms.py** - Python script to import terms from YAML

### For dbt (Step 2)
- **examples/dbt_schema_example.yml** - Example showing how to add meta properties to models and columns

### For Ingestion Recipe (Step 3)
- **examples/dbt_ingestion_recipe_example.yml** - Example showing how to configure meta mappings

## Getting Started

1. **Read README.md** - Start with the main guide
2. **Choose import method** - CLI (use examples/import_glossary_terms.py) or UI (see UI_IMPORT_GUIDE.md)
3. **Follow the 5 steps** - Use QUICK_REFERENCE.md as a cheat sheet
4. **Verify with checklist** - Use VERIFICATION_CHECKLIST.md to ensure everything works

## Key Concepts

- **Terms must exist first** - Create terms in DataHub before running ingestion
- **Names must match exactly** - Term names must match dbt meta values (case-sensitive)
- **Meta mapping connects them** - Ingestion recipe maps dbt meta → DataHub terms
- **PATCH semantics** - Adds terms without overwriting existing ones

## Common Patterns

See README.md for detailed examples of:
- Single term from meta value
- Dynamic term name from meta (using `{{ $match }}`)
- Multiple terms from comma-separated list
- Column-level terms

## Troubleshooting

See README.md Troubleshooting section for:
- Terms not appearing
- Column-level terms not appearing
- Ingestion failures

