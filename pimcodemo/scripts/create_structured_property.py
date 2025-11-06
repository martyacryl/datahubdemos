#!/usr/bin/env python3
"""
PIMCO Municipal Bond Demo - Apply Structured Property to Gold Schema Views
Applies "Authorized for Reporting" structured property to datasets

NOTE: The structured property must be created in the DataHub UI first:
1. Go to Govern > Structured Properties
2. Click + Create
3. Set:
   - Name: Authorized for Reporting
   - Qualified Name: authorized_for_reporting
   - Description: Indicates whether a dataset is authorized for use in reporting
   - Property Type: Text
   - Allowed Values: Yes, No
   - Applies To: Dataset
4. Save the property

Then run this script to apply the property values to datasets.
"""

import os
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.metadata.schema_classes import (
    StructuredPropertiesClass,
    StructuredPropertyValueAssignmentClass,
    PropertyValueClass,
)


def apply_structured_property_to_dataset(
    emitter: DatahubRestEmitter,
    dataset_urn: str,
    property_urn: str,
    value: str,
):
    """Apply structured property value to a dataset"""
    # Create structured property value assignment
    # Note: values should be a list of strings/floats, not PropertyValueClass objects
    property_assignment = StructuredPropertyValueAssignmentClass(
        propertyUrn=property_urn,
        values=[value],  # Direct string value, not PropertyValueClass
    )
    
    # Create structured properties aspect
    # Note: properties should be a list of StructuredPropertyValueAssignmentClass objects
    structured_properties = StructuredPropertiesClass(
        properties=[property_assignment],
    )
    
    event = MetadataChangeProposalWrapper(
        entityType="dataset",
        entityUrn=dataset_urn,
        aspect=structured_properties,
    )
    
    emitter.emit(event)
    print(f"  Applied '{value}' to {dataset_urn}")


def apply_to_all_datasets(datahub_url: str, datahub_token: str, property_urn: str):
    """Apply structured property to all datasets"""
    emitter = DatahubRestEmitter(gms_server=datahub_url, token=datahub_token)
    
    database = os.getenv('SNOWFLAKE_DATABASE', 'PIMCO_DEMO').lower()
    
    # Gold schema views - should have "Yes"
    gold_views = [
        "GLD_003.POS_9912",
        "GLD_003.SEG_4421",
        "GLD_003.REG_7733",
        "GLD_003.ISS_8844",
        "GLD_003.GRO_5566",
    ]
    
    # Silver schema views - should have "No"
    silver_views = [
        "SLV_009.TXN_7821",
        "SLV_009.DIM_BND_001",
        "SLV_009.DIM_ISS_002",
    ]
    
    # Bronze schema tables - should have "No"
    bronze_tables = [
        "BRZ_001.TX_0421",
        "BRZ_001.REF_7832",
        "BRZ_001.ISS_5510",
    ]
    
    # Silver schema static tables - should have "No"
    silver_tables = [
        "SLV_009.DIM_REG_003",
        "SLV_009.DIM_SEG_4421",
    ]
    
    print("\nApplying structured property to Gold schema views (Yes)...")
    for view_name in gold_views:
        parts = view_name.split('.')
        schema_name = parts[0].lower()
        table_name = parts[1].lower()
        dataset_urn = f"urn:li:dataset:(urn:li:dataPlatform:snowflake,{database}.{schema_name}.{table_name},PROD)"
        apply_structured_property_to_dataset(emitter, dataset_urn, property_urn, "Yes")
    
    print("\nApplying structured property to Silver schema views (No)...")
    for view_name in silver_views:
        parts = view_name.split('.')
        schema_name = parts[0].lower()
        table_name = parts[1].lower()
        dataset_urn = f"urn:li:dataset:(urn:li:dataPlatform:snowflake,{database}.{schema_name}.{table_name},PROD)"
        apply_structured_property_to_dataset(emitter, dataset_urn, property_urn, "No")
    
    print("\nApplying structured property to Bronze schema tables (No)...")
    for table_name in bronze_tables:
        parts = table_name.split('.')
        schema_name = parts[0].lower()
        table_name_only = parts[1].lower()
        dataset_urn = f"urn:li:dataset:(urn:li:dataPlatform:snowflake,{database}.{schema_name}.{table_name_only},PROD)"
        apply_structured_property_to_dataset(emitter, dataset_urn, property_urn, "No")
    
    print("\nApplying structured property to Silver schema tables (No)...")
    for table_name in silver_tables:
        parts = table_name.split('.')
        schema_name = parts[0].lower()
        table_name_only = parts[1].lower()
        dataset_urn = f"urn:li:dataset:(urn:li:dataPlatform:snowflake,{database}.{schema_name}.{table_name_only},PROD)"
        apply_structured_property_to_dataset(emitter, dataset_urn, property_urn, "No")
    
    emitter.flush()
    print("\nStructured property application complete!")


def main():
    """Main execution function"""
    datahub_url = os.getenv('DATAHUB_GMS_URL', 'https://test-environment.acryl.io/gms')
    datahub_token = os.getenv('DATAHUB_PAT')
    
    if not datahub_token:
        raise ValueError("DATAHUB_PAT environment variable must be set")
    
    # Property URN - must match the qualified name created in UI
    # If you created it with qualified name "authorized_for_reporting", use this URN
    property_urn = "urn:li:structuredProperty:authorized_for_reporting"
    
    print("Applying structured property to all datasets...")
    print(f"Using property URN: {property_urn}")
    print("NOTE: If the property doesn't exist, create it in the DataHub UI first.")
    print("      See the script header for instructions.\n")
    
    apply_to_all_datasets(datahub_url, datahub_token, property_urn)
    
    print("\nDone!")


if __name__ == "__main__":
    main()

