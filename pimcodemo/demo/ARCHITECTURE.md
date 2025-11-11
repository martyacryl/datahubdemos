# PIMCO DataHub LLM Demo - Architecture & Story

## Overview

This demo showcases how **DataHub transforms LLM text-to-SQL generation** by providing context about opaque schema and table names. The architecture demonstrates a real-world data pipeline with Bronze → Silver → Gold transformations, enhanced by DataHub metadata for better AI context.

---

## The Story: Without vs. With DataHub

### The Problem: Opaque Names in Production

In real-world production systems, data engineers often use cryptic naming conventions:
- `POS_9912` - What does this mean?
- `SEG_4421` - What is this?
- `REG_7733` - How do I use this?

**Without DataHub**, LLMs see these opaque names and must guess what they mean, leading to incorrect SQL generation.

### The Solution: DataHub Provides Context

**With DataHub**, LLMs can retrieve context about:
- What each table contains
- What each column means
- How tables relate to each other
- Business terminology for cryptic names

This enables **correct SQL generation** with proper joins, filters, and aggregations.

---

## Data Architecture: Bronze → Silver → Gold

### Data Flow Diagram

```mermaid
graph TB
    subgraph Bronze["🗄️ BRONZE LAYER - Raw Data (BRZ_001)"]
        TX["TX_0421<br/>Transactions"]
        REF["REF_7832<br/>Bond Reference"]
        ISS["ISS_5510<br/>Issuer Info"]
    end
    
    subgraph Silver["✨ SILVER LAYER - Cleaned (SLV_009)"]
        DT1["DT_TXN_7821<br/>Cleaned Trans"]
        DT2["DT_DIM_BND_001<br/>Bond Dim"]
        DT3["DT_DIM_ISS_002<br/>Issuer Dim"]
        DIM1["DIM_REG_003<br/>Regions"]
        DIM2["DIM_SEG_4421<br/>Segments"]
        
        V1["VIEW: TXN_7821"]
        V2["VIEW: DIM_BND_001"]
        V3["VIEW: DIM_ISS_002"]
    end
    
    subgraph Gold["💎 GOLD LAYER - Reporting (GLD_003)"]
        DT4["DT_POS_9912<br/>Positions"]
        DT5["DT_SEG_4421<br/>Seg Agg"]
        DT6["DT_REG_7733<br/>Region Agg"]
        DT7["DT_ISS_8844<br/>Issuer Agg"]
        DT8["DT_GRO_5566<br/>Growth"]
        
        V4["VIEW: POS_9912"]
        V5["VIEW: SEG_4421"]
        V6["VIEW: REG_7733"]
        V7["VIEW: ISS_8844"]
        V8["VIEW: GRO_5566"]
    end
    
    TX -->|Dynamic Table| DT1
    REF -->|Dynamic Table| DT2
    ISS -->|Dynamic Table| DT3
    
    DT1 -->|Dynamic Table| DT4
    DT2 -->|Dynamic Table| DT4
    DT3 -->|Dynamic Table| DT4
    
    DT4 -->|Dynamic Table| DT5
    DT4 -->|Dynamic Table| DT6
    DT4 -->|Dynamic Table| DT7
    DT4 -->|Dynamic Table| DT8
    
    DT1 -.->|View| V1
    DT2 -.->|View| V2
    DT3 -.->|View| V3
    DT4 -.->|View| V4
    DT5 -.->|View| V5
    DT6 -.->|View| V6
    DT7 -.->|View| V7
    DT8 -.->|View| V8
    
    style Bronze fill:#ff9999
    style Silver fill:#99ccff
    style Gold fill:#99ff99
```

### Layer Details

#### 🗄️ Bronze Layer (BRZ_001) - Raw Data
- **TX_0421**: Raw bond transactions
- **REF_7832**: Bond reference data
- **ISS_5510**: Issuer information
- **Opaque naming** by design (simulates production systems)

#### ✨ Silver Layer (SLV_009) - Cleaned Data
- **Dynamic Tables**: Automatically transform bronze data
  - `DT_TXN_7821`: Cleaned transactions
  - `DT_DIM_BND_001`: Bond dimension
  - `DT_DIM_ISS_002`: Issuer dimension
- **Static Tables**: Reference dimensions
  - `DIM_REG_003`: Region lookup
  - `DIM_SEG_4421`: Segment lookup
- **Views**: Clean querying interface

#### 💎 Gold Layer (GLD_003) - Reporting Data
- **Dynamic Tables**: Auto-aggregated reporting data
  - `DT_POS_9912`: Aggregated positions
  - `DT_SEG_4421`: Segment aggregations
  - `DT_REG_7733`: Region aggregations
  - `DT_ISS_8844`: Issuer aggregations
  - `DT_GRO_5566`: Growth metrics
- **Views**: Business-friendly querying interface

---

## The Challenge: Opaque Names

### What LLMs See Without DataHub

```
PIMCO_DEMO Database
│
├── BRZ_001 (Bronze)
│   ├── TX_0421      ← What is this?
│   ├── REF_7832     ← What is this?
│   └── ISS_5510     ← What is this?
│
├── SLV_009 (Silver)
│   ├── DT_TXN_7821  ← What is this?
│   ├── DIM_BND_001  ← What is this?
│   └── DIM_ISS_002  ← What is this?
│
└── GLD_003 (Gold)
    ├── POS_9912     ← What is this?
    ├── SEG_4421     ← What is this?
    ├── REG_7733     ← What is this?
    ├── ISS_8844     ← What is this?
    └── GRO_5566     ← What is this?
```

### What LLMs Don't Know
- ❌ What `POS_9912` means
- ❌ What `SEGMENT_CD` contains
- ❌ How to join tables together
- ❌ What `TAX_EXEMPT_FLAG = 1` means
- ❌ Which tables have the data they need

**Result**: ❌ Guessing, wrong SQL, missing joins, incorrect filters

---

## The Solution: DataHub Context

### DataHub Metadata Layer

```mermaid
graph LR
    subgraph DataHub["📊 DataHub Cloud"]
        G["Business Glossary<br/>• Municipal Bond Position<br/>• Tax-Exempt Bond<br/>• Par Value<br/>• Market Value"]
        T["Tags<br/>• Municipal Bonds<br/>• Fixed Income<br/>• Gold Schema<br/>• Reporting"]
        D["Domains<br/>• Municipal Bonds<br/>• Trading Operations<br/>• Reporting & Analytics"]
        DOC["Documentation<br/>POS_9912: Aggregated bond positions<br/>SEGMENT_CD: Segment code<br/>PAR_VALUE: Total par value"]
        L["Lineage<br/>Bronze → Silver → Gold<br/>Tables → Dynamic Tables → Views"]
    end
    
    subgraph LLM["🤖 Claude Desktop"]
        MCP["DataHub MCP Server"]
        Query["User Query:<br/>'Show me total positions<br/>by region for tax-exempt bonds'"]
        SQL["Generated SQL<br/>✅ Correct"]
    end
    
    DataHub -->|MCP| MCP
    Query --> MCP
    MCP --> SQL
    
    style DataHub fill:#4a90e2,color:#fff
    style LLM fill:#ff6b6b,color:#fff
```

### What DataHub Provides

#### 📚 Business Glossary
Maps opaque names to business terms:
- `POS_9912` → **"Municipal Bond Position"**
- `SEGMENT_CD` → **"Bond Segment"**
- `PAR_VALUE` → **"Par Value"**
- `TAX_EXEMPT_FLAG` → **"Tax-Exempt Municipal Bond"**

#### 🏷️ Tags
Classification for discovery:
- `Municipal Bonds`, `Fixed Income`, `Gold Schema`, `Reporting`

#### 📁 Domains
Business area organization:
- `Municipal Bonds`, `Trading Operations`, `Reporting & Analytics`

#### 📝 Documentation
Table and column descriptions:
- `POS_9912`: "Aggregated bond positions table. Contains total positions by bond, issuer, region, and segment with par value and market value. This is the primary table for position reporting."
- `SEGMENT_CD`: "Segment code - TAX_EXEMPT or TAXABLE"
- `REGION_CD`: "Region code - links to DIM_REG_003 for region names"

#### 🔗 Lineage
Shows data flow:
- `BRZ_001.TX_0421` → `SLV_009.DT_TXN_7821` → `GLD_003.DT_POS_9912`
- `GLD_003.POS_9912` (view) → `GLD_003.DT_POS_9912` (dynamic table)

---

## Demo Flow: Before vs. After

### ❌ Without DataHub Context

```mermaid
sequenceDiagram
    participant User
    participant Claude
    participant Snowflake
    
    User->>Claude: "Show me total municipal bond<br/>positions by region for<br/>tax-exempt bonds"
    Claude->>Claude: Sees opaque names:<br/>POS_9912, SEGMENT_CD, REGION_CD
    Claude->>Claude: ❌ Doesn't know what they mean<br/>❌ Guesses relationships<br/>❌ Missing context
    Claude->>User: Generated SQL (WRONG):<br/>SELECT REGION_CD, SUM(PAR_VALUE)<br/>FROM GLD_003.POS_9912<br/>WHERE SEGMENT_CD = 'TAX_EXEMPT'
    User->>Snowflake: Execute SQL
    Snowflake->>User: ❌ Wrong results<br/>❌ Missing joins<br/>❌ No region names<br/>❌ Incorrect filter logic
```

**Issues:**
- Missing joins with dimension tables
- No region names (only codes)
- Wrong filter logic
- No understanding of data relationships

### ✅ With DataHub Context

```mermaid
sequenceDiagram
    participant User
    participant Claude
    participant DataHub
    participant Snowflake
    
    User->>Claude: "Show me total municipal bond<br/>positions by region for<br/>tax-exempt bonds"
    Claude->>DataHub: Query via MCP: "What is POS_9912?"
    DataHub->>Claude: "POS_9912 = Aggregated bond positions table"
    Claude->>DataHub: Query: "What is SEGMENT_CD?"
    DataHub->>Claude: "SEGMENT_CD = Segment code<br/>Links to DIM_SEG_4421<br/>TAX_EXEMPT_FLAG = 1 means tax-exempt"
    Claude->>DataHub: Query: "What is REGION_CD?"
    DataHub->>Claude: "REGION_CD = Region code<br/>Links to DIM_REG_003 for region names"
    Claude->>Claude: ✅ Understands context<br/>✅ Knows relationships<br/>✅ Has business terminology
    Claude->>User: Generated SQL (CORRECT):<br/>SELECT r.REGION_NAME,<br/>SUM(p.PAR_VALUE) as TOTAL_PAR_VALUE<br/>FROM GLD_003.POS_9912 p<br/>INNER JOIN SLV_009.DIM_SEG_4421 s<br/>ON p.SEGMENT_CD = s.SEGMENT_CD<br/>INNER JOIN SLV_009.DIM_REG_003 r<br/>ON p.REGION_CD = r.REGION_CD<br/>WHERE s.TAX_EXEMPT_FLAG = 1<br/>GROUP BY r.REGION_NAME
    User->>Snowflake: Execute SQL
    Snowflake->>User: ✅ Correct results<br/>✅ Proper joins<br/>✅ Business-friendly names<br/>✅ Accurate filters
```

**Success:**
- ✅ Correct joins with dimension tables
- ✅ Business-friendly column names
- ✅ Proper filter logic
- ✅ Understanding of data relationships

---

## Complete Architecture Diagram

```mermaid
graph TB
    subgraph Sources["📥 Data Sources"]
        ETL["ETL Systems<br/>Raw Data"]
        Legacy["Legacy Systems<br/>Cryptic Names"]
    end
    
    subgraph Bronze["🗄️ Bronze Layer (BRZ_001)"]
        TX["TX_0421<br/>Transactions"]
        REF["REF_7832<br/>Bond Ref"]
        ISS["ISS_5510<br/>Issuer Info"]
    end
    
    subgraph Silver["✨ Silver Layer (SLV_009)"]
        DT_Silver["Dynamic Tables<br/>DT_TXN_7821<br/>DT_DIM_BND_001<br/>DT_DIM_ISS_002"]
        Views_Silver["Views<br/>TXN_7821<br/>DIM_BND_001<br/>DIM_ISS_002"]
    end
    
    subgraph Gold["💎 Gold Layer (GLD_003)"]
        DT_Gold["Dynamic Tables<br/>DT_POS_9912<br/>DT_SEG_4421<br/>DT_REG_7733<br/>DT_ISS_8844<br/>DT_GRO_5566"]
        Views_Gold["Views<br/>POS_9912<br/>SEG_4421<br/>REG_7733<br/>ISS_8844<br/>GRO_5566"]
    end
    
    subgraph DataHub["📊 DataHub Cloud"]
        Glossary["Business Glossary<br/>Terms & Definitions"]
        Tags["Tags<br/>Classification"]
        Docs["Documentation<br/>Table & Column Descriptions"]
        Lineage["Lineage<br/>Data Flow"]
    end
    
    subgraph LLM["🤖 Claude Desktop"]
        MCP["DataHub MCP Server"]
        Query["User Query"]
        SQL["Generated SQL"]
    end
    
    Sources --> Bronze
    Bronze -->|Dynamic Tables| Silver
    Silver -->|Dynamic Tables| Gold
    
    Bronze -.->|Ingestion| DataHub
    Silver -.->|Ingestion| DataHub
    Gold -.->|Ingestion| DataHub
    
    DataHub -->|MCP Context| MCP
    Query --> MCP
    MCP --> SQL
    SQL --> Gold
    
    style Bronze fill:#ff9999,color:#000
    style Silver fill:#99ccff,color:#000
    style Gold fill:#99ff99,color:#000
    style DataHub fill:#4a90e2,color:#fff
    style LLM fill:#ff6b6b,color:#fff
```

---

## Example Queries: Before vs. After

### Example 1: Total Positions by Region for Tax-Exempt Bonds

#### ❌ Without DataHub Context

**Query:**
> "Show me total municipal bond positions by region for tax-exempt bonds"

**Generated SQL:**
```sql
SELECT 
    REGION_CD,
    SUM(PAR_VALUE) as total_par
FROM GLD_003.POS_9912
WHERE SEGMENT_CD = 'TAX_EXEMPT'
GROUP BY REGION_CD;
```

**Problems:**
- ❌ Returns region codes instead of names
- ❌ Missing join with `DIM_REG_003`
- ❌ Missing join with `DIM_SEG_4421`
- ❌ Wrong filter logic (should use `TAX_EXEMPT_FLAG = 1`)

#### ✅ With DataHub Context

**Query:**
> "Show me total municipal bond positions by region for tax-exempt bonds. Use DataHub to understand the schema."

**Generated SQL:**
```sql
SELECT 
    r.REGION_NAME,
    SUM(p.PAR_VALUE) as TOTAL_PAR_VALUE,
    SUM(p.MARKET_VALUE) as TOTAL_MARKET_VALUE,
    COUNT(DISTINCT p.BOND_ID) as POSITION_COUNT
FROM GLD_003.POS_9912 p
INNER JOIN SLV_009.DIM_SEG_4421 s ON p.SEGMENT_CD = s.SEGMENT_CD
INNER JOIN SLV_009.DIM_REG_003 r ON p.REGION_CD = r.REGION_CD
WHERE s.TAX_EXEMPT_FLAG = 1
  AND p.AS_OF_DATE = CURRENT_DATE()
GROUP BY r.REGION_NAME
ORDER BY TOTAL_PAR_VALUE DESC;
```

**Success:**
- ✅ Returns region names (business-friendly)
- ✅ Proper joins with dimension tables
- ✅ Correct filter logic (`TAX_EXEMPT_FLAG = 1`)
- ✅ Includes all relevant metrics

---

### Example 2: Position Growth Over Time

#### ❌ Without DataHub Context

**Generated SQL:**
```sql
SELECT 
    METRIC_DATE,
    SEGMENT_CD,
    TOTAL_PAR_VALUE
FROM GLD_003.GRO_5566
WHERE METRIC_DATE >= DATEADD(day, -30, CURRENT_DATE());
```

**Problems:**
- ❌ Returns segment codes instead of names
- ❌ Missing join with `DIM_SEG_4421`

#### ✅ With DataHub Context

**Generated SQL:**
```sql
SELECT 
    g.METRIC_DATE,
    s.SEGMENT_NAME,
    g.TOTAL_PAR_VALUE,
    g.TOTAL_MARKET_VALUE,
    g.VALUE_CHANGE,
    g.PCT_CHANGE
FROM GLD_003.GRO_5566 g
INNER JOIN SLV_009.DIM_SEG_4421 s ON g.SEGMENT_CD = s.SEGMENT_CD
WHERE g.METRIC_DATE >= DATEADD(day, -30, CURRENT_DATE())
ORDER BY g.METRIC_DATE DESC, s.SEGMENT_NAME;
```

**Success:**
- ✅ Returns segment names (business-friendly)
- ✅ Proper join with dimension table
- ✅ Includes all growth metrics

---

## Key Components Summary

### Data Layers

| Layer | Purpose | Tables | Dynamic Tables | Views |
|-------|---------|--------|----------------|-------|
| **Bronze** | Raw data | 3 tables | - | - |
| **Silver** | Cleaned data | 2 static | 5 dynamic | 3 views |
| **Gold** | Reporting data | - | 5 dynamic | 5 views |

### DataHub Metadata

| Component | Purpose | Examples |
|-----------|---------|----------|
| **Business Glossary** | Maps opaque names to business terms | `POS_9912` → "Municipal Bond Position" |
| **Tags** | Classification for discovery | Municipal Bonds, Gold Schema, Reporting |
| **Domains** | Business area organization | Municipal Bonds, Trading Operations |
| **Documentation** | Table/column descriptions | Explains what cryptic names mean |
| **Lineage** | Data flow visualization | Bronze → Silver → Gold |

### LLM Integration

| Component | Purpose |
|-----------|---------|
| **DataHub MCP Server** | Provides context to Claude Desktop |
| **Claude Desktop** | Generates SQL using DataHub context |
| **Snowflake** | Executes SQL queries |

---

## The Value Proposition

### Without DataHub

```
User Query
    ↓
LLM (No Context)
    ↓
❌ Wrong SQL
    ↓
❌ Wrong Results
    ↓
❌ User Frustration
```

### With DataHub

```
User Query
    ↓
LLM (With DataHub Context)
    ↓
✅ Correct SQL
    ↓
✅ Accurate Results
    ↓
✅ Business Value
```

### Key Benefits

1. **Faster Time to Insights**: No more guessing what tables mean
2. **Accurate SQL Generation**: Proper joins, filters, aggregations
3. **Business-Friendly Results**: Column names users understand
4. **Reduced Errors**: Fewer incorrect queries
5. **Better Decision-Making**: Reliable data for business decisions

---

## Real-World Application

### Production Scenario

```
┌─────────────────────────────────────────────────────────────┐
│  PRODUCTION DATA WAREHOUSE                                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  • ETL systems create tables with cryptic names              │
│  • Legacy systems use abbreviations (POS_9912, SEG_4421)    │
│  • Data warehouses use opaque naming conventions             │
│  • New team members don't understand the schema              │
│                                                              │
│  ❌ Without DataHub:                                         │
│     • LLMs guess what tables mean                           │
│     • Developers write incorrect SQL                         │
│     • Analysts struggle to find the right data              │
│     • Time wasted on debugging wrong queries                │
│                                                              │
│  ✅ With DataHub:                                            │
│     • LLMs understand schema via context                     │
│     • Developers generate correct SQL                        │
│     • Analysts find data quickly                             │
│     • Time saved, insights faster                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Demo Script

### Part 1: Set the Stage (2 minutes)

1. **Show the Problem**
   - Explain opaque naming in production systems
   - Show cryptic table names (`POS_9912`, `SEG_4421`, etc.)
   - Explain why this is a common challenge

2. **Show the Architecture**
   - Bronze → Silver → Gold flow
   - Dynamic tables doing transformations
   - Views providing clean querying

### Part 2: Without DataHub (3 minutes)

1. **Show User Query**
   - "Show me total municipal bond positions by region for tax-exempt bonds"

2. **Show Claude's Response (Without Context)**
   - Sees opaque names
   - Generates incorrect SQL
   - Missing joins, wrong filters

3. **Show Results**
   - Execute SQL in Snowflake
   - Show wrong/missing results
   - Explain the problems

### Part 3: With DataHub (5 minutes)

1. **Show DataHub Metadata**
   - Business glossary mapping opaque names
   - Documentation explaining tables
   - Tags and domains organizing data

2. **Show Claude's Response (With Context)**
   - Queries DataHub via MCP
   - Understands what tables mean
   - Generates correct SQL

3. **Show Results**
   - Execute SQL in Snowflake
   - Show correct results
   - Highlight the difference

### Part 4: The Value (2 minutes)

1. **Compare Before/After**
   - Side-by-side SQL comparison
   - Results comparison
   - Time saved

2. **Real-World Impact**
   - Faster time to insights
   - Accurate SQL generation
   - Better decision-making

---

## Visual Architecture Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                    COMPLETE DATA PIPELINE                         │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   BRONZE     │────▶│   SILVER     │────▶│    GOLD      │
│  (Raw Data)  │     │ (Cleaned)    │     │ (Reporting)  │
│              │     │              │     │              │
│  TX_0421     │     │  DT_TXN_7821 │     │  DT_POS_9912 │
│  REF_7832    │     │  DT_DIM_BND  │     │  DT_SEG_4421 │
│  ISS_5510    │     │  DT_DIM_ISS  │     │  DT_REG_7733 │
│              │     │              │     │  DT_ISS_8844 │
│              │     │              │     │  DT_GRO_5566  │
│              │     │              │     │              │
│              │     │  Views:      │     │  Views:      │
│              │     │  TXN_7821     │     │  POS_9912    │
│              │     │  DIM_BND_001 │     │  SEG_4421    │
│              │     │  DIM_ISS_002 │     │  REG_7733    │
│              │     │              │     │  ISS_8844    │
│              │     │              │     │  GRO_5566    │
└──────────────┘     └──────────────┘     └──────────────┘
       │                    │                    │
       │                    │                    │
       └────────────────────┼────────────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │   DATAHUB     │
                    │   (Metadata)  │
                    │               │
                    │  • Glossary    │
                    │  • Tags        │
                    │  • Domains     │
                    │  • Docs        │
                    │  • Lineage     │
                    └──────────────┘
                            │
                            │ MCP Server
                            ▼
                    ┌──────────────┐
                    │    CLAUDE     │
                    │  (LLM)        │
                    │               │
                    │  Generates    │
                    │  SQL with     │
                    │  Context      │
                    └──────────────┘
                            │
                            │ SQL Query
                            ▼
                    ┌──────────────┐
                    │   SNOWFLAKE   │
                    │  (Results)    │
                    │               │
                    │  ✅ Correct    │
                    │  ✅ Accurate   │
                    │  ✅ Fast       │
                    └──────────────┘
```

---

## Key Takeaways

### 🎯 The Problem
- Production systems use opaque naming conventions
- LLMs can't understand cryptic table/column names
- Without context, LLMs guess and generate incorrect SQL

### 💡 The Solution
- DataHub provides business glossary, documentation, tags, domains
- DataHub MCP server gives LLMs context about schema
- With context, LLMs generate correct SQL with proper joins and filters

### 📈 The Value
- **Faster Time to Insights**: No more guessing what tables mean
- **Accurate SQL Generation**: Proper joins, filters, aggregations
- **Business-Friendly Results**: Column names users understand
- **Reduced Errors**: Fewer incorrect queries
- **Better Decision-Making**: Reliable data for business decisions

---

## Architecture Highlights

### ✅ Clean Architecture
- **Bronze → Silver → Gold**: Clear data flow
- **Dynamic Tables**: Automatic transformations
- **Views**: Clean querying interface
- **No Redundancy**: No empty tables

### ✅ DataHub Integration
- **Business Glossary**: Maps opaque names to business terms
- **Documentation**: Explains what cryptic names mean
- **Tags & Domains**: Organizes data for discovery
- **Lineage**: Shows data flow clearly

### ✅ LLM Enhancement
- **MCP Server**: Provides context to Claude
- **Context-Aware SQL**: Generates correct queries
- **Business-Friendly**: Uses proper terminology

---

This architecture demonstrates how **DataHub transforms LLM text-to-SQL generation** by providing crucial context about opaque data structures, making AI-powered data querying practical for real-world production scenarios.

---

## Demo Checklist

- [ ] Show Bronze → Silver → Gold architecture
- [ ] Demonstrate opaque naming challenge
- [ ] Show DataHub metadata (glossary, tags, docs)
- [ ] Demo without DataHub (wrong SQL)
- [ ] Demo with DataHub (correct SQL)
- [ ] Compare before/after results
- [ ] Explain real-world value
- [ ] Answer questions

**Total Demo Time: ~12-15 minutes**
