"""
Flask application for ApoorvaTron - Personal RAG Chatbot
"""

import os
import uuid
import random
import string
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from rag_system import PersonalRAGChatbot
from gemini_service import gemini_service
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize the RAG system
rag_chatbot = PersonalRAGChatbot()

def generate_test_id():
    """Generate a random test ID in format: test_XXXXXXXXX"""
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
    return f"test_{random_suffix}"

@app.route('/')
def index():
    """Serve the main chat interface"""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        user_input = data.get('user_input', '').strip()
        userid = data.get('userid', generate_test_id())
        
        logger.info(f"Received message from user {userid}: {user_input}")
        
        if not user_input:
            return jsonify({'error': 'Please provide a message'}), 400
        
        # Handle initialization
        if user_input.lower() in ['hi', 'hello', 'hey', 'start']:
            welcome_message = """Hello! I'm ApoorvaTron, representing Apoorva, a Senior Technical Product Manager with 7 years of experience building foundational AI platforms & developer-centric tools. 

I can answer questions about Apoorva's professional experience, achievements, and career stories. What would you like to know about Apoorva's background?"""
            
            return jsonify({
                'next_question': welcome_message,
                'userid': userid,
                'status': 'ready'
            })
        
        # Initialize RAG system if not already done
        if rag_chatbot.vectorstore is None:
            logger.info("Initializing RAG system on first request...")
            try:
                logger.info("Loading and chunking documents...")
                chunks = rag_chatbot.load_and_chunk_documents()
                logger.info(f"Loaded {len(chunks) if chunks else 0} chunks")
                
                if chunks:
                    logger.info("Creating vector store...")
                    success = rag_chatbot.create_vectorstore(chunks)
                    if success:
                        logger.info("RAG system initialized successfully!")
                    else:
                        logger.error("Failed to create vector store")
                        return jsonify({
                            'error': 'Failed to create vector store. Please try again later.',
                            'userid': userid
                        }), 500
                else:
                    logger.error("No chunks loaded from documents")
                    return jsonify({
                        'error': 'Failed to load documents. Please check if data files exist.',
                        'userid': userid
                    }), 500
            except Exception as e:
                logger.error(f"Failed to initialize RAG system: {str(e)}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                return jsonify({
                    'error': f'Failed to initialize the knowledge base: {str(e)}',
                    'userid': userid
                }), 500
        
        # Process the question using RAG system
        answer, sources = rag_chatbot.ask_question(user_input, userid)
        
        # Store the conversation
        gemini_service.store_conversation(userid, user_input, answer)
        
        return jsonify({
            'next_question': answer,
            'userid': userid,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        return jsonify({
            'error': 'Sorry, I encountered an error processing your message. Please try again.',
            'userid': userid or str(uuid.uuid4())
        }), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'ApoorvaTron RAG Chatbot'
    })

@app.route('/stats')
def stats():
    """Get API statistics"""
    try:
        api_stats = gemini_service.get_api_stats()
        return jsonify({
            'api_stats': api_stats,
            'vectorstore_ready': rag_chatbot.vectorstore is not None
        })
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({'error': 'Could not retrieve statistics'}), 500

if __name__ == '__main__':
    # Run the Flask app - RAG system will initialize on first request
    logger.info("Starting ApoorvaTron Flask app...")
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
