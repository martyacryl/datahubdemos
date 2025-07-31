# Prerequisites Guide

## System Requirements

### Software Requirements
- **Python 3.9+** - Required for DataHub CLI
- **DataHub Open Source** - Running on localhost:8080
- **Snowflake Account** - With appropriate permissions
- **dbt Project** - With generated artifacts

### Network Requirements
- Internet access for package installation
- Network connectivity to Snowflake (check firewall/VPN)
- Access to DataHub server (localhost:8080 for local setup)

## DataHub Open Source Setup

### Quick Start with Docker
```bash
# Clone DataHub repository
git clone https://github.com/datahub-project/datahub.git
cd datahub

# Start DataHub with Docker Compose
./docker/quickstart.sh
```

### Verify DataHub is Running
```bash
# Check health endpoint
curl http://localhost:8080/health

# Access DataHub UI
open http://localhost:8080
```

## Snowflake Prerequisites

### 1. Account Access
- Snowflake account with ACCOUNTADMIN role access
- Or user with MANAGE GRANTS privilege

### 2. Network Configuration
If your Snowflake account has network policies:
- Identify your DataHub server's public IP
- Add IP to Snowflake network policy
- See `snowflake/network-policy.sql` for commands

### 3. Required Information
Gather the following details:
- **Account Identifier**: Format like `xy12345.us-east-1`
- **Warehouse Name**: Existing warehouse with appropriate size
- **Database Names**: Databases you want to ingest metadata from
- **Admin Credentials**: To set up DataHub service user

## dbt Prerequisites

### 1. dbt Project Setup
- Working dbt project with valid `dbt_project.yml`
- dbt connected to Snowflake as target platform
- dbt profiles.yml configured properly

### 2. Generate Required Artifacts
```bash
cd /path/to/your/dbt/project

# Generate manifest.json (required)
dbt compile

# Generate catalog.json (required)  
dbt docs generate

# Generate run_results.json (optional, for test results)
dbt run
dbt test
```

### 3. Verify Artifacts Exist
```bash
ls -la target/
# Should show: manifest.json, catalog.json, sources.json, run_results.json
```

## Permissions Checklist

### Snowflake Permissions
- [ ] ACCOUNTADMIN or MANAGE GRANTS access
- [ ] Can create roles and users
- [ ] Access to target databases and schemas
- [ ] Network policy allows DataHub IP (if applicable)

### dbt Project Access
- [ ] Read access to dbt project files
- [ ] dbt artifacts are up-to-date
- [ ] dbt target platform is Snowflake

### DataHub Access
- [ ] DataHub server accessible at localhost:8080
- [ ] Can create ingestion sources
- [ ] Authentication configured (if enabled)
