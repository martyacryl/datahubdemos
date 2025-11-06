#!/usr/bin/env python3
"""
Delete old stored procedures that don't match the new structure
Old ones: sp_LoadTBL_0421, sp_LoadTBL_7832, sp_LoadTBL_5510 (without _From1/_From2)
New ones: sp_LoadTBL_0421_From1, sp_LoadTBL_0421_From2, etc.
"""

import os
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.emitter.mce_builder import make_data_job_urn, make_data_flow_urn
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.metadata.schema_classes import StatusClass

def delete_old_stored_procedures():
    """Delete old stored procedures that don't match the new structure"""
    datahub_url = os.getenv('DATAHUB_GMS_URL', 'https://test-environment.acryl.io/gms')
    datahub_token = os.getenv('DATAHUB_PAT')
    
    if not datahub_token:
        raise ValueError("DATAHUB_PAT environment variable must be set")
    
    emitter = DatahubRestEmitter(gms_server=datahub_url, token=datahub_token)
    
    # Old stored procedure names (without _From1/_From2 suffix)
    old_procedures = [
        "sp_LoadTBL_0421",
        "sp_LoadTBL_7832",
        "sp_LoadTBL_5510",
    ]
    
    print("Deleting old stored procedures...")
    
    for proc_name in old_procedures:
        # Create URNs for old stored procedures
        flow_urn = make_data_flow_urn(
            orchestrator="mssql",
            flow_id=f"sproc_dbo.{proc_name}",
            cluster="PROD"
        )
        
        job_urn = make_data_job_urn(
            orchestrator="mssql",
            flow_id=f"sproc_dbo.{proc_name}",
            job_id=f"dbo.{proc_name}",
            cluster="PROD"
        )
        
        # Delete DataJob
        try:
            status = StatusClass(removed=True)
            job_delete_event = MetadataChangeProposalWrapper(
                entityType="dataJob",
                entityUrn=job_urn,
                aspect=status,
            )
            emitter.emit(job_delete_event)
            print(f"  Deleted DataJob: {job_urn}")
        except Exception as e:
            print(f"  Error deleting DataJob {job_urn}: {e}")
        
        # Delete DataFlow
        try:
            status = StatusClass(removed=True)
            flow_delete_event = MetadataChangeProposalWrapper(
                entityType="dataFlow",
                entityUrn=flow_urn,
                aspect=status,
            )
            emitter.emit(flow_delete_event)
            print(f"  Deleted DataFlow: {flow_urn}")
        except Exception as e:
            print(f"  Error deleting DataFlow {flow_urn}: {e}")
    
    emitter.flush()
    print("\nDeletion complete!")

if __name__ == "__main__":
    delete_old_stored_procedures()

