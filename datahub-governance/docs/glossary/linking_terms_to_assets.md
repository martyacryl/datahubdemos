# Linking Terms to Assets in DataHub

## Overview

Linking terms to assets is a fundamental capability in DataHub that connects business glossary terms to the actual data assets they describe. This document explains what the `link_terms_to_assets.py` script does and how to use it effectively.

## Why Link Terms to Assets?

Connecting glossary terms to data assets provides several key benefits:

- **Business Context**: Adds business meaning to technical data elements
- **Semantic Layer**: Creates a layer of business terminology over your data infrastructure
- **Knowledge Transfer**: Helps technical and business teams share a common language
- **Discoverability**: Enables searching for data assets using business terminology
- **Lineage Enhancement**: Enriches data lineage with business context
- **Governance Support**: Facilitates data governance by connecting policies to data

## The link_terms_to_assets.py Script

The `link_terms_to_assets.py` script in this repository provides functionality to programmatically link business glossary terms to data assets in DataHub.

### Script Functionality

The script:

1. **Establishes Connections**: Links glossary terms to specific data assets (datasets, fields, dashboards, etc.)

2. **Takes Two URNs as Input**:
   - The glossary term URN (e.g., `urn:li:glossaryTerm:customer_lifetime_value`)
   - The data asset URN (e.g., `urn:li:dataset:(urn:li:dataPlatform:snowflake,marketing_data.customer_metrics,PROD)`)

3. **Makes API Call**: Uses DataHub's API to create the link between the term and asset

4. **Provides Feedback**: Logs success or failure of the linking operation

### How to Use the Script

```bash
python link_terms_to_assets.py <term_urn> <asset_urn>
```

For example:
```bash
python link_terms_to_assets.py "urn:li:glossaryTerm:customer_lifetime_value" "urn:li:dataset:(urn:li:dataPlatform:snowflake,marketing_data.customer_metrics,PROD)"
```

### Script Implementation Details

The script works by:

1. Creating a payload that specifies which term should be linked to which asset:
   ```json
   {
     "urn": "<asset_urn>",
     "aspect": {
       "glossaryTerms": {
         "terms": [
           {
             "urn": "<term_urn>"
           }
         ]
       }
     }
   }
   ```

2. Sending this payload to DataHub's entity API endpoint to create the association

3. Handling success and error cases with appropriate logging

## Linking Different Types of Assets

You can link terms to various types of assets in DataHub:

### Datasets

Links a term to an entire dataset:
```bash
python link_terms_to_assets.py "urn:li:glossaryTerm:customer_lifetime_value" "urn:li:dataset:(urn:li:dataPlatform:snowflake,marketing_data.customer_metrics,PROD)"
```

### Schema Fields

Links a term to a specific field within a dataset:
```bash
python link_terms_to_assets.py "urn:li:glossaryTerm:customer_lifetime_value" "urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:snowflake,marketing_data.customer_metrics,PROD),customer_ltv)"
```

### Dashboards

Links a term to a dashboard:
```bash
python link_terms_to_assets.py "urn:li:glossaryTerm:customer_acquisition" "urn:li:dashboard:(looker,marketing_dashboard_123)"
```

### Charts

Links a term to a specific chart:
```bash
python link_terms_to_assets.py "urn:li:glossaryTerm:conversion_rate" "urn:li:chart:(looker,conversion_trend_chart_456)"
```

## Best Practices for Linking Terms to Assets

1. **Be Specific**: Link terms to the most specific asset possible (field level rather than dataset level when appropriate)

2. **Maintain Consistency**: Ensure the same term is used consistently across similar assets

3. **Avoid Over-Linking**: Don't link too many terms to a single asset, which can create clutter

4. **Automate for Scale**: Use the script as part of your data ingestion or governance processes

5. **Regular Maintenance**: Periodically review and update term-to-asset linkages as definitions evolve

6. **Focus on Critical Assets**: Start by linking terms to your most important or widely-used assets

7. **Combine with Domains**: Link assets to both domains (for organizational structure) and terms (for semantic meaning)

## Integration Examples

### Integrating with Data Ingestion

```python
# After ingesting a dataset, link relevant terms
def post_ingestion_hook(dataset_urn):
    # Link "Customer" term to customer-related datasets
    if "customer" in dataset_urn:
        link_terms_to_assets("urn:li:glossaryTerm:customer", dataset_urn)
```

### Bulk Term Linking

```python
# Link a term to multiple assets
def link_term_to_multiple_assets(term_urn, asset_urns):
    for asset_urn in asset_urns:
        link_terms_to_assets(term_urn, asset_urn)
        
# Example usage
customer_assets = [
    "urn:li:dataset:(urn:li:dataPlatform:snowflake,customers.profile,PROD)",
    "urn:li:dataset:(urn:li:dataPlatform:snowflake,customers.transactions,PROD)",
    "urn:li:dataset:(urn:li:dataPlatform:snowflake,customers.preferences,PROD)"
]

link_term_to_multiple_assets("urn:li:glossaryTerm:customer", customer_assets)
```

## Conclusion

Linking glossary terms to data assets is a powerful way to add business context to your data ecosystem. The `link_terms_to_assets.py` script provides a programmatic approach to creating these connections at scale, supporting your overall data governance strategy.

By effectively connecting business terminology to technical assets, you create a more accessible, understandable, and valuable data platform for all users.