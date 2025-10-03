#!/usr/bin/env python3
"""
DataHub Retention Period Enricher
Pulls retention period information from Snowflake and adds it as a structured property to DataHub assets.
"""

import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any
import requests
import snowflake.connector
from snowflake.connector import DictCursor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RetentionEnricher:
    def __init__(self, datahub_gms_url: str, datahub_token: str, 
                 snowflake_config: Dict[str, str]):
        self.datahub_gms_url = datahub_gms_url.rstrip('/')
        self.datahub_token = datahub_token
        self.snowflake_config = snowflake_config
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {datahub_token}',
            'Content-Type': 'application/json'
        })
    
    def get_snowflake_retention_data(self) -> List[Dict[str, Any]]:
        """Query Snowflake to get retention period information for all tables."""
        try:
            # Connect to Snowflake
            conn = snowflake.connector.connect(
                user=self.snowflake_config['user'],
                password=self.snowflake_config['password'],
                account=self.snowflake_config['account'],
                warehouse=self.snowflake_config['warehouse'],
                database=self.snowflake_config['database'],
                schema=self.snowflake_config['schema']
            )
            
            cursor = conn.cursor(DictCursor)
            
            # Query to get retention information
            query = """
            SELECT 
                TABLE_CATALOG as database_name,
                TABLE_SCHEMA as schema_name,
                TABLE_NAME as table_name,
                RETENTION_TIME,
                CASE 
                    WHEN RETENTION_TIME IS NOT NULL THEN 'DAYS'
                    ELSE NULL
                END as retention_unit,
                CASE 
                    WHEN RETENTION_TIME IS NOT NULL THEN TRUE
                    ELSE FALSE
                END as is_retention_enabled,
                CURRENT_TIMESTAMP() as last_updated
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
            AND RETENTION_TIME IS NOT NULL
            ORDER BY TABLE_CATALOG, TABLE_SCHEMA, TABLE_NAME
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            logger.info(f"Retrieved retention data for {len(results)} tables")
            return results
            
        except Exception as e:
            logger.error(f"Error querying Snowflake: {str(e)}")
            raise
    
    def get_datahub_assets(self, database_name: str, schema_name: str) -> List[Dict[str, Any]]:
        """Get DataHub assets for a specific database and schema."""
        try:
            # Search for datasets in the specific database/schema
            search_query = {
                "query": f"database:{database_name} schema:{schema_name}",
                "entityTypes": ["dataset"],
                "start": 0,
                "count": 1000
            }
            
            response = self.session.post(
                f"{self.datahub_gms_url}/graphql",
                json={
                    "query": """
                    query search($input: SearchInput!) {
                        search(input: $input) {
                            searchResults {
                                entity {
                                    urn
                                    type
                                }
                            }
                        }
                    }
                    """,
                    "variables": {"input": search_query}
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Error searching DataHub: {response.status_code} - {response.text}")
                return []
            
            data = response.json()
            if 'errors' in data:
                logger.error(f"GraphQL errors: {data['errors']}")
                return []
            
            search_results = data.get('data', {}).get('search', {}).get('searchResults', [])
            return [result['entity'] for result in search_results]
            
        except Exception as e:
            logger.error(f"Error getting DataHub assets: {str(e)}")
            return []
    
    def add_retention_property(self, asset_urn: str, retention_data: Dict[str, Any]) -> bool:
        """Add retention period as a structured property to a DataHub asset."""
        try:
            # Prepare the structured property data
            property_data = {
                "retention_time": retention_data.get('RETENTION_TIME'),
                "retention_unit": retention_data.get('retention_unit'),
                "is_retention_enabled": retention_data.get('is_retention_enabled'),
                "last_updated": retention_data.get('last_updated').isoformat() if retention_data.get('last_updated') else datetime.now().isoformat()
            }
            
            # Create the structured property
            mutation = """
            mutation addStructuredProperty($input: AddStructuredPropertyInput!) {
                addStructuredProperty(input: $input)
            }
            """
            
            variables = {
                "input": {
                    "entityUrn": asset_urn,
                    "structuredPropertyUrn": "urn:li:structuredProperty:retention_period",
                    "structuredPropertyValue": {
                        "value": json.dumps(property_data)
                    }
                }
            }
            
            response = self.session.post(
                f"{self.datahub_gms_url}/graphql",
                json={
                    "query": mutation,
                    "variables": variables
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Error adding structured property: {response.status_code} - {response.text}")
                return False
            
            data = response.json()
            if 'errors' in data:
                logger.error(f"GraphQL errors: {data['errors']}")
                return False
            
            logger.info(f"Successfully added retention property to {asset_urn}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding retention property to {asset_urn}: {str(e)}")
            return False
    
    def process_retention_data(self):
        """Main method to process retention data and update DataHub assets."""
        try:
            # Get retention data from Snowflake
            retention_data = self.get_snowflake_retention_data()
            
            if not retention_data:
                logger.warning("No retention data found in Snowflake")
                return
            
            # Group by database and schema for efficient processing
            grouped_data = {}
            for row in retention_data:
                db_schema = f"{row['database_name']}.{row['schema_name']}"
                if db_schema not in grouped_data:
                    grouped_data[db_schema] = []
                grouped_data[db_schema].append(row)
            
            # Process each database/schema combination
            for db_schema, tables in grouped_data.items():
                database_name, schema_name = db_schema.split('.', 1)
                logger.info(f"Processing {len(tables)} tables in {db_schema}")
                
                # Get DataHub assets for this database/schema
                assets = self.get_datahub_assets(database_name, schema_name)
                
                if not assets:
                    logger.warning(f"No DataHub assets found for {db_schema}")
                    continue
                
                # Create a mapping of table names to retention data
                retention_map = {row['table_name']: row for row in tables}
                
                # Update assets with retention data
                updated_count = 0
                for asset in assets:
                    # Extract table name from URN (assuming format: urn:li:dataset:(urn:li:dataPlatform:snowflake,db.schema.table,PROD))
                    urn_parts = asset['urn'].split(',')
                    if len(urn_parts) >= 2:
                        table_identifier = urn_parts[1]
                        table_name = table_identifier.split('.')[-1]
                        
                        if table_name in retention_map:
                            success = self.add_retention_property(asset['urn'], retention_map[table_name])
                            if success:
                                updated_count += 1
                
                logger.info(f"Updated {updated_count} assets in {db_schema}")
            
            logger.info("Retention data processing completed successfully")
            
        except Exception as e:
            logger.error(f"Error processing retention data: {str(e)}")
            raise

def main():
    """Main function to run the retention enricher."""
    # Configuration from environment variables
    datahub_gms_url = os.getenv('DATAHUB_GMS_URL', 'https://test-environment.acryl.io/gms')
    datahub_token = os.getenv('DATAHUB_GMS_TOKEN')
    
    # Snowflake configuration
    snowflake_config = {
        'user': os.getenv('SNOWFLAKE_USER'),
        'password': os.getenv('SNOWFLAKE_PASSWORD'),
        'account': os.getenv('SNOWFLAKE_ACCOUNT'),
        'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE'),
        'database': os.getenv('SNOWFLAKE_DATABASE'),
        'schema': os.getenv('SNOWFLAKE_SCHEMA', 'INFORMATION_SCHEMA')
    }
    
    # Validate required environment variables
    required_vars = ['DATAHUB_GMS_TOKEN'] + list(snowflake_config.keys())
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        sys.exit(1)
    
    # Create and run the enricher
    enricher = RetentionEnricher(datahub_gms_url, datahub_token, snowflake_config)
    enricher.process_retention_data()

if __name__ == "__main__":
    main()
