# src/models/embedding_handler.py
import logging
from typing import List, Optional
import chromadb
from src.config import Config

logger = logging.getLogger(__name__)

class EmbeddingHandler:
    """Handle embeddings for ChromaDB"""
    
    def __init__(self):
        # ChromaDB uses sentence-transformers by default
        self.model_name = Config.EMBEDDING_MODEL
    
    def embed_texts(self, texts: List[str]) -> Optional[List[List[float]]]:
        """Embed a list of texts (handled by ChromaDB automatically)"""
        # ChromaDB handles embeddings automatically, so we just return None
        # This method is here for potential future custom embedding logic
        return None
    
    def embed_query(self, query: str) -> Optional[List[float]]:
        """Embed a query (handled by ChromaDB automatically)"""
        # ChromaDB handles query embeddings automatically
        return None
    
    def get_model_info(self) -> dict:
        """Get information about the embedding model"""
        return {
            "model_name": self.model_name,
            "provider": "sentence-transformers (ChromaDB default)",
            "dimensions": 384,  # all-MiniLM-L6-v2 dimensions
            "description": "Default ChromaDB embedding model"
        }