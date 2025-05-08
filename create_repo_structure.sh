#!/bin/bash
# Script to create the file structure for the DataHub Domains & Glossary repository

# Create base directories
mkdir -p datahub-governance
cd datahub-governance

# Add README
cat > README.md << 'EOF'
# DataHub Domains & Business Glossary Guide

This repository provides guidance and examples for effectively using Domains and Business Glossary features in DataHub to organize and define your data assets.

[Full README content is in the main README.md file]
EOF

# Create directory structure
mkdir -p docs/domains
mkdir -p docs/glossary
mkdir -p examples/domains
mkdir -p examples/glossary
mkdir -p scripts
mkdir -p templates

# Create domain documentation
cat > docs/domains/domains_overview.md << 'EOF'
# Domains Overview

Domains in DataHub are organizational constructs that help you logically group related assets together based on business units, teams, or subject areas.

## Key Characteristics

- **Hierarchical Organization**: Domains can have parent-child relationships
- **Asset Grouping**: Multiple assets can belong to the same domain
- **Ownership**: Domains have owners who are responsible for the assets within them
- **Access Control**: Domains can be used for access management

## Domain Structure

A domain typically consists of:

- **Name**: A unique identifier for the domain
- **Description**: A clear explanation of what the domain represents
- **Owners**: People or groups responsible for the domain
- **Assets**: Datasets, dashboards, pipelines, etc. that belong to the domain
- **Sub-domains**: Child domains that represent sub-categories

## Benefits of Using Domains

1. **Improved Organization**: Logical grouping of related assets
2. **Clear Ownership**: Defined responsibilities for data assets
3. **Better Discovery**: Easier to find assets related to a specific business area
4. **Governance Support**: Foundation for data governance policies
EOF

cat > docs/domains/domain_creation_guide.md << 'EOF'
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
EOF

# Create glossary documentation
cat > docs/glossary/glossary_overview.md << 'EOF'
# Business Glossary Overview

The Business Glossary in DataHub is a centralized repository of business terms and definitions that helps establish a common vocabulary across your organization.

## Key Characteristics

- **Standardized Definitions**: Clear, approved definitions of business concepts
- **Term Relationships**: Hierarchical and related term connections
- **Asset Linkage**: Terms can be linked to actual data assets
- **Ownership**: Terms have stewards responsible for their accuracy

## Glossary Structure

A glossary term typically consists of:

- **Name**: The business term being defined
- **Description**: A clear definition of the term
- **Source**: Where the definition originated (internal or external)
- **Stewards**: People responsible for maintaining the term
- **Related Terms**: Other terms that have relationships with this term
- **Linked Assets**: Data assets that represent or use this concept

## Benefits of Using Business Glossary

1. **Common Language**: Establishes shared vocabulary across the organization
2. **Improved Data Literacy**: Helps users understand business concepts
3. **Enhanced Discovery**: Allows finding data assets by business concept
4. **Governance Support**: Provides semantic foundation for data governance
EOF

cat > docs/glossary/glossary_creation_guide.md << 'EOF'
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
EOF

# Create example files
cat > examples/domains/marketing_domain.json << 'EOF'
{
  "urn": "urn:li:domain:marketing",
  "aspect": {
    "domainProperties": {
      "name": "Marketing",
      "description": "Marketing department data assets including campaign analytics, customer segmentation, and attribution models"
    }
  }
}
EOF

cat > examples/glossary/customer_terms.json << 'EOF'
{
  "name": "Customer Lifetime Value",
  "description": "The total worth to a business of a customer over the whole period of their relationship, calculated by multiplying average purchase value, purchase frequency, and average customer lifespan.",
  "termSource": "INTERNAL",
  "owners": [
    {
      "owner": "urn:li:corpuser:data_governance_lead",
      "type": "DATAOWNER"
    }
  ],
  "customProperties": {
    "calculationMethod": "Average Purchase Value × Purchase Frequency × Customer Lifespan",
    "businessUnit": "Marketing",
    "dataClassification": "Internal"
  }
}
EOF

# Copy Python scripts
cp ../domain_creation_example.py scripts/create_domain.py
cp ../glossary_term_creation_example.py scripts/create_glossary_term.py

# Create template files
cat > templates/domain_template.json << 'EOF'
{
  "name": "DOMAIN_NAME",
  "description": "DOMAIN_DESCRIPTION",
  "owners": [
    {
      "owner": "urn:li:corpuser:OWNER_USERNAME",
      "type": "DATAOWNER"
    }
  ]
}
EOF

cat > templates/glossary_term_template.json << 'EOF'
{
  "name": "TERM_NAME",
  "description": "TERM_DESCRIPTION",
  "termSource": "INTERNAL",
  "owners": [
    {
      "owner": "urn:li:corpuser:OWNER_USERNAME",
      "type": "DATAOWNER"
    }
  ],
  "customProperties": {
    "propertyName1": "propertyValue1",
    "propertyName2": "propertyValue2"
  }
}
EOF

# Create a link terms script
cat > scripts/link_terms_to_assets.py << 'EOF'
#!/usr/bin/env python3
"""
Script to link glossary terms to data assets.
"""

import json
import requests
import logging
import sys

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# DataHub API configuration
DATAHUB_URL = "http://localhost:8080"  # Update with your DataHub URL
TOKEN = "YOUR_TOKEN_HERE"  # Update with your authentication token

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def link_term_to_asset(term_urn, asset_urn):
    """
    Link a glossary term to a data asset
    
    Parameters:
        term_urn (str): The URN of the glossary term
        asset_urn (str): The URN of the data asset
    
    Returns:
        bool: True if term was linked successfully, False otherwise
    """
    try:
        # Prepare the payload
        payload = {
            "urn": asset_urn,
            "aspect": {
                "glossaryTerms": {
                    "terms": [
                        {
                            "urn": term_urn
                        }
                    ]
                }
            }
        }
        
        # Link term to asset
        response = requests.post(
            f"{DATAHUB_URL}/entities?action=ingest",
            headers=headers,
            data=json.dumps(payload)
        )
        
        if response.status_code == 200:
            logger.info(f"Successfully linked term {term_urn} to asset {asset_urn}")
            return True
        else:
            logger.error(f"Failed to link term to asset: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error linking term to asset: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: link_terms_to_assets.py <term_urn> <asset_urn>")
        sys.exit(1)
        
    term_urn = sys.argv[1]
    asset_urn = sys.argv[2]
    
    link_term_to_asset(term_urn, asset_urn)
EOF

echo "Repository structure created successfully!"