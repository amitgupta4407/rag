# src/processing/text_chunker.py
import logging
from typing import List, Dict, Any
from src.config import Config

logger = logging.getLogger(__name__)

class TextChunker:
    """Handle text chunking for vector storage"""
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or Config.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or Config.CHUNK_OVERLAP
    
    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Split text into chunks with metadata"""
        if not text or not text.strip():
            logger.warning("Empty text provided for chunking")
            return []
        
        if metadata is None:
            metadata = {}
        
        chunks = []
        text = text.strip()
        
        # Split text into chunks
        for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
            chunk_text = text[i:i + self.chunk_size]
            
            if chunk_text.strip():  # Only add non-empty chunks
                chunk_metadata = metadata.copy()
                chunk_metadata.update({
                    "chunk_index": len(chunks),
                    "chunk_size": len(chunk_text),
                    "start_char": i,
                    "end_char": i + len(chunk_text)
                })
                
                chunks.append({
                    "text": chunk_text.strip(),
                    "metadata": chunk_metadata
                })
        
        logger.info(f"Created {len(chunks)} chunks from text of length {len(text)}")
        return chunks
    
    def chunk_document(self, text: str, document_name: str, file_path: str = None) -> List[Dict[str, Any]]:
        """Chunk a document with proper metadata"""
        base_metadata = {
            "document_name": document_name,
            "file_path": file_path or document_name,
            "document_length": len(text)
        }
        
        return self.chunk_text(text, base_metadata)