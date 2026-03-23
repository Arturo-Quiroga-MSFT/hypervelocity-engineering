# Profisee: Semantic Kernel → Microsoft Agent Framework Migration Guide

**Partner:** PROFISEE  
**Use Case:** MDM Insights — Migrating Semantic Kernel agents to Microsoft Agent Framework  
**PSA:** Arturo Quiroga  
**Date:** March 2026  

---

## 1. Executive Summary

Profisee currently uses **Semantic Kernel (SK)** to power AI-driven insights into their Master Data Management (MDM) system. Microsoft has unified AutoGen and Semantic Kernel into the **Microsoft Agent Framework (MAF)**, making MAF the single production platform for agentic AI going forward. SK is now in **maintenance mode** — no new features will be added.

This guide provides a practical, step-by-step migration path from SK to MAF, specifically tailored to Profisee's MDM insights use case: generating data quality assessments, entity resolution recommendations, and natural-language insights over master data.

### Why Migrate Now

| Factor | Detail |
|--------|--------|
| **SK is in maintenance mode** | All new features, orchestration patterns, and enterprise capabilities land in MAF only |
| **MAF is GA** | Production-ready as of Q1 2026; RC5 packages available via pip/nuget |
| **Unified multi-agent orchestration** | MAF provides built-in graph-based workflows (sequential, parallel, group chat, handoff) that SK required custom code for |
| **Open standards** | Native MCP and A2A protocol support — directly aligns with Profisee's existing MCP Server |
| **Azure AI Foundry integration** | MAF agents deploy natively to Azure AI Foundry Agent Service with managed scaling, observability, and security |

---

## 2. Concept Mapping: Semantic Kernel → MAF

### Core Concepts

| Semantic Kernel Concept | MAF Equivalent | Notes |
|------------------------|----------------|-------|
| `Kernel` | `AIAgent` / `ChatCompletionClient` | No central kernel; agents are self-contained |
| `KernelPlugin` / `[KernelFunction]` | `AIFunctionFactory.Create()` / tool functions | Functions registered directly; no plugin class needed |
| `ChatCompletionService` | `IChatClient` (Microsoft.Extensions.AI) | Unified abstraction across providers |
| `KernelArguments` | Method parameters / agent context | Arguments passed directly to functions |
| `PromptTemplate` | Agent `instructions` / `system_message` | Inline instructions on agent construction |
| `Planner` (Handlebars/Stepwise) | MAF Orchestration Workflows | Graph-based: sequential, parallel, group chat |
| `AgentGroupChat` | `GroupChatOrchestration` | Built-in with selector strategies |
| `OpenAIAssistantAgent` | `FoundryAgentClient` / `AIAgent` | Managed via Azure AI Foundry |
| Semantic Memory / `IMemoryStore` | Azure AI Search + `VectorStoreTextSearch` | RAG patterns via search integration |
| `AutoFunctionInvocation` filter | Tool execution middleware | MAF supports tool-call interception |

### Namespace Changes

```
# Semantic Kernel (Python)
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.functions import kernel_function

# Microsoft Agent Framework (Python)
from agent_framework import AIAgent, AgentRuntime
from agent_framework.azure_ai import AzureAIAgentClient
from azure.ai.projects import AIProjectClient
```

```csharp
// Semantic Kernel (C#)
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Agents;
using Microsoft.SemanticKernel.Connectors.AzureOpenAI;

// Microsoft Agent Framework (C#)
using Microsoft.Extensions.AI;
using Microsoft.Agents.AI;
using Azure.AI.Projects;
```

---

## 3. Migration Patterns for Profisee MDM Insights

### Pattern A: SK Plugin → MAF Tool Function

Profisee's MDM insights app likely has SK plugins for querying master data, computing quality scores, and generating NL summaries. Here's how to migrate:

**Before (Semantic Kernel):**
```python
from semantic_kernel.functions import kernel_function

class MDMInsightsPlugin:
    @kernel_function(description="Get data quality score for an entity")
    async def get_quality_score(self, entity_type: str, entity_id: str) -> str:
        # Query Profisee REST API for entity
        entity = await profisee_client.get_entity(entity_type, entity_id)
        # Compute quality metrics
        score = compute_quality_metrics(entity)
        return json.dumps({
            "entity_id": entity_id,
            "completeness": score.completeness,
            "accuracy": score.accuracy,
            "overall": score.overall
        })

    @kernel_function(description="Search master data for matching entities")
    async def search_entities(self, query: str, domain: str) -> str:
        results = await profisee_client.search(query, domain=domain)
        return json.dumps([r.to_dict() for r in results])

# Registration
kernel = Kernel()
kernel.add_plugin(MDMInsightsPlugin(), plugin_name="mdm")
kernel.add_service(AzureChatCompletion(
    deployment_name="gpt-4o",
    endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY")
))

# Invocation
result = await kernel.invoke_prompt(
    "What is the data quality score for customer C-1234?",
    settings=PromptExecutionSettings(
        function_choice_behavior=FunctionChoiceBehavior.Auto()
    )
)
```

**After (Microsoft Agent Framework):**
```python
from agent_framework import AIAgent, AgentRuntime
from azure.ai.inference import ChatCompletionsClient
from azure.identity import DefaultAzureCredential

# Define tools as plain functions
async def get_quality_score(entity_type: str, entity_id: str) -> dict:
    """Get data quality score for an entity in Profisee MDM."""
    entity = await profisee_client.get_entity(entity_type, entity_id)
    score = compute_quality_metrics(entity)
    return {
        "entity_id": entity_id,
        "completeness": score.completeness,
        "accuracy": score.accuracy,
        "overall": score.overall
    }

async def search_entities(query: str, domain: str) -> list[dict]:
    """Search master data for matching entities in Profisee MDM."""
    results = await profisee_client.search(query, domain=domain)
    return [r.to_dict() for r in results]

# Create agent with tools
mdm_insights_agent = AIAgent(
    name="MDMInsightsAgent",
    instructions="""You are an MDM insights specialist for Profisee. 
    You help users understand the quality, completeness, and relationships 
    of their master data. Always provide actionable recommendations.""",
    model="gpt-4o",
    tools=[get_quality_score, search_entities],
    model_client=ChatCompletionsClient(
        endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        credential=DefaultAzureCredential()
    )
)

# Invocation
response = await mdm_insights_agent.run(
    "What is the data quality score for customer C-1234?"
)
```

**Key differences:**
- No `Kernel` object — agent is self-contained
- No plugin class or `@kernel_function` decorator — plain async functions
- Tools registered as a list on agent construction
- `DefaultAzureCredential` instead of API keys (best practice)

---

### Pattern B: SK Chat with Memory → MAF Agent with RAG

Profisee's insights app likely uses SK's semantic memory for contextual conversations about MDM content.

**Before (Semantic Kernel):**
```python
from semantic_kernel.memory import SemanticTextMemory
from semantic_kernel.connectors.memory.azure_ai_search import AzureAISearchMemoryStore

# Setup memory
memory_store = AzureAISearchMemoryStore(
    search_endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    admin_key=os.getenv("AZURE_SEARCH_KEY")
)
memory = SemanticTextMemory(storage=memory_store, embeddings_generator=embedding_service)

# Save MDM context to memory
await memory.save_information("mdm-entities", id="schema-customer",
    text="Customer entity has fields: Name, Email, Phone, Address, Industry, Revenue...")

# Query with memory-augmented chat
relevant = await memory.search("mdm-entities", "customer data quality", limit=5)
context = "\n".join([r.text for r in relevant])
result = await kernel.invoke_prompt(
    f"Context:\n{context}\n\nQuestion: {{{{$input}}}}",
    input="What fields are most commonly incomplete for customers?"
)
```

**After (Microsoft Agent Framework):**
```python
from agent_framework import AIAgent
from azure.search.documents import SearchClient
from azure.identity import DefaultAzureCredential

# Azure AI Search as RAG tool
search_client = SearchClient(
    endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    index_name="mdm-entities",
    credential=DefaultAzureCredential()
)

async def search_mdm_knowledge(query: str, top_k: int = 5) -> list[dict]:
    """Search MDM knowledge base for relevant entity information, schemas, and data quality rules."""
    results = search_client.search(
        search_text=query,
        query_type="semantic",
        semantic_configuration_name="mdm-semantic-config",
        top=top_k,
        select=["content", "entity_type", "category"]
    )
    return [{"content": r["content"], "entity_type": r["entity_type"]} for r in results]

# Agent with built-in RAG
mdm_knowledge_agent = AIAgent(
    name="MDMKnowledgeAgent",
    instructions="""You are an expert on Profisee MDM data models and quality rules.
    Use the search tool to find relevant information before answering.
    Cite specific entities, fields, and rules in your responses.""",
    model="gpt-4o",
    tools=[search_mdm_knowledge]
)

response = await mdm_knowledge_agent.run(
    "What fields are most commonly incomplete for customers?"
)
```

---

### Pattern C: SK Planner → MAF Multi-Agent Orchestration

For complex MDM insight workflows (e.g., "analyze this dataset, find quality issues, suggest fixes"):

**Before (Semantic Kernel — Stepwise Planner):**
```python
from semantic_kernel.planners import FunctionCallingStepwisePlanner

planner = FunctionCallingStepwisePlanner(kernel, max_iterations=10)
result = await planner.invoke(
    "Analyze customer domain data quality, identify the top issues, "
    "and generate a remediation plan"
)
```

**After (Microsoft Agent Framework — Multi-Agent Workflow):**
```python
from agent_framework import AIAgent, SequentialOrchestration, AgentRuntime

# Specialized agents
quality_analyst = AIAgent(
    name="QualityAnalyst",
    instructions="Analyze data quality metrics. Report completeness, accuracy, and consistency scores.",
    model="gpt-4o",
    tools=[get_quality_score, get_domain_statistics]
)

issue_detector = AIAgent(
    name="IssueDetector", 
    instructions="Identify the top data quality issues from the analysis. Rank by business impact.",
    model="gpt-4o",
    tools=[search_entities, get_validation_rules]
)

remediation_planner = AIAgent(
    name="RemediationPlanner",
    instructions="Generate actionable remediation plans with specific steps, owners, and timelines.",
    model="gpt-4o",
    tools=[get_stewardship_workflows, create_remediation_task]
)

# Sequential orchestration: analyst → detector → planner
workflow = SequentialOrchestration(
    agents=[quality_analyst, issue_detector, remediation_planner]
)

runtime = AgentRuntime()
result = await runtime.run(
    workflow,
    input="Analyze customer domain data quality, identify top issues, and generate a remediation plan"
)
```

---

## 4. Profisee MCP Server Integration

Profisee already has an **MCP (Model Context Protocol) Server** for Copilot connectivity. MAF has **native MCP support**, making this a natural integration point.

```python
from agent_framework import AIAgent
from agent_framework.mcp import MCPToolProvider

# Connect to Profisee's MCP Server
profisee_mcp = MCPToolProvider(
    server_url="https://profisee-instance.com/mcp",
    auth=DefaultAzureCredential()
)

# Agent automatically discovers Profisee tools via MCP
mdm_agent = AIAgent(
    name="ProfiseeMDMAgent",
    instructions="You provide insights on master data managed in Profisee MDM.",
    model="gpt-4o",
    tool_providers=[profisee_mcp]  # Tools auto-discovered from MCP server
)
```

This replaces any custom SK plugin wrappers around the Profisee REST API — the MCP server advertises available tools, and MAF agents consume them natively.

---

## 5. Step-by-Step Migration Plan

### Phase 1: Foundation (Weeks 1–2)

| Task | Description |
|------|-------------|
| **Inventory SK components** | Catalog all SK plugins, functions, memory stores, and planners in the current codebase |
| **Set up MAF environment** | `pip install agent-framework --pre azure-ai-projects azure-identity` |
| **Migrate simple tools first** | Convert `@kernel_function` methods to plain async functions |
| **Validate MCP connectivity** | Confirm MAF agent can discover and call tools from Profisee MCP Server |

### Phase 2: Core Agent Migration (Weeks 3–4)

| Task | Description |
|------|-------------|
| **Migrate chat/completion logic** | Replace `Kernel.invoke_prompt` with `AIAgent.run()` |
| **Migrate RAG patterns** | Replace SK memory stores with Azure AI Search tool functions |
| **Migrate multi-step workflows** | Replace SK planners with MAF orchestration (Sequential/Parallel) |
| **Integrate authentication** | Switch from API keys to `DefaultAzureCredential` (Managed Identity) |

### Phase 3: Multi-Agent & Production (Weeks 5–6)

| Task | Description |
|------|-------------|
| **Decompose into specialized agents** | Split monolithic SK kernel into focused agents (Quality, Resolution, Governance) |
| **Implement orchestration** | Wire agents into MAF workflows (sequential, group chat, handoff) |
| **Deploy to Azure AI Foundry** | Deploy agents to Foundry Agent Service for managed hosting |
| **Set up observability** | Configure Application Insights + OpenTelemetry tracing |

### Phase 4: Validation & Cutover (Week 7)

| Task | Description |
|------|-------------|
| **A/B testing** | Run SK and MAF side-by-side; compare insight quality and latency |
| **Load testing** | Validate performance at expected record volumes |
| **Cutover** | Switch production traffic to MAF agents |
| **Deprecate SK code** | Archive SK codebase; remove SK dependencies |

---

## 6. Migration Checklist

```
□ Inventory all SK plugins and kernel functions
□ Map each @kernel_function to a plain async function
□ Replace Kernel() with AIAgent() construction
□ Replace AzureChatCompletion service with ChatCompletionsClient
□ Replace SemanticTextMemory with Azure AI Search tool functions
□ Replace SK Planner with MAF SequentialOrchestration / GroupChatOrchestration
□ Replace API key auth with DefaultAzureCredential
□ Validate Profisee MCP Server integration via MCPToolProvider
□ Update pip dependencies (remove semantic-kernel, add agent-framework)
□ Configure Azure AI Foundry Agent Service deployment
□ Set up OpenTelemetry tracing and Application Insights
□ Run integration tests against Profisee MDM
□ Performance benchmark: compare SK vs MAF response times
□ Security review: confirm managed identity, Key Vault, network isolation
□ Update documentation and runbooks
```

---

## 7. Package Dependencies

### Remove (Semantic Kernel)
```
semantic-kernel
semantic-kernel[azure]
# Any semantic-kernel-* extras
```

### Add (Microsoft Agent Framework)
```
agent-framework>=1.0.0rc5
agent-framework-azure-ai>=1.0.0rc5
azure-ai-projects>=2.0.1
azure-ai-agents>=1.1.0
azure-identity
azure-search-documents>=11.5.0
azure-monitor-opentelemetry
```

---

## 8. Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| **MAF is RC (not full GA)** | Use `azure-ai-projects` (GA) for production-critical paths; MAF for orchestration layer |
| **Breaking API changes** | Pin package versions; subscribe to MAF release notes |
| **MCP protocol maturity** | Pin MCP protocol version; maintain REST API fallback for Profisee connectivity |
| **Performance regression** | Benchmark before cutover; MAF has lower overhead than SK's kernel pipeline |
| **Team skill gap** | Run a 1-day migration workshop; MAF is simpler than SK (less boilerplate) |

---

## 9. References

| Resource | URL |
|----------|-----|
| Official SK → MAF Migration Guide | https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-semantic-kernel/ |
| MAF DevBlog: Migration from SK/AutoGen | https://devblogs.microsoft.com/agent-framework/migrate-your-semantic-kernel-and-autogen-projects/ |
| MigrateX VS Code Extension (auto-migration tool) | https://marketplace.visualstudio.com/items?itemName=GenLabX.migratex |
| Microsoft Agent Framework (PyPI) | https://pypi.org/project/agent-framework/ |
| azure-ai-projects (PyPI) | https://pypi.org/project/azure-ai-projects/ |
| Profisee MCP Server | https://profisee.com/press-release/profisee-brings-end-to-end-master-data-management-fully-into-microsoft-fabric-at-fabcon-2026/ |
| Azure AI Foundry Agent Service | https://azure.microsoft.com/en-us/products/ai-foundry/agent-service/ |
| MAF Orchestration Patterns | https://azure-samples.github.io/azure-ai-travel-agents/MAF-README.html |

---

*Prepared for the PROFISEE partner engagement — Semantic Kernel to MAF migration*  
*Partner Solutions Architect: Arturo Quiroga — March 2026*
