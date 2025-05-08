# Advanced Configuration for DataHub-Snowflake Integration

This guide covers advanced configuration options for optimizing your DataHub-Snowflake integration.

## Authentication Methods

### Key Pair Authentication

For enhanced security, configure key pair authentication in your recipe:

```yaml
source:
  type: snowflake
  config:
    account_id: "xy12345"
    warehouse: "COMPUTE_WH"
    username: "datahub_user"
    role: "datahub_role"
    
    # Key pair authentication
    authentication_type: "KEY_PAIR_AUTHENTICATOR"
    private_key: "-----BEGIN PRIVATE KEY-----\nMII...\n-----END PRIVATE KEY-----"
    # If using encrypted private key
    private_key_password: "${PRIVATE_KEY_PASSWORD}"
    
    # ... other configuration
```

Alternatively, you can specify a path to your private key:

```yaml
private_key_path: "/path/to/rsa_key.p8"
```

### OAuth Authentication

For SSO integration with Okta:

```yaml
source:
  type: snowflake
  config:
    account_id: "xy12345"
    warehouse: "COMPUTE_WH"
    username: "datahub_user"
    role: "datahub_role"
    
    # OAuth configuration
    authentication_type: "OAUTH_AUTHENTICATOR"
    oauth_config:
      provider: "okta"
      client_id: "${OAUTH_CLIENT_ID}"
      client_secret: "${OAUTH_CLIENT_SECRET}"
      authority_url: "https://your-org.okta.com/oauth2/v1/token"
      scopes:
        - "session:role:datahub_role"
    
    # ... other configuration
```

## Filtering and Pattern Matching

Control which Snowflake objects are ingested using pattern matching:

```yaml
source:
  type: snowflake
  config:
    # ... connection details
    
    # Database filtering
    database_pattern:
      allow:
        - "^MARKETING_DB$"
        - "^ANALYTICS_DB$"
      deny:
        - "^TEMP_.*$"
        - "^SNOWFLAKE$"
        - "^SNOWFLAKE_SAMPLE_DATA$"
      ignoreCase: true
    
    # Schema filtering
    schema_pattern:
      allow:
        - "^PUBLIC$"
        - "^REPORTING$"
      deny:
        - "^STAGING_.*$"
    
    # Table filtering
    table_pattern:
      allow:
        - ".*"
      deny:
        - ".*_DEPRECATED$"
        - ".*_TEMP$"
    
    # View filtering
    view_pattern:
      allow:
        - ".*_V$"
        - "V_.*"
```

## Data Profiling Configuration

Configure advanced data profiling settings:

```yaml
source:
  type: snowflake
  config:
    # ... connection details
    
    profiling:
      # Enable profiling
      enabled: true
      
      # Control which tables are profiled
      profile_pattern:
        allow:
          - "ANALYTICS_DB.PUBLIC.*"
          - "MARKETING_DB.REPORTING.*"
      
      # Performance optimizations
      turn_off_expensive_profiling_metrics: true
      max_workers: 10
      
      # Size limits for profiled tables
      profile_table_size_limit: 5  # GB
      profile_table_row_limit: 5000000  # rows
      
      # Sampling configuration
      use_sampling: true
      sample_size: 10000
      
      # Control which metrics are included
      include_field_null_count: true
      include_field_distinct_count: true
      include_field_min_value: true
      include_field_max_value: true
      include_field_mean_value: true
      include_field_median_value: false  # Can be expensive
      include_field_stddev_value: true
      include_field_quantiles: false  # Can be expensive
      include_field_histogram: false  # Can be expensive
      include_field_sample_values: true
      field_sample_values_limit: 10
      
      # Limit number of columns profiled per table
      max_number_of_fields_to_profile: 50
      
      # Only profile tables modified recently
      profile_if_updated_since_days: 7
```

## Lineage and Usage Statistics

Configure detailed lineage and usage tracking:

```yaml
source:
  type: snowflake
  config:
    # ... connection details
    
    # Lineage configuration
    include_table_lineage: true
    include_column_lineage: true
    include_view_lineage: true
    include_view_column_lineage: true
    
    # Get all lineage regardless of start time
    ignore_start_time_lineage: true
    
    # Usage statistics configuration
    include_usage_stats: true
    top_n_queries: 20
    bucket_duration: "DAY"  # or "HOUR"
    
    # Time range for usage and lineage
    start_time: "2023-01-01T00:00:00Z"
    end_time: "2023-12-31T23:59:59Z"
    
    # Stateful ingestion for lineage and usage
    enable_stateful_lineage_ingestion: true
    enable_stateful_usage_ingestion: true
    incremental_lineage: true
```

## Tag and Domain Configuration

Configure metadata enrichment:

```yaml
source:
  type: snowflake
  config:
    # ... connection details
    
    # Extract Snowflake tags
    extract_tags: "without_lineage"  # Options: "with_lineage", "without_lineage", "skip"
    extract_tags_as_structured_properties: true
    
    # Filter which tags to extract
    tag_pattern:
      allow:
        - "^PII.*"
        - "^SENSITIVITY_.*"
      deny:
        - "^TEMP_.*"
    
    # Domain mapping using patterns
    domain:
      "urn:li:domain:Marketing":
        allow:
          - "MARKETING_DB.*"
      "urn:li:domain:Sales":
        allow:
          - "SALES_DB.*"
      "urn:li:domain:Finance":
        allow:
          - "FINANCE_DB.*"
```

## Shared Databases Configuration

For Snowflake shared databases across accounts:

```yaml
source:
  type: snowflake
  config:
    # ... connection details
    
    # Configure shared databases
    shares:
      MARKETING_SHARE:  # Share name
        database_name: MARKETING_DB
        platform_instance: primary
        consumers:
          - database_name: MARKETING_DB_CONSUMER
            platform_instance: secondary
      
      SALES_SHARE:  # Another share
        database_name: SALES_DB
        platform_instance: primary
        consumers:
          - database_name: SALES_DB_CONSUMER
            platform_instance: secondary
```

## Performance Optimizations

Optimize ingestion performance:

```yaml
source:
  type: snowflake
  config:
    # ... connection details
    
    # Use improved query parser
    use_queries_v2: true
    
    # Optimize schema resolution
    lazy_schema_resolver: true
    
    # Filter out high-volume users for lineage/usage
    pushdown_deny_usernames:
      - "etl_service"
      - "reporting_bot"
    
    # Optimize database connections
    options:
      connect_timeout: 60
      retry_on_exception: true
      max_pool_size: 5
    
    # Use file-backed cache for view definitions
    use_file_backed_cache: true
    
    # Temporary table pattern for lineage exclusion
    temporary_tables_pattern:
      - ".*\\.FIVETRAN_.*_STAGING\\..*"
      - ".*__DBT_TMP$"
      - ".*\\.SEGMENT_[a-f0-9]{8}[-_][a-f0-9]{4}[-_][a-f0-9]{4}[-_][a-f0-9]{4}[-_][a-f0-9]{12}"
```

## Stateful Ingestion Configuration

Configure stateful ingestion for incremental updates:

```yaml
source:
  type: snowflake
  config:
    # ... connection details
    
    # Enable stateful ingestion
    stateful_ingestion:
      enabled: true
      remove_stale_metadata: true
      fail_safe_threshold: 50.0  # Percentage
    
    # Storage for stateful ingestion
    state_provider:
      type: datahub
      config:
        server: "http://localhost:8080"
```

## Complete Advanced Recipe Example

Here's a comprehensive example combining many advanced features:

```yaml
source:
  type: snowflake
  config:
    # Connection details
    account_id: "xy12345"
    warehouse: "COMPUTE_WH"
    username: "${SNOWFLAKE_USER}"
    authentication_type: "KEY_PAIR_AUTHENTICATOR"
    private_key_path: "/path/to/rsa_key.p8"
    role: "datahub_role"
    
    # Environment and platform instance
    env: "PROD"
    platform_instance: "primary"
    
    # Filtering
    database_pattern:
      allow:
        - "^(MARKETING|SALES|ANALYTICS)_DB$"
      deny:
        - "^SNOWFLAKE.*$"
    
    # Features
    include_tables: true
    include_views: true
    include_streams: true
    include_procedures: false
    
    # Lineage and usage
    include_table_lineage: true
    include_column_lineage: true
    include_view_lineage: true
    include_usage_stats: true
    use_queries_v2: true
    ignore_start_time_lineage: true
    
    # Tags and metadata
    extract_tags: "without_lineage"
    extract_tags_as_structured_properties: true
    
    # Profiling
    profiling:
      enabled: true
      turn_off_expensive_profiling_metrics: true
      use_sampling: true
      sample_size: 10000
      profile_table_size_limit: 5
    
    # Stateful ingestion
    stateful_ingestion:
      enabled: true
      remove_stale_metadata: true
    
    # Performance
    lazy_schema_resolver: true
    use_file_backed_cache: true

sink:
  type: datahub-rest
  config:
    server: "http://localhost:8080"

pipeline_name: snowflake_advanced_ingestion
```

## Next Steps

- For automated deployment, see [Automated Deployment](automated-deployment.md)
- For best practices, see [Best Practices](best-practices.md)