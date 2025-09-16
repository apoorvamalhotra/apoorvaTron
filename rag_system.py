import os
import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from gemini_service import gemini_service
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

class PersonalRAGChatbot:
    def __init__(self):
        self.embeddings = None
        self.vectorstore = None
        self.setup_embeddings()
        
    def setup_embeddings(self):
        """Initialize Hugging Face embeddings"""
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'}
            )
            st.success("Embeddings model loaded successfully!")
        except Exception as e:
            st.error(f"Error loading embeddings: {str(e)}")
    
    
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
            
            st.success(f"Documents loaded and split into {len(chunks)} chunks!")
            return chunks
            
        except Exception as e:
            st.error(f"Error loading documents: {str(e)}")
            return []
    
    def create_vectorstore(self, chunks):
        """Create vector store from document chunks"""
        try:
            if not chunks:
                st.error("No document chunks available")
                return False
            
            # Create Chroma vector store
            self.vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory="./chroma_db"
            )
            
            st.success("Vector store created successfully!")
            return True
            
        except Exception as e:
            st.error(f"Error creating vector store: {str(e)}")
            return False
    
    
    def ask_question(self, question, session_id=None):
        """Ask a question and get an answer using Gemini API"""
        try:
            if not self.vectorstore:
                return "Vector store not initialized. Please set up the system first.", []
            
            # Get session ID
            if not session_id:
                session_id = str(uuid.uuid4())
            
            # Retrieve relevant documents
            retriever = self.vectorstore.as_retriever(search_kwargs={"k": 4})
            docs = retriever.get_relevant_documents(question)
            
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

def main():
    st.set_page_config(
        page_title="Apoorva's Personal RAG Chatbot",
        page_icon="💬",
        layout="wide"
    )
    
    st.title("Apoorva's Personal RAG Chatbot")
    st.markdown("Ask questions about Apoorva's professional experience, achievements, and career stories!")
    
    # Initialize session state
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = PersonalRAGChatbot()
    
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    
    # Sidebar for setup
    with st.sidebar:
        st.header("Setup")
        
        if st.button("Initialize System", type="primary"):
            with st.spinner("Setting up the RAG system..."):
                # Load and chunk documents
                chunks = st.session_state.chatbot.load_and_chunk_documents()
                
                if chunks:
                    # Create vector store
                    st.session_state.chatbot.create_vectorstore(chunks)
        
        st.markdown("---")
        
        # Show API statistics
        api_stats = gemini_service.get_api_stats()
        st.markdown("### API Statistics")
        st.markdown(f"Total Calls: {api_stats['total_calls']}")
        st.markdown(f"Successful: {api_stats['successful_calls']}")
        st.markdown(f"Failed: {api_stats['failed_calls']}")
        
        # Show conversation history
        conversation_history = gemini_service.get_conversation_history(st.session_state.session_id)
        if conversation_history:
            st.markdown("### Conversation History")
            for i, conv in enumerate(conversation_history[-4:], 1):  # Show last 4 messages
                role = "You" if conv['role'] == 'user' else "AI"
                st.markdown(f"**{role}:** {conv['content'][:100]}...")
        
        st.markdown("---")
        st.markdown("### Sample Questions")
        sample_questions = [
            "What was Apoorva's biggest accomplishment at Copart?",
            "Tell me about Apoorva's machine learning experience",
            "What technologies does Apoorva know?",
            "Describe a time Apoorva led a team through a crisis",
            "What is Apoorva's educational background?"
        ]
        
        for question in sample_questions:
            if st.button(question, key=f"sample_{question}"):
                st.session_state.user_question = question
    
    # Main chat interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Chat")
        
        # Chat input
        user_question = st.text_input(
            "Ask a question about Apoorva's experience:",
            value=st.session_state.get('user_question', ''),
            placeholder="e.g., What was Apoorva's biggest accomplishment at Copart?"
        )
        
        if st.button("Ask Question", type="primary") and user_question:
            with st.spinner("Thinking..."):
                answer, sources = st.session_state.chatbot.ask_question(
                    user_question, 
                    st.session_state.session_id
                )
                
                # Display answer
                st.markdown("### Answer")
                st.write(answer)
                
                # Display sources
                if sources:
                    with st.expander("Source Information"):
                        for i, source in enumerate(sources, 1):
                            st.markdown(f"**Source {i}:**")
                            st.text(source)
                
                # Clear the input
                st.session_state.user_question = ""
    
    with col2:
        st.subheader("About")
        st.markdown("""
        This RAG chatbot can answer questions about:
        
        - **Professional Experience** at Copart and TechCorp
        - **Technical Skills** and technologies
        - **Career Achievements** and accomplishments
        - **Behavioral Stories** in STAR format
        - **Educational Background**
        
        The system uses:
        - Hugging Face embeddings
        - Chroma vector database
        - Gemini 2.5 Flash LLM
        - Document chunking with LangChain
        """)

if __name__ == "__main__":
    main()
