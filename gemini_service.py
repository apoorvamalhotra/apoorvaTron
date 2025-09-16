"""
Gemini API Service for direct API calls (single prompt architecture).
Handles conversation history and API communication with Gemini.
"""
import os
import requests
import json
import logging
from typing import Dict, Any, List, Tuple
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class GeminiAPIService:
    """Service for direct Gemini API calls with conversation history management."""
    
    def __init__(self):
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        self.GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
        
        # Store conversation history per session
        self._conversation_store = {}
        
        # Store system instruction per session (sent only once)
        self._system_instructions = {}
        
        # API call statistics
        self._api_call_count = 0
        self._successful_calls = 0
        self._failed_calls = 0
    
    def call_gemini_api(self, chat_session_id: str, user_input: str, context_documents: List[str], is_first_call: bool = False) -> Tuple[str, str]:
        """
        Calls the Gemini API with context documents and conversation history.
        Returns a tuple of (response_text, error_message).
        """
        if not self.GEMINI_API_KEY:
            return None, "API key is not configured."

        self._api_call_count += 1
        
        try:
            # Build payload based on whether it's the first call or not
            if is_first_call:
                # First call: send system_instruction + formatted user input with context
                payload = self._build_first_call_payload(chat_session_id, user_input, context_documents)
            else:
                # Subsequent calls: send conversation history + new formatted user input with context
                payload = self._build_conversation_payload(chat_session_id, user_input, context_documents)
            
            headers = {'Content-Type': 'application/json', 'X-goog-api-key': self.GEMINI_API_KEY}
            
            logger.info(f"Gemini API call #{self._api_call_count} for session {chat_session_id}")
            
            response = requests.post(self.GEMINI_API_URL, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            api_response = response.json()
            
            # Extract response text
            if 'candidates' in api_response and api_response['candidates']:
                candidate = api_response['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    response_text = candidate['content']['parts'][0]['text']
                    
                    # Debug: Log the raw response from Gemini
                    logger.info(f"Raw Gemini API response: {response_text}")
                    
                    self._successful_calls += 1
                    logger.info(f"Gemini API call successful")
                    return response_text, None
                else:
                    self._failed_calls += 1
                    return None, "Unexpected response format from Gemini API"
            else:
                self._failed_calls += 1
                return None, "No candidates in Gemini API response"

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error calling Gemini API: {e}")
            self._failed_calls += 1
            return None, "Sorry, I encountered a network error. Could you please repeat that?"
        except Exception as e:
            logger.error(f"Unexpected error calling Gemini API: {e}")
            self._failed_calls += 1
            return None, "Sorry, I received an unexpected response. Could you please try again?"
    
    def _build_first_call_payload(self, chat_session_id: str, user_input: str, context_documents: List[str]) -> Dict[str, Any]:
        """Build payload for the first API call with system_instruction."""
        # Get the system instruction
        system_instruction = self._get_system_instruction()
        
        # Store it for this session
        self._system_instructions[chat_session_id] = system_instruction
        
        # Format the user message to include context and user input
        formatted_user_message = self._format_user_message_with_context(user_input, context_documents)
        
        payload = {
            "system_instruction": {
                "parts": [
                    {
                        "text": system_instruction
                    }
                ]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": formatted_user_message
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.0,
                "top_p": 0.5,
                "top_k": 30
            }
        }
        
        return payload
    
    def _build_conversation_payload(self, chat_session_id: str, user_input: str, context_documents: List[str]) -> Dict[str, Any]:
        """Build payload for subsequent API calls with conversation history."""
        # Get stored conversation history
        stored_history = self._conversation_store.get(chat_session_id, [])
        
        # Build contents array with conversation history + new formatted user input
        contents = []
        
        # Add conversation history from stored messages
        for conv in stored_history:
            role = "model" if conv['role'] == 'assistant' else "user"
            contents.append({
                "role": role,
                "parts": [{"text": conv['content']}]
            })
        
        # Add new formatted user input with context
        formatted_user_message = self._format_user_message_with_context(user_input, context_documents)
        contents.append({
            "role": "user",
            "parts": [{"text": formatted_user_message}]
        })
        
        payload = {
            "system_instruction": {
                "parts": [
                    {
                        "text": self._system_instructions.get(chat_session_id, self._get_system_instruction())
                    }
                ]
            },
            "contents": contents,
            "generationConfig": {
                "temperature": 0.0,
                "top_p": 0.5,
                "top_k": 20
            }
        }
        
        return payload
    
    def _format_user_message_with_context(self, user_input: str, context_documents: List[str]) -> str:
        """Format user message to include context documents and user input."""
        context_text = "\n\n".join(context_documents) if context_documents else "No relevant context found."
        
        formatted_message = f"""IMPORTANT: You must ONLY use information from the context below. Do not add any details not explicitly mentioned in the context.

CONTEXT INFORMATION:
{context_text}

USER'S QUESTION:
{user_input}

INSTRUCTIONS: Answer the user's question using ONLY the information provided in the context above. Do not invent, assume, or add any details not present in the context."""
        
        return formatted_message
    
    def _get_system_instruction(self) -> str:
        """Get the system instruction for Apoorva's RAG chatbot."""
        try:
            from sys_prompt import SYSTEM_PROMPT
            return SYSTEM_PROMPT
        except ImportError as e:
            logger.error(f"Error importing system prompt: {e}")
            return "Error loading system prompt"
        except Exception as e:
            logger.error(f"Error loading system prompt: {e}")
            return "Error loading system prompt"
    
    def store_conversation(self, chat_session_id: str, user_input: str, ai_response: str):
        """Store conversation for future API calls."""
        if chat_session_id not in self._conversation_store:
            self._conversation_store[chat_session_id] = []
        
        # Store user message
        self._conversation_store[chat_session_id].append({
            'role': 'user',
            'content': user_input,
            'timestamp': self._get_timestamp()
        })
        
        # Store AI response
        self._conversation_store[chat_session_id].append({
            'role': 'assistant',
            'content': ai_response,
            'timestamp': self._get_timestamp()
        })
        
        logger.info(f"Conversation stored: {len(self._conversation_store[chat_session_id])} messages")
    
    def get_conversation_history(self, chat_session_id: str) -> List[Dict[str, Any]]:
        """Get conversation history as list of dictionaries."""
        if chat_session_id not in self._conversation_store:
            logger.info(f"No conversation history found for session {chat_session_id}")
            return []
        
        # Return the raw conversation store in the correct format
        history = []
        for conv in self._conversation_store[chat_session_id]:
            history.append({
                "role": conv['role'],
                "content": conv['content']
            })
        
        logger.info(f"Retrieved {len(history)} messages from conversation history for session {chat_session_id}")
        return history
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_api_stats(self) -> Dict[str, int]:
        """Get API call statistics."""
        return {
            "total_calls": self._api_call_count,
            "successful_calls": self._successful_calls,
            "failed_calls": self._failed_calls
        }

# Global instance
gemini_service = GeminiAPIService()
