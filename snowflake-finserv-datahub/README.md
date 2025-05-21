# Snowflake Financial Services + DataHub Integration

This repository demonstrates the integration of Snowflake's Financial Services Asset Management quickstart with DataHub for enhanced data governance, discovery, and lineage tracking in financial services workloads.

## Overview

Financial services organizations deal with massive volumes of data that require robust governance, lineage tracking, and discovery capabilities. This project combines:

1. **Snowflake's Financial Services Asset Management** - A quickstart that demonstrates how asset managers (banks, insurance companies, hedge funds) can create a Single Version of Truth (SVOT) to make quick data-driven decisions
2. **DataHub** - An open-source metadata platform that provides data discovery, lineage, and governance capabilities

By integrating these technologies, we showcase a comprehensive solution for financial data management that addresses both analytical needs and governance requirements.

## Architecture

![Architecture Diagram](./assets/images/architecture-diagram.png)

The integration follows these key steps:
1. Financial data is loaded and processed in Snowflake using the Asset Management quickstart
2. DataHub connects to Snowflake to ingest metadata, including schemas, lineage, and usage patterns
3. Additional metadata like domains, glossary terms, and tags are added to enhance discoverability
4. Users can discover, understand, and trace financial datasets through the DataHub UI

## Getting Started

### Prerequisites

- Snowflake account with ACCOUNTADMIN privileges
- DataHub Cloud account (or self-hosted DataHub instance)
- Personal Access Token (PAT) for DataHub
- Python 3.7+ and pip

### Setup Steps

1. **Clone this repository**
```bash
git clone https://github.com/yourusername/snowflake-finserv-datahub.git
cd snowflake-finserv-datahub
```

2. **Set up the Snowflake environment**
```bash
# Log in to Snowflake and run the setup scripts
snowsql -a <your_account> -u <your_username> -f snowflake/setup/00_create_datahub_role_user.sql
snowsql -a <your_account> -u <your_username> -f snowflake/setup/01_grant_privileges.sql
snowsql -a <your_account> -u <your_username> -f snowflake/setup/02_finserv_asset_mgmt_setup.sql
```

3. **Configure DataHub ingestion**
```bash
# Install DataHub CLI
pip install acryl-datahub

# Configure environment variables for DataHub
export DATAHUB_GMS_URL=https://test-environment.acryl.io
export DATAHUB_PAT=<your_personal_access_token>

# Run the ingestion pipeline
datahub ingest -c datahub/ingestion/snowflake_config.yaml
```

4. **Apply additional metadata**
```bash
# Use the DataHub REST API to apply domains, glossary terms, and tags
cd datahub/metadata
./apply_metadata.sh
```

## Demo Components

1. **Financial Services Data Model**
   - Trades, positions, and P&L calculation
   - Market data integration
   - Risk analytics

2. **DataHub Integration**
   - Schema metadata
   - Data lineage
   - Usage statistics
   - Business glossary
   - Data domains

## Additional Resources

- [Snowflake Financial Services Asset Management Quickstart](https://quickstarts.snowflake.com/guide/financial-services-asset-management-snowflake/)
- [DataHub Documentation](https://datahubproject.io/docs/)
- [Medium Article](./assets/docs/medium-article.md)
- [LinkedIn Post](./assets/docs/linkedin-post.md)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
