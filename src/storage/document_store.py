# src/storage/document_store.py
import logging
from typing import List, Dict, Any, Optional
import json
from pathlib import Path
from datetime import datetime
from src.config import Config

logger = logging.getLogger(__name__)

class DocumentStore:
    """Handle document metadata and chat history storage"""
    
    def __init__(self):
        self.documents_file = Config.CHAT_HISTORY_DIR / "documents.json"
        self.chat_history_file = Config.CHAT_HISTORY_DIR / "chat_history.json"
    
    def save_document_metadata(self, document_info: Dict[str, Any]) -> bool:
        """Save document metadata"""
        try:
            # Load existing documents
            documents = self.load_documents()
            
            # Add timestamp
            document_info["added_at"] = datetime.now().isoformat()
            
            # Add or update document
            documents[document_info["name"]] = document_info
            
            # Save back to file
            with open(self.documents_file, 'w') as f:
                json.dump(documents, f, indent=2)
            
            logger.info(f"Saved metadata for document: {document_info['name']}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving document metadata: {str(e)}")
            return False
    
    def load_documents(self) -> Dict[str, Any]:
        """Load all document metadata"""
        try:
            if self.documents_file.exists():
                with open(self.documents_file, 'r') as f:
                    return json.load(f)
            return {}
            
        except Exception as e:
            logger.error(f"Error loading documents: {str(e)}")
            return {}
    
    def remove_document(self, document_name: str) -> bool:
        """Remove document metadata"""
        try:
            documents = self.load_documents()
            
            if document_name in documents:
                del documents[document_name]
                
                with open(self.documents_file, 'w') as f:
                    json.dump(documents, f, indent=2)
                
                logger.info(f"Removed metadata for document: {document_name}")
                return True
            else:
                logger.warning(f"Document not found: {document_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error removing document: {str(e)}")
            return False
    
    def save_chat_message(self, message: Dict[str, Any]) -> bool:
        """Save a chat message"""
        try:
            # Load existing chat history
            chat_history = self.load_chat_history()
            
            # Add timestamp
            message["timestamp"] = datetime.now().isoformat()
            
            # Add to history
            chat_history.append(message)
            
            # Keep only last 1000 messages to prevent file from growing too large
            if len(chat_history) > 1000:
                chat_history = chat_history[-1000:]
            
            # Save back to file
            with open(self.chat_history_file, 'w') as f:
                json.dump(chat_history, f, indent=2)
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving chat message: {str(e)}")
            return False
    
    def load_chat_history(self) -> List[Dict[str, Any]]:
        """Load chat history"""
        try:
            if self.chat_history_file.exists():
                with open(self.chat_history_file, 'r') as f:
                    return json.load(f)
            return []
            
        except Exception as e:
            logger.error(f"Error loading chat history: {str(e)}")
            return []
    
    def clear_chat_history(self) -> bool:
        """Clear all chat history"""
        try:
            with open(self.chat_history_file, 'w') as f:
                json.dump([], f)
            
            logger.info("Cleared chat history")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing chat history: {str(e)}")
            return False
    
    def get_recent_chat_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent chat messages"""
        try:
            history = self.load_chat_history()
            return history[-limit:] if history else []
            
        except Exception as e:
            logger.error(f"Error getting recent chat history: {str(e)}")
            return []