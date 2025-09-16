# ApoorvaTron - Personal RAG Chatbot

A Retrieval-Augmented Generation (RAG) chatbot that represents Apoorva Malhotra, answering questions about her professional experience, achievements, and career stories using her resume and behavioral interview data.

## Features

- **AI-Powered Responses**: Uses Google Gemini 2.5 Flash for intelligent, context-aware answers
- **Document-Based Knowledge**: Built from resume and behavioral Q&A documents
- **Vector Search**: ChromaDB with Hugging Face embeddings for accurate information retrieval
- **Web Interface**: Clean, modern Flask-based chat interface
- **Conversation Memory**: Maintains session-based conversation history
- **Real-time Stats**: API usage and performance monitoring

## Live Demo

**Deployed on Google Cloud Run**: [URL will be here after deployment]

## 🛠️ Tech Stack

- **Backend**: Python Flask
- **AI/ML**: Google Gemini API, LangChain, Sentence Transformers
- **Vector Database**: ChromaDB
- **Frontend**: HTML, CSS, JavaScript
- **Deployment**: Google Cloud Run (serverless)


## Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/apoorvamalhotra/apoorvaTron.git
   cd apoorvaTron
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment**
   ```bash
   # Create .env file
   echo "GEMINI_API_KEY=your_actual_api_key_here" > .env
   ```

4. **Run the application**
   ```bash
   python app.py
   ```
   
   Visit: `http://localhost:8080`

### Google Cloud Deployment

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com
   - Create a new project

2. **Enable APIs**
   - Cloud Run API
   - Cloud Build API

3. **Deploy from GitHub**
   - Go to Cloud Run → Create Service
   - Connect repository: `apoorvamalhotra/apoorvaTron`
   - Set environment variable: `GEMINI_API_KEY=your_key`
   - Deploy!

## Usage

### Sample Questions

- "What was your last company?"
- "Tell me about your AI/ML experience"
- "What technologies do you know?"
- "Describe a time you led a team through a crisis"
- "What's your educational background?"
- "Tell me about your product management experience"


## Project Structure

```
apoorvatron/
├── app.py                 # Main Flask application
├── app.yaml              # Google Cloud configuration
├── rag_system.py         # RAG logic and document processing
├── gemini_service.py     # Gemini API integration
├── sys_prompt.py         # System prompts 
├── requirements.txt      # Python dependencies
├── data/
│   ├── resume.txt        # Resume content
│   └── behavioral_qa.txt # Behavioral Q&A stories
├── static/
│   ├── style.css         # Styling
│   ├── script.js         # Frontend logic
│   └── images/           # UI assets
├── templates/
│   └── index.html        # Chat interface
└── README.md
```

## Configuration

### Document Processing
- **Chunk Size**: 1000 characters
- **Chunk Overlap**: 200 characters
- **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2`

### AI Settings
- **Model**: Gemini 2.0 Flash
- **Temperature**: 0.1 (consistent responses)
- **Retrieval**: Top 4 most relevant chunks

## How It Works

1. **Document Loading**: Reads resume and behavioral Q&A files
2. **Text Chunking**: Splits documents into manageable pieces
3. **Embedding Creation**: Converts text to vector embeddings
4. **Vector Storage**: Stores embeddings in ChromaDB
5. **Query Processing**: Converts user questions to embeddings
6. **Similarity Search**: Finds most relevant document chunks
7. **Response Generation**: Uses Gemini API with retrieved context
8. **Session Management**: Maintains conversation history

---

**Built by Apoorva Malhotra**