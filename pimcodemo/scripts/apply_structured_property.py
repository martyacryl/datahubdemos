#!/usr/bin/env python3
"""
PIMCO Municipal Bond Demo - Apply Structured Property Script
Applies "Authorized for Reporting" structured property to all gold assets
"""

import os
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.metadata.schema_classes import (
    StructuredPropertiesClass,
    StructuredPropertyValueAssignmentClass,
    ChangeTypeClass,
)

# Gold assets that should have "Yes" for "Authorized for Reporting"
GOLD_ASSETS = [
    "GLD_003.POS_9912",
    "GLD_003.SEG_4421",
    "GLD_003.REG_7733",
    "GLD_003.ISS_8844",
    "GLD_003.GRO_5566",
]

# Structured property URN (created previously)
STRUCTURED_PROPERTY_URN = "urn:li:structuredProperty:authorized_for_reporting"


def make_dataset_urn(database: str, schema: str, table: str) -> str:
    """Create dataset URN for Snowflake table"""
    database_lower = database.lower()
    schema_lower = schema.lower()
    table_lower = table.lower()
    return f"urn:li:dataset:(urn:li:dataPlatform:snowflake,{database_lower}.{schema_lower}.{table_lower},PROD)"


def apply_structured_property(
    emitter: DatahubRestEmitter,
    dataset_urn: str,
    property_urn: str,
    value: str,
    table_name: str,
):
    """Apply structured property to a dataset"""
    # Create structured property value assignment
    # values should be a list of strings/floats, not PropertyValueClass objects
    property_assignment = StructuredPropertyValueAssignmentClass(
        propertyUrn=property_urn,
        values=[value],  # Direct string value, not PropertyValueClass
    )
    
    # Create structured properties aspect
    structured_properties = StructuredPropertiesClass(
        properties=[property_assignment],
    )
    
    # Create and emit proposal
    proposal = MetadataChangeProposalWrapper(
        entityType="dataset",
        entityUrn=dataset_urn,
        changeType=ChangeTypeClass.UPSERT,
        aspectName="structuredProperties",
        aspect=structured_properties,
    )
    
    emitter.emit(proposal)
    print(f"✓ Applied '{value}' to {table_name}")


def main():
    """Main execution function"""
    # Get configuration from environment variables
    datahub_url = os.getenv('DATAHUB_GMS_URL', 'https://test-environment.acryl.io/gms')
    datahub_token = os.getenv('DATAHUB_PAT')
    
    if not datahub_token:
        raise ValueError("DATAHUB_PAT environment variable must be set")
    
    # Initialize emitter
    emitter = DatahubRestEmitter(gms_server=datahub_url, token=datahub_token)
    
    # Get database from environment
    database = os.getenv('SNOWFLAKE_DATABASE', 'PIMCO_DEMO')
    
    print("Applying 'Authorized for Reporting' structured property to gold assets...")
    print()
    
    # Apply "Yes" to all gold assets
    for table_name in GOLD_ASSETS:
        schema, table = table_name.split('.')
        dataset_urn = make_dataset_urn(database, schema, table)
        
        try:
            apply_structured_property(
                emitter=emitter,
                dataset_urn=dataset_urn,
                property_urn=STRUCTURED_PROPERTY_URN,
                value="Yes",
                table_name=table_name,
            )
        except Exception as e:
            print(f"✗ Error applying to {table_name}: {e}")
    
    # Flush all events
    emitter.flush()
    print()
    print("✓ Structured property application complete!")
    print()
    print("Applied 'Authorized for Reporting = Yes' to:")
    for table_name in GOLD_ASSETS:
        print(f"  - {table_name}")


if __name__ == "__main__":
    main()

