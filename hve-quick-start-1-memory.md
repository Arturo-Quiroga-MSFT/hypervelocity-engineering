---
title: "HVE Quick Start 1: Set Your Context Once, Get Better Answers Always"
description: "Beginner-friendly guide for PSAs to configure the HVE Memory agent for persistent Copilot context"
author: Arturo Quiroga
ms.date: 2026-03-18
ms.topic: tutorial
keywords:
  - hve-core
  - memory agent
  - psa
  - quick start
  - beginner
estimated_reading_time: 2
---

## What You Will Learn

How to tell GitHub Copilot who you are and what you do, once, so every future interaction is grounded in your role as a Partner Solutions Architect (PSA).

## The Problem

Every time you open Copilot Chat and ask a question, you start from zero. Copilot has no idea you work with partners, that you focus on Azure AI services, or that your agents use Microsoft Agent Framework. You end up repeating the same context over and over.

## The Fix (30 Seconds)

1. Open VS Code with HVE Core installed.
2. Open Copilot Chat (`Cmd+Alt+I` on macOS, `Ctrl+Alt+I` on Windows).
3. In the agent picker, select **Memory**.
4. Type the following (adjust to match your actual focus areas):

```text
Remember that I am a Partner Solutions Architect. I help partners build
apps and services on Azure AI services. My AI agents are built with
Microsoft Agent Framework (MAF) and Microsoft Foundry Agent Services
(pro code). I primarily work with Python and C#.
```

5. Press Enter. Done.

## What Happens Next

The Memory agent stores your context persistently. From this point forward, every HVE agent and Copilot interaction can reference this information. When you ask a question about Azure OpenAI SDK usage or request an architecture diagram, Copilot already knows your role, your stack, and your partner-facing context.

You can update your memory at any time by selecting the Memory agent again and adding new details:

```text
Remember that I'm currently working with a partner building a
document processing solution using Azure Document Intelligence
and Azure OpenAI.
```

## Before and After

```mermaid
graph TD
    subgraph before ["Without Memory"]
        direction TB
        Q1["You: How do I build\na RAG agent?"] --> A1["Copilot: Generic answer\n(React? LangChain? Flask?)"]
        Q2["You: Use Azure OpenAI\nand MAF, I'm a PSA..."] --> A2["Copilot: Better answer\n(but you re-explained everything)"]
        Q3["Next session:\nstarts from zero again"] --> A3["Copilot: Who are you?"]
    end

    subgraph after ["With Memory"]
        direction TB
        M["One-time setup:\nMemory agent stores your role,\nstack, and partner context"] --> Q4["You: How do I build\na RAG agent?"]
        Q4 --> A4["Copilot: Here's a MAF-based\nagent on Foundry with\nAzure AI Search + OpenAI"]
    end

    style before fill:#FFEBEE,stroke:#E53935,color:#000
    style after fill:#E8F5E9,stroke:#388E3C,color:#000
    style M fill:#FFF9C4,stroke:#F9A825,color:#000
    style A1 fill:#FFCDD2,stroke:#E53935,color:#000
    style A2 fill:#FFE0B2,stroke:#FB8C00,color:#000
    style A3 fill:#FFCDD2,stroke:#E53935,color:#000
    style A4 fill:#C8E6C9,stroke:#388E3C,color:#000
```

## Why This Matters

| Without Memory | With Memory |
|---|---|
| Generic answers that ignore your role | Answers tailored to partner enablement |
| You re-explain your stack every session | Your stack is known automatically |
| Copilot suggests irrelevant frameworks | Copilot defaults to MAF, Foundry, Azure AI |

## Next Steps

* Try [Quick Start 2: Prep for a Partner Call in 5 Minutes](hve-quick-start-2-researcher.md) to see how your memory context improves research results.
* Explore the full [HVE Core Use Cases for PSAs](hve-core-use-cases-for-psa.md) when you are ready to go deeper.

---

*Part 1 of 3 in the HVE Quick Start series for Partner Solutions Architects*
