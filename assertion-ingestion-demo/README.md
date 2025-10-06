# DataHub External Assertion Ingestion Demo

This demo shows how to ingest external assertions from AWS Glue and Snowflake into DataHub using the DataHub Python SDK. It extracts data quality assertions, constraints, and validation rules from these external systems and creates corresponding assertions in DataHub.

## 🎯 Features

- **AWS Glue Integration**: Extract table properties, constraints, and data quality rules
- **Snowflake Integration**: Extract table constraints, check constraints, and data quality assertions
- **DataHub SDK Integration**: Create assertions using DataHub's assertion framework
- **Flexible Configuration**: Support for multiple assertion types and custom mappings
- **Batch Processing**: Efficient processing of large numbers of assertions
- **Error Handling**: Comprehensive error handling and logging
- **Validation**: Built-in validation for assertion data

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- DataHub Cloud account with appropriate permissions
- DataHub Personal Access Token (PAT)
- AWS Glue access (for Glue assertions)
- Snowflake access (for Snowflake assertions)
- Required Python packages (see `requirements.txt`)

### Installation

```bash
# Clone or download the project
cd assertion-ingestion-demo

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env with your credentials
```

### Basic Usage

```bash
# Test connections
python test_connections.py

# Ingest Glue assertions
python ingest_glue_assertions.py

# Ingest Snowflake assertions
python ingest_snowflake_assertions.py

# Ingest all assertions
python ingest_all_assertions.py
```

## 📊 Supported Assertion Types

### AWS Glue Assertions
- **Table Properties**: Data format, compression, partitioning
- **Column Constraints**: Data types, nullability, length limits
- **Data Quality Rules**: Custom validation rules from Glue Data Quality
- **Schema Validation**: Field requirements and formats

### Snowflake Assertions
- **Check Constraints**: Custom validation expressions
- **Unique Constraints**: Primary keys and unique indexes
- **Foreign Key Constraints**: Referential integrity rules
- **Data Type Constraints**: Column type validations
- **Custom Assertions**: User-defined validation rules

## 🔧 Configuration

### Environment Variables

```bash
# DataHub Cloud Configuration
DATAHUB_GMS_URL=https://your-account-id.acryl.io/gms
DATAHUB_GMS_TOKEN=your_pat_token_here

# AWS Glue Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-west-2
GLUE_DATABASE_NAME=your_glue_database

# Snowflake Configuration
SNOWFLAKE_ACCOUNT=your_snowflake_account
SNOWFLAKE_USER=your_snowflake_username
SNOWFLAKE_PASSWORD=your_snowflake_password
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=your_schema

# Assertion Configuration
ASSERTION_BATCH_SIZE=100
ASSERTION_TIMEOUT=300
DRY_RUN=false
```

### Custom Assertion Mappings

Edit `assertion_mappings.yaml` to customize how external assertions are mapped to DataHub assertions:

```yaml
glue_mappings:
  table_properties:
    - source: "table_type"
      assertion_type: "data_type_assertion"
      description: "Table type validation"
  
  column_constraints:
    - source: "data_type"
      assertion_type: "data_type_assertion"
      description: "Column data type validation"

snowflake_mappings:
  check_constraints:
    - source: "check_clause"
      assertion_type: "custom_assertion"
      description: "Custom validation rule"
```

## 📈 Usage Examples

### Ingest Glue Assertions

```python
from glue_assertion_extractor import GlueAssertionExtractor
from datahub_assertion_ingester import DataHubAssertionIngester

# Extract assertions from Glue
extractor = GlueAssertionExtractor()
assertions = extractor.extract_assertions()

# Ingest into DataHub
ingester = DataHubAssertionIngester()
ingester.ingest_assertions(assertions)
```

### Ingest Snowflake Assertions

```python
from snowflake_assertion_extractor import SnowflakeAssertionExtractor
from datahub_assertion_ingester import DataHubAssertionIngester

# Extract assertions from Snowflake
extractor = SnowflakeAssertionExtractor()
assertions = extractor.extract_assertions()

# Ingest into DataHub
ingester = DataHubAssertionIngester()
ingester.ingest_assertions(assertions)
```

### Custom Assertion Processing

```python
from assertion_processor import AssertionProcessor

processor = AssertionProcessor()

# Process with custom filters
filtered_assertions = processor.filter_assertions(
    assertions,
    assertion_types=['data_type_assertion', 'custom_assertion'],
    confidence_threshold=0.8
)

# Transform assertions
transformed_assertions = processor.transform_assertions(
    filtered_assertions,
    custom_mappings=custom_mappings
)
```

## 🔍 Assertion Types in DataHub

### Data Type Assertions
- Validates column data types
- Ensures type consistency across datasets
- Maps to Glue column types and Snowflake data types

### Custom Assertions
- User-defined validation rules
- Complex business logic validation
- Custom SQL expressions from Snowflake

### Schema Assertions
- Field presence validation
- Required field checks
- Schema evolution tracking

### Data Quality Assertions
- Completeness checks
- Uniqueness validation
- Range and format validation

## 📊 Output and Monitoring

### Assertion Reports
- Detailed ingestion reports
- Success/failure statistics
- Error logs and debugging information

### DataHub UI Integration
- Assertions appear in DataHub UI
- Linked to source datasets
- Searchable and filterable

### Monitoring and Alerts
- Ingestion status monitoring
- Error rate tracking
- Performance metrics

## 🛠️ Advanced Configuration

### Custom Assertion Mappings
Create custom mappings for specific assertion types:

```python
custom_mappings = {
    'glue_data_quality': {
        'assertion_type': 'data_quality_assertion',
        'description_template': 'Glue DQ Rule: {rule_name}',
        'confidence': 0.9
    },
    'snowflake_check_constraint': {
        'assertion_type': 'custom_assertion',
        'description_template': 'Snowflake Constraint: {constraint_name}',
        'confidence': 0.8
    }
}
```

### Batch Processing
Configure batch processing for large datasets:

```python
config = {
    'batch_size': 100,
    'max_workers': 4,
    'timeout': 300,
    'retry_attempts': 3
}
```

## 🚨 Troubleshooting

### Common Issues

1. **Connection Errors**
   - Verify AWS/Snowflake credentials
   - Check network connectivity
   - Ensure proper permissions

2. **Assertion Mapping Errors**
   - Review assertion mappings configuration
   - Check source data format
   - Validate assertion types

3. **DataHub Ingestion Errors**
   - Verify DataHub token permissions
   - Check assertion format
   - Review DataHub logs

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python ingest_all_assertions.py --verbose
```

## 📝 Best Practices

### Assertion Design
- Use descriptive assertion names
- Include clear error messages
- Set appropriate confidence levels
- Group related assertions

### Performance Optimization
- Use batch processing for large datasets
- Implement proper error handling
- Monitor memory usage
- Use connection pooling

### Data Quality
- Validate assertion data before ingestion
- Implement data quality checks
- Monitor assertion accuracy
- Regular validation of mappings

## 🔄 Maintenance

### Regular Tasks
- Update assertion mappings
- Monitor ingestion performance
- Review assertion accuracy
- Clean up old assertions

### Monitoring
- Set up alerts for failures
- Track ingestion metrics
- Monitor assertion usage
- Review error logs

## 📞 Support

For questions, issues, or contributions:
- Check the troubleshooting section
- Review configuration options
- Test with sample data
- Check DataHub documentation

## 🔄 Version History

- **v1.0.0**: Initial release with Glue and Snowflake support
- **v1.1.0**: Added custom assertion mappings
- **v1.2.0**: Enhanced error handling and logging
- **v1.3.0**: Added batch processing and performance optimizations
