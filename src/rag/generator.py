# src/rag/generator.py
import logging
from typing import Dict, Any, Optional, List
from src.models.llm_handler import LLMManager
from src.rag.retriever import Retriever
from src.storage.document_store import DocumentStore

logger = logging.getLogger(__name__)

class RAGGenerator:
    """Handle RAG generation pipeline"""
    
    def __init__(self):
        self.llm_manager = LLMManager()
        self.retriever = Retriever()
        self.document_store = DocumentStore()
    
    def generate_response(self, query: str, llm_name: str = None, k: int = 5) -> Dict[str, Any]:
        """Generate response using RAG pipeline"""
        try:
            # Check if LLM is available
            if not self.llm_manager.is_any_available():
                return {
                    "answer": "No language model is currently available. Please configure OpenAi API key or ensure Ollama is running.",
                    "sources": [],
                    "chunks": [],
                    "error": "No LLM available"
                }
            
            # Retrieve relevant documents
            retrieval_result = self.retriever.retrieve_with_sources(query, k)
            
            if not retrieval_result["chunks"]:
                # No relevant documents found
                fallback_response = self.llm_manager.generate_response(
                    prompt=query,
                    context="",
                    handler_name=llm_name
                )
                
                return {
                    "answer": fallback_response or "I don't have any relevant documents to answer your question.",
                    "sources": [],
                    "chunks": [],
                    "note": "No relevant documents found in the knowledge base."
                }
            
            # Generate response with context
            context = retrieval_result["context"]
            answer = self.llm_manager.generate_response(
                prompt=query,
                context=context,
                handler_name=llm_name
            )
            
            if not answer:
                return {
                    "answer": "Sorry, I couldn't generate a response. There might be an issue with the language model.",
                    "sources": retrieval_result["sources"],
                    "chunks": retrieval_result["chunks"],
                    "error": "LLM generation failed"
                }
            
            # Save to chat history
            self._save_chat_interaction(query, answer, retrieval_result)
            
            return {
                "answer": answer,
                "sources": retrieval_result["sources"],
                "chunks": retrieval_result["chunks"]
            }
            
        except Exception as e:
            logger.error(f"Error in RAG generation: {str(e)}")
            return {
                "answer": f"An error occurred while processing your question: {str(e)}",
                "sources": [],
                "chunks": [],
                "error": str(e)
            }
    
    def _save_chat_interaction(self, query: str, answer: str, retrieval_result: Dict[str, Any]):
        """Save chat interaction to history"""
        try:
            message = {
                "type": "interaction",
                "query": query,
                "answer": answer,
                "sources": retrieval_result["sources"],
                "num_chunks": len(retrieval_result["chunks"])
            }
            
            self.document_store.save_chat_message(message)
            
        except Exception as e:
            logger.error(f"Error saving chat interaction: {str(e)}")
    
    def get_available_llms(self) -> List[str]:
        """Get list of available LLMs"""
        return self.llm_manager.get_available_handlers()
    
    def set_default_llm(self, llm_name: str) -> bool:
        """Set default LLM"""
        return self.llm_manager.set_default_handler(llm_name)
