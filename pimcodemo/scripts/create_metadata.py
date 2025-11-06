#!/usr/bin/env python3
"""
PIMCO Municipal Bond Demo - Metadata Creation Script
Creates glossary terms, tags, domains, and documentation in DataHub Cloud
"""

import os
import re
import time
import yaml
from typing import Dict, List, Any
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.mce_builder import make_term_urn, make_tag_urn, make_domain_urn
from datahub.metadata.schema_classes import (
    GlossaryTermInfoClass,
    GlossaryNodeInfoClass,
    TagPropertiesClass,
    DomainPropertiesClass,
    OwnershipClass,
    OwnerClass,
    OwnershipTypeClass,
    ChangeTypeClass,
    DatasetPropertiesClass,
    SchemaFieldClass,
    SchemaMetadataClass,
    DomainsClass,
    AuditStampClass,
)


class DataHubMetadataCreator:
    """Creates metadata entities in DataHub Cloud"""
    
    def __init__(self, datahub_url: str, datahub_token: str):
        """Initialize DataHub client"""
        self.emitter = DatahubRestEmitter(gms_server=datahub_url, token=datahub_token)
        self.audit_stamp = AuditStampClass(
            time=int(time.time() * 1000),
            actor="urn:li:corpuser:datahub",
        )
        
    def _normalize_urn_name(self, name: str) -> str:
        """Normalize name for URN (replace spaces, special chars)"""
        # Replace spaces and special characters with underscores
        normalized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        # Remove multiple underscores
        normalized = re.sub(r'_+', '_', normalized)
        # Remove leading/trailing underscores
        normalized = normalized.strip('_')
        # Convert to lowercase (DataHub convention)
        return normalized.lower()
        
    def create_glossary_terms(self, glossary_file: str):
        """Create glossary terms from YAML file"""
        with open(glossary_file, 'r') as f:
            config = yaml.safe_load(f)
            
        glossary_terms = config.get('glossary_terms', [])
        term_groups = config.get('term_groups', [])
        
        # Store term configs by name for later use when linking to groups
        term_configs_by_name = {}
        
        # Create individual glossary terms
        for term_config in glossary_terms:
            term_name = term_config['name']
            term_configs_by_name[term_name] = term_config
            term_urn = make_term_urn(self._normalize_urn_name(term_name))
            
            term_info = GlossaryTermInfoClass(
                name=term_name,
                definition=term_config.get('description', ''),
                termSource=term_config.get('term_source', 'MANUAL'),
                sourceRef=term_config.get('term_source_url', ''),
                customProperties=term_config.get('custom_properties', {}),
            )
            
            event = MetadataChangeProposalWrapper(
                entityUrn=term_urn,
                aspect=term_info,
            )
            
            self.emitter.emit(event)
            print(f"Created glossary term: {term_name}")
            
            # Add domain if specified
            if 'domain' in term_config:
                domain_name = term_config['domain']
                domain_urn = make_domain_urn(self._normalize_urn_name(domain_name))
                domains = DomainsClass(
                    domains=[domain_urn]
                )
                domain_proposal = MetadataChangeProposalWrapper(
                    entityUrn=term_urn,
                    aspect=domains,
                )
                self.emitter.emit(domain_proposal)
                print(f"  Assigned domain: {domain_name}")
            
            # Add ownership if specified
            if 'ownership' in term_config:
                for owner_config in term_config['ownership']:
                    owner_urn = f"urn:li:corpuser:{owner_config.get('id', 'datahub')}"
                    ownership = OwnershipClass(
                        owners=[
                            OwnerClass(
                                owner=owner_urn,
                                type=OwnershipTypeClass.DATAOWNER
                            )
                        ]
                    )
                    ownership_proposal = MetadataChangeProposalWrapper(
                        entityUrn=term_urn,
                        aspect=ownership,
                    )
                    self.emitter.emit(ownership_proposal)
            
        # Flush all term creation events before creating groups
        self.emitter.flush()
        print("Flushed all term creation events")
        
        # Create term groups as GlossaryNodes (not GlossaryTerms!)
        for group_config in term_groups:
            group_name = group_config['name']
            # Create GlossaryNode URN manually (format: urn:li:glossaryNode:name)
            group_urn = f"urn:li:glossaryNode:{self._normalize_urn_name(group_name)}"
            
            group_info = GlossaryNodeInfoClass(
                name=group_name,
                definition=group_config.get('description', ''),
            )
            
            event = MetadataChangeProposalWrapper(
                entityUrn=group_urn,
                aspect=group_info,
            )
            
            self.emitter.emit(event)
            self.emitter.flush()
            print(f"Created term group (GlossaryNode): {group_name}")
            
            # Link terms to group by setting parentNode on each child term
            for term_name in group_config.get('terms', []):
                if term_name not in term_configs_by_name:
                    print(f"  Warning: Term '{term_name}' not found in glossary terms, skipping")
                    continue
                    
                term_config = term_configs_by_name[term_name]
                term_urn = make_term_urn(self._normalize_urn_name(term_name))
                
                # Update term with parentNode pointing to GlossaryNode
                term_info_with_parent = GlossaryTermInfoClass(
                    name=term_name,
                    definition=term_config.get('description', ''),
                    termSource=term_config.get('term_source', 'MANUAL'),
                    sourceRef=term_config.get('term_source_url', ''),
                    customProperties=term_config.get('custom_properties', {}),
                    parentNode=group_urn,  # This is now a GlossaryNodeUrn
                )
                
                parent_event = MetadataChangeProposalWrapper(
                    entityUrn=term_urn,
                    aspect=term_info_with_parent,
                )
                
                self.emitter.emit(parent_event)
                print(f"  Linked term '{term_name}' to group '{group_name}'")
            
            # Flush after each group to ensure proper linking
            self.emitter.flush()
                
    def create_tags(self, tags_file: str):
        """Create tags from YAML file"""
        with open(tags_file, 'r') as f:
            config = yaml.safe_load(f)
            
        tags = config.get('tags', [])
        
        for tag_config in tags:
            tag_name = tag_config['name']
            tag_urn = f"urn:li:tag:{self._normalize_urn_name(tag_name)}"
            
            tag_properties = TagPropertiesClass(
                name=tag_name,
                description=tag_config.get('description', ''),
                colorHex=tag_config.get('color', '#000000'),
            )
            
            proposal = MetadataChangeProposalWrapper(
                entityType="tag",
                entityUrn=tag_urn,
                changeType=ChangeTypeClass.UPSERT,
                aspectName="tagProperties",
                aspect=tag_properties,
            )
            
            self.emitter.emit(proposal)
            print(f"Created tag: {tag_name}")
            
    def create_domains(self, domains_file: str):
        """Create domains from YAML file"""
        with open(domains_file, 'r') as f:
            config = yaml.safe_load(f)
            
        domains = config.get('domains', [])
        
        for domain_config in domains:
            domain_name = domain_config['name']
            domain_urn = f"urn:li:domain:{self._normalize_urn_name(domain_name)}"
            
            domain_properties = DomainPropertiesClass(
                name=domain_name,
                description=domain_config.get('description', ''),
                customProperties=domain_config.get('custom_properties', {}),
            )
            
            proposal = MetadataChangeProposalWrapper(
                entityType="domain",
                entityUrn=domain_urn,
                changeType=ChangeTypeClass.UPSERT,
                aspectName="domainProperties",
                aspect=domain_properties,
            )
            
            self.emitter.emit(proposal)
            print(f"Created domain: {domain_name}")
            
            # Add ownership if specified
            if 'ownership' in domain_config:
                for owner_config in domain_config['ownership']:
                    owner_urn = f"urn:li:corpuser:{owner_config.get('id', 'datahub')}"
                    ownership = OwnershipClass(
                        owners=[
                            OwnerClass(
                                owner=owner_urn,
                                type=OwnershipTypeClass.DATAOWNER
                            )
                        ]
                    )
                    ownership_proposal = MetadataChangeProposalWrapper(
                        entityType="domain",
                        entityUrn=domain_urn,
                        changeType=ChangeTypeClass.UPSERT,
                        aspectName="ownership",
                        aspect=ownership,
                    )
                    self.emitter.emit(ownership_proposal)
            
    def apply_documentation(self, table_mappings: Dict[str, Dict[str, str]]):
        """Apply documentation to Snowflake tables and columns"""
        # Table documentation mappings
        table_docs = {
            "BRZ_001.TX_0421": {
                "description": "Raw bond transaction data from trading systems. Contains trade date, settlement date, principal amount, and issuer/bond identifiers. This is the bronze layer raw data.",
                "columns": {
                    "TX_ID": "Unique transaction identifier",
                    "TD_DATE": "Trade date - when the bond trade was executed",
                    "STL_DATE": "Settlement date - when the trade settles",
                    "PRN_AMT": "Principal amount - the par value of bonds traded",
                    "ISS_ID": "Issuer identifier - links to issuer dimension",
                    "BND_ID": "Bond identifier - links to bond reference data",
                    "TRD_TYPE": "Trade type - BUY or SELL",
                    "CUSIP": "CUSIP identifier for the bond",
                }
            },
            "BRZ_001.REF_7832": {
                "description": "Reference data for municipal bonds. Contains bond characteristics like maturity date, coupon rate, credit rating, and issuer type.",
                "columns": {
                    "BND_ID": "Unique bond identifier",
                    "CUSIP": "CUSIP identifier",
                    "ISIN": "ISIN identifier",
                    "MAT_DATE": "Maturity date - when bond principal is repaid",
                    "CPN_RATE": "Coupon rate - annual interest rate as percentage",
                    "CR_RT": "Credit rating - bond issuer creditworthiness rating",
                    "ISS_TYPE": "Issuer type - classification of bond issuer",
                }
            },
            "BRZ_001.ISS_5510": {
                "description": "Issuer information for municipal bond issuers. Contains issuer name, type, state, and municipality details.",
                "columns": {
                    "ISS_ID": "Unique issuer identifier",
                    "ISS_NAME": "Issuer name - full name of the bond issuer",
                    "ISS_TYPE": "Issuer type - classification (municipal, state, authority, etc.)",
                    "STATE_CD": "State code - two-letter state abbreviation",
                    "MUN_NAME": "Municipality name - city or municipality name",
                }
            },
            "SLV_009.DIM_BND_001": {
                "description": "Cleaned bond dimension table. Contains standardized bond attributes including maturity date, coupon rate, credit rating, and segment classification.",
                "columns": {
                    "BND_ID": "Bond identifier",
                    "CUSIP": "CUSIP identifier",
                    "MATURITY_DATE": "Bond maturity date",
                    "COUPON_RATE": "Annual coupon rate as decimal",
                    "CREDIT_RATING": "Credit rating (AAA, AA+, AA, etc.)",
                    "SEGMENT_CD": "Segment code - TAX_EXEMPT, TAXABLE, or OTHER",
                }
            },
            "SLV_009.DIM_ISS_002": {
                "description": "Cleaned issuer dimension table. Contains standardized issuer information with region classification.",
                "columns": {
                    "ISS_ID": "Issuer identifier",
                    "ISSUER_NAME": "Standardized issuer name",
                    "ISSUER_TYPE": "Standardized issuer type",
                    "STATE_CODE": "Two-letter state code",
                    "REGION_CD": "Region code - WEST, NORTHEAST, SOUTH, MIDWEST, OTHER",
                }
            },
            "SLV_009.DIM_REG_003": {
                "description": "Region dimension table. Defines geographic regions for bond issuer analysis.",
                "columns": {
                    "REGION_CD": "Region code identifier",
                    "REGION_NAME": "Full region name",
                    "STATE_CODE": "Primary state code for region",
                }
            },
            "SLV_009.DIM_SEG_4421": {
                "description": "Segment dimension table. Defines bond segments (tax-exempt vs taxable) for portfolio analysis.",
                "columns": {
                    "SEGMENT_CD": "Segment code identifier",
                    "SEGMENT_NAME": "Full segment name",
                    "TAX_EXEMPT_FLAG": "1 if tax-exempt, 0 if taxable",
                }
            },
            "GLD_003.POS_9912": {
                "description": "Aggregated bond positions table. Contains total positions by bond, issuer, region, and segment with par value and market value. This is the primary table for position reporting.",
                "columns": {
                    "POS_ID": "Position identifier",
                    "BOND_ID": "Bond identifier",
                    "ISSUER_ID": "Issuer identifier",
                    "REGION_CD": "Region code",
                    "SEGMENT_CD": "Segment code (TAX_EXEMPT or TAXABLE)",
                    "PAR_VALUE": "Total par value of positions",
                    "MARKET_VALUE": "Total market value of positions",
                    "AS_OF_DATE": "As-of date for the position snapshot",
                }
            },
            "GLD_003.SEG_4421": {
                "description": "Segment aggregations table. Contains total positions aggregated by segment (tax-exempt vs taxable) for reporting.",
                "columns": {
                    "SEGMENT_CD": "Segment code",
                    "AS_OF_DATE": "As-of date",
                    "TOTAL_PAR_VALUE": "Total par value across all positions in segment",
                    "TOTAL_MARKET_VALUE": "Total market value across all positions in segment",
                    "POSITION_COUNT": "Number of distinct positions in segment",
                }
            },
            "GLD_003.REG_7733": {
                "description": "Region aggregations table. Contains total positions aggregated by geographic region for reporting.",
                "columns": {
                    "REGION_CD": "Region code",
                    "AS_OF_DATE": "As-of date",
                    "TOTAL_PAR_VALUE": "Total par value across all positions in region",
                    "TOTAL_MARKET_VALUE": "Total market value across all positions in region",
                    "POSITION_COUNT": "Number of distinct positions in region",
                }
            },
            "GLD_003.ISS_8844": {
                "description": "Issuer aggregations table. Contains total positions aggregated by issuer for reporting.",
                "columns": {
                    "ISSUER_ID": "Issuer identifier",
                    "AS_OF_DATE": "As-of date",
                    "TOTAL_PAR_VALUE": "Total par value across all positions for issuer",
                    "TOTAL_MARKET_VALUE": "Total market value across all positions for issuer",
                    "POSITION_COUNT": "Number of distinct positions for issuer",
                }
            },
            "GLD_003.GRO_5566": {
                "description": "Growth metrics table. Contains position growth metrics over time by segment and region, including value changes and percentage changes.",
                "columns": {
                    "METRIC_DATE": "Date for the metric",
                    "SEGMENT_CD": "Segment code",
                    "REGION_CD": "Region code",
                    "TOTAL_PAR_VALUE": "Total par value for date/segment/region",
                    "TOTAL_MARKET_VALUE": "Total market value for date/segment/region",
                    "VALUE_CHANGE": "Change in value from previous period",
                    "PCT_CHANGE": "Percentage change from previous period",
                }
            },
        }
        
        # Apply documentation to each table
        # Note: This requires the tables to be ingested first
        # The URN format is: urn:li:dataset:(urn:li:dataPlatform:snowflake,{database}.{schema}.{table},PROD)
        database = os.getenv('SNOWFLAKE_DATABASE', 'PIMCO_DEMO')
        
        for table_name, doc_config in table_docs.items():
            # Parse schema.table format
            parts = table_name.split('.')
            if len(parts) == 2:
                schema_name = parts[0]
                table_name_only = parts[1]
            else:
                schema_name = database
                table_name_only = table_name
                
            # Construct dataset URN
            dataset_urn = f"urn:li:dataset:(urn:li:dataPlatform:snowflake,{database}.{schema_name}.{table_name_only},PROD)"
            
            try:
                # Apply table description
                dataset_properties = DatasetPropertiesClass(
                    description=doc_config.get('description', ''),
                    name=table_name_only,
                )
                
                proposal = MetadataChangeProposalWrapper(
                    entityType="dataset",
                    entityUrn=dataset_urn,
                    changeType=ChangeTypeClass.UPSERT,
                    aspectName="datasetProperties",
                    aspect=dataset_properties,
                )
                
                self.emitter.emit(proposal)
                print(f"Applied documentation to {table_name}")
                
                # Note: Column documentation would require schema metadata updates
                # This is a placeholder for future enhancement
                
            except Exception as e:
                print(f"Warning: Could not apply documentation to {table_name}: {e}")
                print(f"  This may be because the table hasn't been ingested yet.")
                print(f"  Expected URN: {dataset_urn}")


def main():
    """Main execution function"""
    # Get configuration from environment variables
    datahub_url = os.getenv('DATAHUB_GMS_URL', 'https://datahub.pimco.com')
    datahub_token = os.getenv('DATAHUB_PAT')
    
    if not datahub_token:
        raise ValueError("DATAHUB_PAT environment variable must be set")
    
    # Initialize creator
    creator = DataHubMetadataCreator(datahub_url, datahub_token)
    
    # Get base directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Create glossary terms
    print("Creating glossary terms...")
    glossary_file = os.path.join(base_dir, 'datahub', 'glossary_terms.yaml')
    creator.create_glossary_terms(glossary_file)
    
    # Create tags
    print("\nCreating tags...")
    tags_file = os.path.join(base_dir, 'datahub', 'tags.yaml')
    creator.create_tags(tags_file)
    
    # Create domains
    print("\nCreating domains...")
    domains_file = os.path.join(base_dir, 'datahub', 'domains.yaml')
    creator.create_domains(domains_file)
    
    # Apply documentation
    print("\nApplying documentation...")
    creator.apply_documentation({})
    
    print("\nMetadata creation complete!")


if __name__ == "__main__":
    main()

