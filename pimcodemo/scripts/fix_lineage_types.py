#!/usr/bin/env python3
"""
PIMCO Municipal Bond Demo - Fix Lineage Types
Updates lineage types from VIEW to TRANSFORMED for proper UI display
"""

import os
import time
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.metadata.schema_classes import (
    UpstreamLineageClass,
    UpstreamClass,
    DatasetLineageTypeClass,
    AuditStampClass,
    ChangeTypeClass,
)
from datahub.ingestion.graph.client import DataHubGraph, DatahubClientConfig

# Lineage mappings: Silver Dynamic Tables → Bronze Tables
LINEAGE_MAPPINGS = {
    "SLV_009.DT_TXN_7821": ["BRZ_001.TX_0421"],
    "SLV_009.DT_DIM_BND_001": ["BRZ_001.REF_7832", "BRZ_001.ISS_5510"],
    "SLV_009.DT_DIM_ISS_002": ["BRZ_001.ISS_5510"],
}

DATABASE = "PIMCO_DEMO"


def make_dataset_urn(database: str, schema: str, table: str) -> str:
    """Create dataset URN for Snowflake table"""
    return f"urn:li:dataset:(urn:li:dataPlatform:snowflake,{database.lower()}.{schema.lower()}.{table.lower()},PROD)"


def fix_lineage_type(
    emitter: DatahubRestEmitter,
    graph: DataHubGraph,
    target_urn: str,
    source_urns: list,
):
    """Fix lineage type to TRANSFORMED"""
    try:
        # Get existing lineage
        existing_lineage = graph.get_aspect(target_urn, UpstreamLineageClass)
        
        # Create new upstreams with TRANSFORMED type
        upstreams = []
        for source_urn in source_urns:
            upstreams.append(
                UpstreamClass(
                    dataset=source_urn,
                    type=DatasetLineageTypeClass.TRANSFORMED,
                    auditStamp=AuditStampClass(
                        time=int(time.time() * 1000),
                        actor="urn:li:corpuser:datahub",
                    ),
                )
            )
        
        # Create new lineage
        lineage = UpstreamLineageClass(upstreams=upstreams)
        
        # Preserve fine-grained lineage if it exists
        if existing_lineage and existing_lineage.fineGrainedLineages:
            lineage.fineGrainedLineages = existing_lineage.fineGrainedLineages
        
        # Emit the update
        proposal = MetadataChangeProposalWrapper(
            entityType="dataset",
            entityUrn=target_urn,
            changeType=ChangeTypeClass.UPSERT,
            aspectName="upstreamLineage",
            aspect=lineage,
        )
        
        emitter.emit(proposal)
        print(f"  ✓ Fixed lineage type for {target_urn.split('.')[-1].split(',')[0]}")
        
    except Exception as e:
        print(f"  ✗ Error fixing lineage for {target_urn}: {e}")


def main():
    """Main execution function"""
    datahub_url = os.getenv('DATAHUB_GMS_URL', 'https://test-environment.acryl.io/gms')
    datahub_token = os.getenv('DATAHUB_PAT')
    
    if not datahub_token:
        raise ValueError("DATAHUB_PAT environment variable must be set")
    
    emitter = DatahubRestEmitter(gms_server=datahub_url, token=datahub_token)
    graph = DataHubGraph(
        config=DatahubClientConfig(
            server=datahub_url,
            token=datahub_token,
        )
    )
    
    print("Fixing lineage types from VIEW to TRANSFORMED...")
    print()
    
    for target_table, source_tables in LINEAGE_MAPPINGS.items():
        schema, table = target_table.split('.')
        target_urn = make_dataset_urn(DATABASE, schema, table)
        
        source_urns = []
        for source_table in source_tables:
            source_schema, source_table_name = source_table.split('.')
            source_urn = make_dataset_urn(DATABASE, source_schema, source_table_name)
            source_urns.append(source_urn)
        
        print(f"Fixing {target_table}...")
        fix_lineage_type(emitter, graph, target_urn, source_urns)
    
    # Flush all events
    emitter.flush()
    print()
    print("✓ Lineage type fixes complete!")


if __name__ == "__main__":
    main()

