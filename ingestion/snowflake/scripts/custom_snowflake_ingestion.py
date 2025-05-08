#!/usr/bin/env python
"""
This script demonstrates a custom Snowflake ingestion pipeline with enhanced metadata extraction.
It adds additional capabilities beyond the standard DataHub ingestion, such as:
1. Custom Snowflake tag to DataHub glossary term mapping
2. Enhanced metadata extraction for table properties
3. Metadata enrichment with custom business context
"""

import os
import sys
import json
import logging
import argparse
import datetime
from typing import Dict, Any, List, Optional

import snowflake.connector
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

from datahub.ingestion.run.pipeline import Pipeline
from datahub.emitter.mce_builder import make_tag_urn, make_term_urn
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.metadata.schema_classes import (
    GlossaryTermAssociationClass,
    GlossaryTermsClass,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

class EnhancedSnowflakeIngestion:
    """Enhanced Snowflake metadata ingestion with custom functionality."""
    
    def __init__(
        self,
        account_id: str,
        username: str,
        password: str,
        warehouse: str,
        role: str,
        database_pattern: List[str],
        datahub_gms_url: str,
    ):
        self.account_id = account_id
        self.username = username
        self.password = password
        self.warehouse = warehouse
        self.role = role
        self.database_pattern = database_pattern
        self.datahub_gms_url = datahub_gms_url
        
        # Create a direct Snowflake connection for custom queries
        self.snowflake_conn = self._create_snowflake_connection()
        
        # Create a dictionary to map Snowflake tags to DataHub terms
        self.tag_to_term_mapping = {
            "PII": "urn:li:glossaryTerm:PII",
            "SENSITIVE": "urn:li:glossaryTerm:Sensitive",
            "CONFIDENTIAL": "urn:li:glossaryTerm:Confidential",
            "PUBLIC": "urn:li:glossaryTerm:Public",
            "GDPR": "urn:li:glossaryTerm:GDPR",
            "PCI": "urn:li:glossaryTerm:PCI",
            "HIPAA": "urn:li:glossaryTerm:HIPAA",
        }
    
    def _create_snowflake_connection(self):
        """Create a direct connection to Snowflake."""
        try:
            conn = snowflake.connector.connect(
                user=self.username,
                password=self.password,
                account=self.account_id,
                warehouse=self.warehouse,
                role=self.role,
            )
            return conn
        except Exception as e:
            logger.error(f"Failed to connect to Snowflake: {e}")
            sys.exit(1)
    
    def get_custom_table_properties(self, database: str, schema: str) -> Dict[str, Dict[str, Any]]:
        """Get custom table properties directly from Snowflake."""
        try:
            cursor = self.snowflake_conn.cursor()
            
            query = f"""
            SELECT 
                TABLE_NAME,
                ROW_COUNT,
                BYTES,
                CREATED,
                LAST_ALTERED,
                COMMENT,
                TABLE_TYPE
            FROM {database}.INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = '{schema}'
            """
            
            cursor.execute(query)
            
            table_properties = {}
            for row in cursor:
                table_name, row_count, bytes_size, created, last_altered, comment, table_type = row
                
                full_name = f"{database}.{schema}.{table_name}"
                table_properties[full_name] = {
                    "row_count": row_count,
                    "bytes": bytes_size,
                    "created": created.isoformat() if created else None,
                    "last_altered": last_altered.isoformat() if last_altered else None,
                    "comment": comment,
                    "table_type": table_type,
                }
            
            return table_properties
        except Exception as e:
            logger.error(f"Failed to get table properties for {database}.{schema}: {e}")
            return {}
    
    def get_custom_tags(self, database: str, schema: str) -> Dict[str, List[str]]:
        """Get custom tags directly from Snowflake."""
        try:
            cursor = self.snowflake_conn.cursor()
            
            query = f"""
            SELECT 
                t.TABLE_NAME,
                tag.TAG_NAME
            FROM {database}.INFORMATION_SCHEMA.TABLES t
            JOIN TABLE({database}.INFORMATION_SCHEMA.TAG_REFERENCES('{database}.{schema}', 'TABLE')) tag
                ON tag.OBJECT_NAME = t.TABLE_NAME
            WHERE t.TABLE_SCHEMA = '{schema}'
            """
            
            try:
                cursor.execute(query)
                
                table_tags = {}
                for row in cursor:
                    table_name, tag_name = row
                    
                    full_name = f"{database}.{schema}.{table_name}"
                    if full_name not in table_tags:
                        table_tags[full_name] = []
                    
                    table_tags[full_name].append(tag_name)
                
                return table_tags
            except snowflake.connector.errors.ProgrammingError as e:
                if "Object 'TAG_REFERENCES' does not exist or not authorized" in str(e):
                    logger.warning(f"Tag references not available for {database}.{schema}. Skipping...")
                    return {}
                raise
        except Exception as e:
            logger.error(f"Failed to get tags for {database}.{schema}: {e}")
            return {}
    
    def create_standard_ingestion_pipeline(self) -> Dict[str, Any]:
        """Create the standard DataHub ingestion configuration."""
        return {
            "source": {
                "type": "snowflake",
                "config": {
                    "account_id": self.account_id,
                    "username": self.username,
                    "password": self.password,
                    "warehouse": self.warehouse,
                    "role": self.role,
                    
                    "database_pattern": {
                        "allow": self.database_pattern,
                        "deny": [
                            "^SNOWFLAKE$",
                            "^SNOWFLAKE_SAMPLE_DATA$"
                        ]
                    },
                    
                    "include_tables": True,
                    "include_views": True,
                    "include_table_lineage": True,
                    "include_column_lineage": True,
                    "include_usage_stats": True,
                    "extract_tags": "without_lineage",
                }
            },
            "sink": {
                "type": "datahub-rest",
                "config": {
                    "server": self.datahub_gms_url
                }
            },
            "pipeline_name": "enhanced_snowflake_ingestion"
        }
    
    def create_glossary_term_mappings(self, table_tags: Dict[str, List[str]]) -> List[MetadataChangeProposalWrapper]:
        """Create glossary term mappings for tagged tables."""
        mcps = []
        
        for full_table_name, tags in table_tags.items():
            # Parse the full table name
            parts = full_table_name.split(".")
            if len(parts) != 3:
                continue
            
            database, schema, table = parts
            
            # Create the dataset URN
            dataset_urn = f"urn:li:dataset:(urn:li:dataPlatform:snowflake,{database}.{schema}.{table},PROD)"
            
            # Map tags to glossary terms
            term_urns = []
            for tag in tags:
                if tag in self.tag_to_term_mapping:
                    term_urns.append(self.tag_to_term_mapping[tag])
            
            if term_urns:
                glossary_terms = GlossaryTermsClass(
                    terms=[
                        GlossaryTermAssociationClass(urn=term_urn) 
                        for term_urn in term_urns
                    ]
                )
                
                mcp = MetadataChangeProposalWrapper(
                    entityUrn=dataset_urn,
                    aspect=glossary_terms,
                )
                mcps.append(mcp)
        
        return mcps
    
    def run_enhanced_ingestion(self):
        """Run the enhanced Snowflake ingestion process."""
        logger.info("Starting enhanced Snowflake ingestion")
        
        # First, run the standard DataHub ingestion
        config = self.create_standard_ingestion_pipeline()
        
        logger.info("Running standard DataHub ingestion")
        pipeline = Pipeline.create(config)
        pipeline.run()
        standard_report = pipeline.get_report()
        
        logger.info(f"Standard ingestion completed: {standard_report.ingestion_summary()}")
        
        # Now, enhance with custom metadata
        for database in self.database_pattern:
            # Remove regex patterns
            clean_db = database.replace("^", "").replace("$", "")
            
            # Get schemas in the database
            cursor = self.snowflake_conn.cursor()
            cursor.execute(f"SHOW SCHEMAS IN DATABASE {clean_db}")
            
            schemas = [row[1] for row in cursor if row[1] not in ("INFORMATION_SCHEMA")]
            
            for schema in schemas:
                logger.info(f"Processing custom metadata for {clean_db}.{schema}")
                
                # Get custom table properties
                table_properties = self.get_custom_table_properties(clean_db, schema)
                
                # Get custom tags
                table_tags = self.get_custom_tags(clean_db, schema)
                
                # Create glossary term mappings
                if table_tags:
                    mcps = self.create_glossary_term_mappings(table_tags)
                    
                    # Emit these to DataHub
                    for mcp in mcps:
                        try:
                            headers = {"Content-Type": "application/json"}
                            response = requests.post(
                                f"{self.datahub_gms_url}/aspects?action=ingestProposal",
                                headers=headers,
                                data=mcp.serialize(),
                            )
                            if response.status_code != 200:
                                logger.error(f"Failed to ingest MCP: {response.text}")
                        except Exception as e:
                            logger.error(f"Error ingesting MCP: {e}")
        
        logger.info("Enhanced ingestion completed")

def main():
    parser = argparse.ArgumentParser(description="Enhanced DataHub Snowflake Ingestion")
    parser.add_argument("--account-id", required=True, help="Snowflake account identifier")
    parser.add_argument("--username", required=True, help="Snowflake username")
    parser.add_argument("--password", required=True, help="Snowflake password")
    parser.add_argument("--warehouse", required=True, help="Snowflake warehouse")
    parser.add_argument("--role", required=True, help="Snowflake role")
    parser.add_argument("--database", action="append", required=True, help="Snowflake databases to ingest")
    parser.add_argument("--datahub-gms-url", required=True, help="DataHub GMS URL")
    
    args = parser.parse_args()
    
    # For security, remove password from args when logging
    safe_args = vars(args).copy()
    safe_args["password"] = "****"
    logger.info(f"Starting enhanced ingestion with args: {safe_args}")
    
    ingestion = EnhancedSnowflakeIngestion(
        account_id=args.account_id,
        username=args.username,
        password=args.password,
        warehouse=args.warehouse,
        role=args.role,
        database_pattern=[f"^{db}$" for db in args.database],
        datahub_gms_url=args.datahub_gms_url,
    )
    
    ingestion.run_enhanced_ingestion()

if __name__ == "__main__":
    import requests  # Import here to avoid issues if the module is imported
    main()