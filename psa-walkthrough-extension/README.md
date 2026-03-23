---
title: HVE PSA Onboarding Walkthrough Extension
description: "VS Code walkthrough extension that guides Partner Solutions Architects through HVE Core onboarding"
author: Arturo Quiroga
ms.date: 2026-03-20
ms.topic: overview
keywords:
  - hve-core
  - walkthrough
  - psa
  - onboarding
  - vs code extension
estimated_reading_time: 3
---

## Overview

A lightweight VS Code extension that provides a native Getting Started walkthrough for Partner Solutions Architects using HVE Core. Each step opens Copilot Chat with the right agent and prompt pre-filled.

## What it does

When installed, the walkthrough appears in the VS Code Getting Started tab with seven steps organized across three phases:

| Phase | Steps | What the PSA does |
|---|---|---|
| Configure, Learn, Visualize | 1. Memory, 2. Researcher, 3. Architecture Diagram | Set identity, research a topic, generate a diagram |
| Document, Demo, Deploy | 4. ADR, 5. Dashboard, 6. IaC Generator | Create a decision record, build a demo, scaffold infrastructure |
| Secure | 7. Security Review | Run security analysis on code |

Each step includes a "Run" button that opens Copilot Chat with the corresponding agent and a starter prompt. Steps auto-complete when the command runs.

## Development

### Prerequisites

- VS Code 1.90+
- Node.js 18+

### Run locally

1. Open the `psa-walkthrough-extension` folder in VS Code
2. Press `F5` to launch the Extension Development Host
3. In the new window, open the Command Palette and run **HVE: Open PSA Onboarding Walkthrough**

### Package as VSIX

```bash
cd psa-walkthrough-extension
npx @vscode/vsce package
```

This produces `hve-psa-walkthrough-0.1.0.vsix` that can be shared or installed with:

```bash
code --install-extension hve-psa-walkthrough-0.1.0.vsix
```

## Structure

```text
psa-walkthrough-extension/
  package.json        Walkthrough contribution points and commands
  extension.js        Command handlers that open Copilot Chat with prompts
  media/
    step-1-memory.md        Markdown content for step 1
    step-2-researcher.md    Markdown content for step 2
    step-3-arch-diagram.md  Markdown content for step 3
    step-4-adr.md           Markdown content for step 4
    step-5-dashboard.md     Markdown content for step 5
    step-6-iac.md           Markdown content for step 6
    step-7-security.md      Markdown content for step 7
```

## Upstream contribution path

This extension is a standalone prototype. The intended path is:

1. Validate the walkthrough flow with a small group of PSAs
2. Gather feedback on step content and prompt quality
3. Propose adding the `contributes.walkthroughs` section to HVE Core's `package.json` directly, eliminating the need for a separate extension

## Customization

### Changing prompts

Edit the `STEP_PROMPTS` object in `extension.js` to update the default prompts for each step.

### Adding steps

1. Add a new command in `package.json` under `contributes.commands`
2. Add a new step in `package.json` under `contributes.walkthroughs[0].steps`
3. Create a matching markdown file in `media/`
4. Add the command handler in `extension.js` under `STEP_PROMPTS`

### Replacing media with images

Swap `"markdown"` for `"image"` in any step's media property:

```json
"media": { "image": "media/step-1-memory.png", "altText": "Memory agent setup" }
```

SVGs with VS Code theme color variables are recommended for images that adapt to light/dark themes.
