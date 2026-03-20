"""
RAG Dashboard Demo Mode
A simplified version that works without Azure credentials for demonstration purposes.
"""

import streamlit as st
import json
import time
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SearchResult:
    """Represents a search result from Azure AI Search"""
    content: str
    title: str
    score: float
    source: str
    metadata: Dict[str, Any]

class RAGDashboardDemo:
    """Demo RAG Dashboard class with mock data"""
    
    def __init__(self):
        self.setup_page_config()
        self.setup_session_state()
        self.setup_mock_data()
        
    def setup_page_config(self):
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title="RAG Demo Dashboard (Demo Mode)",
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
    
    def setup_mock_data(self):
        """Setup mock documents for demonstration"""
        self.mock_documents = [
            {
                "content": "Azure AI Search is a cloud search service that provides infrastructure, APIs, and tools for building rich search applications. It offers vector search capabilities, semantic ranking, and integration with Azure OpenAI Service for advanced AI-powered search scenarios.",
                "title": "Azure AI Search Overview",
                "source": "azure-docs/search/overview.md",
                "metadata": {"category": "documentation", "last_updated": "2024-01-15"}
            },
            {
                "content": "Retrieval-Augmented Generation (RAG) is an approach that combines the power of large language models with external knowledge sources. By first retrieving relevant information from a knowledge base and then using it to generate responses, RAG systems can provide more accurate and contextual answers.",
                "title": "Understanding RAG Architecture",
                "source": "ai-patterns/rag-guide.md",
                "metadata": {"category": "architecture", "complexity": "intermediate"}
            },
            {
                "content": "Azure OpenAI Service provides REST API access to OpenAI's powerful language models including GPT-4, GPT-3.5, and Embeddings models. These models can be used for a wide variety of natural language tasks including content generation, summarization, and semantic search.",
                "title": "Azure OpenAI Service Guide",
                "source": "azure-docs/openai/overview.md",
                "metadata": {"category": "documentation", "service": "openai"}
            },
            {
                "content": "Vector search enables you to index, store, and retrieve data based on high-dimensional vector representations. This is particularly useful for semantic search scenarios where you want to find content based on meaning rather than exact keyword matches.",
                "title": "Vector Search Fundamentals",
                "source": "search-patterns/vector-search.md",
                "metadata": {"category": "technology", "difficulty": "advanced"}
            },
            {
                "content": "Streamlit is an open-source Python framework that makes it easy to create and share beautiful, custom web apps for machine learning and data science. With just a few lines of code, you can build interactive dashboards and deploy them instantly.",
                "title": "Building Apps with Streamlit",
                "source": "frameworks/streamlit-guide.md",
                "metadata": {"category": "development", "framework": "streamlit"}
            }
        ]
    
    def render_sidebar(self):
        """Render the sidebar with configuration options"""
        st.sidebar.header("⚙️ Demo Configuration")
        
        # Demo mode notice
        st.sidebar.info("🎮 **Demo Mode**: Using mock data instead of Azure services")
        
        # Search parameters
        st.sidebar.subheader("Search Parameters")
        top_k = st.sidebar.slider(
            "Number of documents to retrieve",
            min_value=1,
            max_value=5,
            value=3,
            help="How many relevant documents to retrieve"
        )
        
        # Temperature for response generation
        temperature = st.sidebar.slider(
            "Response Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.1,
            step=0.1,
            help="Controls randomness in the response (0.0 = deterministic, 1.0 = creative)"
        )
        
        # Simulation delay
        simulation_delay = st.sidebar.slider(
            "Simulation Delay (seconds)",
            min_value=0.5,
            max_value=3.0,
            value=1.5,
            step=0.5,
            help="Simulate processing time"
        )
        
        return {
            'top_k': top_k,
            'temperature': temperature,
            'simulation_delay': simulation_delay
        }
    
    def search_documents(self, query: str, config: Dict[str, Any]) -> List[SearchResult]:
        """Mock document search with relevance scoring"""
        query_lower = query.lower()
        results = []
        
        # Simple keyword-based relevance scoring
        for doc in self.mock_documents:
            score = 0.0
            
            # Check for keyword matches in content and title
            content_words = doc['content'].lower().split()
            title_words = doc['title'].lower().split()
            query_words = query_lower.split()
            
            for word in query_words:
                if word in content_words:
                    score += 0.3
                if word in title_words:
                    score += 0.5
                if word in doc['content'].lower():
                    score += 0.2
            
            # Add some randomness to make it more realistic
            import random
            score += random.uniform(0.0, 0.1)
            
            if score > 0:
                results.append(SearchResult(
                    content=doc['content'],
                    title=doc['title'],
                    score=min(score, 1.0),  # Cap at 1.0
                    source=doc['source'],
                    metadata=doc['metadata']
                ))
        
        # Sort by score and return top_k
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:config['top_k']]
    
    def generate_answer(self, query: str, context: str, config: Dict[str, Any]) -> str:
        """Mock answer generation"""
        # Simple pattern-based response generation
        query_lower = query.lower()
        
        if 'azure' in query_lower:
            if 'search' in query_lower:
                return "Based on the provided documents, Azure AI Search is a comprehensive cloud search service that offers infrastructure, APIs, and tools for building rich search applications. It includes features like vector search capabilities, semantic ranking, and integration with Azure OpenAI Service, making it ideal for creating AI-powered search experiences and RAG applications."
            elif 'openai' in query_lower:
                return "According to the documentation, Azure OpenAI Service provides REST API access to OpenAI's powerful language models including GPT-4, GPT-3.5, and Embeddings models. This service enables developers to integrate advanced natural language processing capabilities into their applications for tasks like content generation, summarization, and semantic search."
        
        elif 'rag' in query_lower:
            return "Based on the retrieved information, Retrieval-Augmented Generation (RAG) is an advanced approach that combines large language models with external knowledge sources. The process involves first retrieving relevant information from a knowledge base, then using that information to generate more accurate and contextual responses. This architecture is particularly powerful for creating AI systems that can provide factual, up-to-date answers grounded in specific document collections."
        
        elif 'vector' in query_lower or 'search' in query_lower:
            return "According to the provided context, vector search enables indexing, storing, and retrieving data based on high-dimensional vector representations. This technology is particularly valuable for semantic search scenarios where the goal is to find content based on meaning and context rather than exact keyword matches, making it a key component in modern AI-powered search systems."
        
        elif 'streamlit' in query_lower:
            return "Based on the documentation, Streamlit is an open-source Python framework designed to make it easy to create and share beautiful, custom web apps for machine learning and data science. With minimal code, developers can build interactive dashboards and deploy them quickly, making it an excellent choice for prototyping and demonstrating AI applications like this RAG dashboard."
        
        else:
            return f"Based on the retrieved documents, I can provide information related to your query about '{query}'. The context includes information about Azure AI services, RAG architectures, vector search, and development frameworks. Please ask more specific questions about these topics for detailed answers."
    
    def render_main_interface(self, config: Dict[str, Any]):
        """Render the main interface"""
        st.title("🔍 RAG Demo Dashboard")
        st.markdown("**Demo Mode**: Ask questions about Azure AI, RAG, or search technologies!")
        
        # Sample questions
        st.markdown("### 💡 Try these sample questions:")
        sample_questions = [
            "What is Azure AI Search?",
            "How does RAG work?",
            "What is vector search?",
            "Tell me about Azure OpenAI",
            "How do I use Streamlit?"
        ]
        
        cols = st.columns(len(sample_questions))
        for i, question in enumerate(sample_questions):
            if cols[i].button(f"❓ {question}", key=f"sample_{i}"):
                st.session_state.query_input = question
                st.rerun()
        
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
            with st.spinner("Searching for relevant documents..."):
                time.sleep(config['simulation_delay'] / 2)
                
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
                        time.sleep(config['simulation_delay'] / 2)
                        
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
                <p>RAG Demo Dashboard (Demo Mode) | Simulated Azure AI Search & OpenAI</p>
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
    app = RAGDashboardDemo()
    app.run()