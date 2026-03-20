# RAG Demo Dashboard

A Streamlit-based dashboard that demonstrates Retrieval-Augmented Generation (RAG) using Azure AI Search for document retrieval and Azure OpenAI GPT-4o for answer generation.

## 🎮 Quick Start (Demo Mode)

Want to try it immediately? Run the demo version with mock data:

```bash
python launch.py --demo
# OR directly:
streamlit run rag_dashboard_demo.py
```

This demo mode works without any Azure credentials and uses simulated data to demonstrate the RAG workflow.

## Features

- 🔍 **Document Search**: Uses Azure AI Search to find relevant documents
- 🤖 **AI-Powered Answers**: Generates responses using Azure OpenAI GPT-4o
- 📊 **Relevance Scoring**: Shows document relevance scores for transparency
- 📚 **Source Display**: View source documents with metadata
- 📝 **Query History**: Track recent questions and answers
- ⚙️ **Configurable**: Adjust search parameters and AI temperature

## Prerequisites

- Azure AI Search service with an indexed document collection
- Azure OpenAI service with GPT-4o deployment
- Python 3.8 or higher

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Azure Services

Copy the environment template and fill in your Azure service details:

```bash
cp .env.template .env
```

Edit `.env` with your actual values:

```bash
# Azure AI Search Configuration
AZURE_SEARCH_ENDPOINT=https://your-search-service.search.windows.net
AZURE_SEARCH_KEY=your-search-api-key
AZURE_SEARCH_INDEX=your-index-name

# Azure OpenAI Configuration  
AZURE_OPENAI_ENDPOINT=https://your-openai-service.openai.azure.com
AZURE_OPENAI_KEY=your-openai-api-key
AZURE_OPENAI_DEPLOYMENT=gpt-4o
```

### 3. Prepare Your Search Index

Make sure your Azure AI Search index includes these fields:
- `content`: Main document text
- `title`: Document title (optional)
- `source`: Document source/URL (optional)
- `metadata`: Additional metadata (optional)

## Usage

### Running the Dashboard

**Option 1: Automatic launcher (Recommended)**
```bash
python launch.py
```
This will automatically detect if you have Azure dependencies and launch the appropriate version.

**Option 2: Full version (requires Azure services)**
```bash
streamlit run rag_dashboard.py
```

**Option 3: Demo version (works without Azure)**
```bash
streamlit run rag_dashboard_demo.py
```

The dashboard will be available at `http://localhost:8501`

### Using the Interface

1. **Configure Services**: Enter your Azure service details in the sidebar
2. **Ask Questions**: Type your question in the main input field
3. **Review Results**: 
   - View the AI-generated answer
   - Examine source documents with relevance scores
   - Check query history in the sidebar

### Configuration Options

- **Number of Documents**: Control how many documents to retrieve (1-10)
- **Response Temperature**: Adjust AI creativity (0.0 = deterministic, 1.0 = creative)

## Architecture

```
User Query → Azure AI Search → Relevant Documents → Azure OpenAI → Generated Answer
                ↓
            Document Sources + Relevance Scores
```

The RAG process:
1. User submits a question
2. Azure AI Search finds relevant documents
3. Documents are formatted as context
4. Azure OpenAI generates an answer based on the context
5. Both answer and source documents are displayed

## File Structure

```
copilot-outputs/
├── rag_dashboard.py         # Main Streamlit application (full version)
├── rag_dashboard_demo.py    # Demo version with mock data
├── launch.py               # Automatic launcher script
├── requirements.txt        # Python dependencies
├── .env.template          # Environment configuration template
└── README.md             # This file
```

## Customization

### Adding New Search Fields

Modify the `search_documents` method in `rag_dashboard.py`:

```python
select=["content", "title", "source", "metadata", "your_new_field"]
```

### Changing the AI Prompt

Modify the `system_prompt` in the `generate_answer` method:

```python
system_prompt = """Your custom prompt here..."""
```

### UI Customization

The Streamlit interface can be customized by modifying:
- Page configuration in `setup_page_config()`
- Layout and styling throughout the class methods
- CSS styling using `st.markdown()` with `unsafe_allow_html=True`

## Troubleshooting

### Common Issues

1. **"Azure dependencies not installed"**
   - Run: `pip install azure-search-documents azure-identity openai`

2. **"Missing configuration"**
   - Ensure all required fields in the sidebar are filled
   - Check your `.env` file values

3. **"No relevant documents found"**
   - Verify your search index contains data
   - Try different search terms
   - Check index field names match the expected fields

4. **API Errors**
   - Verify your API keys are correct and active
   - Check service endpoints are properly formatted
   - Ensure your Azure services are in the same region if required

### Debug Mode

Set Streamlit to debug mode for more detailed error information:

```bash
streamlit run rag_dashboard.py --logger.level=debug
```

## Security Notes

- Never commit actual API keys to version control
- Use environment variables or secure key management
- Consider implementing authentication for production use
- Monitor API usage to avoid unexpected charges

## License

This project is provided as a demonstration. Please ensure compliance with Azure service terms and your organization's policies.

## Contributing

This is a demo application. For production use, consider:
- Adding authentication and authorization
- Implementing caching for frequently asked questions
- Adding logging and monitoring
- Implementing rate limiting
- Adding unit tests
- Using async operations for better performance