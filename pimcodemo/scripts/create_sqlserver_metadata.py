#!/usr/bin/env python3
"""
PIMCO Municipal Bond Demo - SQL Server Metadata Creation Script
Creates SQL Server tables, stored procedures, Fivetran connector, and lineage in DataHub Cloud
"""

import os
import re
import yaml
from datetime import datetime
from typing import Dict, List, Any
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    DatasetPropertiesClass,
    DataProcessInfoClass,
    DataJobInfoClass,
    DataFlowInfoClass,
    DataJobInputOutputClass,
    OwnershipClass,
    OwnerClass,
    OwnershipTypeClass,
    GlobalTagsClass,
    TagAssociationClass,
    GlossaryTermsClass,
    GlossaryTermAssociationClass,
    DomainsClass,
    UpstreamLineageClass,
    UpstreamClass,
    DatasetLineageTypeClass,
    AuditStampClass,
    SchemaMetadataClass,
    SchemaFieldClass,
    SchemaFieldDataTypeClass,
    StringTypeClass,
)
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.mce_builder import (
    make_term_urn,
    make_tag_urn,
    make_domain_urn,
    make_dataset_urn,
    make_data_job_urn,
    make_data_flow_urn,
)


class SQLServerMetadataCreator:
    """Creates SQL Server metadata entities in DataHub Cloud"""
    
    def __init__(self, datahub_url: str, datahub_token: str):
        """Initialize DataHub emitter"""
        self.emitter = DatahubRestEmitter(gms_server=datahub_url, token=datahub_token)
        self.audit_stamp = AuditStampClass(
            time=int(datetime.now().timestamp() * 1000),
            actor="urn:li:corpuser:datahub"
        )
        
    def _normalize_urn_name(self, name: str) -> str:
        """Normalize name for URN"""
        normalized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        normalized = re.sub(r'_+', '_', normalized)
        normalized = normalized.strip('_')
        return normalized.lower()
    
    def _make_sqlserver_dataset_urn(self, database: str, schema: str, table: str) -> str:
        """Create dataset URN for SQL Server table"""
        database_lower = database.lower()
        schema_lower = schema.lower()
        table_lower = table.lower()
        return f"urn:li:dataset:(urn:li:dataPlatform:mssql,{database_lower}.{schema_lower}.{table_lower},PROD)"
    
    def _make_snowflake_dataset_urn(self, database: str, schema: str, table: str) -> str:
        """Create dataset URN for Snowflake table"""
        database_lower = database.lower()
        schema_lower = schema.lower()
        table_lower = table.lower()
        return f"urn:li:dataset:(urn:li:dataPlatform:snowflake,{database_lower}.{schema_lower}.{table_lower},PROD)"
    
    def _make_data_process_urn(self, name: str) -> str:
        """Create data process URN"""
        return f"urn:li:dataProcess:{self._normalize_urn_name(name)}"
    
    def _make_data_process_instance_urn(self, process_urn: str, instance_id: str = "1") -> str:
        """Create data process instance URN"""
        return f"{process_urn}.instance.{instance_id}"
    
    def create_staging_tables(self, staging_tables_file: str = None):
        """Create staging tables as DataHub datasets with columns"""
        if staging_tables_file is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            staging_tables_file = os.path.join(base_dir, 'datahub', 'sqlserver_staging_tables.yaml')
        
        with open(staging_tables_file, 'r') as f:
            config = yaml.safe_load(f)
        
        staging_tables = config.get('staging_tables', [])
        database = os.getenv('SQLSERVER_DATABASE', 'pimco_source').lower()
        
        print("\nCreating staging tables...")
        for table_config in staging_tables:
            table_name = table_config['table']
            schema = table_config.get('schema', 'dbo')
            full_name = f"{schema}.{table_name}"
            
            print(f"\nCreating staging table: {full_name}")
            
            # Create dataset URN
            dataset_urn = self._make_sqlserver_dataset_urn(database, schema, table_name)
            
            # Create dataset properties
            description = table_config.get('description', '').strip()
            properties = DatasetPropertiesClass(
                name=table_name,
                description=description,
                customProperties={},
            )
            
            event = MetadataChangeProposalWrapper(
                entityType="dataset",
                entityUrn=dataset_urn,
                aspect=properties,
            )
            self.emitter.emit(event)
            print(f"  Created staging table: {table_name}")
            
            # Create schema metadata (columns)
            if 'columns' in table_config and table_config['columns']:
                fields = []
                for idx, col_config in enumerate(table_config['columns']):
                    col_name = col_config['name']
                    col_description = col_config.get('description', '').strip()
                    col_data_type = col_config.get('data_type', 'VARCHAR(255)')
                    
                    # Create field path (fieldPath is required)
                    field_path = col_name
                    
                    # Create field type based on data type
                    # For simplicity, use StringTypeClass for all fields
                    # In production, you'd map data types appropriately
                    field = SchemaFieldClass(
                        fieldPath=field_path,
                        type=SchemaFieldDataTypeClass(type=StringTypeClass()),
                        nativeDataType=col_data_type,
                        description=col_description,
                        nullable=True,
                    )
                    fields.append(field)
                
                # Create platform schema
                # Note: platformSchema is required and must be a dict with schemaName and tableName
                schema_metadata = SchemaMetadataClass(
                    schemaName=table_name,
                    platform=f"urn:li:dataPlatform:mssql",
                    version=0,
                    hash="",
                    platformSchema={
                        "schemaName": schema,
                        "tableName": table_name,
                    },
                    fields=fields,
                )
                
                schema_event = MetadataChangeProposalWrapper(
                    entityType="dataset",
                    entityUrn=dataset_urn,
                    aspect=schema_metadata,
                )
                self.emitter.emit(schema_event)
                print(f"  Created {len(fields)} columns")
            
            # Apply tags
            if 'tags' in table_config:
                tags = []
                for tag_name in table_config['tags']:
                    tag_urn = make_tag_urn(self._normalize_urn_name(tag_name))
                    tags.append(TagAssociationClass(tag=tag_urn))
                
                if tags:
                    global_tags = GlobalTagsClass(tags=tags)
                    tag_event = MetadataChangeProposalWrapper(
                        entityUrn=dataset_urn,
                        aspect=global_tags,
                    )
                    self.emitter.emit(tag_event)
                    print(f"  Applied tags: {', '.join(table_config['tags'])}")
            
            # Apply glossary terms
            if 'glossary_terms' in table_config:
                terms = []
                for term_name in table_config['glossary_terms']:
                    term_urn = make_term_urn(self._normalize_urn_name(term_name))
                    terms.append(GlossaryTermAssociationClass(urn=term_urn))
                
                if terms:
                    glossary_terms = GlossaryTermsClass(terms=terms, auditStamp=self.audit_stamp)
                    term_event = MetadataChangeProposalWrapper(
                        entityUrn=dataset_urn,
                        aspect=glossary_terms,
                    )
                    self.emitter.emit(term_event)
                    print(f"  Applied glossary terms: {', '.join(table_config['glossary_terms'])}")
            
            # Apply domain
            if 'domain' in table_config:
                domain_name = table_config['domain']
                domain_urn = make_domain_urn(self._normalize_urn_name(domain_name))
                domains = DomainsClass(domains=[domain_urn])
                domain_event = MetadataChangeProposalWrapper(
                    entityUrn=dataset_urn,
                    aspect=domains,
                )
                self.emitter.emit(domain_event)
                print(f"  Applied domain: {domain_name}")
            
            # Apply ownership
            owner_name = table_config.get('owner', 'datahub')
            owner_urn = f"urn:li:corpuser:{owner_name}"
            ownership = OwnershipClass(
                owners=[
                    OwnerClass(
                        owner=owner_urn,
                        type=OwnershipTypeClass.DATAOWNER
                    )
                ]
            )
            ownership_event = MetadataChangeProposalWrapper(
                entityUrn=dataset_urn,
                aspect=ownership,
            )
            self.emitter.emit(ownership_event)
            print(f"  Applied ownership: {owner_name}")
    
    def create_sqlserver_tables(self, tables_file: str):
        """Create SQL Server tables as DataHub datasets"""
        with open(tables_file, 'r') as f:
            config = yaml.safe_load(f)
        
        tables = config.get('tables', [])
        database = os.getenv('SQLSERVER_DATABASE', 'pimco_source').lower()
        
        for table_config in tables:
            schema = table_config.get('schema', 'dbo')
            table = table_config.get('table')
            dataset_urn = self._make_sqlserver_dataset_urn(database, schema, table)
            
            print(f"\nCreating SQL Server table: {database}.{schema.lower()}.{table.lower()}")
            
            # Create dataset properties
            description = table_config.get('description', '').strip()
            dataset_properties = DatasetPropertiesClass(
                name=table,
                description=description,
            )
            
            event = MetadataChangeProposalWrapper(
                entityUrn=dataset_urn,
                aspect=dataset_properties,
            )
            self.emitter.emit(event)
            print(f"  Created table: {table}")
            
            # Apply tags
            if 'tags' in table_config:
                tags = []
                for tag_name in table_config['tags']:
                    tag_urn = make_tag_urn(self._normalize_urn_name(tag_name))
                    tags.append(TagAssociationClass(tag=tag_urn))
                
                if tags:
                    global_tags = GlobalTagsClass(tags=tags)
                    tag_event = MetadataChangeProposalWrapper(
                        entityUrn=dataset_urn,
                        aspect=global_tags,
                    )
                    self.emitter.emit(tag_event)
                    print(f"  Applied tags: {', '.join(table_config['tags'])}")
            
            # Apply glossary terms
            if 'glossary_terms' in table_config:
                terms = []
                for term_name in table_config['glossary_terms']:
                    term_urn = make_term_urn(self._normalize_urn_name(term_name))
                    terms.append(GlossaryTermAssociationClass(urn=term_urn))
                
                if terms:
                    glossary_terms = GlossaryTermsClass(terms=terms, auditStamp=self.audit_stamp)
                    term_event = MetadataChangeProposalWrapper(
                        entityUrn=dataset_urn,
                        aspect=glossary_terms,
                    )
                    self.emitter.emit(term_event)
                    print(f"  Applied glossary terms: {', '.join(table_config['glossary_terms'])}")
            
            # Apply domain
            if 'domain' in table_config:
                domain_name = table_config['domain']
                domain_urn = make_domain_urn(self._normalize_urn_name(domain_name))
                domains = DomainsClass(domains=[domain_urn])
                domain_event = MetadataChangeProposalWrapper(
                    entityUrn=dataset_urn,
                    aspect=domains,
                )
                self.emitter.emit(domain_event)
                print(f"  Applied domain: {domain_name}")
            
            # Apply ownership
            owner_name = table_config.get('owner', 'datahub')
            owner_urn = f"urn:li:corpuser:{owner_name}"
            ownership = OwnershipClass(
                owners=[
                    OwnerClass(
                        owner=owner_urn,
                        type=OwnershipTypeClass.DATAOWNER
                    )
                ]
            )
            ownership_event = MetadataChangeProposalWrapper(
                entityUrn=dataset_urn,
                aspect=ownership,
            )
            self.emitter.emit(ownership_event)
            print(f"  Applied ownership: {owner_name}")
    
    def create_stored_procedures(self, procedures_file: str):
        """Create stored procedures as DataHub data processes"""
        with open(procedures_file, 'r') as f:
            config = yaml.safe_load(f)
        
        procedures = config.get('stored_procedures', [])
        
        for proc_config in procedures:
            proc_name = proc_config.get('name')
            schema = proc_config.get('schema', 'dbo')
            full_name = f"{schema}.{proc_name}"
            process_urn = self._make_data_process_urn(full_name)
            
            print(f"\nCreating stored procedure: {full_name}")
            
            # Create input/output relationships
            input_tables = proc_config.get('input_tables', [])
            output_tables = proc_config.get('output_tables', [])
            target_table = proc_config.get('target_table')
            
            database = os.getenv('SQLSERVER_DATABASE', 'pimco_source').lower()
            
            # Build input/output URNs
            input_urns = []
            output_urns = []
            
            # Add input tables
            for input_table in input_tables:
                parts = input_table.split('.')
                if len(parts) == 2:
                    input_schema = parts[0]
                    input_table_name = parts[1]
                else:
                    input_schema = 'dbo'
                    input_table_name = input_table
                
                input_urn = self._make_sqlserver_dataset_urn(database, input_schema, input_table_name)
                input_urns.append(input_urn)
            
            # Add output/target tables (avoid duplicates)
            if target_table and target_table not in output_tables:
                output_tables = [target_table] + output_tables
            
            for output_table in output_tables:
                parts = output_table.split('.')
                if len(parts) == 2:
                    output_schema = parts[0]
                    output_table_name = parts[1]
                else:
                    output_schema = 'dbo'
                    output_table_name = output_table
                
                output_urn = self._make_sqlserver_dataset_urn(database, output_schema, output_table_name)
                output_urns.append(output_urn)
            
            # Create DataFlow and DataJob for stored procedure
            # This is how DataHub's connectors create lineage - using DataJob/DataFlow
            flow_urn = make_data_flow_urn(
                orchestrator="mssql",
                flow_id=f"sproc_{full_name}",
                cluster="PROD"
            )
            
            job_urn = make_data_job_urn(
                orchestrator="mssql",
                flow_id=f"sproc_{full_name}",
                job_id=full_name,
                cluster="PROD"
            )
            
            # Create DataFlowInfoClass
            flow_info = DataFlowInfoClass(
                name=full_name,
                description=proc_config.get('description', ''),
                customProperties={
                    'type': 'stored_procedure',
                    'schema': schema,
                },
            )
            
            flow_event = MetadataChangeProposalWrapper(
                entityType="dataFlow",
                entityUrn=flow_urn,
                aspect=flow_info,
            )
            self.emitter.emit(flow_event)
            print(f"  Created DataFlow: {flow_urn}")
            
            # Create DataJobInfoClass
            job_info = DataJobInfoClass(
                name=full_name,
                description=proc_config.get('description', ''),
                flowUrn=flow_urn,
                type="BATCH",
                env="PROD",
                customProperties={
                    'type': 'stored_procedure',
                    'schema': schema,
                },
            )
            
            job_event = MetadataChangeProposalWrapper(
                entityType="dataJob",
                entityUrn=job_urn,
                aspect=job_info,
            )
            self.emitter.emit(job_event)
            print(f"  Created DataJob: {job_urn}")
            
            # Create DataJobInputOutputClass to define inputs and outputs
            # This is how DataHub's connectors create lineage
            job_input_output = DataJobInputOutputClass(
                inputDatasets=input_urns,
                outputDatasets=output_urns,
            )
            
            job_io_event = MetadataChangeProposalWrapper(
                entityType="dataJob",
                entityUrn=job_urn,
                aspect=job_input_output,
            )
            self.emitter.emit(job_io_event)
            print(f"  Created DataJob inputs/outputs: {job_urn}")
            print(f"  Inputs: {', '.join(input_urns) if input_urns else 'None'}")
            print(f"  Outputs: {', '.join(output_urns) if output_urns else 'None'}")
            
            # Create explicit upstream lineage on SQL Server output tables pointing to staging tables
            # The DataJob with matching inputDatasets and outputDatasets will be visible in the path
            # This creates: Staging Tables → DataJob → Final SQL Server Tables
            for output_table in output_tables:
                parts = output_table.split('.')
                if len(parts) == 2:
                    output_schema = parts[0]
                    output_table_name = parts[1]
                else:
                    output_schema = 'dbo'
                    output_table_name = output_table
                
                output_urn = self._make_sqlserver_dataset_urn(database, output_schema, output_table_name)
                
                # Create upstream lineage on output table pointing to input staging tables
                # The DataJob with matching inputs/outputs will be visible in the path
                if input_urns:
                    upstreams = []
                    for input_urn in input_urns:
                        upstreams.append(
                            UpstreamClass(
                                dataset=input_urn,
                                type=DatasetLineageTypeClass.TRANSFORMED,
                            )
                        )
                    
                    upstream_lineage = UpstreamLineageClass(upstreams=upstreams)
                    lineage_event = MetadataChangeProposalWrapper(
                        entityUrn=output_urn,
                        aspect=upstream_lineage,
                    )
                    self.emitter.emit(lineage_event)
                    print(f"  Created lineage: Staging → {full_name} → {output_table}")
            
            # Apply tags to DataFlow and DataJob
            if 'tags' in proc_config:
                tags = []
                for tag_name in proc_config['tags']:
                    tag_urn = make_tag_urn(self._normalize_urn_name(tag_name))
                    tags.append(TagAssociationClass(tag=tag_urn))
                
                if tags:
                    global_tags = GlobalTagsClass(tags=tags)
                    # Apply tags to DataFlow
                    flow_tag_event = MetadataChangeProposalWrapper(
                        entityUrn=flow_urn,
                        aspect=global_tags,
                    )
                    self.emitter.emit(flow_tag_event)
                    # Apply tags to DataJob
                    job_tag_event = MetadataChangeProposalWrapper(
                        entityUrn=job_urn,
                        aspect=global_tags,
                    )
                    self.emitter.emit(job_tag_event)
                    print(f"  Applied tags: {', '.join(proc_config['tags'])}")
            
            # Apply domain to DataFlow and DataJob
            if 'domain' in proc_config:
                domain_name = proc_config['domain']
                domain_urn = make_domain_urn(self._normalize_urn_name(domain_name))
                domains = DomainsClass(domains=[domain_urn])
                # Apply domain to DataFlow
                flow_domain_event = MetadataChangeProposalWrapper(
                    entityUrn=flow_urn,
                    aspect=domains,
                )
                self.emitter.emit(flow_domain_event)
                # Apply domain to DataJob
                job_domain_event = MetadataChangeProposalWrapper(
                    entityUrn=job_urn,
                    aspect=domains,
                )
                self.emitter.emit(job_domain_event)
                print(f"  Applied domain: {domain_name}")
            
            # Apply ownership to DataFlow and DataJob
            owner_name = proc_config.get('owner', 'datahub')
            owner_urn = f"urn:li:corpuser:{owner_name}"
            ownership = OwnershipClass(
                owners=[
                    OwnerClass(
                        owner=owner_urn,
                        type=OwnershipTypeClass.DATAOWNER
                    )
                ]
            )
            # Apply ownership to DataFlow
            flow_ownership_event = MetadataChangeProposalWrapper(
                entityUrn=flow_urn,
                aspect=ownership,
            )
            self.emitter.emit(flow_ownership_event)
            # Apply ownership to DataJob
            job_ownership_event = MetadataChangeProposalWrapper(
                entityUrn=job_urn,
                aspect=ownership,
            )
            self.emitter.emit(job_ownership_event)
            print(f"  Applied ownership: {owner_name}")
    
    def create_fivetran_connector(self, connector_file: str):
        """Create Fivetran connector as DataHub data process"""
        with open(connector_file, 'r') as f:
            config = yaml.safe_load(f)
        
        connector_config = config.get('fivetran_connector', {})
        connector_name = connector_config.get('name')
        process_urn = self._make_data_process_urn(f"fivetran_{connector_name}")
        
        print(f"\nCreating Fivetran connector: {connector_name}")
        
        # Create input/output relationships and lineage
        table_mappings = connector_config.get('table_mappings', [])
        sqlserver_database = os.getenv('SQLSERVER_DATABASE', 'pimco_source').lower()
        snowflake_database = os.getenv('SNOWFLAKE_DATABASE', 'pimco_demo').lower()
        
        # Build input/output URNs
        input_urns = []
        output_urns = []
        
        for mapping in table_mappings:
            source_table = mapping.get('source_table')
            destination_table = mapping.get('destination_table')
            
            # Parse source table (SQL Server)
            source_parts = source_table.split('.')
            if len(source_parts) == 2:
                source_schema = source_parts[0]
                source_table_name = source_parts[1]
            else:
                source_schema = 'dbo'
                source_table_name = source_table
            
            source_urn = self._make_sqlserver_dataset_urn(sqlserver_database, source_schema, source_table_name)
            input_urns.append(source_urn)
            
            # Parse destination table (Snowflake)
            dest_parts = destination_table.split('.')
            if len(dest_parts) == 2:
                dest_schema = dest_parts[0]
                dest_table_name = dest_parts[1]
            else:
                dest_schema = 'BRZ_001'
                dest_table_name = destination_table
            
            dest_urn = self._make_snowflake_dataset_urn(snowflake_database, dest_schema, dest_table_name)
            output_urns.append(dest_urn)
            
            # Create explicit upstream lineage on Snowflake Bronze tables pointing to SQL Server tables
            # This makes the lineage visible in the dataset lineage view
            # DataHub will show the data processes (Fivetran) that connect them
            upstreams = [
                UpstreamClass(
                    dataset=source_urn,
                    type=DatasetLineageTypeClass.TRANSFORMED,
                )
            ]
            
            upstream_lineage = UpstreamLineageClass(upstreams=upstreams)
            lineage_event = MetadataChangeProposalWrapper(
                entityUrn=dest_urn,
                aspect=upstream_lineage,
            )
            self.emitter.emit(lineage_event)
            print(f"  Created lineage: {source_table} → {destination_table}")
        
        # Create DataFlow and DataJob for Fivetran connector
        # This is how DataHub's Fivetran connector actually creates lineage
        flow_urn = make_data_flow_urn(
            orchestrator="fivetran",
            flow_id=connector_name,
            cluster="PROD"
        )
        
        job_urn = make_data_job_urn(
            orchestrator="fivetran",
            flow_id=connector_name,
            job_id=connector_name,
            cluster="PROD"
        )
        
        # Create DataFlowInfoClass
        flow_info = DataFlowInfoClass(
            name=connector_name,
            description=connector_config.get('description', ''),
            customProperties={
                'source_platform': connector_config.get('source_platform', ''),
                'destination_platform': connector_config.get('destination_platform', ''),
                'sync_frequency': connector_config.get('sync_frequency', ''),
                'sync_mode': connector_config.get('sync_mode', ''),
            },
        )
        
        flow_event = MetadataChangeProposalWrapper(
            entityType="dataFlow",
            entityUrn=flow_urn,
            aspect=flow_info,
        )
        self.emitter.emit(flow_event)
        print(f"  Created DataFlow: {flow_urn}")
        
        # Create DataJobInfoClass
        job_info = DataJobInfoClass(
            name=connector_name,
            description=connector_config.get('description', ''),
            flowUrn=flow_urn,
            type="BATCH",
            env="PROD",
            customProperties={
                'source_platform': connector_config.get('source_platform', ''),
                'destination_platform': connector_config.get('destination_platform', ''),
                'sync_frequency': connector_config.get('sync_frequency', ''),
                'sync_mode': connector_config.get('sync_mode', ''),
            },
        )
        
        job_event = MetadataChangeProposalWrapper(
            entityType="dataJob",
            entityUrn=job_urn,
            aspect=job_info,
        )
        self.emitter.emit(job_event)
        print(f"  Created DataJob: {job_urn}")
        
        # Create DataJobInputOutputClass to define inputs and outputs
        # This is how DataHub's Fivetran connector creates lineage
        job_input_output = DataJobInputOutputClass(
            inputDatasets=input_urns,
            outputDatasets=output_urns,
        )
        
        job_io_event = MetadataChangeProposalWrapper(
            entityType="dataJob",
            entityUrn=job_urn,
            aspect=job_input_output,
        )
        self.emitter.emit(job_io_event)
        print(f"  Created DataJob inputs/outputs: {job_urn}")
        print(f"  Inputs: {', '.join(input_urns) if input_urns else 'None'}")
        print(f"  Outputs: {', '.join(output_urns) if output_urns else 'None'}")
        
        # Apply tags to DataFlow and DataJob
        if 'tags' in connector_config:
            tags = []
            for tag_name in connector_config['tags']:
                tag_urn = make_tag_urn(self._normalize_urn_name(tag_name))
                tags.append(TagAssociationClass(tag=tag_urn))
            
            if tags:
                global_tags = GlobalTagsClass(tags=tags)
                # Apply tags to DataFlow
                flow_tag_event = MetadataChangeProposalWrapper(
                    entityUrn=flow_urn,
                    aspect=global_tags,
                )
                self.emitter.emit(flow_tag_event)
                # Apply tags to DataJob
                job_tag_event = MetadataChangeProposalWrapper(
                    entityUrn=job_urn,
                    aspect=global_tags,
                )
                self.emitter.emit(job_tag_event)
                print(f"  Applied tags: {', '.join(connector_config['tags'])}")
        
        # Apply domain to DataFlow and DataJob
        if 'domain' in connector_config:
            domain_name = connector_config['domain']
            domain_urn = make_domain_urn(self._normalize_urn_name(domain_name))
            domains = DomainsClass(domains=[domain_urn])
            # Apply domain to DataFlow
            flow_domain_event = MetadataChangeProposalWrapper(
                entityUrn=flow_urn,
                aspect=domains,
            )
            self.emitter.emit(flow_domain_event)
            # Apply domain to DataJob
            job_domain_event = MetadataChangeProposalWrapper(
                entityUrn=job_urn,
                aspect=domains,
            )
            self.emitter.emit(job_domain_event)
            print(f"  Applied domain: {domain_name}")
        
        # Apply ownership to DataFlow and DataJob
        owner_name = connector_config.get('owner', 'datahub')
        owner_urn = f"urn:li:corpuser:{owner_name}"
        ownership = OwnershipClass(
            owners=[
                OwnerClass(
                    owner=owner_urn,
                    type=OwnershipTypeClass.DATAOWNER
                )
            ]
        )
        # Apply ownership to DataFlow
        flow_ownership_event = MetadataChangeProposalWrapper(
            entityUrn=flow_urn,
            aspect=ownership,
        )
        self.emitter.emit(flow_ownership_event)
        # Apply ownership to DataJob
        job_ownership_event = MetadataChangeProposalWrapper(
            entityUrn=job_urn,
            aspect=ownership,
        )
        self.emitter.emit(job_ownership_event)
        print(f"  Applied ownership: {owner_name}")


def main():
    """Main execution function"""
    # Get configuration from environment variables
    datahub_url = os.getenv('DATAHUB_GMS_URL', 'https://test-environment.acryl.io/gms')
    datahub_token = os.getenv('DATAHUB_PAT')
    
    if not datahub_token:
        raise ValueError("DATAHUB_PAT environment variable must be set")
    
    # Initialize creator
    creator = SQLServerMetadataCreator(datahub_url, datahub_token)
    
    # Get base directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Create staging tables FIRST (before stored procedures)
    # Pass the staging tables file path
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    staging_tables_file = os.path.join(base_dir, 'datahub', 'sqlserver_staging_tables.yaml')
    creator.create_staging_tables(staging_tables_file)
    
    # Create SQL Server tables
    print("\nCreating SQL Server tables...")
    tables_file = os.path.join(base_dir, 'datahub', 'sqlserver_tables.yaml')
    creator.create_sqlserver_tables(tables_file)
    
    # Create stored procedures
    print("\nCreating stored procedures...")
    procedures_file = os.path.join(base_dir, 'datahub', 'sqlserver_stored_procedures.yaml')
    creator.create_stored_procedures(procedures_file)
    
    # Create Fivetran connector
    print("\nCreating Fivetran connector...")
    connector_file = os.path.join(base_dir, 'datahub', 'fivetran_connector.yaml')
    creator.create_fivetran_connector(connector_file)
    
    # Flush all events
    print("\nFlushing events to ensure indexing...")
    creator.emitter.flush()
    
    print("\nSQL Server metadata creation complete!")


if __name__ == "__main__":
    main()

