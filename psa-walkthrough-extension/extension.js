const vscode = require("vscode");

// ---------------------------------------------------------------------------
// Partner context key used in workspaceState
// ---------------------------------------------------------------------------
const CTX_KEY = "hve-psa.partnerContext";

// ---------------------------------------------------------------------------
// Step definitions: generic prompt + contextual prompt with {context} placeholder
// When the user sets partner context, all steps automatically thread it through.
// ---------------------------------------------------------------------------
const STEP_PROMPTS = {
  "hve-psa.step.memory": {
    agent: "@memory",
    title: "Set Your Context Once",
    prompt:
      "Remember that I am a Partner Solutions Architect. I help partners build apps and services on Azure AI services. My AI agents are built with Microsoft Agent Framework (MAF) and Microsoft Foundry Agent Services (pro code). I primarily work with Python and C#.",
    contextualPrompt:
      "Remember that I am a Partner Solutions Architect. I help partners build apps and services on Azure AI services. My AI agents are built with Microsoft Agent Framework (MAF) and Microsoft Foundry Agent Services (pro code). I primarily work with Python and C#. My current partner engagement: {context}",
  },
  "hve-psa.step.researcher": {
    agent: "@researcher-subagent",
    title: "Prep for a Partner Call",
    prompt:
      "Research how Azure AI Search integrates with Azure OpenAI for a RAG pattern. Include current SDK versions for Python, key limitations, recommended indexing strategies, and a simple architecture overview.",
    contextualPrompt:
      "I am preparing for a partner call. Partner context: {context}. Research the Azure services and integration patterns most relevant to this engagement. Include current SDK versions for Python, key limitations, recommended architecture patterns, and a simple architecture overview.",
  },
  "hve-psa.step.archDiagram": {
    agent: "@arch-diagram-builder",
    title: "Create Architecture Diagram",
    prompt:
      "Create an architecture diagram for a partner's customer support app. The app uses Azure OpenAI for chat completions, Azure AI Search for document retrieval (RAG pattern), Azure Blob Storage for storing knowledge base documents, and Azure App Service for hosting the web frontend.",
    contextualPrompt:
      "Create an architecture diagram for the following partner engagement: {context}. Identify the Azure services involved and show the data flow between components. Output a Mermaid diagram.",
  },
  "hve-psa.step.adr": {
    agent: "@adr-creation",
    title: "Document Architecture Decision",
    prompt:
      "We chose Azure OpenAI over a self-hosted Llama model for the partner's customer support agent. The partner needs enterprise SLA guarantees, built-in content filtering for compliance, and managed scaling. They don't have a dedicated ML ops team.",
    contextualPrompt:
      "Write an Architecture Decision Record (ADR) for a key technology decision in this partner engagement: {context}. Identify the most important architecture choice, list the alternatives considered, and document the rationale for the chosen approach.",
  },
  "hve-psa.step.dashboard": {
    agent: "@gen-streamlit-dashboard",
    title: "Build Demo Dashboard",
    prompt:
      "Create a Streamlit dashboard for a RAG demo. The user types a question, the app sends it to Azure AI Search for relevant documents, then passes the question and context to Azure OpenAI (GPT-4o) for an answer. Display the answer and source documents with relevance scores.",
    contextualPrompt:
      "Create a Streamlit demo dashboard for this partner engagement: {context}. The dashboard should showcase the core functionality the partner needs. Include interactive inputs, mock data, and a clean UI that the partner can see in a live demo.",
  },
  "hve-psa.step.iac": {
    agent: "@azure-iac-generator",
    title: "Scaffold Azure IaC",
    prompt:
      "Generate Bicep to provision an Azure OpenAI account with a GPT-4o deployment, an Azure AI Search service (Basic tier), an Azure Blob Storage account, and an App Service plan with a Linux web app. All in East US 2, with a common resource group.",
    contextualPrompt:
      "Generate Bicep to provision the Azure resources needed for this partner engagement: {context}. Infer the required services from the use case, set appropriate tiers, and place them in a common resource group in East US 2.",
  },
  "hve-psa.step.security": {
    agent: "@pr-review",
    title: "Run Security Review",
    prompt:
      "Review this project for security issues before production deployment. Focus on OWASP Top 10 risks: authentication, secrets management, injection vulnerabilities, and API endpoint security. Also check for AI-specific risks like prompt injection and data leakage in the RAG pipeline.",
    contextualPrompt:
      "Review this project for security issues before production deployment. The partner engagement: {context}. Focus on OWASP Top 10 risks, secrets management, and any AI-specific risks like prompt injection or data leakage relevant to this use case.",
  },
};

/**
 * Build the final prompt for a step, threading partner context if available.
 */
function buildPrompt(step, partnerContext) {
  if (partnerContext && step.contextualPrompt) {
    return step.contextualPrompt.replace("{context}", partnerContext);
  }
  return step.prompt;
}

/**
 * Send a message to Copilot Chat, falling back to clipboard.
 */
async function sendToChat(message) {
  try {
    await vscode.commands.executeCommand("workbench.action.chat.open", {
      query: message,
    });
  } catch {
    await vscode.env.clipboard.writeText(message);
    vscode.window.showInformationMessage(
      "Prompt copied to clipboard. Paste it into Copilot Chat to continue."
    );
  }
}

/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
  // --- Open walkthrough command ---
  context.subscriptions.push(
    vscode.commands.registerCommand("hve-psa.openWalkthrough", () => {
      vscode.commands.executeCommand(
        "workbench.action.openWalkthrough",
        "ise-hve-essentials.hve-psa-walkthrough#hve-psa-onboarding",
        false
      );
    })
  );

  // --- Set / clear partner context command ---
  context.subscriptions.push(
    vscode.commands.registerCommand("hve-psa.setPartnerContext", async () => {
      const current = context.workspaceState.get(CTX_KEY, "");
      const value = await vscode.window.showInputBox({
        title: "Partner Engagement Context",
        prompt:
          "Describe your current partner engagement. This context threads through all 7 walkthrough steps. Leave blank to use generic sample prompts.",
        value: current,
        placeHolder:
          "e.g., Contoso is building a customer support chatbot using Azure OpenAI and Azure AI Search (RAG pattern) for their insurance claims docs.",
        ignoreFocusOut: true,
      });
      if (value === undefined) return; // cancelled
      await context.workspaceState.update(CTX_KEY, value);
      const label = value
        ? `Partner context set: "${value.substring(0, 60)}${value.length > 60 ? "..." : ""}"`
        : "Partner context cleared. Steps will use generic sample prompts.";
      vscode.window.showInformationMessage(label);
    })
  );

  // --- Register each step command with editable prompt ---
  for (const [commandId, step] of Object.entries(STEP_PROMPTS)) {
    context.subscriptions.push(
      vscode.commands.registerCommand(commandId, async () => {
        const partnerContext = context.workspaceState.get(CTX_KEY, "");
        const defaultPrompt = buildPrompt(step, partnerContext);

        // Let the user review and edit the prompt before sending
        const edited = await vscode.window.showInputBox({
          title: `${step.title} — Edit Prompt`,
          prompt: `Review or modify the prompt before sending to ${step.agent}. Press Enter to send, Escape to cancel.`,
          value: defaultPrompt,
          ignoreFocusOut: true,
        });

        if (edited === undefined) return; // user cancelled
        if (!edited.trim()) {
          vscode.window.showWarningMessage("Empty prompt — skipped.");
          return;
        }

        await sendToChat(`${step.agent} ${edited}`);
      })
    );
  }
}

function deactivate() {}

module.exports = { activate, deactivate };
