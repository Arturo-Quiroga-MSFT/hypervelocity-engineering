---
title: HVE PSA Onboarding Walkthrough Extension
description: "VS Code walkthrough extension that guides Partner Solutions Architects through HVE Core onboarding"
author: Arturo Quiroga
ms.date: 2026-03-23
ms.topic: overview
keywords:
  - hve-core
  - walkthrough
  - psa
  - onboarding
  - vs code extension
  - github copilot
  - azure ai
estimated_reading_time: 5
---

<!-- markdownlint-disable MD033 -->

<h1 align="center">HVE PSA Onboarding Walkthrough</h1>

<p align="center">
  <strong>From zero to partner-ready in seven AI-powered steps</strong><br/>
  A native VS Code walkthrough that puts GitHub Copilot agents to work for Partner Solutions Architects.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/VS_Code-1.90+-blue?logo=visualstudiocode" alt="VS Code 1.90+">
  <img src="https://img.shields.io/badge/HVE_Core-Required-purple" alt="HVE Core Required">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="MIT License">
  <img src="https://img.shields.io/badge/Version-0.2.0-orange" alt="Version 0.2.0">
</p>

---

## The Problem

Partner Solutions Architects juggle research, architecture diagrams, decision records, live demos, infrastructure code, and security reviews across dozens of tools. Preparing for a single partner engagement can take hours of context-switching.

## The Solution

This extension replaces that scattered workflow with a single guided walkthrough inside VS Code. Each step calls a specialized Copilot agent with a contextual prompt, and every step automatically threads your partner engagement context so the output is relevant from the start.

> [!TIP]
> Set your partner context once in Step 1, and all seven steps generate prompts tailored to your specific engagement instead of generic samples.

---

## How It Works

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': {'lineColor': '#ffffff', 'edgeLabelBackground': '#1e1e1e'}}}%%
flowchart TD
    subgraph VSCode["VS Code Getting Started Tab"]
        subgraph Walkthrough["PSA Onboarding Walkthrough"]
            S1["Step 1\n@memory"] --> S2["Step 2\n@researcher-subagent"]
            S2 --> S3["Step 3\n@arch-diagram-builder"]
            S3 --> S4["Step 4\n@adr-creation"]
            S4 --> S5["Step 5\n@gen-streamlit-dashboard"]
            S5 --> S6["Step 6\n@azure-iac-generator"]
            S6 --> S7["Step 7\n@pr-review"]
        end
    end
    S1 & S2 & S3 & S4 & S5 & S6 & S7 --> Chat["Copilot Chat Panel\n(agent + prompt pre-filled)"]

    style VSCode fill:#1e1e1e,stroke:#007acc,color:#fff
    style Walkthrough fill:#252526,stroke:#007acc,color:#fff
    style Chat fill:#0e639c,stroke:#007acc,color:#fff
    linkStyle default stroke:#ffcc00,stroke-width:2px
```

Each "Run" button opens Copilot Chat with the right agent and a starter prompt. Steps auto-complete when the command executes.

---

## The Seven Steps

The walkthrough follows three phases that mirror a typical partner engagement lifecycle:

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': {'lineColor': '#ffffff', 'edgeLabelBackground': '#1e1e1e'}}}%%
flowchart LR
    subgraph P1["Phase 1: Configure · Learn · Visualize"]
        S1["1 MEMORY\n@memory\n~30s"]
        S2["2 RESEARCH\n@researcher-subagent\n~2 min"]
        S3["3 DIAGRAM\n@arch-diagram-builder\n~3 min"]
        S1 --> S2 --> S3
    end
    subgraph P2["Phase 2: Document · Demo · Deploy"]
        S4["4 ADR\n@adr-creation\n~2 min"]
        S5["5 DASHBOARD\n@gen-streamlit-dashboard\n~5 min"]
        S6["6 IaC\n@azure-iac-generator\n~5 min"]
        S4 --> S5 --> S6
    end
    subgraph P3["Phase 3: Secure"]
        S7["7 SECURITY\n@pr-review\n~5 min"]
    end

    S3 --> S4
    S6 --> S7

    S1 -.- O1["Identity &\npartner context"]
    S2 -.- O2["Technical\nbriefing"]
    S3 -.- O3["Mermaid\ndiagram"]
    S4 -.- O4["Decision\nrecord"]
    S5 -.- O5["Streamlit\ndemo app"]
    S6 -.- O6["Bicep /\nTerraform"]
    S7 -.- O7["OWASP &\nAI risk findings"]

    style P1 fill:#264f78,stroke:#007acc,color:#fff
    style P2 fill:#4b3267,stroke:#c586c0,color:#fff
    style P3 fill:#4e3a1a,stroke:#ce9178,color:#fff
    style O1 fill:none,stroke:none,color:#888
    style O2 fill:none,stroke:none,color:#888
    style O3 fill:none,stroke:none,color:#888
    style O4 fill:none,stroke:none,color:#888
    style O5 fill:none,stroke:none,color:#888
    style O6 fill:none,stroke:none,color:#888
    style O7 fill:none,stroke:none,color:#888
    linkStyle default stroke:#ffcc00,stroke-width:2px
```

### Phase 1: Configure, Learn, Visualize

| Step | Agent | You provide | You get |
|------|-------|-------------|---------|
| **1. Set Your Context** | `@memory` | Your role, tech stack, partner engagement | Persistent Copilot context that threads through every step |
| **2. Prep for a Partner Call** | `@researcher-subagent` | A topic or question | Structured briefing with SDK versions, limitations, recommendations |
| **3. Architecture Diagram** | `@arch-diagram-builder` | Plain English architecture description | Professional Mermaid diagram ready for docs or slides |

### Phase 2: Document, Demo, Deploy

| Step | Agent | You provide | You get |
|------|-------|-------------|---------|
| **4. Architecture Decision Record** | `@adr-creation` | A decision and its context | Formal ADR with alternatives, trade-offs, consequences |
| **5. Demo Dashboard** | `@gen-streamlit-dashboard` | Demo scenario description | Runnable Streamlit app with mock data and clean UI |
| **6. Infrastructure as Code** | `@azure-iac-generator` | Required Azure resources | Deployable Bicep with dependencies, naming, parameters |

### Phase 3: Secure

| Step | Agent | You provide | You get |
|------|-------|-------------|---------|
| **7. Security Review** | `@pr-review` | Your project code | Severity-graded findings covering OWASP Top 10 and AI-specific risks |

---

## Context Threading

The extension's most powerful feature is automatic context threading. When you set your partner engagement context in Step 1, every subsequent step uses it:

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': {'lineColor': '#ffffff', 'edgeLabelBackground': '#1e1e1e'}}}%%
flowchart TD
    CTX["Set Partner Context\n\nContoso: customer support chatbot\nusing Azure OpenAI + AI Search\nfor RAG over insurance claims docs"]

    CTX -->|"context = {context}"| S2["Step 2: Research\nRAG patterns"]
    CTX -->|"context = {context}"| S3["Step 3: Diagram\nRAG pipeline"]
    CTX -->|"context = {context}"| S4["Step 4: ADR\nAzure OpenAI choice"]
    CTX -->|"context = {context}"| S5["Step 5: Demo\nRAG chat app"]
    CTX -->|"context = {context}"| S6["Step 6: Bicep\nOpenAI + AI Search"]
    CTX -->|"context = {context}"| S7["Step 7: Security\nRAG pipeline review"]

    style CTX fill:#0e639c,stroke:#007acc,color:#fff
    linkStyle default stroke:#ffcc00,stroke-width:2px
```

> [!NOTE]
> Without partner context, each step uses a sensible default prompt. Context is stored in `workspaceState` and persists across VS Code sessions.

---

## Quick Start

### Prerequisites

* VS Code 1.90+
* **HVE Core - All** extension pack installed
* GitHub Copilot active

### Install and Run

```bash
# Install from VSIX
code --install-extension hve-psa-walkthrough-0.2.0.vsix
```

Then open the Command Palette (`Cmd+Shift+P`) and run:

```text
HVE: Open PSA Onboarding Walkthrough
```

The walkthrough appears in the VS Code Getting Started tab.

---

## Development

### Run locally

1. Open the `psa-walkthrough-extension` folder in VS Code
2. Press **F5** to launch the Extension Development Host
3. In the new window, run **HVE: Open PSA Onboarding Walkthrough** from the Command Palette

### Package as VSIX

```bash
cd psa-walkthrough-extension
npx @vscode/vsce package
```

---

## Architecture

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': {'lineColor': '#ffffff', 'nodeBorder': '#ffcc00', 'clusterBorder': '#007acc'}}}%%
flowchart LR
    subgraph ext["psa-walkthrough-extension/"]
        PJ["package.json\n\nWalkthrough contribution\npoints, commands, step\ndefinitions + media refs"]
        EJ["extension.js\n\nbuildPrompt()\nsendToChat()\nactivate()"]
        subgraph media["media/"]
            M1["step-1-memory.md"]
            M2["step-2-researcher.md"]
            M3["step-3-arch-diagram.md"]
            M4["step-4-adr.md"]
            M5["step-5-dashboard.md"]
            M6["step-6-iac.md"]
            M7["step-7-security.md"]
        end
    end

    style ext fill:#1e1e1e,stroke:#007acc,stroke-width:2px,color:#fff
    style media fill:#252526,stroke:#ffcc00,stroke-width:2px,color:#ccc
    style PJ fill:#264f78,stroke:#ffcc00,stroke-width:2px,color:#fff
    style EJ fill:#4b3267,stroke:#ffcc00,stroke-width:2px,color:#fff
    style M1 fill:#333,stroke:#ffcc00,stroke-width:1px,color:#ccc
    style M2 fill:#333,stroke:#ffcc00,stroke-width:1px,color:#ccc
    style M3 fill:#333,stroke:#ffcc00,stroke-width:1px,color:#ccc
    style M4 fill:#333,stroke:#ffcc00,stroke-width:1px,color:#ccc
    style M5 fill:#333,stroke:#ffcc00,stroke-width:1px,color:#ccc
    style M6 fill:#333,stroke:#ffcc00,stroke-width:1px,color:#ccc
    style M7 fill:#333,stroke:#ffcc00,stroke-width:1px,color:#ccc
```

### Data Flow

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': {'lineColor': '#ffffff', 'edgeLabelBackground': '#1e1e1e'}}}%%
flowchart LR
    PJ["package.json\n\nDefines UI steps\nand commands"] --> EJ["extension.js\n\nSTEP_PROMPTS +\npartner context merge\n\nBuilds final prompt"]
    EJ --> CC["Copilot Chat\n\n@agent + contextual\nprompt\n\nReceives and executes"]

    style PJ fill:#264f78,stroke:#007acc,color:#fff
    style EJ fill:#4b3267,stroke:#c586c0,color:#fff
    style CC fill:#0e639c,stroke:#007acc,color:#fff
    linkStyle default stroke:#ffcc00,stroke-width:2px
```

---

## Customization

### Changing prompts

Edit the `STEP_PROMPTS` object in `extension.js`. Each step has two variants:

* `prompt` — default prompt used when no partner context is set
* `contextualPrompt` — template with `{context}` placeholder that gets replaced with the partner's engagement description

### Adding a new step

1. Add a command in `package.json` under `contributes.commands`
2. Add a step in `package.json` under `contributes.walkthroughs[0].steps`
3. Create a markdown file in `media/`
4. Add an entry in `STEP_PROMPTS` in `extension.js`

### Swapping markdown for images

Replace `"markdown"` with `"image"` in any step's media property:

```json
"media": { "image": "media/step-1-memory.png", "altText": "Memory agent setup" }
```

> [!TIP]
> SVGs with VS Code theme color variables adapt to both light and dark themes.

---

## Upstream Contribution Path

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': {'lineColor': '#ffffff', 'edgeLabelBackground': '#1e1e1e'}}}%%
flowchart LR
    Current["Standalone VSIX\nextension\n(this repo)"] -->|"Propose merge"| Target["HVE Core native\nwalkthrough\n(package.json)"]

    Current -.- Steps["1. Validate with PSAs\n2. Gather feedback\n3. Merge into HVE Core"]
    Target -.- Benefit["No separate install —\nships with HVE Core\nfor all PSAs"]

    style Current fill:#264f78,stroke:#007acc,color:#fff
    style Target fill:#0e639c,stroke:#007acc,color:#fff
    style Steps fill:none,stroke:none,color:#888
    style Benefit fill:none,stroke:none,color:#888
    linkStyle default stroke:#ffcc00,stroke-width:2px
```

---

## License

MIT
