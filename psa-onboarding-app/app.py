"""
HVE Quick Start Onboarding App for Partner Solutions Architects.

A guided wizard that walks PSAs through the 7-step HVE Core onboarding
lifecycle: Configure → Learn → Visualize → Document → Demo → Deploy → Secure.
"""

import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

OUTPUTS_DIR = Path(__file__).parent / "outputs"

# ---------------------------------------------------------------------------
# Copilot CLI model and effort options (v1.0.10+)
# ---------------------------------------------------------------------------

MODEL_OPTIONS = [
    "(default)",
    "claude-sonnet-4.5",
    "claude-sonnet-4",
    "gpt-5",
    "gpt-5.4-mini",
    "gpt-5.2",
    "o4-mini",
]

EFFORT_OPTIONS = [
    "(default)",
    "low",
    "medium",
    "high",
    "xhigh",
]

# ---------------------------------------------------------------------------
# Data: Quick Start definitions
# ---------------------------------------------------------------------------

# Each step carries a generic ``prompt`` (used when no partner context is
# provided) and a ``contextual_prompt`` template with a ``{context}``
# placeholder.  When the sidebar "Partner Context" is filled in, prompts
# auto-populate with the engagement details so all 7 steps follow a single
# coherent narrative.

PHASES = [
    {
        "name": "Configure → Learn → Visualize",
        "color": "#E3F2FD",
        "border": "#1E88E5",
        "steps": [
            {
                "id": 1,
                "title": "Set Your Context Once",
                "subtitle": "Memory Agent",
                "time": "30 sec",
                "icon": "🧠",
                "description": (
                    "Tell GitHub Copilot who you are and what you do, once, "
                    "so every future interaction is grounded in your role."
                ),
                "prompt": (
                    "Remember that I am a Partner Solutions Architect. I help "
                    "partners build apps and services on Azure AI services. "
                    "My AI agents are built with Microsoft Agent Framework "
                    "(MAF) and Microsoft Foundry Agent Services (pro code). "
                    "I primarily work with Python and C#."
                ),
                "contextual_prompt": (
                    "Remember that I am a Partner Solutions Architect. I help "
                    "partners build apps and services on Azure AI services. "
                    "My AI agents are built with Microsoft Agent Framework "
                    "(MAF) and Microsoft Foundry Agent Services (pro code). "
                    "I primarily work with Python and C#. "
                    "My current partner engagement: {context}"
                ),
                "agent": "Memory",
                "doc_link": "hve-quick-start-1-memory.md",
            },
            {
                "id": 2,
                "title": "Prep for a Partner Call",
                "subtitle": "Researcher Subagent",
                "time": "2 min",
                "icon": "🔍",
                "description": (
                    "Get a structured technical briefing on any Azure AI "
                    "topic before a partner call."
                ),
                "prompt": (
                    "Research how Azure AI Search integrates with Azure "
                    "OpenAI for a RAG pattern. Include current SDK versions "
                    "for Python, key limitations, recommended indexing "
                    "strategies, and a simple architecture overview."
                ),
                "contextual_prompt": (
                    "I am preparing for a partner call. Partner context: "
                    "{context}. Research the Azure services and integration "
                    "patterns most relevant to this engagement. Include "
                    "current SDK versions for Python, key limitations, "
                    "recommended architecture patterns, and a simple "
                    "architecture overview."
                ),
                "agent": "Researcher Subagent",
                "doc_link": "hve-quick-start-2-researcher.md",
            },
            {
                "id": 3,
                "title": "Turn Your Whiteboard into a Diagram",
                "subtitle": "arch-diagram-builder Agent",
                "time": "3 min",
                "icon": "📐",
                "description": (
                    "Describe a partner's architecture in plain English and "
                    "get a professional Mermaid diagram."
                ),
                "prompt": (
                    "Create an architecture diagram for a partner's customer "
                    "support app. The app uses Azure OpenAI for chat "
                    "completions, Azure AI Search for document retrieval "
                    "(RAG pattern), Azure Blob Storage for storing knowledge "
                    "base documents, and Azure App Service for hosting the "
                    "web frontend. Users interact through a browser."
                ),
                "contextual_prompt": (
                    "Create an architecture diagram for the following "
                    "partner engagement: {context}. Identify the Azure "
                    "services involved and show the data flow between "
                    "components. Output a Mermaid diagram."
                ),
                "agent": "arch-diagram-builder",
                "doc_link": "hve-quick-start-3-architecture-diagram.md",
            },
        ],
    },
    {
        "name": "Document → Demo → Deploy",
        "color": "#FFF3E0",
        "border": "#FB8C00",
        "steps": [
            {
                "id": 4,
                "title": "Document Architecture Decisions",
                "subtitle": "adr-creation Agent",
                "time": "2 min",
                "icon": "📝",
                "description": (
                    "Turn an architecture decision into a formal ADR "
                    "without writing one from scratch."
                ),
                "prompt": (
                    "We chose Azure OpenAI over a self-hosted Llama model "
                    "for the partner's customer support agent. The partner "
                    "needs enterprise SLA guarantees, built-in content "
                    "filtering for compliance, and managed scaling. They "
                    "don't have a dedicated ML ops team to maintain a "
                    "self-hosted deployment."
                ),
                "contextual_prompt": (
                    "Write an Architecture Decision Record (ADR) for "
                    "a key technology decision in this partner engagement: "
                    "{context}. Identify the most important architecture "
                    "choice, list the alternatives considered, and document "
                    "the rationale for the chosen approach."
                ),
                "agent": "adr-creation",
                "doc_link": "hve-quick-start-4-adr.md",
            },
            {
                "id": 5,
                "title": "Build a Partner Demo Dashboard",
                "subtitle": "gen-streamlit-dashboard Agent",
                "time": "5 min",
                "icon": "📊",
                "description": (
                    "Generate a runnable demo dashboard from a plain "
                    "English description."
                ),
                "prompt": (
                    "Create a Streamlit dashboard for a RAG demo. The user "
                    "types a question in a text input. The app sends the "
                    "question to Azure AI Search to retrieve relevant "
                    "documents, then passes the question and retrieved "
                    "context to Azure OpenAI (GPT-4o) for an answer. "
                    "Display the answer and show the source documents with "
                    "relevance scores below it."
                ),
                "contextual_prompt": (
                    "Create a Streamlit demo dashboard for this partner "
                    "engagement: {context}. The dashboard should showcase "
                    "the core functionality the partner needs. Include "
                    "interactive inputs, mock data, and a clean UI that "
                    "the partner can see in a live demo."
                ),
                "agent": "gen-streamlit-dashboard",
                "doc_link": "hve-quick-start-5-demo-dashboard.md",
            },
            {
                "id": 6,
                "title": "Scaffold Azure Resources as Code",
                "subtitle": "Azure IaC Generator Agent",
                "time": "5 min",
                "icon": "🏗️",
                "description": (
                    "Describe Azure resources needed and get deployable "
                    "Bicep or Terraform code."
                ),
                "prompt": (
                    "Generate Bicep to provision an Azure OpenAI account "
                    "with a GPT-4o deployment, an Azure AI Search service "
                    "(Basic tier), an Azure Blob Storage account, and an "
                    "App Service plan with a Linux web app. All in East US "
                    "2, with a common resource group."
                ),
                "contextual_prompt": (
                    "Generate Bicep to provision the Azure resources needed "
                    "for this partner engagement: {context}. Infer the "
                    "required services from the use case, set appropriate "
                    "tiers, and place them in a common resource group in "
                    "East US 2."
                ),
                "agent": "Azure IaC Generator",
                "doc_link": "hve-quick-start-6-iac-generator.md",
            },
        ],
    },
    {
        "name": "Secure",
        "color": "#FFEBEE",
        "border": "#E53935",
        "steps": [
            {
                "id": 7,
                "title": "Review Code for Security",
                "subtitle": "PR Review / Security Analysis",
                "time": "5 min",
                "icon": "🔒",
                "description": (
                    "Run a security-focused review of partner code before "
                    "production, catching OWASP Top 10 and AI-specific risks."
                ),
                "prompt": (
                    "Review this project for security issues before "
                    "production deployment. Focus on OWASP Top 10 risks: "
                    "authentication, secrets management, injection "
                    "vulnerabilities, and API endpoint security. Also check "
                    "for AI-specific risks like prompt injection and data "
                    "leakage in the RAG pipeline."
                ),
                "contextual_prompt": (
                    "Review this project for security issues before "
                    "production deployment. The partner engagement: "
                    "{context}. Focus on OWASP Top 10 risks, secrets "
                    "management, and any AI-specific risks like prompt "
                    "injection or data leakage relevant to this use case."
                ),
                "agent": "PR Review",
                "doc_link": "hve-quick-start-7-security-review.md",
            },
        ],
    },
]

PROGRESS_FILE = Path(__file__).parent / ".psa_progress.json"
REPO_ROOT = Path(__file__).parent.parent
COPILOT_OUTPUTS_DIR = REPO_ROOT / "copilot-outputs"


# ---------------------------------------------------------------------------
# Copilot CLI helpers
# ---------------------------------------------------------------------------


def copilot_cli_available() -> bool:
    """Check whether the `copilot` CLI binary is on PATH."""
    return shutil.which("copilot") is not None


def build_cli_command(
    prompt: str,
    *,
    allow_all: bool = False,
    model: str = "",
    effort: str = "",
) -> str:
    """Return a ready-to-run Copilot CLI command string."""
    escaped = prompt.replace('"', '\\"')
    parts = [f'copilot -p "{escaped}"', "--add-dir copilot-outputs"]
    if model and model != "(default)":
        parts.append(f"--model {model}")
    if effort and effort != "(default)":
        parts.append(f"--effort {effort}")
    if allow_all:
        parts.append("--allow-all-tools")
    return " ".join(parts)


def stream_copilot_cli(
    prompt: str,
    container,
    *,
    allow_all: bool = True,
    model: str = "",
    effort: str = "",
):
    """Execute a prompt via Copilot CLI, streaming output into *container*.

    When *allow_all* is True the ``--allow-all-tools`` flag is passed so
    Copilot does not pause for permission prompts (required for
    non-interactive execution from a web UI).

    Returns (returncode, full_output).
    """
    COPILOT_OUTPUTS_DIR.mkdir(exist_ok=True)

    cmd = [
        "copilot", "-p",
        f"{prompt} Save any generated files to the copilot-outputs/ directory.",
        "--add-dir", str(COPILOT_OUTPUTS_DIR),
    ]
    if model and model != "(default)":
        cmd.extend(["--model", model])
    if effort and effort != "(default)":
        cmd.extend(["--effort", effort])
    if allow_all:
        cmd.append("--allow-all-tools")

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        cwd=REPO_ROOT,
    )
    lines: list[str] = []
    for line in proc.stdout:              # type: ignore[union-attr]
        lines.append(line)
        container.code("".join(lines), language="markdown")
    proc.wait()
    full = "".join(lines)
    return proc.returncode, full


# ---------------------------------------------------------------------------
# Prompt generation
# ---------------------------------------------------------------------------


def get_default_prompt(step: dict, partner_context: str) -> str:
    """Return the default prompt for a step, contextualized when possible."""
    ctx = partner_context.strip()
    if ctx and "contextual_prompt" in step:
        return step["contextual_prompt"].format(context=ctx)
    return step["prompt"]


# ---------------------------------------------------------------------------
# Progress persistence (local JSON file)
# ---------------------------------------------------------------------------


def load_progress() -> dict:
    """Load progress from local JSON file."""
    if PROGRESS_FILE.exists():
        return json.loads(PROGRESS_FILE.read_text())
    return {"completed": [], "psa_name": "", "partner_context": ""}


def save_progress(progress: dict) -> None:
    """Save progress to local JSON file."""
    PROGRESS_FILE.write_text(json.dumps(progress, indent=2))


# ---------------------------------------------------------------------------
# UI Helpers
# ---------------------------------------------------------------------------


def render_progress_bar(progress: dict) -> None:
    """Render the overall progress indicator."""
    total = 7
    done = len(progress.get("completed", []))
    pct = done / total

    col1, col2 = st.columns([3, 1])
    with col1:
        st.progress(pct)
    with col2:
        st.metric("Completed", f"{done} / {total}")


def render_phase_header(phase: dict) -> None:
    """Render a styled phase header."""
    st.markdown(
        f"""
        <div style="
            background-color: {phase['color']};
            border-left: 4px solid {phase['border']};
            padding: 12px 16px;
            border-radius: 6px;
            margin: 24px 0 12px 0;
        ">
            <strong style="font-size: 1.1em;">{phase['name']}</strong>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_step_card(step: dict, progress: dict) -> dict:
    """Render a single quick start step card. Returns updated progress."""
    step_id = step["id"]
    is_done = step_id in progress.get("completed", [])

    status_icon = "✅" if is_done else f"**{step['icon']}**"
    status_text = "Completed" if is_done else step["time"]

    with st.container(border=True):
        header_col, status_col = st.columns([4, 1])
        with header_col:
            st.markdown(
                f"### {status_icon} Step {step_id}: {step['title']}\n"
                f"*{step['subtitle']}*"
            )
        with status_col:
            st.markdown(
                f"<div style='text-align: right; padding-top: 12px;'>"
                f"<code>{status_text}</code></div>",
                unsafe_allow_html=True,
            )

        st.markdown(step["description"])

        partner_context = progress.get("partner_context", "")
        default_prompt = get_default_prompt(step, partner_context)

        if partner_context:
            st.caption(
                "📌 Prompt tailored to your partner context. "
                "Edit below to refine."
            )

        # Editable prompt — shared across all delivery tabs
        active_prompt = st.text_area(
            "Prompt",
            value=default_prompt,
            height=120,
            key=f"edited_prompt_{step_id}",
            label_visibility="collapsed",
        )

        # Three delivery mode tabs
        tab_chat, tab_cli, tab_run = st.tabs(
            ["💬 VS Code Chat", "⌨️ Copilot CLI", "▶️ Run Now"]
        )

        with tab_chat:
            st.code(active_prompt, language="text")
            st.caption(f"Agent: **{step['agent']}**")

        with tab_cli:
            _model = progress.get("cli_model", "(default)")
            _effort = progress.get("cli_effort", "(default)")
            cli_cmd = build_cli_command(
                active_prompt,
                allow_all=True,
                model=_model,
                effort=_effort,
            )
            st.code(cli_cmd, language="bash")
            st.caption(
                "Paste into your terminal. Requires "
                "`copilot` CLI v1.0.10+ — "
                "[install guide]"
                "(https://docs.github.com/en/copilot/"
                "how-tos/copilot-cli/cli-getting-started)"
            )
            st.caption(
                "Or use the companion script: "
                "`python cli.py --step "
                f"{step_id}`"
            )
            st.caption(
                "`--allow-all-tools` lets Copilot run commands "
                "without pausing for permission."
            )

        with tab_run:
            if not copilot_cli_available():
                st.warning(
                    "Copilot CLI not found on PATH. "
                    "Install it first: `brew install copilot-cli`",
                    icon="⚠️",
                )
            else:
                run_model = progress.get("cli_model", "(default)")
                run_effort = progress.get("cli_effort", "(default)")
                allow_all = st.checkbox(
                    "Auto-approve tool actions",
                    value=True,
                    key=f"allow_all_{step_id}",
                    help=(
                        "When checked, passes --allow-all-tools so "
                        "Copilot CLI runs commands without pausing "
                        "for permission (required for non-interactive "
                        "execution)."
                    ),
                )
                if run_model != "(default)" or run_effort != "(default)":
                    st.caption(
                        f"Model: **{run_model}** | "
                        f"Effort: **{run_effort}** "
                        "(change in sidebar)"
                    )
                if st.button(
                    f"🚀 Run Step {step_id} via Copilot CLI",
                    key=f"run_cli_{step_id}",
                    use_container_width=True,
                ):
                    output_box = st.empty()
                    with st.spinner(
                        f"Running step {step_id} — streaming output..."
                    ):
                        rc, output = stream_copilot_cli(
                            active_prompt,
                            output_box,
                            allow_all=allow_all,
                            model=run_model,
                            effort=run_effort,
                        )
                    if rc == 0:
                        st.success("Copilot CLI completed.")
                    else:
                        st.error(f"Copilot CLI exited with code {rc}.")
                    output_box.code(output, language="markdown")
                    # Store output in session state for the save button
                    st.session_state[f"output_{step_id}"] = output

                # Save button — available whenever output exists
                if f"output_{step_id}" in st.session_state:
                    saved_output = st.session_state[f"output_{step_id}"]
                    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
                    filename = f"step-{step_id}-{ts}.md"
                    md_content = (
                        f"# Step {step_id}: {step['title']}\n\n"
                        f"**Agent:** {step['agent']}  \n"
                        f"**Date:** {ts}  \n\n"
                        f"## Prompt\n\n"
                        f"{active_prompt}\n\n"
                        f"## Output\n\n"
                        f"```\n{saved_output}\n```\n"
                    )
                    save_col, dl_col = st.columns(2)
                    with save_col:
                        if st.button(
                            f"💾 Save to outputs/",
                            key=f"save_{step_id}",
                            use_container_width=True,
                        ):
                            OUTPUTS_DIR.mkdir(exist_ok=True)
                            out_path = OUTPUTS_DIR / filename
                            out_path.write_text(md_content)
                            st.success(f"Saved to `{out_path.name}`")
                    with dl_col:
                        st.download_button(
                            "⬇️ Download .md",
                            data=md_content,
                            file_name=filename,
                            mime="text/markdown",
                            key=f"dl_{step_id}",
                            use_container_width=True,
                        )

        # Action buttons
        btn_col1, btn_col2, btn_col3 = st.columns(3)
        with btn_col1:
            if not is_done:
                if st.button(
                    "✅ Mark Complete",
                    key=f"complete_{step_id}",
                    use_container_width=True,
                ):
                    if step_id not in progress["completed"]:
                        progress["completed"].append(step_id)
                        save_progress(progress)
                        st.rerun()
            else:
                if st.button(
                    "↩️ Undo",
                    key=f"undo_{step_id}",
                    use_container_width=True,
                ):
                    progress["completed"].remove(step_id)
                    save_progress(progress)
                    st.rerun()
        with btn_col2:
            st.link_button(
                "📖 Read Guide",
                f"https://github.com/Arturo-Quiroga-MSFT/"
                f"hypervelocity-engineering/blob/main/{step['doc_link']}",
                use_container_width=True,
            )

    return progress


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------


def render_sidebar(progress: dict) -> dict:
    """Render the sidebar with PSA profile and navigation."""
    with st.sidebar:
        st.image(
            "https://img.icons8.com/fluency/96/rocket.png",
            width=64,
        )
        st.title("HVE Onboarding")
        st.caption("Quick Start Series for PSAs")

        st.divider()

        # PSA profile
        st.subheader("Your Profile")
        name = st.text_input(
            "Your Name",
            value=progress.get("psa_name", ""),
            placeholder="e.g., Arturo Quiroga",
        )
        if name != progress.get("psa_name", ""):
            progress["psa_name"] = name
            save_progress(progress)

        context = st.text_area(
            "Partner Context",
            value=progress.get("partner_context", ""),
            placeholder=(
                "Describe your partner engagement here. This text "
                "flows into every prompt so all 7 steps stay focused "
                "on the same use case.\n\n"
                "Example: Working with Contoso on a multi-agent MDM "
                "system using Azure OpenAI and Azure AI Search for "
                "data quality validation."
            ),
            height=140,
            help=(
                "All step prompts auto-adapt to this context. "
                "Leave blank to use the generic sample prompts."
            ),
        )
        if context != progress.get("partner_context", ""):
            progress["partner_context"] = context
            save_progress(progress)

        if context:
            st.success("Prompts tailored to your context", icon="📌")
        else:
            st.info("Add context to personalize prompts", icon="💡")

        st.divider()

        # Quick nav
        st.subheader("Jump To")
        for phase in PHASES:
            for step in phase["steps"]:
                is_done = step["id"] in progress.get("completed", [])
                marker = "✅" if is_done else "⬜"
                st.markdown(
                    f"{marker} **{step['id']}**. {step['title']}"
                )

        st.divider()

        # Reset
        if st.button("🔄 Reset All Progress", use_container_width=True):
            progress = {"completed": [], "psa_name": name, "partner_context": context}
            save_progress(progress)
            st.rerun()

        st.divider()

        # Copilot CLI status
        st.subheader("Copilot CLI")
        if copilot_cli_available():
            st.success("v1.0.10 detected", icon="✅")
        else:
            st.warning("Not found", icon="⚠️")
            st.caption(
                "Install: "
                "`curl -fsSL https://gh.io/copilot-install | bash` "
                "([docs](https://docs.github.com/en/copilot/"
                "how-tos/copilot-cli/cli-getting-started))"
            )

        # Model and effort selectors
        st.subheader("Model & Effort")
        sel_model = st.selectbox(
            "Model",
            MODEL_OPTIONS,
            index=MODEL_OPTIONS.index(
                progress.get("cli_model", "(default)")
            ),
            key="sidebar_model",
            help=(
                "AI model for Copilot CLI. Default is "
                "Claude Sonnet 4.5. Use /model in interactive "
                "mode to see all available models."
            ),
        )
        sel_effort = st.selectbox(
            "Reasoning Effort",
            EFFORT_OPTIONS,
            index=EFFORT_OPTIONS.index(
                progress.get("cli_effort", "(default)")
            ),
            key="sidebar_effort",
            help=(
                "How deeply the model reasons. Low is faster "
                "and cheaper; high/xhigh is slower but more "
                "thorough. Maps to --effort flag."
            ),
        )
        if sel_model != progress.get("cli_model", "(default)"):
            progress["cli_model"] = sel_model
            save_progress(progress)
        if sel_effort != progress.get("cli_effort", "(default)"):
            progress["cli_effort"] = sel_effort
            save_progress(progress)

        st.divider()
        st.caption(
            "[HVE Core Repo](https://github.com/microsoft/hve-core) · "
            "[VS Code Extension]("
            "https://marketplace.visualstudio.com/items?"
            "itemName=ise-hve-essentials.hve-core)"
        )

    return progress


# ---------------------------------------------------------------------------
# Main App
# ---------------------------------------------------------------------------


def main() -> None:
    """Main application entry point."""
    st.set_page_config(
        page_title="HVE Quick Start for PSAs",
        page_icon="🚀",
        layout="wide",
    )

    progress = load_progress()

    # Sidebar
    progress = render_sidebar(progress)

    # Header
    st.title("🚀 HVE Quick Start Onboarding")
    st.markdown(
        "A guided path through the **7-step HVE Core lifecycle** for "
        "Partner Solutions Architects. Complete each step to build your "
        "HVE proficiency."
    )

    if progress.get("psa_name"):
        st.markdown(f"Welcome back, **{progress['psa_name']}**.")

    # Progress bar
    render_progress_bar(progress)

    st.divider()

    # Render phases and steps
    for phase in PHASES:
        render_phase_header(phase)
        for step in phase["steps"]:
            progress = render_step_card(step, progress)

    # Completion message
    if len(progress.get("completed", [])) == 7:
        st.divider()
        st.balloons()
        st.success(
            "🎉 **Congratulations!** You have completed the full HVE Quick "
            "Start series. You can now configure your tools, research topics, "
            "produce diagrams, document decisions, build demos, deploy "
            "infrastructure, and review security — all with HVE Core.",
            icon="🏆",
        )
        st.markdown(
            "**Next**: Explore the full "
            "[HVE Core Use Cases for PSAs]("
            "https://github.com/Arturo-Quiroga-MSFT/"
            "hypervelocity-engineering/blob/main/"
            "hve-core-use-cases-for-psa.md) for advanced workflows."
        )


if __name__ == "__main__":
    main()
