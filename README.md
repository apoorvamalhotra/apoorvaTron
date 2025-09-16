# Personal RAG Chatbot for Resume

A Retrieval-Augmented Generation (RAG) chatbot that can answer questions about Apoorva's professional experience based on resume and behavioral interview stories.

## Features

- **Document Processing**: Automatically chunks resume and behavioral Q&A documents
- **Vector Search**: Uses Hugging Face embeddings with Chroma vector database
- **AI Responses**: Powered by Google Gemini 2.0 Flash via direct API calls
- **Web Interface**: Clean, intuitive Streamlit frontend
- **Source Transparency**: Shows which documents were used for each answer
- **Conversation Memory**: Maintains conversation history per session
- **API Statistics**: Real-time tracking of API call success/failure rates

## Tech Stack

- **Python**: Core programming language
- **LangChain**: Document processing and chunking
- **Sentence Transformers**: Hugging Face embeddings (`all-MiniLM-L6-v2`)
- **Chroma**: Local vector database for embeddings storage
- **Google Gemini API**: Direct API calls for generating responses
- **Flask**: Web application framework for the chat interface
- **Streamlit**: Alternative web application interface
- **Requests**: HTTP library for API communication

## Prerequisites

- Python 3.8 or higher
- Google Gemini API key (free tier available)

## Quick Start

### 1. Clone and Setup

```bash
# Navigate to your project directory
cd apoorvatron

# Install dependencies
pip install -r requirements.txt
```

### 2. Get Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the API key

### 3. Configure Environment

Create a `.env` file in the project root and add your Gemini API key:

```bash
# Create .env file and add your API key
GEMINI_API_KEY=your_actual_api_key_here
```

### 4. Prepare Your Documents

Replace the content in these files with your actual data:
- `data/resume.txt` - Your resume content
- `data/behavioral_qa.txt` - Your behavioral interview stories in STAR format

### 5. Run the Application

You have two options to run the application:

**Option 1: Flask Web App (Recommended)**
```bash
python app.py
```
The application will open in your browser at `http://localhost:8080`

**Option 2: Streamlit Interface**
```bash
streamlit run rag_system.py
```
The application will open in your browser at `http://localhost:8501`

## Usage

### Flask Web App
1. **Start Chat**: Click "Start Chat" to begin your conversation with Apoorvatron (a random test ID is generated automatically)
2. **Ask Questions**: Type questions about Apoorva's experience, achievements, or career stories
3. **View Sources**: The AI will show which parts of the documents were used for each answer
4. **Switch Sessions**: Use the "Switch Session" button to start a new conversation with a new random test ID

### Streamlit Interface
1. **Initialize System**: Click "Initialize System" in the sidebar to load and process your documents
2. **Ask Questions**: Type questions about your experience, achievements, or career stories
3. **View Sources**: Expand "Source Information" to see which parts of your documents were used

### Sample Questions

- "What was Apoorva's biggest accomplishment at Copart?"
- "Tell me about Apoorva's machine learning experience"
- "What technologies does Apoorva know?"
- "Describe a time Apoorva led a team through a crisis"
- "What is Apoorva's educational background?"

## Project Structure

```
apoorvatron/
├── data/
│   ├── resume.txt              # Resume content
│   └── behavioral_qa.txt       # Behavioral Q&A stories
├── rag_system.py              # Main Streamlit application
├── gemini_service.py          # Gemini API service
├── sys_prompt.py              # System prompt configuration
├── app.py                    # Flask web application
├── requirements.txt           # Python dependencies
├── run.py                    # Application launcher
├── test_system.py            # System testing script
├── templates/
│   └── index.html            # HTML template for web UI
├── static/
│   ├── style.css             # CSS styling
│   ├── script.js             # JavaScript functionality
│   └── images/               # UI images
├── chroma_db/               # Vector database (created automatically)
└── README.md               # This file
```

## Configuration

### Document Chunking
The system uses `RecursiveCharacterTextSplitter` with:
- Chunk size: 1000 characters
- Chunk overlap: 200 characters

### Embeddings
- Model: `sentence-transformers/all-MiniLM-L6-v2`
- Device: CPU (change to 'cuda' for GPU)

### Vector Database
- Database: Chroma
- Storage: Local directory (`./chroma_db`)
- Retrieval: Top 4 most relevant chunks

### LLM Settings
- Model: Gemini 2.0 Flash (via direct API calls)
- Temperature: 0.1 (for consistent responses)
- API Endpoint: Google Generative Language API

## How It Works

1. **Document Loading**: Reads resume and behavioral Q&A files
2. **Text Chunking**: Splits documents into manageable chunks
3. **Embedding Creation**: Converts text chunks to vector embeddings
4. **Vector Storage**: Stores embeddings in Chroma database
5. **Query Processing**: Converts user questions to embeddings
6. **Similarity Search**: Finds most relevant document chunks
7. **Response Generation**: Uses Gemini API to generate answers based on retrieved context
8. **Conversation History**: Maintains session-based conversation memory

## Troubleshooting

### Common Issues

**API Key Error**
```
Please set your GEMINI_API_KEY in the .env file
```
- Ensure your `.env` file exists and contains the correct API key

**Embeddings Loading Error**
```
Error loading embeddings
```
- Check internet connection for downloading the model
- Ensure sufficient disk space

**Document Loading Error**
```
Error loading documents
```
- Verify that `data/resume.txt` and `data/behavioral_qa.txt` exist
- Check file permissions

### Performance Tips

- First run may be slow due to model downloads
- Consider using GPU for embeddings if available
- Vector database persists between runs for faster startup

## Future Enhancements

- [ ] Support for PDF and DOCX files
- [ ] Multiple embedding models comparison
- [ ] Conversation memory/history
- [ ] Export chat conversations
- [ ] Advanced search filters
- [ ] Multi-language support

## License

This project is for personal use and educational purposes.

## Contributing

Feel free to fork this project and customize it for your own resume and career stories!

---

**Happy chatting with your AI assistant!**
