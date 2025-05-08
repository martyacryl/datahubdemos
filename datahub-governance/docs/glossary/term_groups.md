# Working with Term Groups in DataHub

Term groups are collections of related business glossary terms that help organize your business vocabulary into logical categories. This document explains how to create and manage term groups in DataHub.

## What are Term Groups?

Term groups (also called nodes in the API) serve as containers for related business terms. They help:

- Organize terms by category, department, or domain
- Create hierarchical relationships between terms
- Improve navigation and discovery of business terminology
- Support governance through structured organization

## Term Group Hierarchy

DataHub supports a hierarchical organization of term groups:

- A glossary can have multiple term groups
- Term groups can have child term groups (sub-groups)
- Terms can belong to one or more term groups
- Terms can have parent-child relationships with other terms

## Creating Term Groups

### Via UI

1. Navigate to the "Glossary" section in the DataHub UI
2. Click "Create New Node"
3. Fill in the required information:
   - Name: A descriptive name for the group (e.g., "Financial Metrics")
   - Description: An explanation of what terms are in this group
4. Click "Create" to save the term group

### Via API

```python
import requests

DATAHUB_URL = "http://localhost:8080"
TOKEN = "YOUR_TOKEN_HERE"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Create a new term group node
response = requests.post(
    f"{DATAHUB_URL}/glossary/main/node",
    headers=headers
)

group_urn = response.json()["urn"]

# Update the group with details
group_data = {
    "name": "Financial Metrics",
    "description": "Terms related to financial performance and metrics"
}

response = requests.put(
    f"{DATAHUB_URL}/glossaryNodes/{group_urn.split(':')[-1]}",
    headers=headers,
    json=group_data
)
```

## Adding Terms to a Group

### Via UI

1. Create a new term or navigate to an existing term
2. In the term details page, click "Edit"
3. Under "Term Group," click "Add Term Group"
4. Select the appropriate term group from the dropdown
5. Click "Save" to add the term to the group

### Via API

```python
import requests

DATAHUB_URL = "http://localhost:8080"
TOKEN = "YOUR_TOKEN_HERE"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Add a term to a group
term_urn = "urn:li:glossaryTerm:revenue"
group_urn = "urn:li:glossaryNode:financial_metrics"

payload = {
    "urn": term_urn,
    "aspect": {
        "parentNodes": {
            "nodes": [
                {
                    "urn": group_urn
                }
            ]
        }
    }
}

response = requests.post(
    f"{DATAHUB_URL}/entities?action=ingest",
    headers=headers,
    json=payload
)
```

## Creating Hierarchical Terms

Terms can also have parent-child relationships. For example, "Adjusted EBITDA" might be a child term of "EBITDA". This creates a hierarchical organization of terms.

### Via UI

1. Create a new term
2. In the term details page, click "Edit"
3. Under "Parent Term," click "Add Parent Term"
4. Select the appropriate parent term
5. Click "Save" to establish the relationship

### Via API

```python
import requests

DATAHUB_URL = "http://localhost:8080"
TOKEN = "YOUR_TOKEN_HERE"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Add a term as a child of another term
child_term_urn = "urn:li:glossaryTerm:adjusted_ebitda"
parent_term_urn = "urn:li:glossaryTerm:ebitda"

payload = {
    "urn": child_term_urn,
    "aspect": {
        "parentNodes": {
            "nodes": [
                {
                    "urn": parent_term_urn
                }
            ]
        }
    }
}

response = requests.post(
    f"{DATAHUB_URL}/entities?action=ingest",
    headers=headers,
    json=payload
)
```

## Term Group Best Practices

1. **Create a Clear Structure**
   - Organize term groups by business domain or department
   - Limit the depth of hierarchies (2-3 levels is optimal)
   - Use consistent naming conventions

2. **Assign Ownership**
   - Each term group should have a clear owner responsible for the terms within it
   - Term group owners should regularly review and maintain their terms

3. **Document Relationships**
   - Clearly document why terms are grouped together
   - Explain the relationship between parent and child terms

4. **Regular Maintenance**
   - Review term groups periodically to ensure they remain relevant
   - Archive obsolete term groups rather than deleting them

## Example Term Group Structure

Here's an example of how you might organize financial terms using term groups:

```
Financial Metrics (Term Group)
├── Revenue (Term)
├── Expenses (Term)
├── Profitability Metrics (Term Group)
│   ├── Gross Profit Margin (Term)
│   ├── Operating Margin (Term)
│   └── Net Profit Margin (Term)
└── EBITDA (Term)
    └── Adjusted EBITDA (Child Term)
```

## Integration with Domains

Term groups can be aligned with your domain structure to create a comprehensive organizational framework:

1. Create domains that match your business units or subject areas
2. Create corresponding term groups for each domain
3. Populate term groups with relevant business terms
4. Link terms to data assets within their respective domains

This approach ensures that both organizational structure (domains) and business vocabulary (term groups) are aligned.