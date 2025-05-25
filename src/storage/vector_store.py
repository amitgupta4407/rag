# src/storage/vector_store.py
import logging
from typing import List, Dict, Any, Optional, Tuple
import chromadb
from chromadb.config import Settings
from src.config import Config
import uuid
import json

logger = logging.getLogger(__name__)

class VectorStore:
    """Handle ChromaDB vector storage operations"""
    
    def __init__(self, storage_type: str = None):
        self.storage_type = storage_type or Config.STORAGE_TYPE
        self.collection_name = "pdf_documents"
        self.client = None
        self.collection = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize ChromaDB client based on storage type"""
        try:
            if self.storage_type == "memory":
                self.client = chromadb.Client()
                logger.info("Initialized in-memory ChromaDB client")
            else:  # local storage
                self.client = chromadb.PersistentClient(
                    path=str(Config.VECTOR_DB_PATH)
                )
                logger.info(f"Initialized persistent ChromaDB client at: {Config.VECTOR_DB_PATH}")
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "PDF document chunks for RAG"}
            )
            
            logger.info(f"Initialized collection: {self.collection_name}")
            
        except Exception as e:
            logger.error(f"Error initializing ChromaDB client: {str(e)}")
            raise
    
    def add_documents(self, chunks: List[Dict[str, Any]]) -> bool:
        """Add document chunks to the vector store"""
        if not chunks:
            logger.warning("No chunks provided to add")
            return False
        
        try:
            # Prepare data for ChromaDB
            documents = []
            metadatas = []
            ids = []
            
            for chunk in chunks:
                # Generate unique ID for each chunk
                chunk_id = str(uuid.uuid4())
                ids.append(chunk_id)
                
                # Extract text content
                documents.append(chunk["text"])
                
                # Prepare metadata (ChromaDB requires flat dict)
                metadata = chunk.get("metadata", {})
                # Convert nested metadata to flat structure
                flat_metadata = self._flatten_metadata(metadata)
                metadatas.append(flat_metadata)
            
            # Add to collection
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(chunks)} chunks to vector store")
            return True
            
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {str(e)}")
            return False
    
    def search(self, query: str, n_results: int = 5, filter_metadata: Dict = None) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        try:
            # Perform similarity search
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=filter_metadata
            )
            
            # Format results
            formatted_results = []
            
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    result = {
                        "id": results['ids'][0][i],
                        "text": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "distance": results['distances'][0][i] if results.get('distances') else None
                    }
                    formatted_results.append(result)
            
            logger.info(f"Found {len(formatted_results)} results for query")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching vector store: {str(e)}")
            return []
    
    def delete_by_document(self, document_name: str) -> bool:
        """Delete all chunks from a specific document"""
        try:
            # Query to find all chunks from the document
            results = self.collection.query(
                query_texts=[""],  # Empty query to get all
                n_results=10000,  # Large number to get all results
                where={"document_name": document_name}
            )
            
            if results['ids'] and results['ids'][0]:
                ids_to_delete = results['ids'][0]
                self.collection.delete(ids=ids_to_delete)
                logger.info(f"Deleted {len(ids_to_delete)} chunks from document: {document_name}")
                return True
            else:
                logger.info(f"No chunks found for document: {document_name}")
                return True
                
        except Exception as e:
            logger.error(f"Error deleting document chunks: {str(e)}")
            return False
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection"""
        try:
            count = self.collection.count()
            
            # Get sample documents to understand structure
            sample_results = self.collection.query(
                query_texts=[""],
                n_results=min(5, count)
            ) if count > 0 else None
            
            documents = set()
            if sample_results and sample_results['metadatas']:
                for metadata in sample_results['metadatas'][0]:
                    if 'document_name' in metadata:
                        documents.add(metadata['document_name'])
            
            return {
                "total_chunks": count,
                "storage_type": self.storage_type,
                "collection_name": self.collection_name,
                "unique_documents": len(documents),
                "document_names": list(documents)
            }
            
        except Exception as e:
            logger.error(f"Error getting collection info: {str(e)}")
            return {"error": str(e)}
    
    def clear_collection(self) -> bool:
        """Clear all documents from the collection"""
        try:
            # Delete the collection and recreate it
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "PDF document chunks for RAG"}
            )
            logger.info("Cleared all documents from collection")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing collection: {str(e)}")
            return False
    
    def _flatten_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Flatten nested metadata for ChromaDB"""
        flattened = {}
        
        for key, value in metadata.items():
            if isinstance(value, (str, int, float, bool)):
                flattened[key] = value
            elif isinstance(value, (list, dict)):
                # Convert complex types to JSON strings
                flattened[key] = json.dumps(value)
            else:
                flattened[key] = str(value)
        
        return flattened
