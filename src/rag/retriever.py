# src/rag/retriever.py
import logging
from typing import List, Dict, Any, Optional
from src.storage.vector_store import VectorStore
from src.config import Config

logger = logging.getLogger(__name__)

class Retriever:
    """Handle document retrieval for RAG"""
    
    def __init__(self, vector_store: VectorStore = None):
        self.vector_store = vector_store or VectorStore()
        self.default_k = 5  # Number of chunks to retrieve
    
    def retrieve(self, query: str, k: int = None, filter_metadata: Dict = None) -> List[Dict[str, Any]]:
        """Retrieve relevant documents for a query"""
        k = k or self.default_k
        
        try:
            results = self.vector_store.search(
                query=query,
                n_results=k,
                filter_metadata=filter_metadata
            )
            
            logger.info(f"Retrieved {len(results)} chunks for query")
            return results
            
        except Exception as e:
            logger.error(f"Error during retrieval: {str(e)}")
            return []
    
    def retrieve_with_sources(self, query: str, k: int = None) -> Dict[str, Any]:
        """Retrieve documents with source information"""
        results = self.retrieve(query, k)
        
        if not results:
            return {
                "chunks": [],
                "sources": [],
                "context": ""
            }
        
        # Extract unique sources
        sources = set()
        chunks = []
        
        for result in results:
            metadata = result.get("metadata", {})
            document_name = metadata.get("document_name", "Unknown")
            sources.add(document_name)
            
            chunks.append({
                "text": result["text"],
                "source": document_name,
                "chunk_index": metadata.get("chunk_index", 0),
                "distance": result.get("distance")
            })
        
        # Create context from chunks
        context = "\n\n".join([chunk["text"] for chunk in chunks])
        
        return {
            "chunks": chunks,
            "sources": list(sources),
            "context": context
        }