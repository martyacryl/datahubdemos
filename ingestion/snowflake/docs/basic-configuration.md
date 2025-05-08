# Basic Configuration for DataHub-Snowflake Integration

This guide covers the basic configuration required to set up DataHub to ingest metadata from Snowflake.

## Configuration Overview

DataHub's Snowflake integration can be configured through:

1. DataHub UI (recommended for beginners)
2. YAML recipe files (recommended for automation and advanced use cases)

## Using the DataHub UI

### 1. Navigate to Ingestion

Log in to your DataHub instance and navigate to the Ingestion tab. If you don't see the Ingestion tab, your user may not have the required permissions.

### 2. Create a Snowflake Source

Click on "Create new source" and select "Snowflake" from the list of available connectors.

### 3. Set Up Access Credentials

1. Navigate to the Secrets tab and click "Create new secret"
2. Enter a name for your secret (e.g., "SNOWFLAKE_PASSWORD")
3. Enter your Snowflake password and click "Create"

### 4. Configure Connection Details

Enter the following information:

- **Snowflake Account ID**: Your Snowflake account identifier (e.g., `xy12345`, `xy12345.us-east-2.aws`)
- **Username**: The DataHub user created in Snowflake (e.g., `datahub_user`)
- **Password**: Select the secret you created in step 3
- **Role**: The role to use (e.g., `datahub_role`)
- **Warehouse**: The warehouse to use for queries (e.g., `COMPUTE_WH`)

### 5. Test Connection

Click "Test Connection" to verify your credentials and permissions.

### 6. Configure Ingestion Settings

Adjust the following settings based on your needs:

- **Include Tables**: Toggle to include tables (default: enabled)
- **Include Views**: Toggle to include views (default: enabled)
- **Include Streams**: Toggle to include streams (default: enabled)
- **Include Usage Statistics**: Toggle to include usage data (default: enabled)
- **Include Table Lineage**: Toggle to include lineage data (default: enabled)
- **Include Column Lineage**: Toggle to include column-level lineage (default: enabled)
- **Enable Profiling**: Toggle to enable data profiling (default: disabled)

### 7. Schedule Ingestion

Set the frequency of metadata ingestion (e.g., daily, hourly) and click "Create".

## Using YAML Recipe Files

For automated deployments or more advanced configurations, you can use YAML recipe files with the DataHub CLI.

### Basic Recipe Template

Create a file named `snowflake_ingestion.yaml` with the following content:

```yaml
source:
  type: snowflake
  config:
    # Connection details
    account_id: "xy12345"  # Your Snowflake account identifier
    warehouse: "COMPUTE_WH"
    username: "${SNOWFLAKE_USER}"  # Using environment variables for credentials
    password: "${SNOWFLAKE_PASS}"
    role: "datahub_role"
    
    # Scope of ingestion
    database_pattern:
      allow:
        - "^MARKETING_DB$"
        - "^SALES_DB$"
      deny:
        - "^SNOWFLAKE$"
        - "^SNOWFLAKE_SAMPLE_DATA$"
    
    # Feature flags
    include_tables: true
    include_views: true
    include_usage_stats: true
    include_table_lineage: true
    include_column_lineage: true
    
    # Advanced features
    use_queries_v2: true  # Use the improved query parser
    ignore_start_time_lineage: true  # Include all available lineage data
    
    # For Enterprise Edition or higher
    extract_tags: "without_lineage"  # Extract Snowflake tags

    # Performance optimization
    lazy_schema_resolver: true

sink:
  type: datahub-rest
  config:
    server: "http://localhost:8080"

```

### Running the Ingestion Pipeline

Execute the ingestion using the DataHub CLI:

```bash
# Set environment variables for credentials
export SNOWFLAKE_USER=datahub_user
export SNOWFLAKE_PASS=your_password

# Run the ingestion
datahub ingest -c snowflake_ingestion.yaml
```

### Scheduling with Cron or Airflow

For production environments, set up a scheduled job using cron or Apache Airflow:

**Cron example:**
```bash
0 1 * * * cd /path/to/recipes && datahub ingest -c snowflake_ingestion.yaml
```

**Airflow example:**
```python
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'datahub_snowflake_ingestion',
    default_args=default_args,
    description='Ingest metadata from Snowflake into DataHub',
    schedule_interval='0 1 * * *',
    catchup=False,
)

ingest_task = BashOperator(
    task_id='ingest_snowflake_metadata',
    bash_command='cd /path/to/recipes && datahub ingest -c snowflake_ingestion.yaml',
    env={
        'SNOWFLAKE_USER': '{{ var.value.snowflake_user }}',
        'SNOWFLAKE_PASS': '{{ var.value.snowflake_pass }}',
    },
    dag=dag,
)
```

## Next Steps

- For more advanced configurations, see [Advanced Configuration](advanced-configuration.md)
- For deployment automation, see [Automated Deployment](automated-deployment.md)
- For best practices, see [Best Practices](best-practices.md)