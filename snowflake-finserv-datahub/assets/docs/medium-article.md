# Building a Governed Financial Data Platform with Snowflake and DataHub

## Introduction

Financial services organizations face unique challenges when it comes to data management. They need to process and analyze massive volumes of trading, position, and market data while maintaining strict governance and lineage tracking for regulatory compliance.

In this article, I'll demonstrate how to build a comprehensive financial data platform that combines Snowflake's powerful data processing capabilities with DataHub's governance and metadata management features. We'll use Snowflake's Financial Services Asset Management quickstart as a foundation and extend it with DataHub integration for a complete solution.

## The Challenge

Asset managers, investment banks, and other financial institutions spend hundreds of millions of dollars on systems to provide a Single Version of Truth (SVOT) for their financial data. These systems need to:

1. Process millions of trades daily
2. Calculate positions and P&L in real-time
3. Monitor risk limits and generate alerts
4. Create dashboards for traders, risk managers, and executives
5. Document data lineage for regulatory compliance
6. Enable data discovery across the organization

Snowflake's Financial Services Data Cloud provides the processing power, but governance and discovery remain challenges. That's where DataHub comes in.

## The Solution: Integrating Snowflake with DataHub

Our solution combines:

1. **Snowflake Financial Services Asset Management** - Provides the data model and processing for trading, positions, and risk
2. **DataHub** - Provides data discovery, lineage tracking, and governance capabilities

This integration enables financial institutions to not only process their data efficiently but also maintain proper governance and documentation.

## Setting Up the Environment

### Step 1: Create the Snowflake Financial Services Environment

We'll start by creating a Snowflake database with schemas for different aspects of financial data:

```sql
-- Create database and schemas
CREATE DATABASE FINSERV_DEMO;
CREATE SCHEMA MARKET_DATA;  -- Stock prices and reference data
CREATE SCHEMA TRADING;      -- Trader and trade information
CREATE SCHEMA RISK;         -- Position limits and risk monitoring
CREATE SCHEMA REPORTING;    -- Daily P&L and position reports
CREATE SCHEMA ETL;          -- Data transformation processes
```

Then we'll create tables for our financial data model:

```sql
-- Market data tables
CREATE TABLE MARKET_DATA.STOCK_PRICES (
    SYMBOL STRING,
    TRADE_DATE DATE,
    OPEN_PRICE FLOAT,
    HIGH_PRICE FLOAT,
    LOW_PRICE FLOAT,
    CLOSE_PRICE FLOAT,
    VOLUME INTEGER,
    SOURCE STRING,
    LOAD_TIMESTAMP TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Trading tables
CREATE TABLE TRADING.TRADERS (
    TRADER_ID INTEGER,
    TRADER_NAME STRING,
    DESK STRING,
    REGION STRING,
    STATUS STRING,
    CREATED_DATE DATE DEFAULT CURRENT_DATE,
    LAST_UPDATED_TIMESTAMP TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE TRADING.TRADES (
    TRADE_ID STRING,
    TRADER_ID INTEGER,
    TRADE_DATE DATE,
    TRADE_TIMESTAMP TIMESTAMP_NTZ,
    SYMBOL STRING,
    QUANTITY INTEGER,
    PRICE FLOAT,
    BUY_SELL STRING,
    STATUS STRING,
    LOAD_TIMESTAMP TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Additional tables omitted for brevity...
```

### Step 2: Create Views and Stored Procedures for Lineage

The real power of this integration comes from the lineage that DataHub can track. We'll create views and stored procedures that transform data, establishing a clear lineage path:

```sql
-- Create view for current positions
CREATE OR REPLACE VIEW TRADING.CURRENT_POSITIONS AS
SELECT 
    TR.TRADER_ID,
    TR.TRADER_NAME,
    TR.DESK,
    TR.REGION,
    T.SYMBOL,
    SUM(CASE WHEN T.BUY_SELL = 'BUY' THEN T.QUANTITY ELSE -T.QUANTITY END) AS POSITION,
    MAX(T.TRADE_DATE) AS LAST_TRADE_DATE
FROM 
    TRADING.TRADES T
JOIN 
    TRADING.TRADERS TR ON T.TRADER_ID = TR.TRADER_ID
WHERE 
    T.STATUS = 'SETTLED'
GROUP BY 
    TR.TRADER_ID, TR.TRADER_NAME, TR.DESK, TR.REGION, T.SYMBOL
HAVING 
    POSITION <> 0;
```

We'll also create stored procedures for ETL processes that will generate additional lineage:

```sql
CREATE OR REPLACE PROCEDURE ETL.CALCULATE_DAILY_PNL()
RETURNS STRING
LANGUAGE JAVASCRIPT
AS
$$
// JavaScript code to calculate daily P&L
// This establishes lineage from source to target tables
$$;
```

### Step 3: Set Up DataHub Ingestion

Now let's configure DataHub to ingest metadata from our Snowflake environment. First, we create a DataHub-specific role and user in Snowflake:

```sql
-- Create a DataHub-specific role
CREATE ROLE DATAHUB_ROLE;
GRANT USAGE ON WAREHOUSE FINSERV_WH TO ROLE DATAHUB_ROLE;

-- Create a DataHub-specific user
CREATE USER DATAHUB_USER
    PASSWORD = '<your-secure-password>'
    DEFAULT_ROLE = DATAHUB_ROLE
    DEFAULT_WAREHOUSE = FINSERV_WH;

-- Grant the DataHub role to the DataHub user
GRANT ROLE DATAHUB_ROLE TO USER DATAHUB_USER;

-- Grant access to account usage for lineage extraction
GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE TO ROLE DATAHUB_ROLE;
```

Then we configure DataHub ingestion with a YAML file:

```yaml
source:
  type: snowflake
  config:
    account_id: "<your-snowflake-account-id>"
    username: "DATAHUB_USER"
    password: "${SNOWFLAKE_PASSWORD}"
    role: "DATAHUB_ROLE"
    warehouse: "FINSERV_WH"
    database_pattern:
      allow:
        - "FINSERV_DEMO"
    include_table_lineage: true
    include_column_lineage: true
    include_views: true
    include_usage_stats: true
```

### Step 4: Enhance Metadata in DataHub

To make our financial data more discoverable and understandable, we'll add domains, glossary terms, and tags in DataHub:

```json
{
  "domains": [
    {
      "name": "Financial Services",
      "id": "financial_services",
      "description": "Data related to financial services operations and analytics."
    },
    {
      "name": "Trading",
      "id": "trading",
      "description": "Data related to trading operations, positions, and performance."
    },
    // Additional domains...
  ]
}
```

We'll also create a business glossary with financial terms:

```json
{
  "glossaryTerms": [
    {
      "name": "Position",
      "description": "The amount of a security, asset, or property that is owned (or sold short) by an individual or entity.",
      "termSource": "BusinessGlossary"
    },
    {
      "name": "P&L",
      "description": "Profit and Loss. The financial benefit or loss derived from trading activities over a specific time period.",
      "synonyms": ["Profit and Loss", "PnL"],
      "termSource": "BusinessGlossary"
    },
    // Additional terms...
  ]
}
```

## The Benefits: Bringing It All Together

When we integrate Snowflake's financial services capabilities with DataHub's governance features, we get a powerful platform that provides:

### 1. Complete Data Lineage

DataHub tracks how data flows from source tables through views, stored procedures, and into final reports. This lineage is crucial for regulatory compliance and understanding data dependencies.

![Data Lineage Example](./assets/images/datahub-lineage-view.png)

### 2. Business Context through Glossary Terms

Financial terminology can be complex. DataHub's glossary provides business context for technical assets, making them more understandable to all users.

### 3. Data Quality Monitoring

Data quality is critical in financial services. Our integration includes data quality assertions that monitor for issues like stale data or invalid values.

### 4. Impact Analysis

When changes are needed, DataHub's lineage capabilities make it easy to understand the potential impact. This reduces the risk of unexpected issues when modifying tables or processes.

### 5. Simplified Discovery

Business users can find financial data assets through DataHub's search capabilities, filtering by domains, glossary terms, and tags.

## Conclusion

By combining Snowflake's Financial Services Asset Management capabilities with DataHub's governance features, financial institutions can build a comprehensive data platform that meets both their analytical needs and governance requirements.

This integration provides the best of both worlds: Snowflake's powerful data processing and DataHub's metadata management and lineage tracking. The result is a platform that enables financial institutions to make data-driven decisions while maintaining proper governance and documentation.

Ready to get started? The complete code for this integration is available on GitHub: [link to GitHub repository]

## About the Author

[Your bio here]
