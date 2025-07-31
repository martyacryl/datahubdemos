# DataHub Ingestion Setup for Snowflake & dbt

This repository provides a complete setup for ingesting Snowflake and dbt metadata into DataHub Open Source using the CLI. Everything is configured for localhost:8080 deployment.

## 📁 Repository Structure

```
datahub-snowflake-dbt-ingestion/
├── README.md                    # This file
├── configs/
│   ├── snowflake-config.yml     # Snowflake ingestion configuration
│   ├── dbt-config.yml          # dbt ingestion configuration
│   └── .env.example            # Environment variables template
├── scripts/
│   ├── setup.sh                # Installation and setup script
│   ├── run-ingestion.sh        # Execute ingestion jobs
│   └── validate-setup.sh       # Validate configurations
├── snowflake/
│   ├── setup-permissions.sql   # Snowflake permissions setup
│   └── network-policy.sql      # Network policy configuration
└── docs/
    ├── prerequisites.md         # Prerequisites and requirements
    ├── troubleshooting.md       # Common issues and solutions
    └── configuration-guide.md   # Detailed configuration guide
```

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.9+ installed
- DataHub Open Source running on localhost:8080
- Snowflake account with appropriate permissions
- dbt project with generated artifacts

### 2. Clone and Setup
```bash
git clone <this-repo>
cd datahub-snowflake-dbt-ingestion
chmod +x scripts/*.sh
./scripts/setup.sh
```

### 3. Configure Environment
```bash
cp configs/.env.example .env
# Edit .env with your credentials
```

### 4. Run Ingestion
```bash
./scripts/run-ingestion.sh
```

## 📋 Configuration Files

### Snowflake Configuration (`configs/snowflake-config.yml`)
Pre-configured with best practices for:
- ✅ Connection settings with environment variables
- ✅ Database/schema/table filtering patterns
- ✅ Usage statistics and lineage extraction
- ✅ Performance optimizations
- ✅ Network policy compatibility

### dbt Configuration (`configs/dbt-config.yml`)
Pre-configured with:
- ✅ Local dbt artifacts ingestion
- ✅ Snowflake platform mapping
- ✅ Column lineage extraction
- ✅ Test results inclusion
- ✅ Documentation and tags preservation

## 🔧 Environment Variables

Create `.env` file with these variables:
```bash
# Snowflake Credentials
SNOWFLAKE_USERNAME=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ACCOUNT=your_account_id
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_ROLE=DATAHUB_ROLE

# DataHub Settings (optional)
DATAHUB_SERVER=http://localhost:8080
# DATAHUB_TOKEN=your_token_if_auth_enabled

# dbt Project Path
DBT_PROJECT_ROOT=/path/to/your/dbt/project
```

## 🔐 Snowflake Permissions Setup

Run the SQL commands in `snowflake/setup-permissions.sql` to create the required DataHub role with proper permissions.

### Network Policy Configuration
If your Snowflake has network policies, add your DataHub server's IP using the commands in `snowflake/network-policy.sql`.

## 📊 Expected Results

After successful ingestion, you'll see in DataHub:

**From Snowflake:**
- 📁 Databases, schemas, tables, and views
- 📈 Usage statistics and query history
- 🔗 Table-level lineage
- 📝 Column descriptions and tags
- 📊 Profiling data (if enabled)

**From dbt:**
- 🔄 dbt models, sources, and tests
- 📈 Column-level lineage
- 📚 Documentation and descriptions
- 🏷️ dbt tags and meta properties
- ✅ Test results and freshness checks
- 🔗 Cross-platform lineage (dbt ↔ Snowflake)

## 🛠️ Scripts

### `scripts/setup.sh`
- Installs DataHub CLI with Snowflake and dbt connectors
- Validates Python version
- Checks DataHub connectivity

### `scripts/run-ingestion.sh`
- Validates configurations with dry-run
- Executes Snowflake ingestion first
- Executes dbt ingestion second
- Provides detailed logging

### `scripts/validate-setup.sh`
- Tests Snowflake connectivity
- Validates dbt artifacts exist
- Checks DataHub server accessibility

## 📖 Documentation

- **[Prerequisites](docs/prerequisites.md)**: Detailed requirements and setup steps
- **[Configuration Guide](docs/configuration-guide.md)**: Advanced configuration options
- **[Troubleshooting](docs/troubleshooting.md)**: Common issues and solutions

## 🔍 Validation

Test your setup:
```bash
# Validate configurations
./scripts/validate-setup.sh

# Dry run (recommended first)
datahub ingest -c configs/snowflake-config.yml --dry-run
datahub ingest -c configs/dbt-config.yml --dry-run

# Check DataHub connectivity
datahub check localhost:8080
```

## 🆘 Support

1. Check [troubleshooting guide](docs/troubleshooting.md)
2. Validate all prerequisites are met
3. Ensure network connectivity and permissions
4. Review logs for specific error messages

## 📚 References

- [DataHub Snowflake Connector Documentation](https://docs.datahub.com/docs/generated/ingestion/sources/snowflake)
- [DataHub dbt Connector Documentation](https://docs.datahub.com/docs/generated/ingestion/sources/dbt)
- [DataHub CLI Documentation](https://datahubproject.io/docs/cli/)
- [DataHub Metadata Ingestion Guide](https://docs.datahub.com/docs/metadata-ingestion)

---

**Note**: This setup assumes DataHub Open Source running on localhost:8080. For production deployments, update the server URLs and implement proper authentication.
