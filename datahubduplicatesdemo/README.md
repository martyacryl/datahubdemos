# DataHub Duplicate Asset Detector

A comprehensive tool for finding duplicated tables, views, stored procedures, charts, dashboards, and other assets in DataHub. The detector uses multiple algorithms to identify potential duplicates based on name similarity, schema similarity, and description similarity.

## 🎯 Features

- **Multi-Type Detection**: Finds duplicates across datasets, charts, dashboards, data flows, and data jobs
- **Multiple Algorithms**: 
  - Name-based similarity detection
  - Schema-based similarity detection (for datasets)
  - Description-based similarity detection
- **Configurable Thresholds**: Adjustable similarity thresholds for different detection types
- **Confidence Scoring**: High, medium, and low confidence levels for findings
- **Comprehensive Reporting**: Markdown and JSON output formats
- **Smart Normalization**: Handles common naming patterns and variations
- **Batch Processing**: Efficiently processes large numbers of assets

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.8+
- Access to DataHub GMS with appropriate permissions
- Valid DataHub Personal Access Token

### 2. Installation

```bash
# Clone or download the project
cd datahubduplicatesdemo

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env with your DataHub credentials
```

### 3. Configuration

Edit `.env` file with your settings:

```bash
# DataHub Configuration
DATAHUB_GMS_URL=https://your-datahub-instance.acryl.io/gms
DATAHUB_GMS_TOKEN=your_datahub_token_here

# Detection Configuration
ENTITY_TYPES=dataset,chart,dashboard,dataFlow,dataJob
DETECTION_TYPES=name,schema,description

# Advanced Configuration (optional)
NAME_SIMILARITY_THRESHOLD=0.8
SCHEMA_SIMILARITY_THRESHOLD=0.7
MIN_ASSETS_FOR_DUPLICATE=2
CASE_SENSITIVE=false
```

### 4. Test Connection

```bash
python test_connection.py
```

### 5. Run Detection

```bash
# Basic detection
python run_detector.py

# Advanced detection with custom parameters
python run_detector.py --entity-types dataset,chart --detection-types name,schema --name-threshold 0.9

# Dry run (no reports generated)
python run_detector.py --dry-run
```

## 📊 Detection Types

### Name-Based Detection
Finds assets with similar names, handling common variations:
- Case differences (`CustomerData` vs `customer_data`)
- Common suffixes (`_v1`, `_backup`, `_old`, `_temp`)
- Common prefixes (`backup_`, `old_`, `temp_`)
- Special character variations (`user-table` vs `user_table`)

### Schema-Based Detection
For datasets, compares field structures:
- Field names and types
- Jaccard similarity calculation
- Handles different naming conventions

### Description-Based Detection
Finds assets with similar descriptions:
- Text similarity using SequenceMatcher
- High threshold (80%) for description matching
- Useful for finding assets with copy-pasted descriptions

## 🔧 Configuration Options

### Command Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--entity-types` | Comma-separated entity types to analyze | `dataset,chart,dashboard` |
| `--detection-types` | Detection algorithms to use | `name,schema,description` |
| `--name-threshold` | Name similarity threshold (0-1) | `0.8` |
| `--schema-threshold` | Schema similarity threshold (0-1) | `0.7` |
| `--min-assets` | Minimum assets for duplicate group | `2` |
| `--output-dir` | Output directory for reports | `./reports` |
| `--format` | Output format (markdown/json/both) | `both` |
| `--verbose` | Enable verbose logging | `False` |
| `--dry-run` | Run without generating reports | `False` |

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATAHUB_GMS_URL` | DataHub GMS endpoint URL | Required |
| `DATAHUB_GMS_TOKEN` | DataHub authentication token | Required |
| `ENTITY_TYPES` | Entity types to analyze | `dataset,chart,dashboard,dataFlow,dataJob` |
| `DETECTION_TYPES` | Detection types to use | `name,schema,description` |
| `NAME_SIMILARITY_THRESHOLD` | Name similarity threshold | `0.8` |
| `SCHEMA_SIMILARITY_THRESHOLD` | Schema similarity threshold | `0.7` |
| `MIN_ASSETS_FOR_DUPLICATE` | Minimum assets for duplicate | `2` |
| `CASE_SENSITIVE` | Case sensitive matching | `false` |

## 📈 Output Reports

### Markdown Report
- Executive summary with counts by type and confidence
- Detailed findings with asset information
- Similarity scores and reasoning
- URNs for easy navigation in DataHub

### JSON Report
- Machine-readable format
- Complete asset metadata
- Structured for programmatic processing
- Includes similarity scores and confidence levels

## 🎯 Use Cases

### Data Governance
- Identify redundant datasets across different schemas
- Find duplicate charts and dashboards
- Clean up legacy or backup assets

### Migration Planning
- Discover duplicate assets before migration
- Plan consolidation strategies
- Identify dependencies

### Quality Assurance
- Ensure naming conventions are followed
- Find assets with similar purposes
- Validate data lineage

### Cost Optimization
- Identify unused or duplicate resources
- Plan storage optimization
- Reduce maintenance overhead

## 🔍 Example Findings

### Name-Based Duplicates
```
Primary Asset: customer_data
Duplicates: customer_data_v2, customer_data_backup
Similarity: 95% (high confidence)
Reason: Similar names with version suffixes
```

### Schema-Based Duplicates
```
Primary Asset: users table
Duplicates: user_info table, customer_users table
Similarity: 87% (medium confidence)
Reason: Similar schemas with 87% field overlap
```

### Description-Based Duplicates
```
Primary Asset: Sales Dashboard
Duplicates: Revenue Dashboard, Sales Report
Similarity: 92% (high confidence)
Reason: Similar descriptions with 92% text overlap
```

## 🛠️ Advanced Usage

### Custom Detection Rules
```python
from duplicate_detector import DataHubDuplicateDetector

detector = DataHubDuplicateDetector(gms_url, token)

# Custom configuration
detector.config.name_similarity_threshold = 0.9
detector.config.ignore_common_suffixes = ['_backup', '_old', '_archive']
detector.config.case_sensitive = True

# Run detection
findings = detector.detect_duplicates(['dataset'], ['name'])
```

### Programmatic Access
```python
# Get findings as data structures
findings = detector.detect_duplicates()

for finding in findings:
    print(f"Found {len(finding.duplicate_assets)} duplicates of {finding.primary_asset['name']}")
    print(f"Confidence: {finding.confidence}")
    print(f"Similarity: {finding.similarity_score:.2%}")
```

## 🚨 Troubleshooting

### Common Issues

1. **No assets found**
   - Check DataHub GMS URL and token
   - Verify entity types are correct
   - Ensure assets exist in DataHub

2. **High false positive rate**
   - Increase similarity thresholds
   - Add more suffixes/prefixes to ignore
   - Use more specific entity types

3. **Missing duplicates**
   - Decrease similarity thresholds
   - Enable case-sensitive matching
   - Check if assets have proper metadata

4. **Performance issues**
   - Reduce the number of entity types
   - Use smaller batch sizes
   - Filter by specific queries

### Debug Mode
```bash
python run_detector.py --verbose --dry-run
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Support

For questions, issues, or contributions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the configuration options

## 🔄 Version History

- **v1.0.0**: Initial release with basic duplicate detection
- **v1.1.0**: Added schema-based detection for datasets
- **v1.2.0**: Added description-based detection
- **v1.3.0**: Enhanced reporting and configuration options
