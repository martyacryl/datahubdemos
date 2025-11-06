# PIMCO DataHub LLM Demo - Opaque Business Logic Story

## The Challenge: Understanding Complex Business Logic

### The Problem

In real-world data environments, business logic is often embedded in SQL transformations that are hard to understand without context. The `GLD_003.DT_POS_9912` dynamic table is a perfect example:

**What you see in Snowflake**:
- Opaque status codes: `STATUS_CD IN ('A', '1', 'Y')` - What do these mean?
- Opaque multipliers: `MATURITY_MULTIPLIER = 1.05` - Why 1.05? What's the logic?
- Opaque risk factors: `RISK_FACTOR = 0.98` - Why 0.98? What's the calculation?
- Complex market value: `MARKET_VALUE = PAR_VALUE * (1 + COUPON_RATE/100) * MATURITY_MULTIPLIER * RISK_FACTOR` - Why this formula?

**What you don't see**:
- Why status codes 'A', '1', 'Y' mean "active"
- Why maturity multiplier is 1.05 for bonds < 5 years to maturity
- Why risk factor is 0.98 for investment-grade bonds
- The business rationale behind the complex market value calculation

### The Solution: DataHub Context

DataHub provides the missing context:
- **Glossary Terms**: Explain what each opaque code means
- **Table Documentation**: Explains the business logic and rationale
- **Column Documentation**: Explains the opaque calculations
- **Business Rules**: Documents why the logic exists

## The Story: From Opaque to Clear

### Scene 1: The Analyst's Dilemma

**Analyst**: "I need to query total market value of active positions by segment for tax-exempt bonds."

**Without DataHub**:
- Sees `GLD_003.POS_9912` table
- Sees `STATUS_CD`, `MATURITY_MULTIPLIER`, `RISK_FACTOR` columns
- Doesn't know what they mean
- Guesses at the SQL
- Gets wrong results

**With DataHub**:
- Queries DataHub via MCP server
- Gets context about opaque codes
- Understands the business logic
- Generates correct SQL
- Gets accurate results

### Scene 2: The Opaque Business Logic

**The Dynamic Table** (`GLD_003.DT_POS_9912`) applies complex business rules:

1. **Status Code Filtering**: Only includes active positions
   - Opaque codes: 'A', '1', 'Y' = active (currently held)
   - Opaque codes: 'I', '0', 'N' = inactive (sold/closed, excluded)
   - Business rule: Only active positions are included in reporting

2. **Maturity Multiplier**: Adjusts for time value
   - < 5 years to maturity → multiplier 1.05 (premium for near-term bonds)
   - 5-10 years → multiplier 1.02 (moderate premium)
   - > 10 years → multiplier 1.0 (no premium)
   - Business rationale: Reflects time value and liquidity premium for bonds approaching maturity

3. **Risk Factor**: Adjusts for credit risk
   - AAA/AA/A (investment grade) → risk factor 0.98 (lower risk, slight discount)
   - BBB/BB/B (speculative grade) → risk factor 1.0 (standard risk)
   - Others → risk factor 1.05 (higher risk premium)
   - Business rationale: Adjusts market value to reflect credit risk premiums

4. **Adjusted Market Value**: Complex calculation
   - Formula: `PAR_VALUE * (1 + COUPON_RATE/100) * MATURITY_MULTIPLIER * RISK_FACTOR`
   - Business rationale: Provides adjusted market value reflecting maturity premium and credit risk

### Scene 3: The DataHub Context

**DataHub provides**:
- **Glossary Terms**: 
  - "Position Status" - explains opaque codes ('A'/'1'/'Y' = active)
  - "Maturity Multiplier" - explains opaque calculation (< 5 years = 1.05)
  - "Risk Factor" - explains opaque credit rating mapping
  - "Adjusted Market Value" - explains complex formula

- **Table Documentation**:
  - Explains the opaque business logic
  - Documents the status code filtering
  - Explains the maturity multiplier calculation
  - Explains the risk factor calculation
  - Documents the complex market value formula

- **Column Documentation**:
  - `STATUS_CD`: Explains opaque codes and filtering logic
  - `MATURITY_MULTIPLIER`: Explains opaque calculation and business rationale
  - `RISK_FACTOR`: Explains opaque credit rating mapping
  - `MARKET_VALUE`: Explains complex formula and components

## The Demo Flow

### Step 1: Show the Problem (Without DataHub)

1. **Ask Claude**: "Show me total market value of active positions by segment for tax-exempt bonds"
2. **Claude generates SQL** without understanding:
   - Doesn't know STATUS_CD opaque codes
   - Doesn't know to filter by STATUS_CD
   - Doesn't understand adjusted market value
   - Uses wrong segment code
3. **Show incorrect results** or empty results

### Step 2: Show the Solution (With DataHub)

1. **Ask Claude**: "Show me total adjusted market value of active positions by segment for tax-exempt bonds. Use DataHub to understand the opaque business logic."
2. **Claude queries DataHub** via MCP server:
   - Gets context about STATUS_CD opaque codes
   - Understands maturity multiplier calculation
   - Understands risk factor calculation
   - Understands adjusted market value formula
3. **Claude generates correct SQL**:
   - Filters by STATUS_CD IN ('A', '1', 'Y') for active positions
   - Uses correct segment code ('001' for tax-exempt)
   - Joins with dimension tables for readable names
   - Includes AS_OF_DATE filter for current positions
4. **Show correct results** with proper aggregations

### Step 3: Explain the Value

**Key Points**:
- **Without DataHub**: LLM sees opaque codes and guesses
- **With DataHub**: LLM understands the business logic
- **Result**: Correct SQL and accurate results
- **Value**: DataHub provides the context that Snowflake doesn't have

## The Narrative

### The Challenge

In production data environments, business logic is often embedded in SQL transformations that are hard to understand without context. The `GLD_003.DT_POS_9912` dynamic table applies complex business rules:

- **Opaque status codes** filter to only active positions
- **Opaque maturity multipliers** adjust for time value
- **Opaque risk factors** adjust for credit risk
- **Complex market value formula** uses all factors

Without DataHub, an LLM sees these opaque codes and calculations but doesn't understand:
- What the codes mean
- Why the multipliers exist
- How the risk factors are calculated
- The business rationale behind the formula

### The Solution

DataHub provides the missing context:
- **Glossary terms** explain what each opaque code means
- **Table documentation** explains the business logic and rationale
- **Column documentation** explains the opaque calculations
- **Business rules** document why the logic exists

When an LLM queries DataHub via MCP server, it gets:
- Context about opaque status codes ('A'/'1'/'Y' = active)
- Understanding of maturity multiplier calculation (< 5 years = 1.05)
- Understanding of risk factor calculation (AAA/AA/A = 0.98)
- Understanding of adjusted market value formula

### The Result

With DataHub context, the LLM can:
- Generate correct SQL that filters by STATUS_CD for active positions
- Understand the complex market value calculation
- Use correct segment codes ('001' for tax-exempt)
- Join with dimension tables for readable names
- Include proper filters (AS_OF_DATE, STATUS_CD, SEGMENT_CD)

Without DataHub context, the LLM:
- Guesses at opaque codes
- Doesn't understand the business logic
- Generates incorrect SQL
- Gets wrong or empty results

## Key Takeaways

1. **Opaque Business Logic**: Real-world SQL often contains opaque codes and calculations that aren't obvious
2. **DataHub Context**: DataHub provides the missing context that explains the opaque logic
3. **LLM Understanding**: With DataHub context, LLMs can understand and generate correct SQL
4. **Business Value**: DataHub enables LLMs to work with complex business logic that Snowflake doesn't document

