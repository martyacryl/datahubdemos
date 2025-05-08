# Prerequisites for DataHub-Snowflake Integration

Before setting up the DataHub-Snowflake integration, you need to ensure that several prerequisites are met.

## Snowflake Prerequisites

### Role and User Setup

As a Snowflake administrator with the `ACCOUNTADMIN` role or `MANAGE GRANTS` privilege, run the following commands to create a dedicated role and user for DataHub:

```sql
-- Create a dedicated role for DataHub
CREATE OR REPLACE ROLE datahub_role;

-- Grant access to a warehouse to run queries for metadata extraction
GRANT OPERATE, USAGE ON WAREHOUSE "<your-warehouse>" TO ROLE datahub_role;

-- Grant access to the databases and schemas you want to catalog
GRANT USAGE ON DATABASE "<your-database>" TO ROLE datahub_role;
GRANT USAGE ON ALL SCHEMAS IN DATABASE "<your-database>" TO ROLE datahub_role;
GRANT USAGE ON FUTURE SCHEMAS IN DATABASE "<your-database>" TO ROLE datahub_role;

-- For streams (if using)
GRANT SELECT ON ALL STREAMS IN DATABASE "<your-database>" TO ROLE datahub_role;
GRANT SELECT ON FUTURE STREAMS IN DATABASE "<your-database>" TO ROLE datahub_role;

-- For basic metadata (no profiling)
GRANT REFERENCES ON ALL TABLES IN DATABASE "<your-database>" TO ROLE datahub_role;
GRANT REFERENCES ON FUTURE TABLES IN DATABASE "<your-database>" TO ROLE datahub_role;
GRANT REFERENCES ON ALL EXTERNAL TABLES IN DATABASE "<your-database>" TO ROLE datahub_role;
GRANT REFERENCES ON FUTURE EXTERNAL TABLES IN DATABASE "<your-database>" TO ROLE datahub_role;
GRANT REFERENCES ON ALL VIEWS IN DATABASE "<your-database>" TO ROLE datahub_role;
GRANT REFERENCES ON FUTURE VIEWS IN DATABASE "<your-database>" TO ROLE datahub_role;
GRANT MONITOR ON ALL DYNAMIC TABLES IN DATABASE "<your-database>" TO ROLE datahub_role;
GRANT MONITOR ON FUTURE DYNAMIC TABLES IN DATABASE "<your-database>" TO ROLE datahub_role;

-- If using profiling features (optional but recommended)
GRANT SELECT ON ALL TABLES IN DATABASE "<your-database>" TO ROLE datahub_role;
GRANT SELECT ON FUTURE TABLES IN DATABASE "<your-database>" TO ROLE datahub_role;
GRANT SELECT ON ALL EXTERNAL TABLES IN DATABASE "<your-database>" TO ROLE datahub_role;
GRANT SELECT ON FUTURE EXTERNAL TABLES IN DATABASE "<your-database>" TO ROLE datahub_role;
GRANT SELECT ON ALL DYNAMIC TABLES IN DATABASE "<your-database>" TO ROLE datahub_role;
GRANT SELECT ON FUTURE DYNAMIC TABLES IN DATABASE "<your-database>" TO ROLE datahub_role;

-- Create a dedicated user for DataHub
CREATE USER datahub_user 
    DISPLAY_NAME = 'DataHub' 
    PASSWORD = '<strong-password>' 
    DEFAULT_ROLE = datahub_role 
    DEFAULT_WAREHOUSE = '<your-warehouse>';

-- Grant the role to the user
GRANT ROLE datahub_role TO USER datahub_user;

-- For lineage, usage stats, and tags (Enterprise or higher editions only)
GRANT IMPORTED PRIVILEGES ON DATABASE snowflake TO ROLE datahub_role;
```

> **Note**: Replace `<your-database>`, `<your-warehouse>`, and `<strong-password>` with your actual values.

### Authentication Options

DataHub supports multiple authentication methods for Snowflake:

1. **Username and Password** (simplest)
2. **Key Pair Authentication** (more secure)
3. **OAuth Authentication** (most secure, supports SSO)

#### Setting Up Key Pair Authentication

1. Generate a private key:
   ```bash
   openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out rsa_key.p8 -nocrypt
   ```

2. Generate a public key:
   ```bash
   openssl rsa -in rsa_key.p8 -pubout -out rsa_key.pub
   ```

3. Assign the public key to your DataHub user:
   ```sql
   ALTER USER datahub_user SET RSA_PUBLIC_KEY='<public-key>';
   ```

## DataHub Prerequisites

### DataHub Installation

Ensure you have a working DataHub instance. You can set up DataHub using:

1. **Docker Compose** (for development/testing)
2. **Kubernetes** (for production)

Follow the [official DataHub documentation](https://datahubproject.io/docs/quickstart) for installation instructions.

### DataHub CLI

Install the DataHub CLI for metadata ingestion:

```bash
pip install "acryl-datahub[snowflake]"
```

## Network Configuration

Ensure network connectivity between your DataHub instance and Snowflake:

1. If running in the cloud, configure appropriate security groups or firewall rules
2. For on-premises DataHub, ensure outbound connectivity to Snowflake's endpoints

## Limitations and Considerations

- Some features like lineage tracking and usage statistics require Snowflake Enterprise Edition or higher
- The Snowflake Account Usage views have a latency of 45 minutes to 3 hours
- Metadata extraction can be resource-intensive for large Snowflake deployments

## Next Steps

Once you've completed these prerequisites, proceed to [Basic Configuration](basic-configuration.md).