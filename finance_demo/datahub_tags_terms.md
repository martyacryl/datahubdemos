# DataHub Tags and Terms for Finance Analytics Demo

This document provides the definitions for all tags and glossary terms that should be created in DataHub Cloud for the finance analytics demo.

## Tags to Create

### 1. Financial
- **Description**: General financial data classification tag
- **Category**: Data Classification
- **Use Case**: Applied to all financial datasets and assets
- **How to Create**: In DataHub UI, go to Tags → Create New Tag → Name: "Financial"

### 2. Sensitive
- **Description**: Sensitive financial information that requires special handling
- **Category**: Data Classification
- **Use Case**: Applied to datasets containing sensitive financial data
- **How to Create**: In DataHub UI, go to Tags → Create New Tag → Name: "Sensitive"

### 3. PII
- **Description**: Personally Identifiable Information
- **Category**: Data Classification
- **Use Case**: Applied to columns and datasets containing personally identifiable information
- **How to Create**: In DataHub UI, go to Tags → Create New Tag → Name: "PII"

### 4. Revenue Analytics
- **Description**: Revenue-focused datasets and analytics
- **Category**: Business Domain
- **Use Case**: Applied to revenue-related models and datasets
- **How to Create**: In DataHub UI, go to Tags → Create New Tag → Name: "Revenue Analytics"

### 5. Regulatory
- **Description**: Regulatory/compliance related data
- **Category**: Compliance
- **Use Case**: Applied to datasets that must comply with regulatory requirements
- **How to Create**: In DataHub UI, go to Tags → Create New Tag → Name: "Regulatory"

## Glossary Terms to Create

### 1. Revenue
- **Name**: Revenue
- **Description**: Total income from sales of products or services
- **Formula**: Sum of all transaction amounts
- **Examples**: 
  - Product sales revenue
  - Service revenue
  - Subscription revenue
- **Business Context**: Core financial metric representing the total amount of money generated from business operations
- **Related Terms**: Gross Revenue, Net Revenue, Product Revenue
- **How to Create**: In DataHub UI, go to Glossary → Add Term → Name: "Revenue"

### 2. Product Revenue
- **Name**: Product Revenue
- **Description**: Revenue broken down by product or product category
- **Formula**: Sum of transaction amounts grouped by product_id
- **Examples**:
  - Revenue from Product A: $15,000
  - Revenue from Product B: $25,000
- **Business Context**: Helps understand which products generate the most revenue and drive product strategy
- **Calculation**: `SELECT product_id, SUM(amount) FROM revenue_transactions GROUP BY product_id`
- **Related Terms**: Revenue, Customer Revenue
- **How to Create**: In DataHub UI, go to Glossary → Add Term → Name: "Product Revenue"

### 3. Customer Revenue
- **Name**: Customer Revenue
- **Description**: Revenue attributed to individual customers or customer segments
- **Formula**: Sum of transaction amounts grouped by customer_id
- **Examples**:
  - Enterprise customer revenue: $50,000
  - SMB customer revenue: $10,000
- **Business Context**: Critical for customer segmentation, retention analysis, and identifying high-value customers
- **Calculation**: `SELECT customer_id, SUM(amount) FROM revenue_transactions GROUP BY customer_id`
- **Related Terms**: Revenue, Product Revenue
- **How to Create**: In DataHub UI, go to Glossary → Add Term → Name: "Customer Revenue"

### 4. Financial Metrics
- **Name**: Financial Metrics
- **Description**: Key performance indicators (KPIs) used to measure financial performance
- **Examples**:
  - Total Revenue
  - Revenue Growth Rate
  - Average Transaction Value
  - Revenue by Region
- **Business Context**: Essential metrics for financial reporting, forecasting, and business decision-making
- **Related Terms**: Revenue, Gross Revenue, Net Revenue
- **How to Create**: In DataHub UI, go to Glossary → Add Term → Name: "Financial Metrics"

### 5. Transaction Amount
- **Name**: Transaction Amount
- **Description**: Individual transaction value representing a single sale or purchase
- **Formula**: Direct value from transaction record
- **Examples**:
  - Transaction TXN001: $1,500.00
  - Transaction TXN002: $2,500.00
- **Business Context**: Basic unit of financial transaction data, used to calculate aggregated metrics
- **Data Type**: DECIMAL(18, 2)
- **Related Terms**: Revenue, Financial Metrics
- **How to Create**: In DataHub UI, go to Glossary → Add Term → Name: "Transaction Amount"

### 6. Gross Revenue
- **Name**: Gross Revenue
- **Description**: Total revenue before any deductions, returns, discounts, or allowances
- **Formula**: Sum of all transaction amounts without deductions
- **Examples**:
  - Q1 Gross Revenue: $100,000
  - Annual Gross Revenue: $1,200,000
- **Business Context**: Represents the total sales value before accounting for returns, discounts, or adjustments
- **Calculation**: `SELECT SUM(amount) FROM revenue_transactions WHERE transaction_date BETWEEN start_date AND end_date`
- **Related Terms**: Revenue, Net Revenue
- **How to Create**: In DataHub UI, go to Glossary → Add Term → Name: "Gross Revenue"

### 7. Net Revenue
- **Name**: Net Revenue
- **Description**: Revenue after deductions for returns, discounts, allowances, and other adjustments
- **Formula**: Gross Revenue - Returns - Discounts - Allowances
- **Examples**:
  - Q1 Net Revenue: $95,000 (after $5,000 in returns)
  - Annual Net Revenue: $1,150,000
- **Business Context**: Represents the actual revenue recognized after all adjustments, providing a more accurate picture of business performance
- **Calculation**: `Gross Revenue - (Returns + Discounts + Allowances)`
- **Related Terms**: Revenue, Gross Revenue
- **How to Create**: In DataHub UI, go to Glossary → Add Term → Name: "Net Revenue"

### 8. Silver
- **Name**: Silver
- **Description**: Data tier representing cleaned, validated, and enriched data ready for analytics
- **Category**: Data Tier
- **Business Context**: Silver layer data is typically cleaned from bronze (raw) data, with data quality checks applied and business logic applied
- **Related Terms**: Bronze, Gold
- **How to Create**: In DataHub UI, go to Glossary → Add Term → Name: "Silver"

### 9. Gold
- **Name**: Gold
- **Description**: Data tier representing aggregated, business-ready datasets optimized for reporting and analytics
- **Category**: Data Tier
- **Business Context**: Gold layer data is typically aggregated summaries, KPIs, and metrics ready for business consumption
- **Related Terms**: Bronze, Silver
- **How to Create**: In DataHub UI, go to Glossary → Add Term → Name: "Gold"

## How to Create Tags and Terms in DataHub Cloud

### Creating Tags

1. Navigate to **Settings** → **Tags** in DataHub UI
2. Click **Create Tag**
3. Enter the tag name (e.g., "Financial")
4. Optionally add a description
5. Save the tag

### Creating Glossary Terms

1. Navigate to **Glossary** in DataHub UI
2. Click **Add Term**
3. Enter the term name (e.g., "Revenue")
4. Add a description (use the descriptions provided above)
5. Optionally add related terms
6. Save the term

### Bulk Creation (Alternative)

If you have many terms to create, you can use the DataHub CLI or API:

```bash
# Using DataHub CLI (requires authentication)
datahub glossary term upsert --urn "urn:li:glossaryTerm:Revenue" --name "Revenue" --description "Total income from sales"
```

## Notes

- All tags and terms should be created **before** running the dbt ingestion
- Tags and terms are case-sensitive
- The meta mappings in the dbt ingestion recipe will automatically apply these tags and terms based on dbt model meta properties
- Column-level tags (like PII) will be applied automatically based on column meta properties

