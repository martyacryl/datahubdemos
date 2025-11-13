# Creating Glossary Terms in DataHub UI

This guide shows how to manually create glossary terms in the DataHub UI. Use this if you prefer the UI over CLI import.

## Prerequisites

- Access to DataHub Cloud or self-hosted DataHub instance
- Permissions to create glossary terms (typically requires Editor or Admin role)

## Step-by-Step: Create Term Groups (Glossary Nodes)

1. **Navigate to Glossary**:
   - Log in to DataHub
   - Click on **Glossary** in the left navigation menu
   - You should see the Glossary page

2. **Create a Term Group**:
   - Click the **"+ Create"** button (usually in the top right)
   - Select **"Create Term Group"** or **"Create Glossary Node"**
   - Enter the following:
     - **Name**: e.g., "Data Tier"
     - **Description**: e.g., "Data tier classification for medallion architecture"
   - Click **"Create"** or **"Save"**

3. **Repeat for all term groups**:
   - Create all term groups you need first
   - Examples: "Data Tier", "Revenue", "Customer", etc.

## Step-by-Step: Create Glossary Terms

1. **Select a Term Group**:
   - Click on the term group you created (e.g., "Data Tier")
   - This opens the term group page

2. **Create a Term**:
   - Click **"+ Create Term"** or **"Add Term"** button
   - Enter the following:
     - **Name**: e.g., "Silver" - **IMPORTANT: This must match exactly what you'll use in dbt meta**
     - **Description**: e.g., "Data tier representing cleaned, validated, and enriched data ready for analytics"
   - Click **"Create"** or **"Save"**

3. **Repeat for all terms**:
   - Create all terms within each term group
   - Make sure term names match exactly (case-sensitive) what you'll use in dbt meta properties

## Important Notes

### Term Names Must Match Exactly

- If your dbt model has `data_tier: Silver`, the term must be named exactly **"Silver"** (not "silver" or "SILVER")
- Term names are case-sensitive
- Spaces matter: "Product Revenue" is different from "ProductRevenue"

### Example Term Names

Based on the example dbt schema, you would need these terms:

**In "Data Tier" group:**
- Silver
- Gold

**In "Revenue" group:**
- Revenue
- Product Revenue
- Customer Revenue
- Financial Metrics
- Transaction Amount
- Gross Revenue
- Net Revenue

### Verification Checklist

After creating terms, verify:

- [ ] All term groups are created
- [ ] All terms are created within their groups
- [ ] Term names match exactly what you'll use in dbt meta (case-sensitive)
- [ ] You can see terms in the Glossary section
- [ ] Terms are clickable and show descriptions

## Next Steps

After creating terms in the UI:

1. ✅ Terms are ready for use
2. ✅ Add meta properties to your dbt models (see README.md Step 2)
3. ✅ Configure meta mappings in ingestion recipe (see README.md Step 3)
4. ✅ Run dbt ingestion (see README.md Step 4)
5. ✅ Verify terms are applied (see README.md Step 5)

