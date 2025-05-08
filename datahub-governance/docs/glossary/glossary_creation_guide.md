# Glossary Term Creation Guide

This guide provides step-by-step instructions for creating and managing business glossary terms in DataHub.

## Creating a Term via UI

1. Navigate to the "Glossary" section in the DataHub UI
2. Click on "Create New Term"
3. Fill in the required information:
   - Name: The business term to define
   - Description: A clear, concise definition
   - Term Source: Internal or External
4. Click "Create" to save the term

## Creating a Term via API

```python
import requests

DATAHUB_URL = "http://localhost:8080"
TOKEN = "YOUR_TOKEN_HERE"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# First create a term node
response = requests.post(
    f"{DATAHUB_URL}/glossary/main/term",
    headers=headers
)
term_urn = response.json()["urn"]

# Then update the term with details
term_data = {
    "name": "Customer Lifetime Value",
    "description": "The total worth to a business of a customer over the whole period of their relationship.",
    "termSource": "INTERNAL"
}

response = requests.put(
    f"{DATAHUB_URL}/glossaryTerms/{term_urn.split(':')[-1]}",
    headers=headers,
    json=term_data
)

print(response.json())
```

## Adding Related Terms

1. Navigate to the term you want to modify
2. Click on the "Related Terms" tab
3. Click "Add Related Term"
4. Select the related term and relationship type
5. Click "Save" to create the relationship

## Linking Terms to Assets

1. Navigate to the asset you want to link a term to
2. Click on the "Terms" tab
3. Click "Add Term"
4. Search for and select the relevant term
5. Click "Save" to create the link

## Glossary Best Practices

- Keep definitions clear and concise
- Use consistent formatting across terms
- Define relationships between related terms
- Assign stewards to maintain term accuracy
- Review and update terms regularly
- Link terms to actual data assets
