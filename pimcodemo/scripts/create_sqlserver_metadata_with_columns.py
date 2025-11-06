#!/usr/bin/env python3
"""
PIMCO Municipal Bond Demo - Create SQL Server Metadata with Columns and Column-Level Lineage
Creates SQL Server tables, stored procedures, and Fivetran metadata with full column-level lineage
"""

import os
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.metadata.schema_classes import (
    DatasetPropertiesClass,
    SchemaMetadataClass,
    SchemaFieldClass,
    SchemaFieldDataTypeClass,
    StringTypeClass,
    OtherSchemaClass,
    DataProcessInfoClass,
    UpstreamLineageClass,
    UpstreamClass,
    FineGrainedLineageClass,
    FineGrainedLineageDownstreamTypeClass,
    FineGrainedLineageUpstreamTypeClass,
    DatasetLineageTypeClass,
    ChangeTypeClass,
    AuditStampClass,
)
import time

# SQL Server database and schema
SQL_SERVER_DATABASE = "PIMCO_SOURCE"
SQL_SERVER_SCHEMA = "dbo"

# Snowflake database and schema
SNOWFLAKE_DATABASE = "PIMCO_DEMO"
SNOWFLAKE_SCHEMA = "BRZ_001"

# Fivetran connector name
FIVETRAN_CONNECTOR = "pimco_sqlserver_to_snowflake"

# Table mappings: SQL Server staging → SQL Server final → Snowflake Bronze
TABLE_MAPPINGS = {
    "TBL_0421": {
        "staging_tables": ["STG_0421_001", "STG_0421_002", "STG_0421_003"],
        "stored_procedures": ["SP_LOAD_TBL_0421_A", "SP_LOAD_TBL_0421_B"],
        "snowflake_table": "TX_0421",
        "columns": {
            "TX_ID": {"type": "VARCHAR(50)", "description": "Unique transaction identifier"},
            "TD_DATE": {"type": "DATE", "description": "Trade date - when the bond trade was executed"},
            "STL_DATE": {"type": "DATE", "description": "Settlement date - when the trade settles"},
            "PRN_AMT": {"type": "DECIMAL(18,2)", "description": "Principal amount - the par value of bonds traded"},
            "ISS_ID": {"type": "VARCHAR(50)", "description": "Issuer identifier - links to issuer dimension"},
            "BND_ID": {"type": "VARCHAR(50)", "description": "Bond identifier - links to bond reference data"},
            "TRD_TYPE": {"type": "VARCHAR(10)", "description": "Trade type - BUY or SELL"},
            "CUSIP": {"type": "VARCHAR(9)", "description": "CUSIP identifier for the bond"},
        }
    },
    "TBL_7832": {
        "staging_tables": ["STG_7832_001", "STG_7832_002", "STG_7832_003"],
        "stored_procedures": ["SP_LOAD_TBL_7832_A", "SP_LOAD_TBL_7832_B"],
        "snowflake_table": "REF_7832",
        "columns": {
            "BND_ID": {"type": "VARCHAR(50)", "description": "Unique bond identifier"},
            "CUSIP": {"type": "VARCHAR(9)", "description": "CUSIP identifier"},
            "ISIN": {"type": "VARCHAR(20)", "description": "ISIN identifier"},
            "MAT_DATE": {"type": "DATE", "description": "Maturity date - when bond principal is repaid"},
            "CPN_RATE": {"type": "DECIMAL(5,3)", "description": "Coupon rate - annual interest rate as percentage"},
            "CR_RT": {"type": "VARCHAR(5)", "description": "Credit rating - bond issuer creditworthiness rating"},
            "ISS_TYPE": {"type": "VARCHAR(50)", "description": "Issuer type - classification of bond issuer"},
        }
    },
    "TBL_5510": {
        "staging_tables": ["STG_5510_001", "STG_5510_002", "STG_5510_003"],
        "stored_procedures": ["SP_LOAD_TBL_5510_A", "SP_LOAD_TBL_5510_B"],
        "snowflake_table": "ISS_5510",
        "columns": {
            "ISS_ID": {"type": "VARCHAR(50)", "description": "Unique issuer identifier"},
            "ISS_NAME": {"type": "VARCHAR(200)", "description": "Issuer name - full name of the bond issuer"},
            "ISS_TYPE": {"type": "VARCHAR(50)", "description": "Issuer type - classification (municipal, state, authority, etc.)"},
            "STATE_CD": {"type": "VARCHAR(2)", "description": "State code - two-letter state abbreviation"},
            "MUN_NAME": {"type": "VARCHAR(100)", "description": "Municipality name - city or municipality name"},
        }
    }
}


def make_sqlserver_dataset_urn(database: str, schema: str, table: str) -> str:
    """Create dataset URN for SQL Server table"""
    # DataHub uses 'mssqlserver' as the platform identifier for SQL Server
    return f"urn:li:dataset:(urn:li:dataPlatform:mssqlserver,{database.lower()}.{schema.lower()}.{table.lower()},PROD)"


def make_snowflake_dataset_urn(database: str, schema: str, table: str) -> str:
    """Create dataset URN for Snowflake table"""
    return f"urn:li:dataset:(urn:li:dataPlatform:snowflake,{database.lower()}.{schema.lower()}.{table.lower()},PROD)"


def make_data_process_urn(process_name: str) -> str:
    """Create data process URN"""
    # DataHub uses 'mssqlserver' as the platform identifier for SQL Server
    return f"urn:li:dataProcess:(urn:li:dataPlatform:mssqlserver,{process_name.lower()},PROD)"


def make_fivetran_urn(connector_name: str) -> str:
    """Create Fivetran connector URN"""
    return f"urn:li:dataProcess:(urn:li:dataPlatform:fivetran,{connector_name.lower()},PROD)"


def create_schema_metadata(columns: dict) -> SchemaMetadataClass:
    """Create schema metadata with columns"""
    fields = []
    for col_name, col_info in columns.items():
        field = SchemaFieldClass(
            fieldPath=col_name,
            type=SchemaFieldDataTypeClass(type=StringTypeClass()),
            nativeDataType=col_info["type"],
            description=col_info["description"],
        )
        fields.append(field)
    
    return SchemaMetadataClass(
        schemaName="",
        platform="urn:li:dataPlatform:mssqlserver",
        version=0,
        hash="",
        platformSchema=OtherSchemaClass(rawSchema=""),
        fields=fields,
    )


def create_sqlserver_table_with_columns(
    emitter: DatahubRestEmitter,
    database: str,
    schema: str,
    table: str,
    columns: dict,
    description: str,
):
    """Create SQL Server table with schema metadata"""
    dataset_urn = make_sqlserver_dataset_urn(database, schema, table)
    
    # Create dataset properties
    dataset_properties = DatasetPropertiesClass(
        name=table,
        description=description,
    )
    
    proposal = MetadataChangeProposalWrapper(
        entityType="dataset",
        entityUrn=dataset_urn,
        changeType=ChangeTypeClass.UPSERT,
        aspectName="datasetProperties",
        aspect=dataset_properties,
    )
    emitter.emit(proposal)
    print(f"  Created table: {schema}.{table}")
    
    # Create schema metadata with columns
    schema_metadata = create_schema_metadata(columns)
    
    schema_proposal = MetadataChangeProposalWrapper(
        entityType="dataset",
        entityUrn=dataset_urn,
        changeType=ChangeTypeClass.UPSERT,
        aspectName="schemaMetadata",
        aspect=schema_metadata,
    )
    emitter.emit(schema_proposal)
    print(f"    Added {len(columns)} columns to {schema}.{table}")


def create_stored_procedure_with_lineage(
    emitter: DatahubRestEmitter,
    sp_name: str,
    input_tables: list,
    output_table: str,
    columns: dict,
    description: str,
):
    """Create stored procedure with column-level lineage"""
    sp_urn = make_data_process_urn(sp_name)
    
    # Create data process info with inputs and outputs
    input_urns = []
    for input_table in input_tables:
        input_urn = make_sqlserver_dataset_urn(SQL_SERVER_DATABASE, SQL_SERVER_SCHEMA, input_table)
        input_urns.append(input_urn)
    
    output_urn = make_sqlserver_dataset_urn(SQL_SERVER_DATABASE, SQL_SERVER_SCHEMA, output_table)
    
    process_info = DataProcessInfoClass(
        inputs=input_urns,
        outputs=[output_urn],
    )
    
    proposal = MetadataChangeProposalWrapper(
        entityType="dataProcess",
        entityUrn=sp_urn,
        changeType=ChangeTypeClass.UPSERT,
        aspectName="dataProcessInfo",
        aspect=process_info,
    )
    emitter.emit(proposal)
    print(f"  Created stored procedure: {sp_name} ({description})")
    
    # Create upstream lineage for output table with column-level lineage
    output_urn = make_sqlserver_dataset_urn(SQL_SERVER_DATABASE, SQL_SERVER_SCHEMA, output_table)
    
    # Create fine-grained lineage for each column
    fine_grained_lineages = []
    for col_name in columns.keys():
        # Map column from input tables to output table
        upstream_cols = []
        for input_table in input_tables:
            input_urn = make_sqlserver_dataset_urn(SQL_SERVER_DATABASE, SQL_SERVER_SCHEMA, input_table)
            upstream_cols.append(f"{input_urn}#{col_name}")
        
        downstream_col = f"{output_urn}#{col_name}"
        
        fine_grained_lineage = FineGrainedLineageClass(
            upstreamType=FineGrainedLineageUpstreamTypeClass.FIELD_SET,
            upstreams=upstream_cols,
            downstreamType=FineGrainedLineageDownstreamTypeClass.FIELD,
            downstreams=[downstream_col],
            confidenceScore=1.0,
            transformOperation="COPY",
        )
        fine_grained_lineages.append(fine_grained_lineage)
    
    # Create upstream lineage with fine-grained lineage
    upstreams = []
    for input_table in input_tables:
        input_urn = make_sqlserver_dataset_urn(SQL_SERVER_DATABASE, SQL_SERVER_SCHEMA, input_table)
        upstreams.append(
            UpstreamClass(
                dataset=input_urn,
                type=DatasetLineageTypeClass.TRANSFORMED,
                auditStamp=AuditStampClass(
                    time=int(time.time() * 1000),
                    actor="urn:li:corpuser:datahub",
                ),
            )
        )
    
    lineage = UpstreamLineageClass(
        upstreams=upstreams,
        fineGrainedLineages=fine_grained_lineages,
    )
    
    lineage_proposal = MetadataChangeProposalWrapper(
        entityType="dataset",
        entityUrn=output_urn,
        changeType=ChangeTypeClass.UPSERT,
        aspectName="upstreamLineage",
        aspect=lineage,
    )
    emitter.emit(lineage_proposal)
    print(f"    Created column-level lineage: {input_tables} → {output_table}")


def create_fivetran_with_lineage(
    emitter: DatahubRestEmitter,
    connector_name: str,
    sqlserver_table: str,
    snowflake_table: str,
    columns: dict,
    description: str,
):
    """Create Fivetran connector with column-level lineage"""
    fivetran_urn = make_fivetran_urn(connector_name)
    
    # Create data process info with inputs and outputs
    sqlserver_urn = make_sqlserver_dataset_urn(SQL_SERVER_DATABASE, SQL_SERVER_SCHEMA, sqlserver_table)
    snowflake_urn = make_snowflake_dataset_urn(SNOWFLAKE_DATABASE, SNOWFLAKE_SCHEMA, snowflake_table)
    
    process_info = DataProcessInfoClass(
        inputs=[sqlserver_urn],
        outputs=[snowflake_urn],
    )
    
    proposal = MetadataChangeProposalWrapper(
        entityType="dataProcess",
        entityUrn=fivetran_urn,
        changeType=ChangeTypeClass.UPSERT,
        aspectName="dataProcessInfo",
        aspect=process_info,
    )
    emitter.emit(proposal)
    print(f"  Created Fivetran connector: {connector_name} ({description})")
    
    # Create upstream lineage for Snowflake table with column-level lineage
    # (sqlserver_urn and snowflake_urn already created above)
    
    # Create fine-grained lineage for each column
    fine_grained_lineages = []
    for col_name in columns.keys():
        upstream_col = f"{sqlserver_urn}#{col_name}"
        downstream_col = f"{snowflake_urn}#{col_name}"
        
        fine_grained_lineage = FineGrainedLineageClass(
            upstreamType=FineGrainedLineageUpstreamTypeClass.FIELD_SET,
            upstreams=[upstream_col],
            downstreamType=FineGrainedLineageDownstreamTypeClass.FIELD,
            downstreams=[downstream_col],
            confidenceScore=1.0,
            transformOperation="COPY",
        )
        fine_grained_lineages.append(fine_grained_lineage)
    
    upstreams = [
        UpstreamClass(
            dataset=sqlserver_urn,
            type=DatasetLineageTypeClass.TRANSFORMED,
            auditStamp=AuditStampClass(
                time=int(time.time() * 1000),
                actor="urn:li:corpuser:datahub",
            ),
        )
    ]
    
    lineage = UpstreamLineageClass(
        upstreams=upstreams,
        fineGrainedLineages=fine_grained_lineages,
    )
    
    lineage_proposal = MetadataChangeProposalWrapper(
        entityType="dataset",
        entityUrn=snowflake_urn,
        changeType=ChangeTypeClass.UPSERT,
        aspectName="upstreamLineage",
        aspect=lineage,
    )
    emitter.emit(lineage_proposal)
    print(f"    Created column-level lineage: {SQL_SERVER_SCHEMA}.{sqlserver_table} → {SNOWFLAKE_SCHEMA}.{snowflake_table}")


def main():
    """Main execution function"""
    datahub_url = os.getenv('DATAHUB_GMS_URL', 'https://test-environment.acryl.io/gms')
    datahub_token = os.getenv('DATAHUB_PAT')
    
    if not datahub_token:
        raise ValueError("DATAHUB_PAT environment variable must be set")
    
    emitter = DatahubRestEmitter(gms_server=datahub_url, token=datahub_token)
    
    print("Creating SQL Server metadata with columns and column-level lineage...")
    print()
    
    for final_table, config in TABLE_MAPPINGS.items():
        print(f"Processing {final_table}...")
        
        # Create staging tables with columns
        for staging_table in config["staging_tables"]:
            create_sqlserver_table_with_columns(
                emitter=emitter,
                database=SQL_SERVER_DATABASE,
                schema=SQL_SERVER_SCHEMA,
                table=staging_table,
                columns=config["columns"],
                description=f"Staging table for {final_table}",
            )
        
        # Create final SQL Server table with columns
        create_sqlserver_table_with_columns(
            emitter=emitter,
            database=SQL_SERVER_DATABASE,
            schema=SQL_SERVER_SCHEMA,
            table=final_table,
            columns=config["columns"],
            description=f"Final SQL Server table for {config['snowflake_table']}",
        )
        
        # Create stored procedures with lineage
        for i, sp_name in enumerate(config["stored_procedures"]):
            # Each stored procedure loads from 2 staging tables
            input_tables = config["staging_tables"][i*2:(i+1)*2]
            create_stored_procedure_with_lineage(
                emitter=emitter,
                sp_name=sp_name,
                input_tables=input_tables,
                output_table=final_table,
                columns=config["columns"],
                description=f"Stored procedure to load {final_table} from staging tables",
            )
        
        # Create Fivetran connector with lineage
        create_fivetran_with_lineage(
            emitter=emitter,
            connector_name=f"{FIVETRAN_CONNECTOR}_{final_table.lower()}",
            sqlserver_table=final_table,
            snowflake_table=config["snowflake_table"],
            columns=config["columns"],
            description=f"Fivetran connector from {final_table} to {config['snowflake_table']}",
        )
        
        print()
    
    # Flush all events
    emitter.flush()
    print("✓ SQL Server metadata creation complete!")
    print()
    print("Created:")
    print("  - Staging tables with columns")
    print("  - Final SQL Server tables with columns")
    print("  - Stored procedures with lineage")
    print("  - Fivetran connectors with lineage")
    print()
    print("Column-level lineage flow:")
    print("  SQL Server Staging → Stored Procedures → SQL Server Final → Fivetran → Snowflake Bronze")


if __name__ == "__main__":
    main()

