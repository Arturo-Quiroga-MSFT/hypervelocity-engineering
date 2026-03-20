#!/usr/bin/env python3
"""
HVE Quick Start CLI Runner.

Runs any of the 7 quick start prompts through GitHub Copilot CLI
so you never have to copy and paste.

Usage:
    python cli.py --step 1          # Run step 1 (Memory Agent)
    python cli.py --step 3          # Run step 3 (Architecture Diagram)
    python cli.py --list            # List all steps
    python cli.py --all             # Run all 7 steps sequentially
    python cli.py --step 2 --verbose  # Show full Copilot output info
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Step definitions (mirrors app.py PHASES structure)
# ---------------------------------------------------------------------------

STEPS: dict[int, dict[str, str]] = {
    1: {
        "title": "Set Your Context Once",
        "agent": "Memory",
        "prompt": (
            "Remember that I am a Partner Solutions Architect. I help "
            "partners build apps and services on Azure AI services. "
            "My AI agents are built with Microsoft Agent Framework "
            "(MAF) and Microsoft Foundry Agent Services (pro code). "
            "I primarily work with Python and C#."
        ),
    },
    2: {
        "title": "Prep for a Partner Call",
        "agent": "Researcher Subagent",
        "prompt": (
            "Research how Azure AI Search integrates with Azure "
            "OpenAI for a RAG pattern. Include current SDK versions "
            "for Python, key limitations, recommended indexing "
            "strategies, and a simple architecture overview."
        ),
    },
    3: {
        "title": "Turn Your Whiteboard into a Diagram",
        "agent": "arch-diagram-builder",
        "prompt": (
            "Create an architecture diagram for a partner's customer "
            "support app. The app uses Azure OpenAI for chat "
            "completions, Azure AI Search for document retrieval "
            "(RAG pattern), Azure Blob Storage for storing knowledge "
            "base documents, and Azure App Service for hosting the "
            "web frontend. Users interact through a browser."
        ),
    },
    4: {
        "title": "Document Architecture Decisions",
        "agent": "adr-creation",
        "prompt": (
            "We chose Azure OpenAI over a self-hosted Llama model "
            "for the partner's customer support agent. The partner "
            "needs enterprise SLA guarantees, built-in content "
            "filtering for compliance, and managed scaling. They "
            "don't have a dedicated ML ops team to maintain a "
            "self-hosted deployment."
        ),
    },
    5: {
        "title": "Build a Partner Demo Dashboard",
        "agent": "gen-streamlit-dashboard",
        "prompt": (
            "Create a Streamlit dashboard for a RAG demo. The user "
            "types a question in a text input. The app sends the "
            "question to Azure AI Search to retrieve relevant "
            "documents, then passes the question and retrieved "
            "context to Azure OpenAI (GPT-4o) for an answer. "
            "Display the answer and show the source documents with "
            "relevance scores below it."
        ),
    },
    6: {
        "title": "Scaffold Azure Resources as Code",
        "agent": "Azure IaC Generator",
        "prompt": (
            "Generate Bicep to provision an Azure OpenAI account "
            "with a GPT-4o deployment, an Azure AI Search service "
            "(Basic tier), an Azure Blob Storage account, and an "
            "App Service plan with a Linux web app. All in East US "
            "2, with a common resource group."
        ),
    },
    7: {
        "title": "Review Code for Security",
        "agent": "PR Review / Security Analysis",
        "prompt": (
            "Review this project for security issues before "
            "production deployment. Focus on OWASP Top 10 risks: "
            "authentication, secrets management, injection "
            "vulnerabilities, and API endpoint security. Also check "
            "for AI-specific risks like prompt injection and data "
            "leakage in the RAG pipeline."
        ),
    },
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def check_copilot_cli() -> None:
    """Exit with a helpful message if copilot CLI is not installed."""
    if not shutil.which("copilot"):
        print(
            "Error: 'copilot' CLI not found on PATH.\n"
            "Install it first:\n"
            "  macOS/Linux:  brew install copilot-cli\n"
            "  Windows:      winget install GitHub.Copilot\n"
            "  npm:          npm install -g @github/copilot\n\n"
            "Docs: https://docs.github.com/en/copilot/"
            "how-tos/copilot-cli/cli-getting-started",
            file=sys.stderr,
        )
        sys.exit(1)


def list_steps() -> None:
    """Print a table of all available steps."""
    print("\nHVE Quick Start Steps\n")
    print(f"  {'#':<4}{'Title':<42}{'Agent':<28}{'Time'}")
    print(f"  {'─'*4}{'─'*42}{'─'*28}{'─'*8}")
    times = ["30 sec", "2 min", "3 min", "2 min", "5 min", "5 min", "5 min"]
    for step_id, step in STEPS.items():
        t = times[step_id - 1]
        print(f"  {step_id:<4}{step['title']:<42}{step['agent']:<28}{t}")
    print(
        "\nRun a step:  python cli.py --step <number>"
        "\nRun all:     python cli.py --all"
    )


def run_step(
    step_id: int, *, verbose: bool = False, allow_all: bool = True
) -> int:
    """Run a single step via Copilot CLI. Returns the exit code."""
    step = STEPS[step_id]
    print(f"\n{'='*60}")
    print(f"  Step {step_id}: {step['title']}")
    print(f"  Agent: {step['agent']}")
    if allow_all:
        print("  Mode: --allow-all-tools (auto-approve actions)")
    print(f"{'='*60}\n")

    repo_root = Path(__file__).parent.parent

    cmd = ["copilot", "-p", step["prompt"]]
    if allow_all:
        cmd.append("--allow-all-tools")

    result = subprocess.run(
        cmd,
        text=True,
        cwd=repo_root,
    )
    return result.returncode


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Parse arguments and dispatch."""
    parser = argparse.ArgumentParser(
        description="Run HVE Quick Start prompts via GitHub Copilot CLI.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python cli.py --list            List all steps\n"
            "  python cli.py --step 1          Run step 1\n"
            "  python cli.py --step 3 -v       Run step 3 (verbose)\n"
            "  python cli.py --all             Run all 7 steps\n"
        ),
    )
    parser.add_argument(
        "--step",
        type=int,
        choices=range(1, 8),
        metavar="N",
        help="Step number to run (1-7)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available steps",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all 7 steps sequentially",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show full Copilot CLI output (uses -p instead of -sp)",
    )
    parser.add_argument(
        "--no-allow-all",
        action="store_true",
        help="Disable --allow-all-tools (Copilot will pause for permission)",
    )

    args = parser.parse_args()

    if args.list:
        list_steps()
        return

    if not args.step and not args.all:
        parser.print_help()
        return

    check_copilot_cli()

    if args.all:
        print("Running all 7 HVE Quick Start steps...\n")
        for sid in STEPS:
            rc = run_step(
                sid,
                verbose=args.verbose,
                allow_all=not args.no_allow_all,
            )
            if rc != 0:
                print(
                    f"\nStep {sid} failed (exit {rc}). "
                    "Continue? [Y/n] ",
                    end="",
                )
                answer = input().strip().lower()
                if answer in ("n", "no"):
                    sys.exit(rc)
        print("\nAll 7 steps complete.")
    else:
        rc = run_step(
            args.step,
            verbose=args.verbose,
            allow_all=not args.no_allow_all,
        )
        sys.exit(rc)


if __name__ == "__main__":
    main()
