---
title: "HVE Quick Start 7: Review Your Partner's Code for Security Before Production"
description: "Beginner-friendly guide for PSAs to use HVE security review capabilities for partner app security assessments"
author: Arturo Quiroga
ms.date: 2026-03-20
ms.topic: tutorial
keywords:
  - hve-core
  - security review
  - owasp
  - psa
  - quick start
  - beginner
estimated_reading_time: 3
---

## What You Will Learn

How to run a security-focused review of a partner's code or architecture before it goes to production, catching common vulnerabilities without being a security specialist yourself.

## The Problem

A partner is ready to deploy their Azure AI application to production. Before go-live, someone needs to review the code for security issues: hardcoded secrets, missing authentication, open endpoints, prompt injection risks in their AI layer. You are not a security engineer, and hiring one for a PoC review is overkill. But letting obvious issues slip through hurts the partner's trust and your credibility.

## The Fix (5 Minutes)

1. Open the partner's project in VS Code with HVE Core installed.
2. Open Copilot Chat (`Cmd+Alt+I` on macOS, `Ctrl+Alt+I` on Windows).
3. In the agent picker, select **PR Review** (which includes security analysis capabilities).
4. Point it at the code you want reviewed:

```text
Review this project for security issues before production deployment.
Focus on OWASP Top 10 risks: authentication, secrets management,
injection vulnerabilities, and API endpoint security. Also check for
AI-specific risks like prompt injection and data leakage in the RAG
pipeline.
```

5. The agent scans the codebase and returns findings organized by severity.

## How the Security Review Works

```mermaid
graph LR
    Code["Partner's\nCodebase"] --> Agent["PR Review /\nSecurity Analysis"]

    Agent --> Auth["Authentication\n& Access Control"]
    Agent --> Secrets["Secrets\nManagement"]
    Agent --> Injection["Injection\nVulnerabilities"]
    Agent --> AI["AI-Specific\nRisks"]

    Auth --> Report["Security\nFindings Report"]
    Secrets --> Report
    Injection --> Report
    AI --> Report

    Report --> Critical["Critical\n(Fix before deploy)"]
    Report --> Warning["Warning\n(Should fix)"]
    Report --> Info["Info\n(Best practice)"]

    style Code fill:#4FC3F7,stroke:#0288D1,color:#000
    style Agent fill:#FF7043,stroke:#E64A19,color:#fff
    style Auth fill:#CE93D8,stroke:#8E24AA,color:#000
    style Secrets fill:#CE93D8,stroke:#8E24AA,color:#000
    style Injection fill:#CE93D8,stroke:#8E24AA,color:#000
    style AI fill:#CE93D8,stroke:#8E24AA,color:#000
    style Report fill:#FFB74D,stroke:#FB8C00,color:#000
    style Critical fill:#EF5350,stroke:#C62828,color:#fff
    style Warning fill:#FFA726,stroke:#EF6C00,color:#000
    style Info fill:#66BB6A,stroke:#388E3C,color:#000
```

One review request in, severity-graded security findings out, organized by OWASP category.

## Common Security Issues the Review Catches

For Azure AI applications, the review typically flags:

* API keys or connection strings hardcoded in source (should use Azure Key Vault)
* Missing authentication on API endpoints exposed through App Service
* Azure OpenAI API keys passed in client-side code (should stay server-side)
* No input validation on user prompts before sending to Azure OpenAI (prompt injection risk)
* Overly permissive CORS settings on the web API
* Missing managed identity configuration (using keys instead of RBAC)
* Logging sensitive data (PII in chat histories, prompt content in application logs)

## More Examples for Common PSA Security Reviews

Adapt the prompt to the specific area you want to focus on:

```text
Review the authentication and authorization setup in this project.
The app uses Azure App Service with Easy Auth and calls Azure OpenAI.
Check that the auth flow is secure and that API keys are properly
managed through Key Vault.
```

```text
Review the RAG pipeline for data leakage risks. The app retrieves
documents from Azure AI Search and sends them to Azure OpenAI as
context. Check that document access control is enforced and that
sensitive content cannot leak through the AI responses.
```

```text
Review the Bicep infrastructure code for security misconfigurations.
Check for public endpoints that should be private, missing network
security groups, and overly permissive RBAC role assignments.
```

## Why This Matters

| No Security Review | With Security Review |
|---|---|
| Obvious vulnerabilities reach production | Critical issues caught before deploy |
| Partner loses trust if breached | Partner sees you add security value |
| You miss issues you are not trained to find | Agent checks OWASP Top 10 systematically |
| Security is an afterthought | Security becomes part of the delivery |

> [!IMPORTANT]
> This review is not a substitute for a professional security audit on high-sensitivity workloads. It catches common issues and enforces baseline security hygiene. For regulated industries (healthcare, finance), recommend the partner also engage a dedicated security review.

> [!TIP]
> Combine this with [Quick Start 6](hve-quick-start-6-iac-generator.md). When you generate IaC for the partner's environment, immediately follow up with a security review of the generated Bicep or Terraform to ensure the infrastructure is configured securely from day one.

## Next Steps

* You have completed the full HVE Quick Start series. You can now configure your tools, research topics, produce diagrams, document decisions, build demos, deploy infrastructure, and review security.
* Explore the full [HVE Core Use Cases for PSAs](hve-core-use-cases-for-psa.md) for advanced workflows including the RPI (Research, Plan, Implement) methodology, custom agent creation, and more.
* Return to the [Quick Start Series README](README.md) for the full learning path.

---

*Part 7 of 7 in the HVE Quick Start series for Partner Solutions Architects*
