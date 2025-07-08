# DataHub Metadata Generator

A Python project that generates realistic fake metadata for DataHub, including SQL Server databases, Power BI dashboards, and complete lineage relationships across Finance, Engineering, and Data Science domains.

## 🚀 Features

- **Multi-Domain Support**: Generate metadata for Finance, Engineering, and Data Science domains
- **Realistic Data Structures**: SQL Server tables with proper schemas and relationships
- **Power BI Dashboards**: Business intelligence dashboards with realistic names and descriptions
- **Complete Lineage**: Full lineage relationships from SQL Server tables to Power BI dashboards
- **DataHub Compatible**: Output in DataHub-compatible JSON format ready for ingestion
- **CLI Interface**: Easy-to-use command line interface with multiple commands
- **Environment Configuration**: Support for environment variables and configuration files
- **Validation**: Built-in metadata validation and preview capabilities

## 📋 Requirements

- Python 3.8+
- DataHub CLI (`acryl-datahub`)
- Access to a DataHub instance (local or cloud)

## 🛠️ Installation

1. **Clone or download the project**:
   ```bash
   cd metadata_generator_project
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the project**:
   ```bash
   python -m src.cli init
   ```

4. **Configure your environment**:
   ```bash
   cp .env.template .env
   # Edit .env with your DataHub connection details
   ```

## ⚙️ Configuration

The project uses environment variables for configuration. Create a `.env` file with the following settings:

```env
# DataHub Connection
DATAHUB_SERVER=https://your-datahub-instance.com
DATAHUB_TOKEN=your_personal_access_token_here
DATAHUB_GMS_URL=https://your-datahub-instance.com/gms

# Generator Configuration
OUTPUT_FILE=generated_metadata.json
INCLUDE_FINANCE=true
INCLUDE_ENGINEERING=true
INCLUDE_DATA_SCIENCE=true
NUM_TABLES_PER_DOMAIN=5
NUM_DASHBOARDS_PER_DOMAIN=3
INCLUDE_LINEAGE=true
```

## 🎯 Usage

### Basic Usage

Generate metadata with default settings:
```bash
python -m src.cli generate
```

### Advanced Usage

Generate metadata with custom options:
```bash
python -m src.cli generate \
  --output my_metadata.json \
  --finance \
  --no-engineering \
  --data-science \
  --tables-per-domain 10 \
  --dashboards-per-domain 5 \
  --lineage \
  --verbose
```

### Ingest to DataHub

Ingest generated metadata to your DataHub instance:
```bash
python -m src.cli ingest --file generated_metadata.json --verbose
```

### Validate Metadata

Validate generated metadata before ingestion:
```bash
python -m src.cli validate --file generated_metadata.json
```

### Preview Metadata

Preview the first few records:
```bash
python -m src.cli preview --file generated_metadata.json --lines 10
```

### Show Configuration

Display current configuration:
```bash
python -m src.cli config
```

## 📊 Generated Metadata

### Finance Domain

**Database**: `FinanceDB`
- **Tables**:
  - `general_ledger` - Chart of accounts and general ledger entries
  - `budget_allocations` - Department budget allocations and spending
  - `expense_reports` - Employee expense reports and reimbursements
  - `revenue_forecasts` - Revenue projections and forecasting data
  - `financial_ratios` - Key financial ratios and metrics

**Dashboards**:
- Financial Performance Dashboard
- Budget vs Actual Analysis
- Revenue Forecasting Dashboard

### Engineering Domain

**Database**: `EngineeringDB`
- **Tables**:
  - `projects` - Engineering projects and their details
  - `team_members` - Engineering team members and their roles
  - `sprint_planning` - Agile sprint planning and execution data
  - `code_reviews` - Code review metrics and quality data
  - `deployment_metrics` - Deployment frequency and success rates

**Dashboards**:
- Project Portfolio Dashboard
- Team Velocity Dashboard
- Code Quality Dashboard

### Data Science Domain

**Database**: `DataScienceDB`
- **Tables**:
  - `ml_models` - Machine learning models and their metadata
  - `experiments` - ML experiment tracking and results
  - `feature_store` - Feature definitions and metadata
  - `predictions` - Model predictions and inference results
  - `data_pipelines` - Data pipeline execution and monitoring

**Dashboards**:
- Model Performance Dashboard
- Experiment Tracking Dashboard
- Data Pipeline Monitoring

## 🔗 Lineage Relationships

The generator creates complete lineage relationships showing how data flows from SQL Server tables to Power BI dashboards:

```
SQL Server Tables → Power BI Dashboards
```

Each dashboard is connected to all tables in its domain, creating realistic data lineage scenarios.

## 📁 Project Structure

```
metadata_generator_project/
├── src/
│   ├── __init__.py
│   ├── cli.py              # Command line interface
│   ├── config.py           # Configuration management
│   └── metadata_generator.py # Main generator class
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── .env.template          # Environment template
└── generated_metadata.json # Generated output (after running)
```

## 🎨 CLI Commands

| Command | Description | Options |
|---------|-------------|---------|
| `generate` | Generate metadata | `--output`, `--finance`, `--engineering`, `--data-science`, `--tables-per-domain`, `--dashboards-per-domain`, `--lineage`, `--verbose` |
| `ingest` | Ingest to DataHub | `--file`, `--server`, `--token`, `--verbose` |
| `validate` | Validate metadata | `--file` |
| `preview` | Preview metadata | `--file`, `--lines` |
| `config` | Show configuration | None |
| `init` | Initialize project | `--template` |

## 🔧 Customization

### Adding New Domains

To add a new domain, modify the `domains` dictionary in `src/metadata_generator.py`:

```python
'new_domain': {
    'database_name': 'NewDomainDB',
    'description': 'Description of the new domain',
    'tables': [
        {
            'name': 'table_name',
            'description': 'Table description',
            'columns': [
                {'name': 'column_name', 'type': 'VARCHAR(100)', 'description': 'Column description'}
            ]
        }
    ],
    'dashboards': [
        {
            'name': 'Dashboard Name',
            'description': 'Dashboard description',
            'type': 'Power BI'
        }
    ]
}
```

### Modifying Table Schemas

Edit the `columns` array for each table to add, remove, or modify columns:

```python
'columns': [
    {'name': 'new_column', 'type': 'INT', 'description': 'New column description'},
    # ... existing columns
]
```

## 🚨 Troubleshooting

### Common Issues

1. **DataHub token not found**:
   - Set `DATAHUB_TOKEN` environment variable
   - Or use `--token` option with ingest command

2. **Import errors**:
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version (3.8+ required)

3. **Ingestion failures**:
   - Validate metadata first: `python -m src.cli validate`
   - Check DataHub server connectivity
   - Verify token permissions

4. **Large file generation**:
   - Reduce `NUM_TABLES_PER_DOMAIN` and `NUM_DASHBOARDS_PER_DOMAIN`
   - Use `--no-lineage` to skip lineage generation

### Debug Mode

Enable verbose output for debugging:
```bash
python -m src.cli generate --verbose
python -m src.cli ingest --verbose
```

## 📈 Performance

- **Generation time**: ~1-5 seconds for default configuration
- **File size**: ~50-200KB for default configuration
- **Memory usage**: ~50-100MB during generation
- **Records generated**: ~100-500 records for default configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the CLI help: `python -m src.cli --help`
3. Validate your configuration: `python -m src.cli config`
4. Open an issue with detailed error information

## 🎯 Use Cases

- **DataHub Demos**: Create realistic metadata for DataHub demonstrations
- **Testing**: Generate test data for DataHub development and testing
- **Training**: Provide sample data for DataHub training sessions
- **Proof of Concept**: Quickly populate DataHub with realistic business scenarios
- **Development**: Test DataHub features with comprehensive metadata

---

**Happy metadata generation! 🎉** 