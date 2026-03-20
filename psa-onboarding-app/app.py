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
# Data: Quick Start definitions
# ---------------------------------------------------------------------------

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
                "agent": "PR Review",
                "doc_link": "hve-quick-start-7-security-review.md",
            },
        ],
    },
]

PROGRESS_FILE = Path(__file__).parent / ".psa_progress.json"


# ---------------------------------------------------------------------------
# Copilot CLI helpers
# ---------------------------------------------------------------------------


def copilot_cli_available() -> bool:
    """Check whether the `copilot` CLI binary is on PATH."""
    return shutil.which("copilot") is not None


def build_cli_command(
    prompt: str, *, allow_all: bool = False
) -> str:
    """Return a ready-to-run Copilot CLI command string."""
    escaped = prompt.replace('"', '\\"')
    allow = " --allow-all-tools" if allow_all else ""
    return f'copilot -p "{escaped}"{allow}'


def stream_copilot_cli(
    prompt: str, container, *, allow_all: bool = True
):
    """Execute a prompt via Copilot CLI, streaming output into *container*.

    When *allow_all* is True the ``--allow-all-tools`` flag is passed so
    Copilot does not pause for permission prompts (required for
    non-interactive execution from a web UI).

    Returns (returncode, full_output).
    """
    cmd = ["copilot", "-p", prompt]
    if allow_all:
        cmd.append("--allow-all-tools")

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        cwd=Path(__file__).parent.parent,  # repo root
    )
    lines: list[str] = []
    for line in proc.stdout:              # type: ignore[union-attr]
        lines.append(line)
        container.code("".join(lines), language="markdown")
    proc.wait()
    full = "".join(lines)
    return proc.returncode, full


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

        # Expandable prompt section — three delivery modes
        tab_chat, tab_cli, tab_run = st.tabs(
            ["💬 VS Code Chat", "⌨️ Copilot CLI", "▶️ Run Now"]
        )

        cli_cmd = build_cli_command(step["prompt"], allow_all=True)

        with tab_chat:
            st.code(step["prompt"], language="text")
            st.caption(f"Agent: **{step['agent']}**")

        with tab_cli:
            st.code(cli_cmd, language="bash")
            st.caption(
                "Paste into your terminal. Requires "
                "`copilot` CLI — "
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
                            step["prompt"],
                            output_box,
                            allow_all=allow_all,
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
                        f"{step['prompt']}\n\n"
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
            "Partner Context (optional)",
            value=progress.get("partner_context", ""),
            placeholder="e.g., Working with Contoso on a RAG app",
            height=80,
        )
        if context != progress.get("partner_context", ""):
            progress["partner_context"] = context
            save_progress(progress)

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
            st.success("Detected on PATH", icon="✅")
        else:
            st.warning("Not found", icon="⚠️")
            st.caption(
                "Install: `brew install copilot-cli` "
                "([docs](https://docs.github.com/en/copilot/"
                "how-tos/copilot-cli/cli-getting-started))"
            )

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
