# Snowflake Financial Services + DataHub Integration Demo Script

## Introduction

Hello everyone! Today I'm excited to demonstrate how we can use Snowflake's Financial Services Asset Management capabilities with DataHub for comprehensive data governance, lineage, and discovery. This integration showcases how financial institutions can manage their trading and risk data while maintaining proper governance and documentation.

## Demo Flow

### 1. Snowflake Financial Services Environment

Let's start by exploring the Snowflake environment we've set up:

1. **Login to Snowflake:** 
   - Navigate to your Snowflake account
   - Show the FINSERV_DEMO database structure with its schemas:
     - MARKET_DATA: Contains stock prices and reference data
     - TRADING: Contains trader and trade information
     - RISK: Contains position limits and risk monitoring
     - REPORTING: Contains daily P&L and position reports
     - ETL: Contains data transformation processes

2. **Explore Financial Data Model:**
   - Show trader information: `SELECT * FROM TRADING.TRADERS;`
   - Show trade data: `SELECT * FROM TRADING.TRADES;`
   - Show position calculations: `SELECT * FROM TRADING.CURRENT_POSITIONS;`
   - Show risk monitoring: `SELECT * FROM RISK.POSITION_LIMIT_MONITORING;`

3. **Demonstrate Dashboard Views:**
   - Show trader performance: `SELECT * FROM REPORTING.TRADER_PERFORMANCE_DASHBOARD;`
   - Show risk overview: `SELECT * FROM REPORTING.RISK_OVERVIEW_DASHBOARD;`
   - Show how these views combine data from multiple sources

4. **ETL Processes:**
   - Show the stored procedures we've created
   - Demonstrate how they process data and create lineage
   - Run a sample procedure: `CALL ETL.CALCULATE_DAILY_PNL();`

### 2. DataHub Integration

Now let's see how this data is represented in DataHub:

1. **Login to DataHub:**
   - Navigate to https://test-environment.acryl.io/
   - Show the home page and search functionality

2. **Browse Snowflake Assets:**
   - Navigate to the Snowflake platform
   - Show how the FINSERV_DEMO database is organized
   - Explore the schemas and tables that were ingested

3. **Discover Data through Search:**
   - Search for "position" to find position-related datasets
   - Search for "risk" to find risk-related datasets
   - Demonstrate how business users can easily find relevant data

4. **Explore Data Lineage:**
   - Open the REPORTING.DAILY_PNL table
   - Show upstream lineage - where the data comes from
   - Trace lineage all the way back to source tables
   - Show how the views and stored procedures are represented
   - Highlight how this helps understand data flow

5. **Governance and Documentation:**
   - Show how domains organize datasets by business function
   - Show how glossary terms provide business context
   - Show how tags provide additional metadata
   - Demonstrate how data quality assertions work

6. **Impact Analysis:**
   - Show how you can analyze impact of changes
   - Example: "If we change the STOCK_PRICES table schema, what downstream objects would be affected?"
   - Trace downstream dependencies through lineage

### 3. Business Value

To wrap up, let's discuss the business value of this integration:

1. **For Financial Data Teams:**
   - Single platform for data discovery across Snowflake
   - Understand data lineage for regulatory compliance
   - Track data quality with assertions

2. **For Business Users:**
   - Easily find and understand financial data
   - Trust data with clear lineage and ownership
   - Collaborate with data team using a common vocabulary

3. **For Management:**
   - Improved data governance and compliance
   - Better understanding of data assets
   - Reduced risk from data issues

## Q&A

Thank you for attending this demo! I'm happy to answer any questions about the Snowflake Financial Services Asset Management quickstart or its integration with DataHub.
