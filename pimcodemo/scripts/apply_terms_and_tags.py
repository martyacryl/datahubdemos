#!/usr/bin/env python3
"""
PIMCO Municipal Bond Demo - Apply Glossary Terms and Tags to Tables/Columns
Applies glossary terms and tags to Snowflake tables and columns based on mappings
"""

import os
import yaml
from datetime import datetime
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.ingestion.graph.client import DataHubGraph, DatahubClientConfig
from datahub.metadata.schema_classes import (
    GlobalTagsClass,
    TagAssociationClass,
    GlossaryTermsClass,
    GlossaryTermAssociationClass,
    DomainsClass,
    AuditStampClass,
    SchemaMetadataClass,
)
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.mce_builder import make_term_urn, make_tag_urn, make_domain_urn


class TermsAndTagsApplicator:
    """Applies glossary terms and tags to Snowflake datasets"""
    
    def __init__(self, datahub_url: str, datahub_token: str):
        """Initialize DataHub emitter and graph client"""
        self.emitter = DatahubRestEmitter(gms_server=datahub_url, token=datahub_token)
        self.graph = DataHubGraph(
            config=DatahubClientConfig(
                server=datahub_url,
                token=datahub_token,
            )
        )
        self.audit_stamp = AuditStampClass(
            time=int(datetime.now().timestamp() * 1000),
            actor="urn:li:corpuser:datahub"
        )
        
    def _normalize_urn_name(self, name: str) -> str:
        """Normalize name for URN"""
        import re
        normalized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        normalized = re.sub(r'_+', '_', normalized)
        normalized = normalized.strip('_')
        return normalized.lower()
    
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
    
    def apply_tags_to_table(self, dataset_urn: str, tag_names: list):
        """Apply tags to a table"""
        tags = []
        for tag_name in tag_names:
            tag_urn = make_tag_urn(self._normalize_urn_name(tag_name))
            tags.append(TagAssociationClass(tag=tag_urn))
        
        if tags:
            global_tags = GlobalTagsClass(tags=tags)
            event = MetadataChangeProposalWrapper(
                entityUrn=dataset_urn,
                aspect=global_tags,
            )
            self.emitter.emit(event)
            print(f"  Applied tags to table: {', '.join(tag_names)}")
    
    def apply_terms_to_table(self, dataset_urn: str, term_names: list):
        """Apply glossary terms to a table"""
        terms = []
        for term_name in term_names:
            term_urn = make_term_urn(self._normalize_urn_name(term_name))
            terms.append(GlossaryTermAssociationClass(urn=term_urn))
        
        if terms:
            glossary_terms = GlossaryTermsClass(terms=terms, auditStamp=self.audit_stamp)
            event = MetadataChangeProposalWrapper(
                entityUrn=dataset_urn,
                aspect=glossary_terms,
            )
            self.emitter.emit(event)
            print(f"  Applied glossary terms to table: {', '.join(term_names)}")
    
    def apply_domain_to_table(self, dataset_urn: str, domain_name: str):
        """Apply domain to a table"""
        domain_urn = make_domain_urn(self._normalize_urn_name(domain_name))
        domains = DomainsClass(domains=[domain_urn])
        event = MetadataChangeProposalWrapper(
            entityUrn=dataset_urn,
            aspect=domains,
        )
        self.emitter.emit(event)
        print(f"  Applied domain to table: {domain_name}")
    
    def apply_terms_to_column(self, column_urn: str, term_names: list):
        """Apply glossary terms to a column"""
        terms = []
        for term_name in term_names:
            term_urn = make_term_urn(self._normalize_urn_name(term_name))
            terms.append(GlossaryTermAssociationClass(urn=term_urn))
        
        if terms:
            glossary_terms = GlossaryTermsClass(terms=terms, auditStamp=self.audit_stamp)
            event = MetadataChangeProposalWrapper(
                entityUrn=column_urn,
                aspect=glossary_terms,
            )
            self.emitter.emit(event)
            print(f"  Applied glossary terms to column: {', '.join(term_names)}")
    
    def apply_tags_to_column(self, column_urn: str, tag_names: list):
        """Apply tags to a column"""
        tags = []
        for tag_name in tag_names:
            tag_urn = make_tag_urn(self._normalize_urn_name(tag_name))
            tags.append(TagAssociationClass(tag=tag_urn))
        
        if tags:
            global_tags = GlobalTagsClass(tags=tags)
            event = MetadataChangeProposalWrapper(
                entityUrn=column_urn,
                aspect=global_tags,
            )
            self.emitter.emit(event)
            print(f"  Applied tags to column: {', '.join(tag_names)}")
    
    def apply_mappings(self, mappings_file: str):
        """Apply terms and tags from mappings YAML file"""
        # DataHub normalizes database names to lowercase in URNs
        database = os.getenv('SNOWFLAKE_DATABASE', 'pimco_demo').lower()
        
        with open(mappings_file, 'r') as f:
            config = yaml.safe_load(f)
        
        tables = config.get('tables', [])
        
        for table_config in tables:
            schema = table_config.get('schema')
            table = table_config.get('table')
            # URN will normalize schema and table to lowercase too
            dataset_urn = self._make_dataset_urn(database, schema, table)
            
            print(f"\nApplying metadata to {database}.{schema.lower()}.{table.lower()}:")
            
            # Apply tags to table
            if 'tags' in table_config:
                self.apply_tags_to_table(dataset_urn, table_config['tags'])
            
            # Apply glossary terms to table
            if 'glossary_terms' in table_config:
                self.apply_terms_to_table(dataset_urn, table_config['glossary_terms'])
            
            # Apply domain to table
            if 'domain' in table_config:
                self.apply_domain_to_table(dataset_urn, table_config['domain'])
            
            # Apply terms and tags to columns
            if 'columns' in table_config:
                # Get schema metadata to find actual field paths
                from datahub.metadata.schema_classes import SchemaMetadataClass
                schema = self.graph.get_aspect(entity_urn=dataset_urn, aspect_type=SchemaMetadataClass)
                
                if schema:
                    # Create mapping of column names to field paths (case-insensitive)
                    field_path_map = {f.fieldPath.lower(): f.fieldPath for f in schema.fields}
                    
                    for column_config in table_config['columns']:
                        column_name = column_config.get('name')
                        # Find matching field path (case-insensitive)
                        column_name_lower = column_name.lower()
                        field_path = field_path_map.get(column_name_lower)
                        
                        if not field_path:
                            print(f"  Warning: Column '{column_name}' not found in schema metadata, skipping")
                            continue
                        
                        # Use the actual field path from schema metadata
                        column_urn = f"{dataset_urn}#{field_path}"
                        
                        if 'glossary_terms' in column_config:
                            self.apply_terms_to_column(column_urn, column_config['glossary_terms'])
                        
                        if 'tags' in column_config:
                            self.apply_tags_to_column(column_urn, column_config['tags'])
                else:
                    print(f"  Warning: No schema metadata found for {dataset_urn}, skipping column metadata")
        
        # Flush all events
        self.emitter.flush()
        print("\nAll metadata applied successfully!")


def main():
    """Main execution function"""
    # Get configuration from environment variables
    datahub_url = os.getenv('DATAHUB_GMS_URL', 'https://test-environment.acryl.io/gms')
    datahub_token = os.getenv('DATAHUB_PAT')
    
    if not datahub_token:
        raise ValueError("DATAHUB_PAT environment variable must be set")
    
    # Initialize applicator
    applicator = TermsAndTagsApplicator(datahub_url, datahub_token)
    
    # Get base directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Apply mappings
    mappings_file = os.path.join(base_dir, 'datahub', 'table_term_tag_mappings.yaml')
    
    if not os.path.exists(mappings_file):
        print(f"Error: Mappings file not found: {mappings_file}")
        print("Please create the mappings file first.")
        return
    
    print("Applying glossary terms and tags to tables and columns...")
    applicator.apply_mappings(mappings_file)
    
    print("\nDone!")


if __name__ == "__main__":
    main()

