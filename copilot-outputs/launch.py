#!/usr/bin/env python3
"""
RAG Dashboard Launcher
Automatically detects if Azure dependencies are available and launches the appropriate version.
"""

import subprocess
import sys

def check_azure_dependencies():
    """Check if Azure dependencies are installed"""
    try:
        import azure.search.documents
        import azure.core.credentials
        import openai
        return True
    except ImportError:
        return False

def main():
    """Main launcher function"""
    print("🚀 RAG Dashboard Launcher")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        print("🎮 Starting demo mode...")
        subprocess.run([sys.executable, "-m", "streamlit", "run", "rag_dashboard_demo.py"])
    elif check_azure_dependencies():
        print("✅ Azure dependencies found. Starting full version...")
        subprocess.run([sys.executable, "-m", "streamlit", "run", "rag_dashboard.py"])
    else:
        print("⚠️  Azure dependencies not found.")
        print("🎮 Starting demo mode instead...")
        print("\nTo use the full version, install dependencies:")
        print("pip install azure-search-documents azure-identity openai")
        print("=" * 50)
        subprocess.run([sys.executable, "-m", "streamlit", "run", "rag_dashboard_demo.py"])

if __name__ == "__main__":
    main()