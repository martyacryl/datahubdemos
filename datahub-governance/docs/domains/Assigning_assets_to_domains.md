# Assigning Assets to Domains in DataHub

## Overview

Assigning assets to domains is a critical step in organizing your data catalog in DataHub. This document explains how to assign various types of assets to domains, both through the UI and programmatically using the scripts provided in this repository.

## Why Assign Assets to Domains?

Connecting data assets to domains provides several key benefits:

- **Organized Discovery**: Users can browse assets by business domain
- **Clear Ownership**: Assets inherit domain ownership for governance
- **Context Awareness**: Assets are presented with organizational context
- **Simplified Management**: Related assets can be managed as a group
- **Business Alignment**: Technical assets are aligned with business functions
- **Enhanced Search**: Domain facets improve search capabilities

## The add_asset_to_domain Function

The `add_asset_to_domain` function in the `domain_creation_example.py` script enables you to programmatically assign assets to domains in DataHub.

### Function Functionality

The function:

1. **Takes Two URNs**: The asset URN and the domain URN
2. **Creates Association**: Establishes a link between the asset and domain
3. **Updates Metadata**: Modifies the asset's metadata to include domain information
4. **Provides Feedback**: Logs success or failure of the operation

### How to Use the Function

```python
# Import the function from the script
from domain_creation_example import add_asset_to_domain

# Example usage
asset_urn = "urn:li:dataset:(urn:li:dataPlatform:snowflake,marketing_analytics.campaign_performance,PROD)"
domain_urn = "urn:li:domain:marketing"

# Add the asset to the domain
add_asset_to_domain(asset_urn, domain_urn)
```

### Function Implementation Details

The function works by:

1. Creating a payload that specifies which asset should be assigned to which domain:
   ```json
   {
     "urn": "asset_urn",
     "aspect": {
       "domains": {
         "domains": [
           {
             "domain": "domain_urn"
           }
         ]
       }
     }
   }
   ```

2. Sending this payload to DataHub's entity API endpoint to create the association

3. Handling success and error cases with appropriate logging

## Assigning Different Types of Assets to Domains

You can assign various types of assets to domains in DataHub:

### Datasets

```python
# Assign a dataset to a domain
dataset_urn = "urn:li:dataset:(urn:li:dataPlatform:snowflake,marketing_analytics.campaign_performance,PROD)"
domain_urn = "urn:li:domain:marketing"
add_asset_to_domain(dataset_urn, domain_urn)
```

### Dashboards

```python
# Assign a dashboard to a domain
dashboard_urn = "urn:li:dashboard:(looker,marketing_dashboard_123)"
domain_urn = "urn:li:domain:marketing"
add_asset_to_domain(dashboard_urn, domain_urn)
```

### Data Pipelines

```python
# Assign a data pipeline to a domain
pipeline_urn = "urn:li:dataFlow:(airflow,marketing_etl_pipeline,PROD)"
domain_urn = "urn:li:domain:marketing"
add_asset_to_domain(pipeline_urn, domain_urn)
```

### Charts

```python
# Assign a chart to a domain
chart_urn = "urn:li:chart:(looker,campaign_performance_chart_456)"
domain_urn = "urn:li:domain:marketing"
add_asset_to_domain(chart_urn, domain_urn)
```

## Assigning Assets to Domains via UI

If you prefer using the DataHub UI:

1. **Navigate to the Asset**: Find the dataset, dashboard, or other asset you want to assign
2. **Access Domain Assignment**:
   - Click on the "..." menu in the top right of the asset page
   - Select "Move to Domain"
3. **Select Domain**:
   - Choose the appropriate domain from the dropdown menu
   - Click "Save" to assign the asset to the domain
4. **Verify Assignment**:
   - The domain should now appear on the asset's page
   - The asset should appear when browsing the domain

## Bulk Asset Assignment

For large-scale domain assignments, you can use a script to process multiple assets:

```python
def bulk_assign_assets_to_domain(asset_urns, domain_urn):
    """
    Assign multiple assets to a domain
    
    Parameters:
        asset_urns (list): List of asset URNs to assign
        domain_urn (str): The domain URN
    
    Returns:
        tuple: (success_count, failure_count)
    """
    success_count = 0
    failure_count = 0
    
    for asset_urn in asset_urns:
        result = add_asset_to_domain(asset_urn, domain_urn)
        if result:
            success_count += 1
        else:
            failure_count += 1
    
    return (success_count, failure_count)

# Example usage
marketing_assets = [
    "urn:li:dataset:(urn:li:dataPlatform:snowflake,marketing_analytics.campaign_performance,PROD)",
    "urn:li:dataset:(urn:li:dataPlatform:snowflake,marketing_analytics.customer_segments,PROD)",
    "urn:li:dashboard:(looker,marketing_dashboard_123)",
    "urn:li:chart:(looker,campaign_performance_chart_456)"
]

success, failure = bulk_assign_assets_to_domain(marketing_assets, "urn:li:domain:marketing")
print(f"Successfully assigned {success} assets, failed to assign {failure} assets")
```

## Domain Assignment During Ingestion

You can also assign assets to domains during the ingestion process:

```python
# Example DataHub ingestion source configuration with domain assignment
source_config = {
    "type": "snowflake",
    "config": {
        "username": "username",
        "password": "password",
        "account_id": "account_id",
        "warehouse": "warehouse",
        "database_pattern": {
            "allow": ["marketing_analytics"]
        },
        "domain": {
            "marketing_analytics.*": "urn:li:domain:marketing"
        }
    }
}
```

This approach automatically assigns assets to domains based on patterns in their names or locations.

## Moving Assets Between Domains

As your organization evolves, you may need to move assets between domains:

```python
def move_asset_to_new_domain(asset_urn, new_domain_urn):
    """
    Move an asset to a new domain (replaces any existing domain assignment)
    
    Parameters:
        asset_urn (str): The asset URN to move
        new_domain_urn (str): The target domain URN
    
    Returns:
        bool: True if asset was moved successfully, False otherwise
    """
    try:
        # Prepare the payload with the new domain
        payload = {
            "urn": asset_urn,
            "aspect": {
                "domains": {
                    "domains": [
                        {
                            "domain": new_domain_urn
                        }
                    ]
                }
            }
        }
        
        # Update the asset with the new domain
        response = requests.post(
            f"{DATAHUB_URL}/entities?action=ingest",
            headers=headers,
            data=json.dumps(payload)
        )
        
        if response.status_code == 200:
            logger.info(f"Successfully moved asset {asset_urn} to domain {new_domain_urn}")
            return True
        else:
            logger.error(f"Failed to move asset to new domain: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error moving asset to new domain: {str(e)}")
        return False
```

## Finding Unassigned Assets

To identify assets that haven't been assigned to any domain:

```python
def find_unassigned_assets(asset_type="dataset", limit=100):
    """
    Find assets that are not assigned to any domain
    
    Parameters:
        asset_type (str): Type of asset to search for (default: "dataset")
        limit (int): Maximum number of results to return
    
    Returns:
        list: URNs of unassigned assets
    """
    try:
        # Prepare the search query
        query = {
            "query": "*",
            "filters": {
                "and": [
                    {"entity_type": [asset_type]},
                    {"not": {"condition": {"EXISTS": {"field": "domains"}}}}
                ]
            },
            "start": 0,
            "count": limit
        }
        
        # Execute the search
        response = requests.post(
            f"{DATAHUB_URL}/search",
            headers=headers,
            data=json.dumps(query)
        )
        
        if response.status_code == 200:
            data = response.json()
            unassigned_assets = [entity["urn"] for entity in data.get("entities", [])]
            logger.info(f"Found {len(unassigned_assets)} unassigned {asset_type}s")
            return unassigned_assets
        else:
            logger.error(f"Failed to search for unassigned assets: {response.text}")
            return []
            
    except Exception as e:
        logger.error(f"Error searching for unassigned assets: {str(e)}")
        return []
```

## Best Practices for Domain Assignment

1. **Consistent Assignment**: Ensure related assets are assigned to the same domain

2. **Complete Coverage**: Aim to assign all important assets to appropriate domains

3. **Automation for Scale**: Use scripts for bulk assignment rather than manual UI work

4. **Pattern-Based Assignment**: Develop naming conventions that enable pattern-based domain assignment

5. **Regular Audit**: Periodically check for unassigned assets and assign them to domains

6. **Consider Lineage**: When assigning assets, consider their lineage relationships
   - Assign related assets in a data pipeline to the same domain where appropriate
   - For cross-domain data flows, assign assets to their primary business domain

7. **Domain Transfer Process**: Establish a process for moving assets between domains when responsibilities change

## Integration with Glossary Terms

For comprehensive context, combine domain assignment with glossary term linkage:

1. **Assign Asset to Domain**: Place the asset in its organizational context
2. **Link Business Terms**: Connect relevant glossary terms to the asset
3. **Add Documentation**: Provide additional context and usage information

This multi-layered approach provides both organizational and semantic context to your data assets.

## Conclusion

Assigning assets to domains is a foundational step in organizing your data catalog. By systematically connecting assets to their business domains, you create a more intuitive, business-aligned data environment that supports both discovery and governance.

The scripts and examples in this repository provide tools for programmatically managing domain assignments, allowing you to implement at scale across your organization.