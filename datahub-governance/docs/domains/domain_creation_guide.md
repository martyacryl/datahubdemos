# Domain Creation Guide

This guide provides step-by-step instructions for creating and managing domains in DataHub.

## Creating a Domain via UI

1. Navigate to the "Domains" section in the DataHub UI
2. Click on "Create New Domain"
3. Fill in the required information:
   - Name: A unique, descriptive name for the domain
   - Description: A clear explanation of what the domain represents
4. Click "Create" to save the domain

## Creating a Domain via API

```python
import requests

DATAHUB_URL = "http://localhost:8080"
TOKEN = "YOUR_TOKEN_HERE"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

domain_data = {
    "urn": "urn:li:domain:marketing",
    "aspect": {
        "domainProperties": {
            "name": "Marketing",
            "description": "Marketing department data assets"
        }
    }
}

response = requests.post(
    f"{DATAHUB_URL}/entities?action=ingest",
    headers=headers,
    json=domain_data
)

print(response.json())
```

## Adding Assets to a Domain

1. Navigate to the asset you want to add to a domain
2. Click on the "..." menu and select "Move to Domain"
3. Select the target domain from the dropdown
4. Click "Save" to assign the asset to the domain

## Creating Domain Hierarchy

1. Create a parent domain (e.g., "Marketing")
2. Create child domains (e.g., "Campaign Analytics") 
3. When creating the child domain, select the parent domain from the "Parent Domain" dropdown

## Domain Best Practices

- Keep domain names concise and clear
- Use a consistent naming convention
- Limit the depth of domain hierarchies (2-3 levels is optimal)
- Assign clear ownership for each domain
- Review and maintain domain structure regularly
