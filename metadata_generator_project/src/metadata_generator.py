import json
import uuid
from datetime import datetime

class MetadataGenerator:
   def __init__(self):
       self.metadata_records = []
       
       # Define domains and their tables
       self.domains = {
           "finance": {
               "database": "FinanceDB",
               "tables": [
                   {
                       "name": "general_ledger",
                       "description": "Chart of accounts and general ledger entries",
                       "columns": [
                           {"name": "account_id", "type": "INT", "description": "Unique account identifier"},
                           {"name": "account_name", "type": "VARCHAR(100)", "description": "Account name"},
                           {"name": "balance", "type": "DECIMAL(15,2)", "description": "Current account balance"},
                           {"name": "fiscal_year", "type": "INT", "description": "Fiscal year"}
                       ]
                   },
                   {
                       "name": "budget_allocations", 
                       "description": "Department budget allocations and spending",
                       "columns": [
                           {"name": "budget_id", "type": "INT", "description": "Unique budget identifier"},
                           {"name": "department_id", "type": "INT", "description": "Department identifier"},
                           {"name": "allocated_amount", "type": "DECIMAL(15,2)", "description": "Budget allocation"},
                           {"name": "spent_amount", "type": "DECIMAL(15,2)", "description": "Amount spent"}
                       ]
                   },
                   {
                       "name": "financial_reports",
                       "description": "Monthly and quarterly financial reports",
                       "columns": [
                           {"name": "report_id", "type": "INT", "description": "Unique report identifier"},
                           {"name": "report_date", "type": "DATE", "description": "Report generation date"},
                           {"name": "revenue", "type": "DECIMAL(15,2)", "description": "Total revenue"},
                           {"name": "expenses", "type": "DECIMAL(15,2)", "description": "Total expenses"}
                       ]
                   }
               ],
               "dashboards": [
                   {
                       "name": "Financial_Performance_Dashboard",
                       "display_name": "Financial Performance Dashboard", 
                       "description": "Comprehensive view of financial metrics and KPIs",
                       "upstream_tables": ["general_ledger", "financial_reports"]
                   },
                   {
                       "name": "Budget_Analysis_Dashboard",
                       "display_name": "Budget Analysis Dashboard",
                       "description": "Budget vs actual spending analysis",
                       "upstream_tables": ["budget_allocations", "general_ledger"]
                   }
               ]
           },
           "engineering": {
               "database": "EngineeringDB", 
               "tables": [
                   {
                       "name": "projects",
                       "description": "Engineering projects and their details",
                       "columns": [
                           {"name": "project_id", "type": "INT", "description": "Unique project identifier"},
                           {"name": "project_name", "type": "VARCHAR(100)", "description": "Project name"},
                           {"name": "status", "type": "VARCHAR(20)", "description": "Planning, Active, Completed"},
                           {"name": "budget", "type": "DECIMAL(15,2)", "description": "Project budget"}
                       ]
                   },
                   {
                       "name": "team_members",
                       "description": "Engineering team members and their assignments",
                       "columns": [
                           {"name": "member_id", "type": "INT", "description": "Team member identifier"},
                           {"name": "name", "type": "VARCHAR(100)", "description": "Team member name"},
                           {"name": "role", "type": "VARCHAR(50)", "description": "Engineering role"},
                           {"name": "project_id", "type": "INT", "description": "Assigned project"}
                       ]
                   },
                   {
                       "name": "sprint_metrics",
                       "description": "Agile sprint performance metrics",
                       "columns": [
                           {"name": "sprint_id", "type": "INT", "description": "Sprint identifier"},
                           {"name": "velocity", "type": "INT", "description": "Sprint velocity"},
                           {"name": "burndown", "type": "DECIMAL(5,2)", "description": "Burndown percentage"},
                           {"name": "project_id", "type": "INT", "description": "Associated project"}
                       ]
                   }
               ],
               "dashboards": [
                   {
                       "name": "Project_Portfolio_Dashboard",
                       "display_name": "Project Portfolio Dashboard",
                       "description": "Overview of all engineering projects and their status",
                       "upstream_tables": ["projects", "team_members"]
                   },
                   {
                       "name": "Sprint_Performance_Dashboard", 
                       "display_name": "Sprint Performance Dashboard",
                       "description": "Sprint metrics and team performance tracking",
                       "upstream_tables": ["sprint_metrics", "team_members"]
                   }
               ]
           },
           "data_science": {
               "database": "DataScienceDB",
               "tables": [
                   {
                       "name": "model_registry",
                       "description": "ML model registry with metadata",
                       "columns": [
                           {"name": "model_id", "type": "INT", "description": "Model identifier"},
                           {"name": "model_name", "type": "VARCHAR(100)", "description": "Model name"},
                           {"name": "accuracy", "type": "DECIMAL(5,4)", "description": "Model accuracy"},
                           {"name": "created_date", "type": "DATETIME", "description": "Model creation date"}
                       ]
                   },
                   {
                       "name": "experiments",
                       "description": "ML experiments and their results",
                       "columns": [
                           {"name": "experiment_id", "type": "INT", "description": "Experiment identifier"},
                           {"name": "model_id", "type": "INT", "description": "Associated model"},
                           {"name": "parameters", "type": "TEXT", "description": "Experiment parameters"},
                           {"name": "score", "type": "DECIMAL(5,4)", "description": "Experiment score"}
                       ]
                   },
                   {
                       "name": "feature_store",
                       "description": "Feature store for ML pipelines",
                       "columns": [
                           {"name": "feature_id", "type": "INT", "description": "Feature identifier"},
                           {"name": "feature_name", "type": "VARCHAR(100)", "description": "Feature name"},
                           {"name": "data_type", "type": "VARCHAR(50)", "description": "Feature data type"},
                           {"name": "importance", "type": "DECIMAL(5,4)", "description": "Feature importance"}
                       ]
                   }
               ],
               "dashboards": [
                   {
                       "name": "ML_Model_Performance_Dashboard",
                       "display_name": "ML Model Performance Dashboard",
                       "description": "Machine learning model performance tracking",
                       "upstream_tables": ["model_registry", "experiments"]
                   },
                   {
                       "name": "Feature_Analytics_Dashboard",
                       "display_name": "Feature Analytics Dashboard", 
                       "description": "Feature store usage and importance analytics",
                       "upstream_tables": ["feature_store", "model_registry"]
                   }
               ]
           }
       }
   
   def generate_data_platform(self):
       return {
           "entityType": "dataPlatform",
           "changeType": "UPSERT",
           "entityUrn": "urn:li:dataPlatform:mssql",
           "aspectName": "dataPlatformInfo",
           "aspect": {
               "name": "mssql",
               "displayName": "SQL Server",
               "type": "RELATIONAL_DB",
               "datasetNameDelimiter": ".",
               "logoUrl": "https://logos-world.net/wp-content/uploads/2021/03/Microsoft-SQL-Server-Logo.png"
           }
       }
   
   def generate_table_records(self, domain, table_config, database_name):
       table_name = table_config["name"]
       full_table_name = f"{database_name}.dbo.{table_name}"
       table_urn = f"urn:li:dataset:(urn:li:dataPlatform:mssql,{full_table_name},PROD)"
       
       records = []
       
       # Dataset properties
       records.append({
           "entityType": "dataset",
           "changeType": "UPSERT",
           "entityUrn": table_urn,
           "aspectName": "datasetProperties",
           "aspect": {
               "customProperties": {
                   "domain": domain,
                   "database": database_name,
                   "schema": "dbo",
                   "platform": "mssql",
                   "env": "PROD"
               },
               "name": table_name,
               "qualifiedName": full_table_name,
               "description": table_config["description"],
               "tags": []
           }
       })
       
       # Schema metadata
       schema_fields = []
       for column in table_config["columns"]:
           schema_fields.append({
               "fieldPath": column["name"],
               "type": {
                   "type": {"com.linkedin.schema.StringType": {}}
               },
               "nativeDataType": column["type"],
               "description": column["description"]
           })
       
       records.append({
           "entityType": "dataset",
           "changeType": "UPSERT",
           "entityUrn": table_urn,
           "aspectName": "schemaMetadata",
           "aspect": {
               "schemaName": table_name,
               "platform": "urn:li:dataPlatform:mssql",
               "version": 1,
               "created": {
                   "time": int(datetime.now().timestamp() * 1000),
                   "actor": "urn:li:corpuser:datahub"
               },
               "lastModified": {
                   "time": int(datetime.now().timestamp() * 1000),
                   "actor": "urn:li:corpuser:datahub"
               },
               "hash": str(uuid.uuid4()),
               "fields": schema_fields
           }
       })
       
       return records
   
   def generate_dashboard_records(self, dashboard_config, domain, database_name):
       dashboard_name = dashboard_config["name"]
       dashboard_urn = f"urn:li:dashboard:(powerbi,{dashboard_name},PROD)"
       
       records = []
       
       # Dashboard info
       records.append({
           "entityType": "dashboard",
           "changeType": "UPSERT", 
           "entityUrn": dashboard_urn,
           "aspectName": "dashboardInfo",
           "aspect": {
               "customProperties": {
                   "domain": domain,
                   "platform": "powerbi",
                   "env": "PROD"
               },
               "title": dashboard_config["display_name"],
               "description": dashboard_config["description"],
               "tool": "powerbi",
               "lastModified": {
                   "time": int(datetime.now().timestamp() * 1000),
                   "actor": "urn:li:corpuser:datahub"
               }
           }
       })
       
       # Generate lineage for each upstream table
       if "upstream_tables" in dashboard_config:
           upstream_urns = []
           for table_name in dashboard_config["upstream_tables"]:
               table_urn = f"urn:li:dataset:(urn:li:dataPlatform:mssql,{database_name}.dbo.{table_name},PROD)"
               upstream_urns.append({
                   "dataset": table_urn,
                   "type": "TRANSFORMED"
               })
           
           records.append({
               "entityType": "dashboard",
               "changeType": "UPSERT",
               "entityUrn": dashboard_urn,
               "aspectName": "upstreamLineage", 
               "aspect": {
                   "upstreams": upstream_urns
               }
           })
       
       return records
   
   def generate(self):
       print("🚀 Starting metadata generation...")
       
       # Generate data platform
       self.metadata_records.append(self.generate_data_platform())
       
       # Generate metadata for each domain
       for domain, domain_config in self.domains.items():
           print(f"📊 Generating {domain} domain metadata...")
           
           # Generate tables
           for table_config in domain_config["tables"]:
               table_records = self.generate_table_records(domain, table_config, domain_config["database"])
               self.metadata_records.extend(table_records)
           
           # Generate dashboards with lineage
           for dashboard_config in domain_config["dashboards"]:
               dashboard_records = self.generate_dashboard_records(dashboard_config, domain, domain_config["database"])
               self.metadata_records.extend(dashboard_records)
       
       print(f"✅ Generated {len(self.metadata_records)} metadata records")
       return self.metadata_records
   
   def save_to_file(self, filename="metadata_output.json"):
       with open(filename, "w") as f:
           json.dump(self.metadata_records, f, indent=2)
       
       print(f"💾 Metadata saved to {filename}")
       return filename
   
   def get_statistics(self):
       stats = {
           "total_records": len(self.metadata_records),
           "domains": {},
           "entity_types": {}
       }
       
       for record in self.metadata_records:
           entity_type = record["entityType"]
           stats["entity_types"][entity_type] = stats["entity_types"].get(entity_type, 0) + 1
           
           if "aspect" in record and "customProperties" in record["aspect"]:
               domain = record["aspect"]["customProperties"].get("domain", "unknown")
               stats["domains"][domain] = stats["domains"].get(domain, 0) + 1
       
       return stats

if __name__ == "__main__":
   generator = MetadataGenerator()
   records = generator.generate()
   stats = generator.get_statistics()
   
   print("\n📈 Generation Statistics:")
   print(f"Total Records: {stats['total_records']}")
   print(f"Domains: {stats['domains']}")
   print(f"Entity Types: {stats['entity_types']}")
   
   # Save to file
   generator.save_to_file()