# PIMCO DataHub LLM Demo - Claude Desktop Prompts

This file contains example prompts to use with Claude Desktop for the PIMCO Municipal Bond demo. These prompts demonstrate how to use DataHub context to generate better SQL queries.

## Setup

1. **Claude Desktop** should be configured with:
   - Snowflake MCP server (for executing queries)
   - DataHub MCP server (for retrieving context)

2. **DataHub MCP Server Configuration**:
   - Ensure DataHub MCP server is configured in Claude Desktop
   - The server should have access to your DataHub instance

## Example Prompts

### Example 1: Total Positions by Region for Tax-Exempt Bonds

**Without DataHub Context**:
```
I need to query Snowflake for total municipal bond positions by region for tax-exempt bonds. 
The database is PIMCO_DEMO. What SQL query should I use?
```

**With DataHub Context**:
```
I need to query Snowflake for total municipal bond positions by region for tax-exempt bonds. 
The database is PIMCO_DEMO. 

First, use DataHub to search for tables related to bond positions, regions, and tax-exempt bonds. 
Then use that context to generate the correct SQL query.
```

**Using DataHub MCP Server**:
```
I need to query Snowflake for total municipal bond positions by region for tax-exempt bonds. 
The database is PIMCO_DEMO.

Please:
1. Search DataHub for tables containing bond positions
2. Search DataHub for tables containing region information
3. Search DataHub for tables containing tax-exempt bond classification
4. Use the context from DataHub to understand the schema and relationships
5. Generate the correct SQL query using Snowflake MCP server
```

---

### Example 2: Position Growth Over Time by Segment

**Without DataHub Context**:
```
I need to query Snowflake to show bond position growth over the last 30 days by segment. 
The database is PIMCO_DEMO. What SQL should I use?
```

**With DataHub Context**:
```
I need to query Snowflake to show bond position growth over the last 30 days by segment. 
The database is PIMCO_DEMO.

First, use DataHub to search for tables containing growth metrics and segment information. 
Then use that context to generate the correct SQL query.
```

**Using DataHub MCP Server**:
```
I need to query Snowflake to show bond position growth over the last 30 days by segment. 
The database is PIMCO_DEMO.

Please:
1. Search DataHub for tables containing growth metrics or time series data
2. Search DataHub for tables containing segment information
3. Use the context from DataHub to understand the schema and relationships
4. Generate the correct SQL query using Snowflake MCP server
```

---

### Example 3: Top Issuers by Total Position Value

**Without DataHub Context**:
```
I need to query Snowflake for the top 10 issuers by total position value. 
The database is PIMCO_DEMO. What SQL should I use?
```

**With DataHub Context**:
```
I need to query Snowflake for the top 10 issuers by total position value. 
The database is PIMCO_DEMO.

First, use DataHub to search for tables containing issuer information and position data. 
Then use that context to generate the correct SQL query.
```

**Using DataHub MCP Server**:
```
I need to query Snowflake for the top 10 issuers by total position value. 
The database is PIMCO_DEMO.

Please:
1. Search DataHub for tables containing issuer information
2. Search DataHub for tables containing position value data
3. Use the context from DataHub to understand the schema and relationships
4. Generate the correct SQL query using Snowflake MCP server
```

---

### Example 4: Bond Positions with Maturity Analysis

**Without DataHub Context**:
```
I need to query Snowflake to show bond positions by years to maturity for tax-exempt bonds. 
The database is PIMCO_DEMO. What SQL should I use?
```

**With DataHub Context**:
```
I need to query Snowflake to show bond positions by years to maturity for tax-exempt bonds. 
The database is PIMCO_DEMO.

First, use DataHub to search for tables containing bond positions, maturity dates, and tax-exempt classification. 
Then use that context to generate the correct SQL query.
```

**Using DataHub MCP Server**:
```
I need to query Snowflake to show bond positions by years to maturity for tax-exempt bonds. 
The database is PIMCO_DEMO.

Please:
1. Search DataHub for tables containing bond positions
2. Search DataHub for tables containing bond maturity information
3. Search DataHub for tables containing tax-exempt classification
4. Use the context from DataHub to understand the schema and relationships
5. Generate the correct SQL query using Snowflake MCP server
```

---

### Example 5: Total Adjusted Market Value of Active Positions by Segment

**Without DataHub Context**:
```
I need to query Snowflake for total adjusted market value of active bond positions by segment. 
The database is PIMCO_DEMO. What SQL should I use?
```

**With DataHub Context**:
```
I need to query Snowflake for total adjusted market value of active bond positions by segment. 
The database is PIMCO_DEMO.

First, use DataHub to search for:
- Tables containing bond positions
- Columns containing adjusted market value
- Columns containing position status (active/inactive)
- Tables containing segment information

Then use that context to generate the correct SQL query.
```

**Using DataHub MCP Server**:
```
I need to query Snowflake for total adjusted market value of active bond positions by segment. 
The database is PIMCO_DEMO.

Please:
1. Search DataHub for tables containing bond positions and market value
2. Search DataHub for glossary terms related to "adjusted market value" and "position status"
3. Search DataHub for tables containing segment information
4. Use the context from DataHub to understand:
   - Which column contains adjusted market value
   - Which status codes indicate active positions
   - How to join with segment tables
5. Generate the correct SQL query using Snowflake MCP server
```

---

### Example 6: Active Positions with Maturity Multiplier Analysis

**Without DataHub Context**:
```
I need to query Snowflake to show active bond positions grouped by maturity multiplier. 
The database is PIMCO_DEMO. What SQL should I use?
```

**With DataHub Context**:
```
I need to query Snowflake to show active bond positions grouped by maturity multiplier. 
The database is PIMCO_DEMO.

First, use DataHub to search for:
- Tables containing bond positions
- Columns containing maturity multiplier
- Glossary terms explaining what maturity multiplier means
- Columns containing position status

Then use that context to generate the correct SQL query.
```

**Using DataHub MCP Server**:
```
I need to query Snowflake to show active bond positions grouped by maturity multiplier. 
The database is PIMCO_DEMO.

Please:
1. Search DataHub for glossary terms related to "maturity multiplier"
2. Search DataHub for tables containing bond positions
3. Search DataHub for columns containing maturity multiplier and position status
4. Use the context from DataHub to understand:
   - What maturity multiplier means (opaque business logic)
   - Which status codes indicate active positions
   - How to group by maturity multiplier
5. Generate the correct SQL query using Snowflake MCP server
```

---

## Using DataHub MCP Server Directly

If you want to explicitly use DataHub MCP server functions, you can use prompts like:

```
Search DataHub for tables in the PIMCO_DEMO database that contain bond positions.

Then search for tables containing region information.

Then search for glossary terms related to "tax-exempt" bonds.

Use all this context to generate a SQL query for total positions by region for tax-exempt bonds.
```

---

## Key Differences: With vs Without DataHub

### Without DataHub Context:
- LLM sees opaque table names (e.g., `POS_9912`, `SEG_4421`)
- LLM doesn't know what columns mean (e.g., `SEGMENT_CD`, `STATUS_CD`)
- LLM doesn't understand relationships between tables
- LLM may generate incorrect SQL with wrong joins or filters

### With DataHub Context:
- LLM understands table purposes (e.g., `POS_9912` = aggregated bond positions)
- LLM knows column meanings (e.g., `SEGMENT_CD` = segment code, links to segment dimension)
- LLM understands relationships (e.g., `POS_9912` links to `DIM_SEG_4421` via `SEGMENT_CD`)
- LLM can access glossary terms for opaque business logic (e.g., "Position Status", "Maturity Multiplier")
- LLM generates correct SQL with proper joins, filters, and aggregations

---

## Tips for Best Results

1. **Be specific about what you're looking for**: Mention "bond positions", "tax-exempt", "by region", etc.

2. **Ask DataHub to search first**: Use prompts that explicitly ask DataHub to search for relevant tables/columns/terms

3. **Use glossary terms**: Reference business terms like "tax-exempt bonds", "adjusted market value", "maturity multiplier" - DataHub will find the related glossary terms

4. **Ask for context**: Explicitly ask Claude to use DataHub context before generating SQL

5. **Verify results**: After generating SQL, ask Claude to explain why it chose certain tables/joins based on the DataHub context

---

## Demo Flow

1. **Start without DataHub**: Ask Claude to generate SQL without DataHub context
   - Show the incorrect/guessed SQL
   - Explain why it's wrong (opaque names, missing joins, etc.)

2. **Enable DataHub MCP Server**: Configure DataHub MCP server in Claude Desktop

3. **Ask again with DataHub**: Use the same prompt but ask Claude to use DataHub context
   - Show the correct SQL with proper joins and filters
   - Explain how DataHub context helped

4. **Compare results**: Show side-by-side comparison of SQL queries and results

