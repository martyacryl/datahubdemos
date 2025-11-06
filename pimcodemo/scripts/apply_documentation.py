#!/usr/bin/env python3
"""
PIMCO Municipal Bond Demo - Apply Table Documentation
Applies comprehensive table and column documentation from YAML file to DataHub
"""

import os
import yaml
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.ingestion.graph.client import DataHubGraph
from datahub.ingestion.graph.client import DatahubClientConfig
from datahub.metadata.schema_classes import (
    DatasetPropertiesClass,
    SchemaMetadataClass,
    SchemaFieldClass,
    SchemaFieldDataTypeClass,
    StringTypeClass,
)
from datahub.emitter.mcp import MetadataChangeProposalWrapper


class DocumentationApplicator:
    """Applies table and column documentation to Snowflake datasets"""
    
    def __init__(self, datahub_url: str, datahub_token: str):
        """Initialize DataHub emitter and graph client"""
        self.emitter = DatahubRestEmitter(gms_server=datahub_url, token=datahub_token)
        self.graph = DataHubGraph(
            config=DatahubClientConfig(
                server=datahub_url,
                token=datahub_token,
            )
        )
        
    def _make_dataset_urn(self, database: str, schema: str, table: str) -> str:
        """Create dataset URN for Snowflake table"""
        # DataHub normalizes all identifiers to lowercase in URNs
        database_lower = database.lower()
        schema_lower = schema.lower()
        table_lower = table.lower()
        return f"urn:li:dataset:(urn:li:dataPlatform:snowflake,{database_lower}.{schema_lower}.{table_lower},PROD)"
    
    def _make_schema_field_urn(self, dataset_urn: str, column: str) -> str:
        """Create schema field URN for column"""
        return f"{dataset_urn}#{column}"
    
    def apply_table_documentation(self, dataset_urn: str, description: str):
        """Apply description to a table"""
        dataset_properties = DatasetPropertiesClass(
            description=description,
            name=None,  # Don't override the name
        )
        
        event = MetadataChangeProposalWrapper(
            entityUrn=dataset_urn,
            aspect=dataset_properties,
        )
        
        self.emitter.emit(event)
        print(f"  Applied table description to {dataset_urn}")
    
    def apply_column_documentation(self, dataset_urn: str, column_name: str, description: str):
        """Apply description to a column by updating schema metadata"""
        try:
            # Get existing schema metadata
            schema_metadata = self.graph.get_aspect(
                entity_urn=dataset_urn,
                aspect_type=SchemaMetadataClass,
            )
            
            if not schema_metadata:
                print(f"  Warning: No schema metadata found for {dataset_urn}, skipping column documentation")
                return
            
            # Find and update the column description
            updated = False
            for field in schema_metadata.fields:
                if field.fieldPath.lower() == column_name.lower():
                    field.description = description
                    updated = True
                    break
            
            if not updated:
                print(f"  Warning: Column '{column_name}' not found in schema metadata for {dataset_urn}")
                return
            
            # Emit updated schema metadata
            event = MetadataChangeProposalWrapper(
                entityUrn=dataset_urn,
                aspect=schema_metadata,
            )
            
            self.emitter.emit(event)
            print(f"  Applied column description: {column_name}")
            
        except Exception as e:
            print(f"  Warning: Could not apply column documentation for {column_name}: {e}")
    
    def apply_documentation_from_yaml(self, yaml_file: str):
        """Apply documentation from YAML file"""
        with open(yaml_file, 'r') as f:
            config = yaml.safe_load(f)
        
        tables = config.get('tables', [])
        database = os.getenv('SNOWFLAKE_DATABASE', 'PIMCO_DEMO')
        
        for table_config in tables:
            table_name = table_config.get('table')
            schema = table_config.get('schema', '')
            
            # Parse schema.table format if needed
            if '.' in table_name:
                parts = table_name.split('.')
                schema = parts[0]
                table_name = parts[1]
            
            dataset_urn = self._make_dataset_urn(database, schema, table_name)
            
            # Apply table description
            if 'description' in table_config:
                self.apply_table_documentation(dataset_urn, table_config['description'])
            
            # Apply column descriptions
            if 'columns' in table_config:
                for col_name, col_config in table_config['columns'].items():
                    if isinstance(col_config, dict) and 'description' in col_config:
                        self.apply_column_documentation(
                            dataset_urn,
                            col_name,
                            col_config['description']
                        )
                    elif isinstance(col_config, str):
                        # Simple string description
                        self.apply_column_documentation(
                            dataset_urn,
                            col_name,
                            col_config
                        )
        
        # Flush all events
        self.emitter.flush()
        print("\nDocumentation application complete!")


def main():
    """Main execution function"""
    datahub_url = os.getenv('DATAHUB_GMS_URL', 'https://test-environment.acryl.io/gms')
    datahub_token = os.getenv('DATAHUB_PAT')
    
    if not datahub_token:
        raise ValueError("DATAHUB_PAT environment variable must be set")
    
    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    yaml_file = os.path.join(project_root, 'datahub', 'table_documentation.yaml')
    
    print(f"Applying documentation from: {yaml_file}")
    print(f"DataHub URL: {datahub_url}\n")
    
    applicator = DocumentationApplicator(datahub_url, datahub_token)
    applicator.apply_documentation_from_yaml(yaml_file)


if __name__ == "__main__":
    main()

