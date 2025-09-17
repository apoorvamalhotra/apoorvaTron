import os
import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from gemini_service import gemini_service
from dotenv import load_dotenv
import uuid

# Try to import embeddings with fallback
try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class PersonalRAGChatbot:
    def __init__(self):
        self.embeddings = None
        self.vectorstore = None
        self.setup_embeddings()
        
    def setup_embeddings(self):
        """Initialize embeddings - try multiple approaches"""
        if not EMBEDDINGS_AVAILABLE:
            logger.error("Embeddings not available - cannot initialize RAG system")
            self.embeddings = None
            return False
            
        try:
            logger.info("Loading Hugging Face embeddings model...")
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'}
            )
            logger.info("Embeddings model loaded successfully!")
            return True
        except Exception as e:
            logger.error(f"Error loading embeddings: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            self.embeddings = None
            return False
    
    
    def load_and_chunk_documents(self):
        """Load documents and split them into chunks"""
        try:
            # Read resume
            with open('data/resume.txt', 'r', encoding='utf-8') as f:
                resume_text = f.read()
            
            # Read behavioral Q&A
            with open('data/behavioral_qa.txt', 'r', encoding='utf-8') as f:
                behavioral_text = f.read()
            
            # Combine documents
            documents = [resume_text, behavioral_text]
            
            # Initialize text splitter
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
            )
            
            # Split documents
            chunks = text_splitter.create_documents(documents)
            
            logger.info(f"Documents loaded and split into {len(chunks)} chunks!")
            return chunks
            
        except Exception as e:
            logger.error(f"Error loading documents: {str(e)}")
            return []
    
    def create_vectorstore(self, chunks):
        """Create vector store from document chunks"""
        try:
            if not chunks:
                logger.error("No document chunks available")
                return False
            
            # Check if embeddings are loaded
            if self.embeddings is None:
                logger.error("Embeddings not loaded - attempting to reload...")
                self.setup_embeddings()
                if self.embeddings is None:
                    logger.error("Failed to load embeddings")
                    return False
            
            # Try to load existing vector store first
            try:
                logger.info("Attempting to load existing vector store...")
                self.vectorstore = Chroma(
                    persist_directory="./chroma_db",
                    embedding_function=self.embeddings
                )
                logger.info("Existing vector store loaded successfully!")
                return True
            except Exception as e:
                logger.info(f"Could not load existing vector store: {str(e)}")
                logger.info("Creating new vector store...")
            
            # Create new Chroma vector store
            self.vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory="./chroma_db"
            )
            
            logger.info("Vector store created successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Error creating vector store: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    def _smart_workflow_retrieve(self, question):
        """Smart workflow: timeline questions -> sys prompt -> retrieve; company questions -> direct retrieve"""
        question_lower = question.lower()
        
        # Check if question mentions a specific company
        companies = {
            'stealth startup': 'Stealth Startup',
            'startup': 'Stealth Startup',
            'meta': 'Meta', 
            'facebook': 'Meta',
            'copart': 'Copart',
            'scale ai': 'Scale AI',
            'fidelity': 'Fidelity'
        }
        
        # Direct company name questions
        for keyword, company_name in companies.items():
            if keyword in question_lower:
                return self._retrieve_company_experience(company_name)
        
        # Timeline/experience questions - let system prompt handle company identification
        timeline_keywords = ['most recent', 'last company', 'current', 'latest', 'recent experience', 'previous', 'earliest', 'first']
        if any(keyword in question_lower for keyword in timeline_keywords):
            # For timeline questions, get broader context and let system prompt decide
            retriever = self.vectorstore.as_retriever(search_kwargs={"k": 6})
            return retriever.get_relevant_documents(question)
        
        # General questions - default retrieval
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": 4})
        return retriever.get_relevant_documents(question)
    
    def _retrieve_company_experience(self, company_name):
        """Retrieve experience for a specific company"""
        # Search for chunks containing this company name with more specific queries
        if company_name == "Meta":
            company_docs = self.vectorstore.similarity_search("Meta Technical Program Manager Global Security GPS anomaly detection", k=4)
        elif company_name == "Copart":
            company_docs = self.vectorstore.similarity_search("Copart Technical Product Manager Generative AI platform", k=4)
        elif company_name == "Stealth Startup":
            company_docs = self.vectorstore.similarity_search("Stealth Startup AI Product Lead travel concierge", k=4)
        elif company_name == "Scale AI":
            company_docs = self.vectorstore.similarity_search("Scale AI Product Manager", k=4)
        elif company_name == "Fidelity":
            company_docs = self.vectorstore.similarity_search("Fidelity International Limited Global Infrastructure Automation", k=4)
        else:
            company_docs = self.vectorstore.similarity_search(company_name, k=4)
        
        return company_docs
    
    def ask_question(self, question, session_id=None):
        """Ask a question and get an answer using Gemini API"""
        try:
            if not self.vectorstore:
                return "Vector store not initialized. Please set up the system first.", []
            
            # Get session ID
            if not session_id:
                session_id = str(uuid.uuid4())
            
            # Smart workflow: Determine question type and retrieve accordingly
            docs = self._smart_workflow_retrieve(question)
            
            
            # Extract context from retrieved documents
            context_documents = [doc.page_content for doc in docs]
            
            # Check if this is the first call for this session
            conversation_history = gemini_service.get_conversation_history(session_id)
            is_first_call = len(conversation_history) == 0
            
            # Call Gemini API
            answer, error = gemini_service.call_gemini_api(
                chat_session_id=session_id,
                user_input=question,
                context_documents=context_documents,
                is_first_call=is_first_call
            )
            
            if error:
                return f"Error: {error}", []
            
            # Store conversation
            gemini_service.store_conversation(session_id, question, answer)
            
            # Prepare source information
            source_info = []
            for doc in docs:
                source_info.append(doc.page_content[:200] + "...")
            
            return answer, source_info
            
        except Exception as e:
            return f"Error getting answer: {str(e)}", []

# Flask-compatible RAG system - no Streamlit dependencies