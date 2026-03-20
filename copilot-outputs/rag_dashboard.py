"""
Streamlit RAG Dashboard
A demo application that uses Azure AI Search for document retrieval and Azure OpenAI for answer generation.
"""

import streamlit as st
import os
import json
from typing import List, Dict, Any
import requests
from dataclasses import dataclass
from datetime import datetime

# Azure SDK imports (install with: pip install azure-search-documents azure-identity openai)
try:
    from azure.search.documents import SearchClient
    from azure.core.credentials import AzureKeyCredential
    from openai import AzureOpenAI
    AZURE_DEPS_AVAILABLE = True
except ImportError:
    AZURE_DEPS_AVAILABLE = False
    st.error("Azure dependencies not installed. Run: pip install azure-search-documents azure-identity openai")

@dataclass
class SearchResult:
    """Represents a search result from Azure AI Search"""
    content: str
    title: str
    score: float
    source: str
    metadata: Dict[str, Any]

class RAGDashboard:
    """Main RAG Dashboard class"""
    
    def __init__(self):
        self.setup_page_config()
        self.setup_session_state()
        
    def setup_page_config(self):
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title="RAG Demo Dashboard",
            page_icon="🔍",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
    def setup_session_state(self):
        """Initialize session state variables"""
        if 'search_results' not in st.session_state:
            st.session_state.search_results = []
        if 'generated_answer' not in st.session_state:
            st.session_state.generated_answer = ""
        if 'query_history' not in st.session_state:
            st.session_state.query_history = []
    
    def render_sidebar(self):
        """Render the sidebar with configuration options"""
        st.sidebar.header("⚙️ Configuration")
        
        # Azure AI Search configuration
        st.sidebar.subheader("Azure AI Search")
        search_endpoint = st.sidebar.text_input(
            "Search Endpoint",
            value=os.getenv("AZURE_SEARCH_ENDPOINT", ""),
            help="Your Azure AI Search service endpoint"
        )
        search_key = st.sidebar.text_input(
            "Search API Key",
            value=os.getenv("AZURE_SEARCH_KEY", ""),
            type="password",
            help="Your Azure AI Search API key"
        )
        search_index = st.sidebar.text_input(
            "Search Index",
            value=os.getenv("AZURE_SEARCH_INDEX", "documents"),
            help="The name of your search index"
        )
        
        # Azure OpenAI configuration
        st.sidebar.subheader("Azure OpenAI")
        openai_endpoint = st.sidebar.text_input(
            "OpenAI Endpoint",
            value=os.getenv("AZURE_OPENAI_ENDPOINT", ""),
            help="Your Azure OpenAI service endpoint"
        )
        openai_key = st.sidebar.text_input(
            "OpenAI API Key",
            value=os.getenv("AZURE_OPENAI_KEY", ""),
            type="password",
            help="Your Azure OpenAI API key"
        )
        deployment_name = st.sidebar.text_input(
            "Deployment Name",
            value=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o"),
            help="Your GPT-4o deployment name"
        )
        
        # Search parameters
        st.sidebar.subheader("Search Parameters")
        top_k = st.sidebar.slider(
            "Number of documents to retrieve",
            min_value=1,
            max_value=10,
            value=5,
            help="How many relevant documents to retrieve"
        )
        
        # Temperature for OpenAI
        temperature = st.sidebar.slider(
            "Response Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.1,
            step=0.1,
            help="Controls randomness in the response (0.0 = deterministic, 1.0 = creative)"
        )
        
        return {
            'search_endpoint': search_endpoint,
            'search_key': search_key,
            'search_index': search_index,
            'openai_endpoint': openai_endpoint,
            'openai_key': openai_key,
            'deployment_name': deployment_name,
            'top_k': top_k,
            'temperature': temperature
        }
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate that all required configuration is provided"""
        required_fields = [
            'search_endpoint', 'search_key', 'search_index',
            'openai_endpoint', 'openai_key', 'deployment_name'
        ]
        
        missing_fields = [field for field in required_fields if not config.get(field)]
        
        if missing_fields:
            st.error(f"Missing configuration: {', '.join(missing_fields)}")
            return False
        return True
    
    def search_documents(self, query: str, config: Dict[str, Any]) -> List[SearchResult]:
        """Search for relevant documents using Azure AI Search"""
        if not AZURE_DEPS_AVAILABLE:
            return []
            
        try:
            # Initialize search client
            credential = AzureKeyCredential(config['search_key'])
            client = SearchClient(
                endpoint=config['search_endpoint'],
                index_name=config['search_index'],
                credential=credential
            )
            
            # Perform search
            results = client.search(
                search_text=query,
                top=config['top_k'],
                include_total_count=True,
                select=["content", "title", "source", "metadata"]  # Adjust field names as needed
            )
            
            # Convert to SearchResult objects
            search_results = []
            for result in results:
                search_results.append(SearchResult(
                    content=result.get('content', ''),
                    title=result.get('title', 'Untitled'),
                    score=result['@search.score'],
                    source=result.get('source', 'Unknown'),
                    metadata=result.get('metadata', {})
                ))
            
            return search_results
            
        except Exception as e:
            st.error(f"Error searching documents: {str(e)}")
            return []
    
    def generate_answer(self, query: str, context: str, config: Dict[str, Any]) -> str:
        """Generate an answer using Azure OpenAI"""
        if not AZURE_DEPS_AVAILABLE:
            return "Azure dependencies not available. Please install required packages."
            
        try:
            # Initialize OpenAI client
            client = AzureOpenAI(
                azure_endpoint=config['openai_endpoint'],
                api_key=config['openai_key'],
                api_version="2024-02-15-preview"
            )
            
            # Create the prompt
            system_prompt = """You are a helpful AI assistant that answers questions based on the provided context. 
            Use only the information from the context to answer the question. If the context doesn't contain 
            enough information to answer the question, say so clearly. Be accurate and concise."""
            
            user_prompt = f"""Context:
{context}

Question: {query}

Please provide a comprehensive answer based on the context above."""
            
            # Generate response
            response = client.chat.completions.create(
                model=config['deployment_name'],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=config['temperature'],
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            st.error(f"Error generating answer: {str(e)}")
            return "An error occurred while generating the answer."
    
    def render_main_interface(self, config: Dict[str, Any]):
        """Render the main interface"""
        st.title("🔍 RAG Demo Dashboard")
        st.markdown("Ask a question and get AI-powered answers based on your document collection.")
        
        # Query input
        col1, col2 = st.columns([4, 1])
        with col1:
            query = st.text_input(
                "Enter your question:",
                placeholder="What would you like to know?",
                key="query_input"
            )
        with col2:
            search_button = st.button("🔍 Search", type="primary", use_container_width=True)
        
        # Process query
        if search_button and query.strip():
            if not self.validate_config(config):
                return
                
            with st.spinner("Searching for relevant documents..."):
                # Search for documents
                search_results = self.search_documents(query, config)
                st.session_state.search_results = search_results
                
                if search_results:
                    # Prepare context from search results
                    context = "\n\n".join([
                        f"Document: {result.title}\nSource: {result.source}\nContent: {result.content}"
                        for result in search_results
                    ])
                    
                    with st.spinner("Generating AI response..."):
                        # Generate answer
                        answer = self.generate_answer(query, context, config)
                        st.session_state.generated_answer = answer
                        
                        # Add to query history
                        st.session_state.query_history.insert(0, {
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'query': query,
                            'answer': answer,
                            'num_sources': len(search_results)
                        })
                else:
                    st.warning("No relevant documents found for your query.")
                    st.session_state.generated_answer = ""
        
        # Display results
        if st.session_state.generated_answer:
            st.markdown("### 💡 AI Response")
            st.markdown(st.session_state.generated_answer)
        
        if st.session_state.search_results:
            st.markdown("### 📚 Source Documents")
            
            for i, result in enumerate(st.session_state.search_results, 1):
                with st.expander(f"Document {i}: {result.title} (Relevance: {result.score:.3f})"):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**Source:** {result.source}")
                        st.markdown(f"**Content:**")
                        st.text_area(
                            "Document content",
                            value=result.content,
                            height=200,
                            disabled=True,
                            label_visibility="collapsed",
                            key=f"content_{i}"
                        )
                    with col2:
                        st.metric("Relevance Score", f"{result.score:.3f}")
                        if result.metadata:
                            st.markdown("**Metadata:**")
                            st.json(result.metadata)
    
    def render_query_history(self):
        """Render query history in sidebar"""
        if st.session_state.query_history:
            st.sidebar.markdown("### 📝 Query History")
            for i, item in enumerate(st.session_state.query_history[:5]):  # Show last 5 queries
                with st.sidebar.expander(f"{item['timestamp']} ({item['num_sources']} sources)"):
                    st.markdown(f"**Q:** {item['query']}")
                    st.markdown(f"**A:** {item['answer'][:150]}...")
    
    def render_footer(self):
        """Render footer information"""
        st.markdown("---")
        st.markdown(
            """
            <div style='text-align: center; color: #666;'>
                <p>RAG Demo Dashboard | Powered by Azure AI Search & Azure OpenAI</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    def run(self):
        """Main application entry point"""
        # Render sidebar and get configuration
        config = self.render_sidebar()
        
        # Render query history in sidebar
        self.render_query_history()
        
        # Render main interface
        self.render_main_interface(config)
        
        # Render footer
        self.render_footer()

# Main execution
if __name__ == "__main__":
    if not AZURE_DEPS_AVAILABLE:
        st.error("""
        **Missing Dependencies!**
        
        Please install the required Azure packages:
        ```bash
        pip install azure-search-documents azure-identity openai streamlit
        ```
        """)
    else:
        app = RAGDashboard()
        app.run()