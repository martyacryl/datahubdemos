#!/usr/bin/env python3
"""
AWS Glue Assertion Extractor
Extracts data quality assertions, constraints, and validation rules from AWS Glue.
"""

import logging
import os
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class GlueTableInfo:
    """Information about a Glue table."""
    database_name: str
    table_name: str
    table_type: str
    parameters: Dict[str, str]
    storage_descriptor: Dict[str, Any]
    partition_keys: List[Dict[str, Any]]
    columns: List[Dict[str, Any]]

class GlueAssertionExtractor:
    """Extracts assertions from AWS Glue tables and databases."""
    
    def __init__(self, region_name: str = None, database_name: str = None):
        self.region_name = region_name or os.getenv('AWS_REGION', 'us-west-2')
        self.database_name = database_name or os.getenv('GLUE_DATABASE_NAME')
        
        # Initialize Glue client
        try:
            self.glue_client = boto3.client('glue', region_name=self.region_name)
            logger.info(f"Initialized Glue client for region: {self.region_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Glue client: {str(e)}")
            raise
    
    def extract_assertions(self, database_name: str = None) -> List[Dict[str, Any]]:
        """
        Extract all assertions from Glue tables in the specified database.
        """
        db_name = database_name or self.database_name
        if not db_name:
            raise ValueError("Database name must be provided")
        
        logger.info(f"Extracting assertions from Glue database: {db_name}")
        
        assertions = []
        
        try:
            # Get all tables in the database
            tables = self._get_tables_in_database(db_name)
            logger.info(f"Found {len(tables)} tables in database {db_name}")
            
            for table in tables:
                table_assertions = self._extract_table_assertions(table)
                assertions.extend(table_assertions)
            
            logger.info(f"Extracted {len(assertions)} assertions from {len(tables)} tables")
            return assertions
            
        except Exception as e:
            logger.error(f"Error extracting assertions from Glue: {str(e)}")
            raise
    
    def _get_tables_in_database(self, database_name: str) -> List[GlueTableInfo]:
        """Get all tables in the specified database."""
        tables = []
        
        try:
            paginator = self.glue_client.get_paginator('get_tables')
            page_iterator = paginator.paginate(DatabaseName=database_name)
            
            for page in page_iterator:
                for table in page['TableList']:
                    table_info = GlueTableInfo(
                        database_name=table['DatabaseName'],
                        table_name=table['Name'],
                        table_type=table.get('TableType', 'EXTERNAL_TABLE'),
                        parameters=table.get('Parameters', {}),
                        storage_descriptor=table.get('StorageDescriptor', {}),
                        partition_keys=table.get('PartitionKeys', []),
                        columns=table.get('StorageDescriptor', {}).get('Columns', [])
                    )
                    tables.append(table_info)
            
            return tables
            
        except ClientError as e:
            logger.error(f"Error getting tables from Glue database {database_name}: {str(e)}")
            raise
    
    def _extract_table_assertions(self, table: GlueTableInfo) -> List[Dict[str, Any]]:
        """Extract assertions from a single Glue table."""
        assertions = []
        
        # Generate DataHub entity URN for the table
        entity_urn = f"urn:li:dataset:(urn:li:dataPlatform:glue,{table.database_name}.{table.table_name},PROD)"
        
        # Extract table-level assertions
        table_assertions = self._extract_table_level_assertions(table, entity_urn)
        assertions.extend(table_assertions)
        
        # Extract column-level assertions
        column_assertions = self._extract_column_level_assertions(table, entity_urn)
        assertions.extend(column_assertions)
        
        # Extract data quality assertions
        dq_assertions = self._extract_data_quality_assertions(table, entity_urn)
        assertions.extend(dq_assertions)
        
        return assertions
    
    def _extract_table_level_assertions(self, table: GlueTableInfo, entity_urn: str) -> List[Dict[str, Any]]:
        """Extract table-level assertions from Glue table properties."""
        assertions = []
        
        # Table type assertion
        if table.table_type:
            assertion = {
                'source_id': f"glue-table-type-{table.database_name}-{table.table_name}",
                'entity_urn': entity_urn,
                'assertion_type': 'Table Type Validation',
                'description': f'Validates that table type is {table.table_type}',
                'platform': 'aws-glue',
                'external_url': f"https://console.aws.amazon.com/glue/home?region={self.region_name}#etl:tab=databases",
                'properties': {
                    'table_type': table.table_type,
                    'database_name': table.database_name,
                    'table_name': table.table_name
                }
            }
            assertions.append(assertion)
        
        # Storage format assertion
        storage_format = table.storage_descriptor.get('InputFormat')
        if storage_format:
            assertion = {
                'source_id': f"glue-storage-format-{table.database_name}-{table.table_name}",
                'entity_urn': entity_urn,
                'assertion_type': 'Storage Format Validation',
                'description': f'Validates that storage format is {storage_format}',
                'platform': 'aws-glue',
                'external_url': f"https://console.aws.amazon.com/glue/home?region={self.region_name}#etl:tab=databases",
                'properties': {
                    'storage_format': storage_format,
                    'database_name': table.database_name,
                    'table_name': table.table_name
                }
            }
            assertions.append(assertion)
        
        # Compression assertion
        compression = table.storage_descriptor.get('Parameters', {}).get('compression.type')
        if compression:
            assertion = {
                'source_id': f"glue-compression-{table.database_name}-{table.table_name}",
                'entity_urn': entity_urn,
                'assertion_type': 'Compression Validation',
                'description': f'Validates that compression type is {compression}',
                'platform': 'aws-glue',
                'external_url': f"https://console.aws.amazon.com/glue/home?region={self.region_name}#etl:tab=databases",
                'properties': {
                    'compression_type': compression,
                    'database_name': table.database_name,
                    'table_name': table.table_name
                }
            }
            assertions.append(assertion)
        
        return assertions
    
    def _extract_column_level_assertions(self, table: GlueTableInfo, entity_urn: str) -> List[Dict[str, Any]]:
        """Extract column-level assertions from Glue table columns."""
        assertions = []
        
        for column in table.columns:
            column_name = column.get('Name')
            column_type = column.get('Type')
            column_comment = column.get('Comment', '')
            
            if not column_name or not column_type:
                continue
            
            # Data type assertion
            assertion = {
                'source_id': f"glue-column-type-{table.database_name}-{table.table_name}-{column_name}",
                'entity_urn': entity_urn,
                'assertion_type': 'Data Type Validation',
                'description': f'Validates that column {column_name} is of type {column_type}',
                'platform': 'aws-glue',
                'field_path': column_name,
                'external_url': f"https://console.aws.amazon.com/glue/home?region={self.region_name}#etl:tab=databases",
                'logic': f"SELECT COUNT(*) FROM {table.database_name}.{table.table_name} WHERE {column_name} IS NOT NULL AND {column_name}::{column_type} IS NULL",
                'properties': {
                    'column_name': column_name,
                    'expected_type': column_type,
                    'column_comment': column_comment,
                    'database_name': table.database_name,
                    'table_name': table.table_name
                }
            }
            assertions.append(assertion)
            
            # Nullable assertion (if column is marked as NOT NULL)
            if 'NOT NULL' in column_comment.upper() or 'NOTNULL' in column_comment.upper():
                assertion = {
                    'source_id': f"glue-column-nullable-{table.database_name}-{table.table_name}-{column_name}",
                    'entity_urn': entity_urn,
                    'assertion_type': 'Nullability Validation',
                    'description': f'Validates that column {column_name} is NOT NULL',
                    'platform': 'aws-glue',
                    'field_path': column_name,
                    'external_url': f"https://console.aws.amazon.com/glue/home?region={self.region_name}#etl:tab=databases",
                    'logic': f"SELECT COUNT(*) FROM {table.database_name}.{table.table_name} WHERE {column_name} IS NULL",
                    'properties': {
                        'column_name': column_name,
                        'nullable': 'false',
                        'database_name': table.database_name,
                        'table_name': table.table_name
                    }
                }
                assertions.append(assertion)
        
        return assertions
    
    def _extract_data_quality_assertions(self, table: GlueTableInfo, entity_urn: str) -> List[Dict[str, Any]]:
        """Extract data quality assertions from Glue table parameters."""
        assertions = []
        
        # Look for data quality rules in table parameters
        dq_rules = []
        for key, value in table.parameters.items():
            if 'data.quality' in key.lower() or 'dq' in key.lower():
                dq_rules.append((key, value))
        
        for rule_key, rule_value in dq_rules:
            assertion = {
                'source_id': f"glue-dq-rule-{table.database_name}-{table.table_name}-{rule_key}",
                'entity_urn': entity_urn,
                'assertion_type': 'Data Quality Rule',
                'description': f'Data quality rule: {rule_key} = {rule_value}',
                'platform': 'aws-glue',
                'external_url': f"https://console.aws.amazon.com/glue/home?region={self.region_name}#etl:tab=databases",
                'properties': {
                    'rule_key': rule_key,
                    'rule_value': rule_value,
                    'database_name': table.database_name,
                    'table_name': table.table_name
                }
            }
            assertions.append(assertion)
        
        # Extract partitioning assertions
        if table.partition_keys:
            partition_columns = [pk['Name'] for pk in table.partition_keys]
            assertion = {
                'source_id': f"glue-partitioning-{table.database_name}-{table.table_name}",
                'entity_urn': entity_urn,
                'assertion_type': 'Partitioning Validation',
                'description': f'Validates that table is partitioned by: {", ".join(partition_columns)}',
                'platform': 'aws-glue',
                'external_url': f"https://console.aws.amazon.com/glue/home?region={self.region_name}#etl:tab=databases",
                'properties': {
                    'partition_columns': ', '.join(partition_columns),
                    'partition_count': str(len(partition_columns)),
                    'database_name': table.database_name,
                    'table_name': table.table_name
                }
            }
            assertions.append(assertion)
        
        return assertions
    
    def get_database_info(self, database_name: str = None) -> Dict[str, Any]:
        """Get information about a Glue database."""
        db_name = database_name or self.database_name
        if not db_name:
            raise ValueError("Database name must be provided")
        
        try:
            response = self.glue_client.get_database(Name=db_name)
            return response['Database']
        except ClientError as e:
            logger.error(f"Error getting database info for {db_name}: {str(e)}")
            raise

def main():
    """Example usage of the Glue Assertion Extractor."""
    # Configuration from environment variables
    region_name = os.getenv('AWS_REGION', 'us-west-2')
    database_name = os.getenv('GLUE_DATABASE_NAME')
    
    if not database_name:
        logger.error("GLUE_DATABASE_NAME environment variable is required")
        return
    
    try:
        # Create extractor
        extractor = GlueAssertionExtractor(region_name, database_name)
        
        # Extract assertions
        logger.info(f"Extracting assertions from Glue database: {database_name}")
        assertions = extractor.extract_assertions()
        
        # Print results
        logger.info(f"Extracted {len(assertions)} assertions:")
        for i, assertion in enumerate(assertions, 1):
            logger.info(f"{i}. {assertion['assertion_type']}: {assertion['description']}")
            logger.info(f"   Source ID: {assertion['source_id']}")
            logger.info(f"   Entity URN: {assertion['entity_urn']}")
            if assertion.get('field_path'):
                logger.info(f"   Field Path: {assertion['field_path']}")
            logger.info("")
        
        # Save to file for inspection
        output_file = f"glue_assertions_{database_name}.json"
        with open(output_file, 'w') as f:
            json.dump(assertions, f, indent=2)
        
        logger.info(f"Assertions saved to: {output_file}")
        
    except Exception as e:
        logger.error(f"Error extracting Glue assertions: {str(e)}")

if __name__ == "__main__":
    main()
