"""
PROFISEE Multi-Agent MDM System - Demo Dashboard

This Streamlit app demonstrates the multi-agent Master Data Management
system built with Microsoft Agent Framework (MAF) and Azure AI services.

Author: Arturo Quiroga, Partner Solutions Architect
Partner: PROFISEE
Date: March 2026
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="PROFISEE Multi-Agent MDM System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #0078d4;
        margin-bottom: 2rem;
    }
    .agent-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #0078d4;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .status-success {
        color: #28a745;
        font-weight: bold;
    }
    .status-warning {
        color: #ffc107;
        font-weight: bold;
    }
    .status-error {
        color: #dc3545;
        font-weight: bold;
    }
    .agent-status {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.875rem;
        font-weight: bold;
    }
    .agent-active {
        background-color: #d4edda;
        color: #155724;
    }
    .agent-idle {
        background-color: #fff3cd;
        color: #856404;
    }
</style>
""", unsafe_allow_html=True)

# Sample data for demonstration
@st.cache_data
def load_sample_data():
    """Load sample data for the demo"""
    
    # Sample customer records with varying quality
    customer_data = [
        {
            "id": "CUST_001",
            "source_system": "Salesforce", 
            "first_name": "John",
            "last_name": "Smith",
            "email": "john.smith@acme.com",
            "phone": "+1-555-123-4567",
            "address": "123 Main St",
            "city": "Seattle",
            "state": "WA",
            "zip": "98101",
            "quality_score": 0.95,
            "validation_status": "Valid",
            "processing_status": "Completed"
        },
        {
            "id": "CUST_002", 
            "source_system": "SAP",
            "first_name": "Jane",
            "last_name": "",  # Missing last name
            "email": "jane@example",  # Invalid email
            "phone": "555.123.4567",  # Inconsistent format
            "address": "456 Oak Ave",
            "city": "Portland",
            "state": "OR", 
            "zip": "",  # Missing zip
            "quality_score": 0.62,
            "validation_status": "Validation Errors",
            "processing_status": "In Progress"
        },
        {
            "id": "CUST_003",
            "source_system": "Oracle",
            "first_name": "Michael",
            "last_name": "Johnson", 
            "email": "m.johnson@company.com",
            "phone": "(555) 987-6543",
            "address": "789 Pine Rd",
            "city": "San Francisco",
            "state": "CA",
            "zip": "94102",
            "quality_score": 0.88,
            "validation_status": "Valid", 
            "processing_status": "Completed"
        },
        {
            "id": "CUST_004",
            "source_system": "Dynamics",
            "first_name": "",  # Missing first name
            "last_name": "Davis",
            "email": "sarah.davis@email.com",
            "phone": "",  # Missing phone
            "address": "321 Elm St",
            "city": "",  # Missing city
            "state": "TX",
            "zip": "75201", 
            "quality_score": 0.45,
            "validation_status": "Quality Issues",
            "processing_status": "Rejected"
        },
        {
            "id": "CUST_005",
            "source_system": "Salesforce",
            "first_name": "Robert", 
            "last_name": "Wilson",
            "email": "rob.wilson@tech.com",
            "phone": "+1 (555) 246-8135",
            "address": "654 Maple Dr",
            "city": "Austin",
            "state": "TX",
            "zip": "73301",
            "quality_score": 0.91,
            "validation_status": "Valid",
            "processing_status": "Completed"
        }
    ]
    
    # Agent performance metrics
    agent_metrics = {
        "Data Quality Agent": {
            "status": "Active",
            "requests_processed": 1247,
            "avg_response_time": 1.8,
            "success_rate": 0.97,
            "quality_improvements": 89
        },
        "Data Validation Agent": {
            "status": "Active", 
            "requests_processed": 1198,
            "avg_response_time": 2.1,
            "success_rate": 0.95,
            "validation_passes": 934
        },
        "Data Enrichment Agent": {
            "status": "Active",
            "requests_processed": 856,
            "avg_response_time": 3.2,
            "success_rate": 0.92,
            "fields_enriched": 2341
        },
        "Data Resolution Agent": { 
            "status": "Active",
            "requests_processed": 723,
            "avg_response_time": 2.7,
            "success_rate": 0.94,
            "duplicates_resolved": 127
        },
        "Data Governance Agent": {
            "status": "Active",
            "requests_processed": 1456,
            "avg_response_time": 1.2,
            "success_rate": 0.99,
            "audit_trails_created": 1456
        }
    }
    
    # Processing history
    processing_history = pd.DataFrame([
        {"timestamp": datetime.now().replace(hour=9), "records_processed": 145, "avg_quality": 0.78},
        {"timestamp": datetime.now().replace(hour=10), "records_processed": 167, "avg_quality": 0.82},
        {"timestamp": datetime.now().replace(hour=11), "records_processed": 198, "avg_quality": 0.85},
        {"timestamp": datetime.now().replace(hour=12), "records_processed": 223, "avg_quality": 0.87},
        {"timestamp": datetime.now().replace(hour=13), "records_processed": 189, "avg_quality": 0.89},
        {"timestamp": datetime.now().replace(hour=14), "records_processed": 156, "avg_quality": 0.91},
        {"timestamp": datetime.now().replace(hour=15), "records_processed": 134, "avg_quality": 0.88},
    ])
    
    return pd.DataFrame(customer_data), agent_metrics, processing_history

def render_header():
    """Render the main header and navigation"""
    st.markdown('<div class="main-header">🤖 PROFISEE Multi-Agent MDM System</div>', unsafe_allow_html=True)
    st.markdown("**Partner:** PROFISEE | **Technology:** Microsoft Agent Framework (MAF) + Azure AI Services")
    st.divider()

def render_agent_status_overview(agent_metrics):
    """Render agent status overview cards"""
    st.subheader("🔄 Agent Status Overview")
    
    cols = st.columns(len(agent_metrics))
    
    for idx, (agent_name, metrics) in enumerate(agent_metrics.items()):
        with cols[idx]:
            status_class = "agent-active" if metrics["status"] == "Active" else "agent-idle"
            
            st.markdown(f"""
            <div class="agent-card">
                <h4>{agent_name}</h4>
                <span class="agent-status {status_class}">{metrics["status"]}</span>
                <p><strong>Processed:</strong> {metrics["requests_processed"]:,}</p>
                <p><strong>Avg Time:</strong> {metrics["avg_response_time"]:.1f}s</p>
                <p><strong>Success Rate:</strong> {metrics["success_rate"]:.1%}</p>
            </div>
            """, unsafe_allow_html=True)

def render_system_metrics(agent_metrics, processing_history):
    """Render system performance metrics"""
    st.subheader("📊 System Performance Metrics")
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    total_processed = sum(m["requests_processed"] for m in agent_metrics.values())
    avg_success_rate = sum(m["success_rate"] for m in agent_metrics.values()) / len(agent_metrics)
    current_throughput = processing_history["records_processed"].iloc[-1]
    avg_quality = processing_history["avg_quality"].iloc[-1]
    
    with col1:
        st.metric("Total Records Processed", f"{total_processed:,}", "+156 today")
    
    with col2:
        st.metric("Average Success Rate", f"{avg_success_rate:.1%}", "+2.1%")
    
    with col3:
        st.metric("Current Throughput", f"{current_throughput}/hour", "+12/hour")
    
    with col4:
        st.metric("Average Data Quality", f"{avg_quality:.1%}", "+3.2%")
    
    # Performance charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Records Processed Over Time")
        fig_throughput = px.line(
            processing_history, 
            x="timestamp", 
            y="records_processed",
            title="Hourly Processing Volume",
            labels={"records_processed": "Records/Hour", "timestamp": "Time"}
        )
        fig_throughput.update_layout(height=300)
        st.plotly_chart(fig_throughput, use_container_width=True)
    
    with col2:
        st.subheader("Data Quality Trend")
        fig_quality = px.line(
            processing_history,
            x="timestamp",
            y="avg_quality", 
            title="Average Data Quality Score",
            labels={"avg_quality": "Quality Score", "timestamp": "Time"}
        )
        fig_quality.update_layout(height=300, yaxis_range=[0, 1])
        st.plotly_chart(fig_quality, use_container_width=True)

def render_record_processing_demo(customer_df):
    """Render interactive record processing demonstration"""
    st.subheader("🔍 Record Processing Demo")
    
    # Record selection
    selected_record = st.selectbox(
        "Select a customer record to process:",
        options=customer_df["id"].tolist(),
        format_func=lambda x: f"{x} - {customer_df[customer_df['id']==x]['first_name'].iloc[0]} {customer_df[customer_df['id']==x]['last_name'].iloc[0]}".strip()
    )
    
    if selected_record:
        record = customer_df[customer_df["id"] == selected_record].iloc[0]
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### Original Record Data")
            record_data = {
                "ID": record["id"],
                "Source": record["source_system"], 
                "First Name": record["first_name"],
                "Last Name": record["last_name"],
                "Email": record["email"],
                "Phone": record["phone"],
                "Address": record["address"],
                "City": record["city"],
                "State": record["state"],
                "ZIP": record["zip"]
            }
            
            for key, value in record_data.items():
                if value == "" or pd.isna(value):
                    st.markdown(f"**{key}:** <span style='color: red;'>*Missing*</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"**{key}:** {value}")
        
        with col2:
            st.markdown("#### Processing Results")
            
            # Quality score with color coding
            quality_score = record["quality_score"]
            if quality_score >= 0.8:
                quality_color = "green"
            elif quality_score >= 0.6:
                quality_color = "orange"
            else:
                quality_color = "red"
            
            st.markdown(f"**Quality Score:** <span style='color: {quality_color}; font-weight: bold;'>{quality_score:.1%}</span>", unsafe_allow_html=True)
            
            # Validation status
            validation_status = record["validation_status"]
            if "Valid" in validation_status:
                st.markdown(f"**Validation:** <span class='status-success'>{validation_status}</span>", unsafe_allow_html=True)
            elif "Error" in validation_status:
                st.markdown(f"**Validation:** <span class='status-error'>{validation_status}</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"**Validation:** <span class='status-warning'>{validation_status}</span>", unsafe_allow_html=True)
            
            # Processing status
            processing_status = record["processing_status"]
            if processing_status == "Completed":
                st.markdown(f"**Processing:** <span class='status-success'>{processing_status}</span>", unsafe_allow_html=True)
            elif processing_status == "In Progress":
                st.markdown(f"**Processing:** <span class='status-warning'>{processing_status}</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"**Processing:** <span class='status-error'>{processing_status}</span>", unsafe_allow_html=True)
        
        # Process button simulation
        if st.button(f"🚀 Re-process {selected_record}", type="primary"):
            with st.spinner("Processing record through multi-agent pipeline..."):
                # Simulate processing steps
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                steps = [
                    ("Data Quality Agent analyzing...", 20),
                    ("Data Validation Agent checking rules...", 40),
                    ("Data Enrichment Agent enhancing...", 60),
                    ("Data Resolution Agent resolving duplicates...", 80),
                    ("Data Governance Agent creating audit trail...", 100)
                ]
                
                for step_text, progress in steps:
                    status_text.text(step_text)
                    time.sleep(1.5)  # Simulate processing time
                    progress_bar.progress(progress)
                
                status_text.text("✅ Processing completed!")
                st.success(f"Record {selected_record} has been successfully processed through the multi-agent pipeline!")
                st.balloons()

def render_quality_analysis(customer_df):
    """Render data quality analysis dashboard"""
    st.subheader("📈 Data Quality Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Quality score distribution
        fig_quality_dist = px.histogram(
            customer_df,
            x="quality_score",
            nbins=10,
            title="Data Quality Score Distribution",
            labels={"quality_score": "Quality Score", "count": "Number of Records"}
        )
        fig_quality_dist.update_layout(height=300)
        st.plotly_chart(fig_quality_dist, use_container_width=True)
    
    with col2:
        # Processing status breakdown
        status_counts = customer_df["processing_status"].value_counts()
        fig_status = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Processing Status Breakdown"
        )
        fig_status.update_layout(height=300)
        st.plotly_chart(fig_status, use_container_width=True)
    
    # Source system quality comparison
    st.subheader("Quality by Source System")
    source_quality = customer_df.groupby("source_system").agg({
        "quality_score": ["mean", "count"]
    }).round(3)
    source_quality.columns = ["Average Quality", "Record Count"]
    
    fig_source = px.bar(
        x=source_quality.index,
        y=source_quality["Average Quality"],
        title="Average Data Quality by Source System",
        labels={"x": "Source System", "y": "Average Quality Score"}
    )
    fig_source.update_layout(height=300)
    st.plotly_chart(fig_source, use_container_width=True)

def render_agent_workflow():
    """Render agent workflow visualization"""
    st.subheader("🔄 Multi-Agent Workflow")
    
    st.markdown("""
    The PROFISEE MDM system uses 5 specialized agents working in coordination:
    """)
    
    # Workflow diagram using mermaid (simplified text version for demo)
    workflow_steps = [
        {"agent": "Data Quality Agent", "action": "Analyzes completeness, accuracy, consistency", "icon": "🔍"},
        {"agent": "Data Validation Agent", "action": "Validates against business rules and schemas", "icon": "✅"},
        {"agent": "Data Enrichment Agent", "action": "Enhances records with missing information", "icon": "📝"},
        {"agent": "Data Resolution Agent", "action": "Resolves duplicates and conflicts", "icon": "🔗"},
        {"agent": "Data Governance Agent", "action": "Creates audit trails and ensures compliance", "icon": "📋"}
    ]
    
    for i, step in enumerate(workflow_steps, 1):
        col1, col2, col3 = st.columns([1, 8, 1])
        
        with col1:
            st.markdown(f"### {i}")
        
        with col2:
            st.markdown(f"""
            **{step['icon']} {step['agent']}**  
            {step['action']}
            """)
        
        if i < len(workflow_steps):
            st.markdown("↓")

def render_sidebar():
    """Render sidebar with configuration and controls"""
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=64)
        st.title("MDM Control Panel")
        
        st.divider()
        
        # System status
        st.subheader("🟢 System Status")
        st.success("All agents operational")
        st.info(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
        
        st.divider()
        
        # Configuration
        st.subheader("⚙️ Configuration")
        
        quality_threshold = st.slider(
            "Quality Score Threshold", 
            min_value=0.0, 
            max_value=1.0, 
            value=0.7,
            help="Minimum quality score for automatic processing"
        )
        
        enable_auto_enrichment = st.checkbox(
            "Enable Auto-Enrichment", 
            value=True,
            help="Automatically enrich records with missing data"
        )
        
        enable_duplicate_resolution = st.checkbox(
            "Enable Duplicate Resolution",
            value=True, 
            help="Automatically resolve duplicate records"
        )
        
        st.divider()
        
        # Statistics
        st.subheader("📊 Quick Stats")
        st.metric("Records Today", "1,247", "+89")
        st.metric("Quality Improved", "89%", "+5%")
        st.metric("Duplicates Resolved", "127", "+12")
        
        st.divider()
        
        # Links
        st.subheader("🔗 Resources")
        st.markdown("- [Technical Architecture](https://github.com)")
        st.markdown("- [API Documentation](https://github.com)")
        st.markdown("- [Agent Framework Guide](https://github.com)")

def main():
    """Main application function"""
    
    # Load sample data
    customer_df, agent_metrics, processing_history = load_sample_data()
    
    # Render sidebar
    render_sidebar()
    
    # Render main content
    render_header()
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏠 Overview",
        "🤖 Agent Status", 
        "🔍 Process Records",
        "📊 Quality Analysis",
        "🔄 Workflow"
    ])
    
    with tab1:
        render_system_metrics(agent_metrics, processing_history)
        st.divider()
        
        # Quick summary
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📋 System Overview")
            st.markdown("""
            The PROFISEE Multi-Agent MDM system demonstrates:
            
            - **5 Specialized Agents** working in coordination
            - **Real-time Processing** of master data records
            - **Automated Quality Assessment** and improvement
            - **Intelligent Duplicate Resolution** across systems
            - **Comprehensive Audit Trails** for governance
            
            Built with **Microsoft Agent Framework (MAF)** and **Azure AI Services**.
            """)
        
        with col2:
            st.subheader("🎯 Key Benefits")
            st.markdown("""
            - **95%+ Data Quality** across all source systems
            - **80% Faster** master data processing
            - **Automated Compliance** with governance policies
            - **Real-time Insights** into data health
            - **Scalable Architecture** for enterprise growth
            """)
    
    with tab2:
        render_agent_status_overview(agent_metrics)
        st.divider()
        
        # Agent performance details
        st.subheader("📈 Agent Performance Details")
        
        perf_data = []
        for agent_name, metrics in agent_metrics.items():
            perf_data.append({
                "Agent": agent_name,
                "Status": metrics["status"],
                "Requests": metrics["requests_processed"],
                "Avg Response (s)": metrics["avg_response_time"],
                "Success Rate": f"{metrics['success_rate']:.1%}"
            })
        
        perf_df = pd.DataFrame(perf_data)
        st.dataframe(perf_df, use_container_width=True)
    
    with tab3:
        render_record_processing_demo(customer_df)
        st.divider()
        
        # Records table
        st.subheader("📋 Customer Records Overview")
        display_df = customer_df[[
            "id", "source_system", "first_name", "last_name", 
            "email", "quality_score", "validation_status", "processing_status"
        ]].copy()
        
        # Format quality score as percentage
        display_df["quality_score"] = display_df["quality_score"].apply(lambda x: f"{x:.1%}")
        
        st.dataframe(display_df, use_container_width=True)
    
    with tab4:
        render_quality_analysis(customer_df)
    
    with tab5:
        render_agent_workflow()
        
        st.divider()
        
        st.subheader("🏗️ Technical Architecture")
        st.markdown("""
        #### Microsoft Agent Framework (MAF) Implementation
        
        - **Agent Orchestration:** Coordinated multi-agent processing pipeline
        - **Azure OpenAI Integration:** GPT-4o for intelligent data analysis  
        - **Vector Search:** Azure AI Search for duplicate detection
        - **Multi-Model Storage:** Cosmos DB + Azure SQL for different data types
        - **Scalable Deployment:** Azure Container Apps with auto-scaling
        
        #### Data Flow
        
        1. **Ingestion:** Records from multiple source systems (Salesforce, SAP, Oracle)
        2. **Processing:** Multi-agent pipeline with quality gates
        3. **Enrichment:** AI-powered data enhancement and standardization
        4. **Resolution:** Duplicate detection and master record creation
        5. **Governance:** Audit trails and compliance validation
        """)

if __name__ == "__main__":
    main()