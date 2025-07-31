# Configuration Guide

## Overview
This guide covers advanced configuration options for Snowflake and dbt ingestion into DataHub.

## Snowflake Configuration Deep Dive

### Connection Options
```yaml
# Basic authentication (recommended for getting started)
username: "${SNOWFLAKE_USERNAME}"
password: "${SNOWFLAKE_PASSWORD}"

# Key-pair authentication (for production)
username: "${SNOWFLAKE_USERNAME}"
private_key_path: "/path/to/private_key.p8"
private_key_passphrase: "${PRIVATE_KEY_PASSPHRASE}"

# OAuth authentication
username: "${SNOWFLAKE_USERNAME}"  
password: "${SNOWFLAKE_PASSWORD}"
oauth_config:
  client_id: "${OAUTH_CLIENT_ID}"
  client_secret: "${OAUTH_CLIENT_SECRET}"
```

### Filtering Strategies

#### Database-Level Filtering
```yaml
database_pattern:
  allow:
    - "PROD_.*"        # All production databases
    - "ANALYTICS"      # Specific database
  deny:
    - ".*_TEMP"        # Exclude temporary databases
    - "DEV_.*"         # Exclude development databases
```

#### Performance Tuning
```yaml
# Usage statistics configuration
start_time: "-30 days"      # Look back further for comprehensive usage
end_time: "now"

# Performance limits
max_workers: 10             # Increase for faster extraction
query_timeout: 600          # 10 minutes for complex queries
```

## dbt Configuration Deep Dive

### Multi-Project Setup
For dbt mesh or multiple dbt projects:

```yaml
# Project 1: Analytics
source:
  type: dbt
  config:
    platform_instance: analytics    # Unique identifier
    manifest_path: "/path/to/analytics/target/manifest.json"
    catalog_path: "/path/to/analytics/target/catalog.json"
    target_platform: snowflake
```

### Meta Property Mapping
Map dbt meta properties to DataHub concepts:

```yaml
meta_mapping:
  # Business ownership
  "owner": "datahub.owner"
  "business_owner": "business_owner"
  
  # Data classification
  "tier": "datahub.tag"
  "criticality": "tier"  
  "classification": "classification"
```

## Security Best Practices

### Credential Management
- Store sensitive data in environment variables
- Use key-pair authentication for production
- Implement credential rotation
- Limit DataHub user permissions to minimum required

### Network Security
- Whitelist DataHub IP in Snowflake network policies
- Use VPN for additional security
- Implement firewall rules
- Monitor access logs
