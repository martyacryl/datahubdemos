# Working with Domains in DataHub

## Overview

Domains in DataHub provide an organizational framework for grouping related data assets together based on business units, subject areas, or functional teams. This document explains how to effectively work with domains, including how to use the domain creation scripts provided in this repository.

## Why Use Domains?

Implementing domains in your DataHub instance offers several key benefits:

- **Logical Organization**: Group related assets by business function or subject area
- **Improved Discoverability**: Make it easier for users to find relevant data assets
- **Ownership Clarity**: Establish clear ownership boundaries for data assets
- **Access Control**: Use domains as a foundation for access management
- **Governance Structure**: Create a framework for implementing data governance policies
- **Business Alignment**: Align technical assets with business functions

## Domain Structure in DataHub

A domain in DataHub consists of:

- **Name**: Unique identifier for the domain (e.g., "Marketing")
- **Description**: Explanation of what the domain represents
- **Owners**: People or groups responsible for the domain
- **Assets**: Datasets, dashboards, pipelines, etc., that belong to the domain
- **Sub-domains**: (Optional) Child domains that represent sub-categories

Domains can be hierarchical, with parent-child relationships that reflect organizational or functional hierarchies.

## The domain_creation_example.py Script

The `domain_creation_example.py` script in this repository provides functionality to programmatically create domains and assign assets to them in DataHub.

### Script Functionality

The script:

1. **Creates Domains**: Establishes new domains in DataHub
2. **Sets Domain Properties**: Configures name, description, and other metadata
3. **Assigns Owners**: Sets ownership for the domain
4. **Adds Assets**: Assigns data assets to the domain
5. **Creates Hierarchy**: (Optional) Establishes parent-child relationships between domains

### How to Use the Script

```bash
# Edit the script to configure your domains
nano scripts/create_domain.py

# Run the script
python scripts/create_domain.py
```

### Script Implementation Details

The script works by:

1. Creating a domain with a unique identifier derived from the domain name:
   ```python
   domain_id = domain_data["name"].lower().replace(" ", "-")
   ```

2. Setting up the domain properties payload:
   ```json
   {
     "urn": "urn:li:domain:marketing",
     "aspect": {
       "domainProperties": {
         "name": "Marketing",
         "description": "Marketing department data assets including campaign analytics, customer segmentation, and attribution models"
       }
     }
   }
   ```

3. Sending the payload to DataHub's entity API endpoint

4. Assigning ownership to the domain (separate API call)

5. Adding assets to the domain by updating each asset with a domain reference

## Working with Different Domain Scenarios

### Creating a Simple Domain

```python
# Example domain data
marketing_domain = {
    "name": "Marketing",
    "description": "Marketing department data assets including campaign analytics, customer segmentation, and attribution models",
    "owners": [
        {
            "owner": "urn:li:corpuser:marketing_lead",
            "type": "DATAOWNER"
        }
    ]
}

# Create the domain
create_domain(marketing_domain)
```

### Creating Domain Hierarchies

To create a domain hierarchy, you first create the parent domain, then create child domains with a reference to the parent:

```python
# Parent domain
finance_domain = {
    "name": "Finance",
    "description": "Financial data assets and metrics",
    "owners": [
        {
            "owner": "urn:li:corpuser:finance_lead",
            "type": "DATAOWNER"
        }
    ]
}

# Create parent domain
create_domain(finance_domain)

# Child domain
accounting_domain = {
    "name": "Accounting",
    "description": "Accounting data assets and reports",
    "owners": [
        {
            "owner": "urn:li:corpuser:accounting_lead",
            "type": "DATAOWNER"
        }
    ],
    "parent_domain": "urn:li:domain:finance"  # Reference to parent domain
}

# Create child domain with reference to parent
# Implementation would need to be extended to handle parent-child relationships
```

### Adding Assets to Domains

You can add assets to domains individually or in bulk:

```python
# Add individual assets to a domain
asset_urns = [
    "urn:li:dataset:(urn:li:dataPlatform:snowflake,marketing_analytics.campaign_performance,PROD)",
    "urn:li:dataset:(urn:li:dataPlatform:snowflake,marketing_analytics.customer_segments,PROD)",
    "urn:li:dashboard:(looker,marketing_dashboard_123)"
]

domain_urn = "urn:li:domain:marketing"

for asset_urn in asset_urns:
    add_asset_to_domain(asset_urn, domain_urn)
```

## Domain URN Formats

Understanding URN formats is essential when working with domains programmatically:

- **Domain URN**: `urn:li:domain:{domain_id}`
- **Dataset URN**: `urn:li:dataset:(urn:li:dataPlatform:{platform},{dataset_name},{env})`
- **Dashboard URN**: `urn:li:dashboard:({tool},{dashboard_id})`
- **Chart URN**: `urn:li:chart:({tool},{chart_id})`
- **User URN**: `urn:li:corpuser:{username}`

## Domain Ownership and Stewardship

Domains support two types of ownership:

1. **Data Owner**: Responsible for the strategic governance of the domain
2. **Data Steward**: Handles day-to-day management of the domain's assets

```python
domain_owners = [
    {
        "owner": "urn:li:corpuser:dept_vp",
        "type": "DATAOWNER"
    },
    {
        "owner": "urn:li:corpuser:data_steward",
        "type": "DATASTEWARD"
    }
]
```

## Best Practices for Working with Domains

1. **Align with Organization Structure**: Create domains that reflect your business organization or subject matter areas

2. **Limit Hierarchy Depth**: Keep domain hierarchies shallow (2-3 levels maximum) for better usability

3. **Clear Naming Conventions**: Use consistent, clear naming patterns for domains

4. **Assign Ownership**: Always assign at least one owner to each domain

5. **Balance Granularity**: Create enough domains to be useful but not so many that they become difficult to manage
   - Too few: "Data" (too broad)
   - Too many: "2023 Q2 Marketing Campaign Analytics" (too specific)
   - Just right: "Marketing" with sub-domains like "Campaign Analytics"

6. **Document Domain Purpose**: Provide clear descriptions for each domain

7. **Regular Maintenance**: Review and update domain structure as your organization evolves

## Integrating Domains with Business Glossary

Domains and business glossary terms work together to provide comprehensive context:

1. **Create Domain Structure**: Establish domains aligned with business areas
2. **Define Business Terms**: Create glossary terms for key business concepts
3. **Link Terms to Assets**: Connect terms to assets within domains
4. **Cross-Reference**: Reference relevant business terms in domain descriptions

This creates a powerful knowledge graph that connects:
- Organizational structure (domains)
- Business concepts (glossary terms)
- Technical assets (datasets, dashboards, etc.)

## Example Domain Structure for an Organization

```
Enterprise
├── Marketing
│   ├── Campaign Analytics
│   ├── Customer Segmentation
│   └── Digital Marketing
├── Sales
│   ├── Opportunity Management
│   ├── Account Management
│   └── Sales Performance
├── Finance
│   ├── Accounting
│   ├── Financial Planning
│   └── Treasury
└── Product
    ├── Product Development
    ├── Product Analytics
    └── Quality Assurance
```

## Automating Domain Management

For large organizations, consider automating domain management:

```python
# Example of bulk domain creation from a configuration file
import json

def create_domains_from_config(config_file):
    with open(config_file, 'r') as f:
        domains_config = json.load(f)
    
    for domain_config in domains_config:
        create_domain(domain_config)
        
        # Process sub-domains if any
        if 'sub_domains' in domain_config:
            for sub_domain in domain_config['sub_domains']:
                # Add parent reference
                sub_domain['parent_domain'] = f"urn:li:domain:{domain_config['name'].lower().replace(' ', '-')}"
                create_domain(sub_domain)

# Call with your configuration file
create_domains_from_config('domain_structure.json')
```

## Migrating Assets Between Domains

As your organization evolves, you may need to move assets between domains:

```python
def move_asset_to_new_domain(asset_urn, old_domain_urn, new_domain_urn):
    """
    Move an asset from one domain to another
    
    Parameters:
        asset_urn (str): The asset URN to move
        old_domain_urn (str): The source domain URN
        new_domain_urn (str): The target domain URN
    
    Returns:
        bool: True if asset was moved successfully, False otherwise
    """
    # Remove from old domain
    # Implementation would update the asset to remove the old domain
    
    # Add to new domain
    return add_asset_to_domain(asset_urn, new_domain_urn)
```

## Conclusion

Domains provide a powerful organizational framework in DataHub that helps align technical assets with business functions. By effectively implementing domains, you create a more intuitive, business-aligned data catalog that supports both discovery and governance.

The scripts and examples in this repository provide a foundation for programmatically managing domains in your DataHub instance, allowing you to scale your domain implementation across your organization.