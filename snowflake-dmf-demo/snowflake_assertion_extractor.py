#!/usr/bin/env python3
"""
Snowflake Assertion Extractor
Extracts constraints, check constraints, and validation rules from Snowflake.
"""

import logging
import os
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import snowflake.connector
from snowflake.connector import DictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class SnowflakeTableInfo:
    """Information about a Snowflake table."""
    database_name: str
    schema_name: str
    table_name: str
    table_type: str
    columns: List[Dict[str, Any]]
    constraints: List[Dict[str, Any]]

class SnowflakeAssertionExtractor:
    """Extracts assertions from Snowflake tables and schemas."""
    
    def __init__(self, account: str = None, user: str = None, password: str = None, 
                 warehouse: str = None, database: str = None, schema: str = None):
        self.account = account or os.getenv('SNOWFLAKE_ACCOUNT')
        self.user = user or os.getenv('SNOWFLAKE_USER')
        self.password = password or os.getenv('SNOWFLAKE_PASSWORD')
        self.warehouse = warehouse or os.getenv('SNOWFLAKE_WAREHOUSE')
        self.database = database or os.getenv('SNOWFLAKE_DATABASE')
        self.schema = schema or os.getenv('SNOWFLAKE_SCHEMA')
        
        # Validate required parameters
        required_params = [self.account, self.user, self.password, self.warehouse, self.database]
        if not all(required_params):
            missing = [param for param, value in zip(['account', 'user', 'password', 'warehouse', 'database'], required_params) if not value]
            raise ValueError(f"Missing required Snowflake parameters: {', '.join(missing)}")
        
        logger.info(f"Initialized Snowflake extractor for account: {self.account}")
    
    def extract_assertions(self, database_name: str = None, schema_name: str = None) -> List[Dict[str, Any]]:
        """
        Extract all assertions from Snowflake tables in the specified database/schema.
        """
        db_name = database_name or self.database
        schema = schema_name or self.schema
        
        if not db_name:
            raise ValueError("Database name must be provided")
        
        logger.info(f"Extracting assertions from Snowflake database: {db_name}, schema: {schema}")
        
        assertions = []
        
        try:
            # Connect to Snowflake
            conn = self._get_connection()
            cursor = conn.cursor(DictCursor)
            
            # Get all tables in the database/schema
            tables = self._get_tables_in_schema(cursor, db_name, schema)
            logger.info(f"Found {len(tables)} tables in database {db_name}, schema {schema}")
            
            for table in tables:
                table_assertions = self._extract_table_assertions(cursor, table)
                assertions.extend(table_assertions)
            
            cursor.close()
            conn.close()
            
            logger.info(f"Extracted {len(assertions)} assertions from {len(tables)} tables")
            return assertions
            
        except Exception as e:
            logger.error(f"Error extracting assertions from Snowflake: {str(e)}")
            raise
    
    def _get_connection(self):
        """Get Snowflake connection."""
        try:
            conn = snowflake.connector.connect(
                user=self.user,
                password=self.password,
                account=self.account,
                warehouse=self.warehouse,
                database=self.database,
                schema=self.schema
            )
            return conn
        except Exception as e:
            logger.error(f"Failed to connect to Snowflake: {str(e)}")
            raise
    
    def _get_tables_in_schema(self, cursor, database_name: str, schema_name: str) -> List[SnowflakeTableInfo]:
        """Get all tables in the specified database/schema."""
        tables = []
        
        try:
            # Query to get table information
            query = """
            SELECT 
                TABLE_CATALOG as database_name,
                TABLE_SCHEMA as schema_name,
                TABLE_NAME as table_name,
                TABLE_TYPE as table_type
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_CATALOG = %s 
            AND TABLE_SCHEMA = %s
            AND TABLE_TYPE IN ('BASE TABLE', 'VIEW')
            ORDER BY TABLE_NAME
            """
            
            cursor.execute(query, (database_name, schema_name))
            table_rows = cursor.fetchall()
            
            logger.info(f"Found {len(table_rows)} table rows in query results")
            
            for row in table_rows:
                logger.info(f"Processing table row: {row}")
                
                # Get columns for this table
                columns = self._get_table_columns(cursor, database_name, schema_name, row['TABLE_NAME'])
                
                # Get constraints for this table
                constraints = self._get_table_constraints(cursor, database_name, schema_name, row['TABLE_NAME'])
                
                table_info = SnowflakeTableInfo(
                    database_name=row['DATABASE_NAME'],
                    schema_name=row['SCHEMA_NAME'],
                    table_name=row['TABLE_NAME'],
                    table_type=row['TABLE_TYPE'],
                    columns=columns,
                    constraints=constraints
                )
                tables.append(table_info)
            
            return tables
            
        except Exception as e:
            logger.error(f"Error getting tables from Snowflake: {str(e)}")
            raise
    
    def _get_table_columns(self, cursor, database_name: str, schema_name: str, table_name: str) -> List[Dict[str, Any]]:
        """Get column information for a table."""
        try:
            query = """
            SELECT 
                COLUMN_NAME as column_name,
                DATA_TYPE as data_type,
                IS_NULLABLE as is_nullable,
                COLUMN_DEFAULT as column_default,
                CHARACTER_MAXIMUM_LENGTH as max_length,
                NUMERIC_PRECISION as numeric_precision,
                NUMERIC_SCALE as numeric_scale,
                COMMENT as column_comment
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_CATALOG = %s 
            AND TABLE_SCHEMA = %s 
            AND TABLE_NAME = %s
            ORDER BY ORDINAL_POSITION
            """
            
            cursor.execute(query, (database_name, schema_name, table_name))
            return cursor.fetchall()
            
        except Exception as e:
            logger.error(f"Error getting columns for table {table_name}: {str(e)}")
            return []
    
    def _get_table_constraints(self, cursor, database_name: str, schema_name: str, table_name: str) -> List[Dict[str, Any]]:
        """Get constraint information for a table."""
        try:
            # Simplified query that doesn't rely on CONSTRAINT_COLUMN_USAGE
            query = """
            SELECT 
                CONSTRAINT_NAME as constraint_name,
                CONSTRAINT_TYPE as constraint_type
            FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS 
            WHERE TABLE_CATALOG = %s 
            AND TABLE_SCHEMA = %s 
            AND TABLE_NAME = %s
            """
            
            cursor.execute(query, (database_name, schema_name, table_name))
            return cursor.fetchall()
            
        except Exception as e:
            logger.error(f"Error getting constraints for table {table_name}: {str(e)}")
            return []
    
    def _extract_table_assertions(self, cursor, table: SnowflakeTableInfo) -> List[Dict[str, Any]]:
        """Extract assertions from a single Snowflake table."""
        assertions = []
        
        # Generate DataHub entity URN for the table
        entity_urn = f"urn:li:dataset:(urn:li:dataPlatform:snowflake,{table.database_name}.{table.schema_name}.{table.table_name},PROD)"
        
        # Extract DMF assertions (Data Metric Functions)
        dmf_assertions = self._extract_dmf_assertions(cursor, table, entity_urn)
        assertions.extend(dmf_assertions)
        
        # Extract column-level assertions
        column_assertions = self._extract_column_level_assertions(table, entity_urn)
        assertions.extend(column_assertions)
        
        # Extract constraint assertions
        constraint_assertions = self._extract_constraint_assertions(table, entity_urn)
        assertions.extend(constraint_assertions)
        
        return assertions
    
    def _extract_dmf_assertions(self, cursor, table: SnowflakeTableInfo, entity_urn: str) -> List[Dict[str, Any]]:
        """Extract DMF (Data Metric Function) assertions from Snowflake table."""
        assertions = []
        
        try:
            # Query to get DMF information from Snowflake's data quality monitoring results
            query = """
            SELECT 
                MEASUREMENT_TIME,
                TABLE_NAME,
                METRIC_NAME,
                ARGUMENT_NAMES,
                VALUE
            FROM SNOWFLAKE.LOCAL.DATA_QUALITY_MONITORING_RESULTS
            WHERE TABLE_NAME = %s
            ORDER BY MEASUREMENT_TIME DESC
            """
            
            cursor.execute(query, (table.table_name,))
            dmf_rows = cursor.fetchall()
            
            for row in dmf_rows:
                measurement_time = row.get('MEASUREMENT_TIME')
                table_name = row.get('TABLE_NAME', 'Unknown')
                metric_name = row.get('METRIC_NAME', 'Unknown')
                argument_names = row.get('ARGUMENT_NAMES', [])
                value = row.get('VALUE')
                
                # Extract column name from argument_names (usually a list)
                column_name = argument_names[0] if argument_names and len(argument_names) > 0 else 'N/A'
                
                # Create DMF assertion
                assertion = {
                    'source_id': f"snowflake-dmf-{table.database_name}-{table.schema_name}-{table.table_name}-{metric_name}",
                    'entity_urn': entity_urn,
                    'assertion_type': 'Data Quality Metric (DMF)',
                    'description': f'Snowflake DMF: {metric_name} on column "{column_name}" with value {value}',
                    'platform': 'snowflake',
                    'field_path': column_name if column_name != 'N/A' else None,
                    'external_url': f"https://app.snowflake.com/console/account/{self.account}/warehouses",
                    'logic': f"{metric_name} ON ({column_name})",
                    'properties': {
                        'dmf_type': 'Data Metric Function',
                        'metric_name': metric_name,
                        'column_name': column_name,
                        'value': value,
                        'argument_names': argument_names,
                        'measurement_time': measurement_time.isoformat() if measurement_time else None,
                        'database_name': table.database_name,
                        'schema_name': table.schema_name,
                        'table_name': table.table_name
                    }
                }
                assertions.append(assertion)
                
                logger.info(f"Found DMF: {metric_name} on {column_name} with value {value}")
            
            if assertions:
                logger.info(f"Extracted {len(assertions)} DMF assertions for table {table.table_name}")
            else:
                logger.info(f"No DMF assertions found for table {table.table_name}")
                
        except Exception as e:
            logger.warning(f"Could not extract DMF assertions for table {table.table_name}: {str(e)}")
            # DMF extraction is optional, so we don't raise the exception
        
        return assertions
    
    def _extract_column_level_assertions(self, table: SnowflakeTableInfo, entity_urn: str) -> List[Dict[str, Any]]:
        """Extract column-level assertions from Snowflake table columns."""
        assertions = []
        
        for column in table.columns:
            column_name = column.get('column_name')
            data_type = column.get('data_type')
            is_nullable = column.get('is_nullable')
            max_length = column.get('max_length')
            numeric_precision = column.get('numeric_precision')
            numeric_scale = column.get('numeric_scale')
            column_comment = column.get('column_comment', '')
            
            if not column_name or not data_type:
                continue
            
            # Data type assertion
            assertion = {
                'source_id': f"snowflake-column-type-{table.database_name}-{table.schema_name}-{table.table_name}-{column_name}",
                'entity_urn': entity_urn,
                'assertion_type': 'Data Type Validation',
                'description': f'Validates that column {column_name} is of type {data_type}',
                'platform': 'snowflake',
                'field_path': column_name,
                'external_url': f"https://app.snowflake.com/console/account/{self.account}/warehouses",
                'logic': f"SELECT COUNT(*) FROM {table.database_name}.{table.schema_name}.{table.table_name} WHERE {column_name} IS NOT NULL AND {column_name}::{data_type} IS NULL",
                'properties': {
                    'column_name': column_name,
                    'expected_type': data_type,
                    'column_comment': column_comment,
                    'database_name': table.database_name,
                    'schema_name': table.schema_name,
                    'table_name': table.table_name
                }
            }
            assertions.append(assertion)
            
            # Nullability assertion
            if is_nullable == 'NO':
                assertion = {
                    'source_id': f"snowflake-column-nullable-{table.database_name}-{table.schema_name}-{table.table_name}-{column_name}",
                    'entity_urn': entity_urn,
                    'assertion_type': 'Nullability Validation',
                    'description': f'Validates that column {column_name} is NOT NULL',
                    'platform': 'snowflake',
                    'field_path': column_name,
                    'external_url': f"https://app.snowflake.com/console/account/{self.account}/warehouses",
                    'logic': f"SELECT COUNT(*) FROM {table.database_name}.{table.schema_name}.{table.table_name} WHERE {column_name} IS NULL",
                    'properties': {
                        'column_name': column_name,
                        'nullable': 'false',
                        'database_name': table.database_name,
                        'schema_name': table.schema_name,
                        'table_name': table.table_name
                    }
                }
                assertions.append(assertion)
            
            # Length constraint assertion (for string types)
            if max_length and data_type in ['VARCHAR', 'CHAR', 'TEXT']:
                assertion = {
                    'source_id': f"snowflake-column-length-{table.database_name}-{table.schema_name}-{table.table_name}-{column_name}",
                    'entity_urn': entity_urn,
                    'assertion_type': 'Length Validation',
                    'description': f'Validates that column {column_name} length is <= {max_length}',
                    'platform': 'snowflake',
                    'field_path': column_name,
                    'external_url': f"https://app.snowflake.com/console/account/{self.account}/warehouses",
                    'logic': f"SELECT COUNT(*) FROM {table.database_name}.{table.schema_name}.{table.table_name} WHERE LENGTH({column_name}) > {max_length}",
                    'properties': {
                        'column_name': column_name,
                        'max_length': str(max_length),
                        'data_type': data_type,
                        'database_name': table.database_name,
                        'schema_name': table.schema_name,
                        'table_name': table.table_name
                    }
                }
                assertions.append(assertion)
            
            # Numeric precision assertion
            if numeric_precision and data_type in ['NUMBER', 'DECIMAL', 'NUMERIC']:
                assertion = {
                    'source_id': f"snowflake-column-precision-{table.database_name}-{table.schema_name}-{table.table_name}-{column_name}",
                    'entity_urn': entity_urn,
                    'assertion_type': 'Precision Validation',
                    'description': f'Validates that column {column_name} precision is {numeric_precision}',
                    'platform': 'snowflake',
                    'field_path': column_name,
                    'external_url': f"https://app.snowflake.com/console/account/{self.account}/warehouses",
                    'properties': {
                        'column_name': column_name,
                        'precision': str(numeric_precision),
                        'scale': str(numeric_scale or 0),
                        'data_type': data_type,
                        'database_name': table.database_name,
                        'schema_name': table.schema_name,
                        'table_name': table.table_name
                    }
                }
                assertions.append(assertion)
        
        return assertions
    
    def _extract_constraint_assertions(self, table: SnowflakeTableInfo, entity_urn: str) -> List[Dict[str, Any]]:
        """Extract constraint assertions from Snowflake table constraints."""
        assertions = []
        
        for constraint in table.constraints:
            constraint_name = constraint.get('constraint_name')
            constraint_type = constraint.get('constraint_type')
            check_clause = constraint.get('check_clause')
            column_name = constraint.get('column_name')
            
            if not constraint_name or not constraint_type:
                continue
            
            # Check constraint assertion
            if constraint_type == 'CHECK' and check_clause:
                assertion = {
                    'source_id': f"snowflake-check-constraint-{table.database_name}-{table.schema_name}-{table.table_name}-{constraint_name}",
                    'entity_urn': entity_urn,
                    'assertion_type': 'Check Constraint',
                    'description': f'Check constraint {constraint_name}: {check_clause}',
                    'platform': 'snowflake',
                    'field_path': column_name,
                    'external_url': f"https://app.snowflake.com/console/account/{self.account}/warehouses",
                    'logic': f"SELECT COUNT(*) FROM {table.database_name}.{table.schema_name}.{table.table_name} WHERE NOT ({check_clause})",
                    'properties': {
                        'constraint_name': constraint_name,
                        'constraint_type': constraint_type,
                        'check_clause': check_clause,
                        'column_name': column_name or 'N/A',
                        'database_name': table.database_name,
                        'schema_name': table.schema_name,
                        'table_name': table.table_name
                    }
                }
                assertions.append(assertion)
            
            # Primary key constraint assertion
            elif constraint_type == 'PRIMARY KEY':
                assertion = {
                    'source_id': f"snowflake-pk-constraint-{table.database_name}-{table.schema_name}-{table.table_name}-{constraint_name}",
                    'entity_urn': entity_urn,
                    'assertion_type': 'Primary Key Constraint',
                    'description': f'Primary key constraint {constraint_name} on column {column_name}',
                    'platform': 'snowflake',
                    'field_path': column_name,
                    'external_url': f"https://app.snowflake.com/console/account/{self.account}/warehouses",
                    'logic': f"SELECT COUNT(*) FROM {table.database_name}.{table.schema_name}.{table.table_name} WHERE {column_name} IS NULL",
                    'properties': {
                        'constraint_name': constraint_name,
                        'constraint_type': constraint_type,
                        'column_name': column_name or 'N/A',
                        'database_name': table.database_name,
                        'schema_name': table.schema_name,
                        'table_name': table.table_name
                    }
                }
                assertions.append(assertion)
            
            # Unique constraint assertion
            elif constraint_type == 'UNIQUE':
                assertion = {
                    'source_id': f"snowflake-unique-constraint-{table.database_name}-{table.schema_name}-{table.table_name}-{constraint_name}",
                    'entity_urn': entity_urn,
                    'assertion_type': 'Unique Constraint',
                    'description': f'Unique constraint {constraint_name} on column {column_name}',
                    'platform': 'snowflake',
                    'field_path': column_name,
                    'external_url': f"https://app.snowflake.com/console/account/{self.account}/warehouses",
                    'logic': f"SELECT COUNT(*) FROM (SELECT {column_name}, COUNT(*) as cnt FROM {table.database_name}.{table.schema_name}.{table.table_name} GROUP BY {column_name} HAVING cnt > 1)",
                    'properties': {
                        'constraint_name': constraint_name,
                        'constraint_type': constraint_type,
                        'column_name': column_name or 'N/A',
                        'database_name': table.database_name,
                        'schema_name': table.schema_name,
                        'table_name': table.table_name
                    }
                }
                assertions.append(assertion)
        
        return assertions

def main():
    """Example usage of the Snowflake Assertion Extractor."""
    # Configuration from environment variables
    account = os.getenv('SNOWFLAKE_ACCOUNT')
    user = os.getenv('SNOWFLAKE_USER')
    password = os.getenv('SNOWFLAKE_PASSWORD')
    warehouse = os.getenv('SNOWFLAKE_WAREHOUSE')
    database = os.getenv('SNOWFLAKE_DATABASE')
    schema = os.getenv('SNOWFLAKE_SCHEMA')
    
    if not all([account, user, password, warehouse, database]):
        logger.error("Required Snowflake environment variables are missing")
        return
    
    try:
        # Create extractor
        extractor = SnowflakeAssertionExtractor(account, user, password, warehouse, database, schema)
        
        # Extract assertions
        logger.info(f"Extracting assertions from Snowflake database: {database}, schema: {schema}")
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
        output_file = f"snowflake_assertions_{database}_{schema}.json"
        with open(output_file, 'w') as f:
            json.dump(assertions, f, indent=2)
        
        logger.info(f"Assertions saved to: {output_file}")
        
    except Exception as e:
        logger.error(f"Error extracting Snowflake assertions: {str(e)}")

if __name__ == "__main__":
    main()
