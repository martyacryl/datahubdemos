# DataHub Domains & Business Glossary Guide

This repository provides guidance and examples for effectively using Domains and Business Glossary features in DataHub to organize and define your data assets.

## Table of Contents
- [Overview](#overview)
- [Domains vs Business Glossary](#domains-vs-business-glossary)
- [When to Use Each](#when-to-use-each)
- [Demo Flows](#demo-flows)
  - [Domain Creation Demo](#domain-creation-demo)
  - [Business Glossary Term Creation Demo](#business-glossary-term-creation-demo)
- [Integration Examples](#integration-examples)
- [Best Practices](#best-practices)
- [Repository Structure](#repository-structure)

## Overview

DataHub provides two powerful features to help organize your data assets and establish a common vocabulary:

**Domains** provide organizational structure for your data assets, helping you group related assets by business unit, team, or subject area.

**Business Glossary** establishes a common vocabulary by defining business terms and their relationships, creating semantic context for your data assets.

## Domains vs Business Glossary

| Feature | Domains | Business Glossary |
|---------|---------|-------------------|
| **Purpose** | Organizational grouping | Semantic definitions |
| **Structure** | Hierarchical | Network of related terms |
| **Primary Use** | Asset organization | Vocabulary standardization |
| **Ownership** | Team/department ownership | Concept stewardship |
| **Typical Admin** | Data platform teams | Data governance teams |

## When to Use Each

### Use Domains when:
- You need to organize assets by team, department, or subject area
- You want to manage ownership and access control at a group level
- You need a hierarchical organization of your data assets
- You want to see all related assets in one place

### Use Business Glossary when:
- You need to define standard business terminology
- You want to establish a common vocabulary across teams
- You need to link business concepts to technical assets
- You're focused on semantic meaning rather than organizational structure

## Demo Flows

### Domain Creation Demo

Below is a step-by-step guide to create a domain in DataHub:

1. **Access Domain Management**
   - Navigate to the "Domains" section in the DataHub UI
   - Click "Create New Domain"

2. **Configure Domain Properties**
   ```json
   {
     "name": "Marketing",
     "description": "Marketing department data assets including campaign analytics, customer segmentation, and attribution models",
     "owners": [
       {
         "owner": "urn:li:corpuser:marketing_lead",
         "type": "DATAOWNER"
       }
     ]
   }
   ```

3. **Create Domain Hierarchy (Optional)**
   - Create sub-domains like "Campaign Analytics" and "Customer Segmentation" under the Marketing domain

4. **Assign Assets to Domain**
   - Search for relevant datasets, dashboards, and pipelines
   - Select assets and use the "Add to Domain" action
   - Choose the Marketing domain

5. **Verify Domain**
   - View the Marketing domain page to ensure all assets are properly assigned
   - Check that the ownership information is correct

### Business Glossary Term Creation Demo

Follow these steps to create a business glossary term in DataHub:

1. **Access Glossary Management**
   - Navigate to the "Glossary" section in the DataHub UI
   - Click "Create New Term"

2. **Configure Term Properties**
   ```json
   {
     "name": "Customer Lifetime Value",
     "description": "The total worth to a business of a customer over the whole period of their relationship, calculated by multiplying average purchase value, purchase frequency, and average customer lifespan.",
     "owners": [
       {
         "owner": "urn:li:corpuser:data_governance_lead",
         "type": "DATAOWNER"
       }
     ],
     "termSource": "INTERNAL"
   }
   ```

3. **Add Related Terms**
   - Link to related terms like "Customer Acquisition Cost"
   - Set up hierarchical relationships if applicable

4. **Link to Data Assets**
   - Search for datasets or fields that represent customer lifetime value
   - Link the term to specific fields or tables
   - Example: Link to `marketing_data.customer_metrics.customer_ltv` field

5. **Verify Term**
   - View the term page to ensure all information is correct
   - Validate that links to data assets work properly

## Integration Examples

Here's how Domains and Business Glossary can work together:

**Example 1: Customer Data Integration**
- Create a "Customer Data" domain to organize all customer-related datasets
- Define glossary terms for "Customer ID", "Customer Segment", and "Customer Lifetime Value"
- Link these terms to specific fields in datasets within the Customer Data domain

**Example 2: Financial Reporting**
- Create a "Finance" domain with sub-domains for "Accounting" and "Financial Planning"
- Define glossary terms for "Revenue", "EBITDA", and "Operating Margin"
- Link finance datasets to the Finance domain and annotate key fields with glossary terms

## Best Practices

1. **Start Small**
   - Begin with a few key domains and terms rather than trying to model everything at once
   - Expand incrementally based on adoption and feedback

2. **Establish Governance**
   - Define clear owners for domains and glossary terms
   - Create approval workflows for adding new terms or domains

3. **Balance Flexibility and Control**
   - Allow teams to suggest new terms but maintain central review
   - Enable domain owners to manage their assets within established guidelines

4. **Integrate with Metadata**
   - Link glossary terms to data dictionary elements
   - Connect domains to data lineage to understand dependencies

5. **Regular Maintenance**
   - Review and update glossary terms regularly
   - Archive obsolete terms rather than deleting them

## Repository Structure

```
datahub-governance/
├── README.md
├── docs/
│   ├── domains/
│   │   ├── domains_overview.md
│   │   ├── domain_creation_guide.md
│   │   └── domain_best_practices.md
│   └── glossary/
│       ├── glossary_overview.md
│       ├── glossary_creation_guide.md
│       └── glossary_best_practices.md
├── examples/
│   ├── domains/
│   │   ├── marketing_domain.json
│   │   ├── finance_domain.json
│   │   └── product_domain.json
│   └── glossary/
│       ├── customer_terms.json
│       ├── financial_terms.json
│       └── product_terms.json
├── scripts/
│   ├── create_domain.py
│   ├── create_glossary_term.py
│   └── link_terms_to_assets.py
└── templates/
    ├── domain_template.json
    └── glossary_term_template.json
```