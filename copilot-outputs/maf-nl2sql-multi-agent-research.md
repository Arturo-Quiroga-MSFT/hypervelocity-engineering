---
title: "MAF Multi-Agent NL2SQL + DBMS Assistant Research"
description: "Research findings on leveraging Microsoft Agent Framework for NL2SQL over large star schema databases with DBMS assistant capabilities"
ms.date: 2026-03-21
ms.topic: reference
author: PSA Onboarding Copilot
keywords:
  - NL2SQL
  - Microsoft Agent Framework
  - star schema
  - multi-agent
  - DBMS assistant
---

## Executive Summary

This document captures research on building a multi-agent NL2SQL + DBMS assistant
application using Microsoft Agent Framework (MAF). The target scenario involves large
star schema databases (100+ tables) where the system serves dual purposes:

1. **NL2SQL Pipeline** — translates natural language questions into SQL, executes them,
   and interprets results for business insights.
2. **DBMS Assistant** — provides database management capabilities including index
   recommendations, query optimization, schema exploration, and data profiling.

## MAF Orchestration Patterns

Microsoft Agent Framework provides five built-in orchestration patterns:

| Pattern | Description | Use Case |
|---------|-------------|----------|
| **Sequential** | Agents execute in a defined order, each receiving the previous agent's output | NL2SQL pipeline stages |
| **Concurrent** | Agents run in parallel, results aggregated | Schema retrieval + few-shot lookup |
| **Handoff** | Agents transfer control based on intent | Routing between NL2SQL and DBMS modes |
| **Group Chat** | Multiple agents collaborate in a shared conversation | Complex analytical planning |
| **Magentic** | LLM-driven dynamic orchestration | Adaptive query resolution |

### Recommended Architecture

Use **Handoff at the top level** to route between NL2SQL pipeline and DBMS assistant,
with **Sequential inside the NL2SQL pipeline** for the query generation flow.

```text
┌─────────────────────────────────────────────────────────┐
│                   Orchestrator Agent                     │
│            (Handoff pattern — intent routing)            │
├────────────────────────┬────────────────────────────────┤
│                        │                                │
│   NL2SQL Pipeline      │     DBMS Assistant             │
│   (Sequential)         │     (Tool-based)               │
│                        │                                │
│   ┌──────────────┐     │     ┌──────────────────────┐   │
│   │ Schema Agent  │     │     │ Index Advisor        │   │
│   └──────┬───────┘     │     ├──────────────────────┤   │
│          ▼             │     │ Query Optimizer      │   │
│   ┌──────────────┐     │     ├──────────────────────┤   │
│   │ Query Planner │     │     │ Schema Explorer      │   │
│   └──────┬───────┘     │     ├──────────────────────┤   │
│          ▼             │     │ Data Profiler        │   │
│   ┌──────────────┐     │     ├──────────────────────┤   │
│   │ SQL Generator │     │     │ Performance Monitor  │   │
│   └──────┬───────┘     │     ├──────────────────────┤   │
│          ▼             │     │ DDL Generator        │   │
│   ┌──────────────┐     │     └──────────────────────┘   │
│   │ SQL Validator │     │                                │
│   └──────┬───────┘     │                                │
│          ▼             │                                │
│   ┌──────────────┐     │                                │
│   │ Results Agent │     │                                │
│   └──────────────┘     │                                │
└────────────────────────┴────────────────────────────────┘
```

## NL2SQL State of the Art for Star Schemas

### SQL-of-Thought (SoT) — NeurIPS 2025 Workshop

The leading approach achieves **91.59% on Spider benchmark** using six specialized
agents. Key innovation: **taxonomy-guided error correction** rather than blind
regeneration.

SoT stages:

1. **Schema Linking** — identify relevant tables and columns
2. **Subproblem Decomposition** — break complex questions into atomic sub-queries
3. **Query Planning** — determine join paths, aggregation strategy
4. **SQL Generation** — produce SQL with schema context
5. **Error Correction** — classify errors by taxonomy, apply targeted fixes
6. **Result Validation** — verify output matches intent

### Tiered Schema Provision Strategy

For large star schemas (100+ tables), provide schema context in tiers to manage token
budgets:

| Tier | Content | Token Cost | When Used |
|------|---------|-----------|-----------|
| **Tier 1** | Schema summary — table names, descriptions, row counts | ~500 tokens | Always (routing) |
| **Tier 2** | Detailed schema for relevant tables — columns, types, keys, relationships | ~2K-5K tokens | After schema linking |
| **Tier 3** | Business glossary, few-shot examples, column statistics | ~1K-3K tokens | Complex or ambiguous queries |

### Star Schema-Specific Techniques

- **Fact-dimension awareness**: Teach the Schema Agent to identify fact tables
  (measures, foreign keys) vs. dimension tables (descriptive attributes, hierarchies)
- **Join path resolution**: Pre-compute common join paths between fact and dimension
  tables; store as metadata the Schema Agent retrieves
- **Aggregation patterns**: Maintain a library of common analytical patterns
  (YoY growth, running totals, top-N, cohort analysis) as few-shot examples
- **SCD handling**: Annotate slowly changing dimensions with effective date columns so
  the SQL Generator applies correct temporal filters

## Agent Definitions for MAF

### Agent 1 — Orchestrator (Handoff Pattern)

**Role**: Routes user requests to the appropriate pipeline.

```python
from microsoft.agents import Agent, HandoffBuilder

orchestrator = Agent(
    name="Orchestrator",
    instructions="""You route user requests to the appropriate specialist:
    - Questions about data, metrics, or insights → NL2SQL Pipeline
    - Questions about database management, performance, schema → DBMS Assistant
    Classify the intent and hand off to the correct agent.""",
    model="gpt-4o",
)

workflow = (
    HandoffBuilder()
    .add_agent(orchestrator)
    .add_agent(nl2sql_pipeline.as_tool())
    .add_agent(dbms_assistant.as_tool())
    .build()
)
```

### Agent 2 — Schema Agent

**Role**: Retrieves relevant schema context for a given natural language question.

**Tools**:

- `get_schema_summary()` — returns Tier 1 schema overview
- `get_table_details(table_names)` — returns Tier 2 details for specified tables
- `get_business_glossary(terms)` — returns Tier 3 business definitions
- `search_few_shot_examples(question)` — retrieves similar past queries

**Implementation approach**:

```python
from microsoft.agents import Agent, tool

@tool
def get_schema_summary(db_connection_id: str) -> str:
    """Return a summary of all tables in the star schema with names,
    descriptions, row counts, and table type (fact/dimension)."""
    # Query sys.tables + sys.extended_properties
    # Return formatted summary
    ...

@tool
def get_table_details(table_names: list[str]) -> str:
    """Return detailed schema for specified tables including columns,
    data types, primary/foreign keys, and column descriptions."""
    # Query INFORMATION_SCHEMA.COLUMNS + sys.extended_properties
    # Include foreign key relationships
    ...

schema_agent = Agent(
    name="SchemaAgent",
    instructions="""You are a star schema expert. Given a natural language question:
    1. First retrieve the schema summary to identify candidate tables
    2. Identify which fact and dimension tables are relevant
    3. Retrieve detailed schema for those tables
    4. Return the relevant schema context with join paths""",
    model="gpt-4o",
    tools=[get_schema_summary, get_table_details, get_business_glossary],
)
```

### Agent 3 — Query Planner

**Role**: Decomposes complex questions into sub-queries and plans the query strategy.

```python
query_planner = Agent(
    name="QueryPlanner",
    instructions="""You decompose complex analytical questions into a query plan.
    Given schema context and a question:
    1. Identify if this requires a single query or multiple sub-queries
    2. For each sub-query, specify: target tables, join conditions, filters,
       aggregations, and sort order
    3. Specify how sub-query results combine (UNION, JOIN, CTE chain)
    4. Flag any ambiguities that need clarification""",
    model="gpt-4o",
)
```

### Agent 4 — SQL Generator

**Role**: Generates SQL from the query plan and schema context.

```python
sql_generator = Agent(
    name="SQLGenerator",
    instructions="""You generate production-quality SQL from a query plan.
    Rules:
    - Use CTEs for readability over nested subqueries
    - Always qualify column names with table aliases
    - Use appropriate JOIN types (INNER for required, LEFT for optional)
    - Apply correct aggregation and GROUP BY
    - Handle NULLs explicitly
    - Add LIMIT/TOP for safety on unbounded queries
    - Target dialect: T-SQL (SQL Server / Azure SQL)""",
    model="gpt-4o",
)
```

### Agent 5 — SQL Validator and Executor

**Role**: Validates SQL syntax, explains the query, and executes it safely.

**Tools**:

- `validate_sql(query)` — dry-run parse without execution
- `explain_query_plan(query)` — get estimated execution plan
- `execute_query(query, max_rows)` — execute with row limit and timeout

```python
@tool
def execute_query(query: str, max_rows: int = 100) -> str:
    """Execute a SQL query with safety guardrails.
    - Enforces read-only (rejects DML/DDL)
    - Applies row limit via TOP/LIMIT
    - Enforces query timeout (30s default)
    - Returns results as markdown table"""
    ...

sql_validator = Agent(
    name="SQLValidator",
    instructions="""You validate and execute SQL queries.
    1. Check syntax correctness
    2. Verify all referenced tables/columns exist in the provided schema
    3. Check for common mistakes (missing GROUP BY, cartesian joins)
    4. If errors found, classify by type and suggest specific fixes
    5. Execute valid queries and return results""",
    model="gpt-4o",
    tools=[validate_sql, explain_query_plan, execute_query],
)
```

### Agent 6 — Results Interpreter

**Role**: Translates query results into business insights.

```python
results_interpreter = Agent(
    name="ResultsInterpreter",
    instructions="""You interpret SQL query results for business users.
    Given the original question, SQL query, and results:
    1. Summarize findings in plain language
    2. Highlight key metrics and trends
    3. Note any data quality concerns (NULLs, unexpected patterns)
    4. Suggest follow-up questions the user might want to explore
    5. Format numbers with appropriate units and precision""",
    model="gpt-4o",
)
```

### Agent 7 — DBMS Assistant

**Role**: Handles database management tasks using DMV-backed tools.

**Tools**:

```python
@tool
def get_missing_index_recommendations(top_n: int = 10) -> str:
    """Query sys.dm_db_missing_index_details and related DMVs
    to return top index recommendations ranked by improvement measure."""
    ...

@tool
def get_query_performance_stats(top_n: int = 20) -> str:
    """Query sys.dm_exec_query_stats for top resource-consuming queries
    with execution counts, avg duration, and logical reads."""
    ...

@tool
def get_table_statistics(table_name: str) -> str:
    """Profile a table: row count, size, column cardinality,
    NULL percentages, min/max/avg for numeric columns."""
    ...

@tool
def get_wait_stats() -> str:
    """Query sys.dm_os_wait_stats for current wait type distribution
    to identify performance bottlenecks."""
    ...

@tool
def generate_ddl(description: str) -> str:
    """Generate T-SQL DDL (CREATE TABLE, ALTER TABLE, CREATE INDEX)
    from a natural language description."""
    ...

@tool
def explore_schema(pattern: str) -> str:
    """Search tables and columns matching a pattern.
    Returns table names, column names, types, and descriptions."""
    ...

dbms_assistant = Agent(
    name="DBMSAssistant",
    instructions="""You are a database administration assistant for SQL Server.
    You help with:
    - Index recommendations and analysis
    - Query performance troubleshooting
    - Schema exploration and documentation
    - Data profiling and quality assessment
    - DDL generation for schema changes
    - Wait statistics and bottleneck analysis
    Always explain recommendations with rationale and impact estimates.""",
    model="gpt-4o",
    tools=[
        get_missing_index_recommendations,
        get_query_performance_stats,
        get_table_statistics,
        get_wait_stats,
        generate_ddl,
        explore_schema,
    ],
)
```

## Assembling the Sequential NL2SQL Pipeline

```python
from microsoft.agents import SequentialBuilder

nl2sql_pipeline = (
    SequentialBuilder()
    .add_agent(schema_agent)
    .add_agent(query_planner)
    .add_agent(sql_generator)
    .add_agent(sql_validator)
    .add_agent(results_interpreter)
    .build()
)
```

## Schema Metadata Strategy for Star Schemas

### Storing Metadata in SQL Server

Use `sys.extended_properties` to attach descriptions to tables and columns:

```sql
-- Table description
EXEC sp_addextendedproperty
    @name = N'MS_Description',
    @value = N'Fact table: daily sales transactions',
    @level0type = N'SCHEMA', @level0name = N'dbo',
    @level1type = N'TABLE', @level1name = N'FactSales';

-- Column description
EXEC sp_addextendedproperty
    @name = N'MS_Description',
    @value = N'Foreign key to DimDate (YYYYMMDD format)',
    @level0type = N'SCHEMA', @level0name = N'dbo',
    @level1type = N'TABLE', @level1name = N'FactSales',
    @level2type = N'COLUMN', @level2name = N'DateKey';

-- Custom property: table type
EXEC sp_addextendedproperty
    @name = N'TableType',
    @value = N'Fact',
    @level0type = N'SCHEMA', @level0name = N'dbo',
    @level1type = N'TABLE', @level1name = N'FactSales';
```

### Business Glossary as a Metadata Table

```sql
CREATE TABLE meta.BusinessGlossary (
    TermId INT IDENTITY PRIMARY KEY,
    Term NVARCHAR(200) NOT NULL,
    Definition NVARCHAR(MAX),
    RelatedTables NVARCHAR(MAX),  -- JSON array of table names
    RelatedColumns NVARCHAR(MAX), -- JSON array of schema.table.column
    Synonyms NVARCHAR(MAX),       -- JSON array of alternative terms
    Category NVARCHAR(100)
);
```

### Few-Shot Example Store

```sql
CREATE TABLE meta.FewShotExamples (
    ExampleId INT IDENTITY PRIMARY KEY,
    Question NVARCHAR(MAX) NOT NULL,
    SqlQuery NVARCHAR(MAX) NOT NULL,
    Explanation NVARCHAR(MAX),
    Difficulty NVARCHAR(20),      -- simple, medium, complex
    TablesUsed NVARCHAR(MAX),     -- JSON array
    EmbeddingVector VARBINARY(MAX) -- for similarity search
);
```

## Error Correction Taxonomy

Based on SQL-of-Thought research, classify SQL generation errors by type for targeted
correction:

| Error Type | Example | Fix Strategy |
|-----------|---------|-------------|
| **Schema error** | Wrong table/column name | Re-run schema linking with broader search |
| **Join error** | Missing JOIN, wrong join condition | Retrieve foreign key paths, add missing join |
| **Aggregation error** | Missing GROUP BY, wrong aggregate function | Validate GROUP BY matches non-aggregated SELECT columns |
| **Filter error** | Wrong WHERE condition, missing date filter | Re-examine question for implicit filters |
| **Syntax error** | T-SQL specific syntax issue | Parse error message, apply dialect-specific fix |
| **Logic error** | Query runs but wrong results | Compare against question intent, replan |

## Microsoft Reference Implementations

### Azure-Samples/azure-sql-nl2sql

- **Repo**: `github.com/Azure-Samples/azure-sql-nl2sql`
- **Pattern**: Two-expert model (Orchestrator + DatabaseExpertAgent)
- **Framework**: Semantic Kernel (predecessor pattern, migrateable to MAF)
- **Key technique**: On-demand schema retrieval via `sys.extended_properties`
- **Database**: AdventureWorks (star schema variant)

### SQL-AI-samples/MssqlMcp

- **Repo**: `github.com/SQL-AI-samples/MssqlMcp`
- **Pattern**: MCP server providing SQL tools via Model Context Protocol
- **Relevance**: Alternative to custom `@tool` implementations — provides pre-built
  SQL execution, schema introspection, and query tools
- **Consideration**: Can be used alongside MAF agents as an MCP tool source

## Deployment Options

| Option | Pros | Cons |
|--------|------|------|
| **Foundry Agent Services** | Managed hosting, built-in auth, scaling, tracing | Requires Foundry project setup |
| **Azure Container Apps** | Full control, custom networking | More operational overhead |
| **Azure Functions** | Event-driven, cost-efficient for low traffic | Cold start latency |
| **Local development** | Fast iteration, no cloud dependency | Not suitable for production |

## Evaluation Approach

### Benchmarks

- **Spider** — 10,181 questions across 200 databases; standard NL2SQL benchmark
- **BIRD** — 12,751 questions with emphasis on real-world dirty data and external
  knowledge
- **Custom star schema benchmark** — create a held-out test set from the target
  database with (question, gold SQL, expected results) triples

### Metrics

- **Execution accuracy** — does the generated query produce correct results?
- **Exact match accuracy** — does the SQL match the gold standard?
- **Query efficiency** — execution time and resource consumption vs. hand-written SQL
- **Error recovery rate** — how often does the error correction agent fix failures?

## Open Questions for Implementation

1. **Target database engine**: Azure SQL Database, SQL Server on-prem, or Synapse?
2. **Schema scale**: How many fact tables and dimension tables?
3. **Language preference**: Python (MAF Python SDK) or C# (MAF .NET SDK)?
4. **Deployment target**: Foundry Agent Services or Container Apps?
5. **Existing assets**: Any (question, SQL) pairs available for few-shot seeding?
6. **Security requirements**: Row-level security, data masking, or audit logging needs?
7. **MCP integration**: Use MssqlMcp server or build custom tools?
