# DataHub Retention Period Enricher

This enricher pulls retention period information from Snowflake's `INFORMATION_SCHEMA.TABLES.RETENTION_TIME` column and adds it as a structured property to DataHub assets.

## Features

- Queries Snowflake `INFORMATION_SCHEMA.TABLES` to get retention period data
- Creates a structured property in DataHub for retention information
- Maps Snowflake tables to DataHub assets by database, schema, and table name
- Handles batch processing for large numbers of tables
- Provides detailed logging and error handling

## Prerequisites

- Python 3.9+
- Access to Snowflake with `INFORMATION_SCHEMA` access
- DataHub GMS access with appropriate permissions
- Required Python packages (see `requirements.txt`)

## Quick Start

### 1. Set up Environment Variables

```bash
# Copy the example environment file
cp env.example .env

# Edit with your actual values
nano .env
```

Required environment variables:
```bash
# DataHub Configuration
DATAHUB_GMS_URL=https://test-environment.acryl.io/gms
DATAHUB_GMS_TOKEN=your_datahub_token_here

# Snowflake Configuration
SNOWFLAKE_USER=your_snowflake_username
SNOWFLAKE_PASSWORD=your_snowflake_password
SNOWFLAKE_ACCOUNT=your_snowflake_account
SNOWFLAKE_WAREHOUSE=your_warehouse_name
SNOWFLAKE_DATABASE=your_database_name
SNOWFLAKE_SCHEMA=INFORMATION_SCHEMA
```

### 2. Register the Structured Property

First, register the structured property in DataHub:

```bash
python register_property.py
```

### 3. Run the Enricher

```bash
# Install dependencies
pip install -r requirements.txt

# Run the enricher
python retention_transformer.py
```

### 4. Using Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or run individual commands
docker build -t retention-enricher .
docker run --env-file .env retention-enricher
```

## Configuration

### Structured Property Schema

The enricher creates a structured property with the following schema:

```json
{
  "name": "retention_period",
  "displayName": "Retention Period",
  "description": "Data retention period information for the table",
  "type": "STRUCT",
  "fields": [
    {
      "name": "retention_time",
      "displayName": "Retention Time",
      "description": "The retention time in days as specified in Snowflake",
      "type": "NUMBER"
    },
    {
      "name": "retention_unit",
      "displayName": "Retention Unit",
      "description": "The unit of the retention period (e.g., DAYS, MONTHS, YEARS)",
      "type": "STRING"
    },
    {
      "name": "is_retention_enabled",
      "displayName": "Retention Enabled",
      "description": "Whether retention is enabled for this table",
      "type": "BOOLEAN"
    },
    {
      "name": "last_updated",
      "displayName": "Last Updated",
      "description": "When this retention information was last updated",
      "type": "STRING"
    }
  ]
}
```

### Snowflake Query

The enricher queries Snowflake using this SQL:

```sql
SELECT 
    TABLE_CATALOG as database_name,
    TABLE_SCHEMA as schema_name,
    TABLE_NAME as table_name,
    RETENTION_TIME,
    CASE 
        WHEN RETENTION_TIME IS NOT NULL THEN 'DAYS'
        ELSE NULL
    END as retention_unit,
    CASE 
        WHEN RETENTION_TIME IS NOT NULL THEN TRUE
        ELSE FALSE
    END as is_retention_enabled,
    CURRENT_TIMESTAMP() as last_updated
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_TYPE = 'BASE TABLE'
AND RETENTION_TIME IS NOT NULL
ORDER BY TABLE_CATALOG, TABLE_SCHEMA, TABLE_NAME
```

## How It Works

1. **Query Snowflake**: Connects to Snowflake and queries `INFORMATION_SCHEMA.TABLES` for retention data
2. **Group by Database/Schema**: Groups tables by database and schema for efficient processing
3. **Find DataHub Assets**: Searches DataHub for assets matching the database/schema/table combination
4. **Add Structured Properties**: Adds the retention period information as structured properties to matching assets
5. **Log Results**: Provides detailed logging of the enrichment process

## Asset Matching

The enricher matches Snowflake tables to DataHub assets using:
- Database name (from `TABLE_CATALOG`)
- Schema name (from `TABLE_SCHEMA`) 
- Table name (from `TABLE_NAME`)

The DataHub asset URN format is expected to be:
```
urn:li:dataset:(urn:li:dataPlatform:snowflake,{database}.{schema}.{table},PROD)
```

## Error Handling

- **Snowflake Connection Errors**: Logs connection issues and stops processing
- **DataHub API Errors**: Logs API errors but continues processing other assets
- **Asset Matching**: Warns when no DataHub assets are found for a database/schema
- **Property Creation**: Logs failures when adding structured properties

## Logging

The enricher provides detailed logging at INFO level:
- Number of tables found in Snowflake
- Number of DataHub assets found per database/schema
- Success/failure status for each property addition
- Summary statistics

## Troubleshooting

### Common Issues

1. **Snowflake Connection Failed**
   - Verify Snowflake credentials and network access
   - Check that the warehouse is running
   - Ensure the user has access to `INFORMATION_SCHEMA`

2. **No DataHub Assets Found**
   - Verify that tables are properly ingested into DataHub
   - Check the URN format matches the expected pattern
   - Ensure the database/schema names match exactly

3. **Structured Property Creation Failed**
   - Verify the DataHub token has appropriate permissions
   - Check that the structured property was registered first
   - Ensure the DataHub GMS URL is correct

4. **Permission Errors**
   - Ensure the DataHub token has `MANAGE_STRUCTURED_PROPERTIES` permission
   - Verify Snowflake user has `USAGE` on `INFORMATION_SCHEMA`

### Debug Mode

Enable debug logging by setting the log level:

```bash
export LOG_LEVEL=DEBUG
python retention_transformer.py
```

## Customization

### Modifying the Snowflake Query

Edit the `get_snowflake_retention_data()` method in `retention_transformer.py` to customize the query.

### Changing the Structured Property Schema

Modify `retention_property_schema.json` and re-register the property.

### Adding Additional Fields

Update both the Snowflake query and the structured property schema to include additional fields.

## Monitoring

The enricher can be run as a scheduled job to keep retention information up to date. Consider:

- Running daily or weekly depending on how often retention policies change
- Setting up monitoring for the enricher logs
- Creating alerts for processing failures
- Tracking the number of assets updated over time

## Security Considerations

- Store Snowflake credentials securely (use environment variables or secret management)
- Use least-privilege access for both Snowflake and DataHub
- Consider using Snowflake key-pair authentication instead of passwords
- Rotate DataHub tokens regularly
