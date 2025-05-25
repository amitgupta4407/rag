# ui/streamlit_app.py
import streamlit as st
import logging
from pathlib import Path
import sys

# Add src to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config import Config
from src.utils.logger import setup_logging
from src.processing.pdf_processor import PDFProcessor
from src.processing.text_chunker import TextChunker
from src.storage.vector_store import VectorStore
from src.storage.document_store import DocumentStore
from src.rag.generator import RAGGenerator
from ui.components.file_upload import FileUploadComponent
from ui.components.chat_interface import ChatInterface
from ui.components.settings import SettingsComponent

# Setup logging
logger = setup_logging()

class RAGPipelineApp:
    """Main Streamlit application for RAG Pipeline"""
    
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.text_chunker = TextChunker()
        self.vector_store = VectorStore()
        self.document_store = DocumentStore()
        self.rag_generator = RAGGenerator()
        
        # Initialize session state
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize Streamlit session state variables"""
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        if 'documents' not in st.session_state:
            st.session_state.documents = self.document_store.load_documents()
        
        if 'current_llm' not in st.session_state:
            available_llms = self.rag_generator.get_available_llms()
            st.session_state.current_llm = available_llms[0] if available_llms else None
    
    def run(self):
        """Run the Streamlit application"""
        st.set_page_config(
            page_title=Config.PAGE_TITLE,
            page_icon=Config.PAGE_ICON,
            layout="wide"
        )
        
        st.title("📚 RAG PDF Pipeline")
        st.markdown("Upload PDF documents and chat with them using AI")
        
        # Check if any LLM is available
        if not self.rag_generator.llm_manager.is_any_available():
            st.error("❌ No language model is available. Please configure Gemini API key or ensure Ollama is running.")
            st.info("💡 Check the Settings tab to configure your LLM.")
        
        # Create tabs
        tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat", "📄 Documents", "⚙️ Settings", "📊 Status"])
        
        with tab1:
            self._render_chat_tab()
        
        with tab2:
            self._render_documents_tab()
        
        with tab3:
            self._render_settings_tab()
        
        with tab4:
            self._render_status_tab()
    
    def _render_chat_tab(self):
        """Render the chat interface tab"""
        st.header("Chat with your documents")
        
        # Check if documents are available
        collection_info = self.vector_store.get_collection_info()
        
        if collection_info.get('total_chunks', 0) == 0:
            st.info("📝 Upload and process some PDF documents first to start chatting!")
            return
        
        # Chat interface
        chat_interface = ChatInterface(self.rag_generator)
        chat_interface.render()
    
    def _render_documents_tab(self):
        """Render the documents management tab"""
        st.header("Document Management")
        
        # File upload component
        file_upload = FileUploadComponent(
            self.pdf_processor,
            self.text_chunker,
            self.vector_store,
            self.document_store
        )
        file_upload.render()
        
        # Display current documents
        st.subheader("📚 Current Documents")
        
        documents = self.document_store.load_documents()
        
        if not documents:
            st.info("No documents uploaded yet.")
        else:
            for doc_name, doc_info in documents.items():
                with st.expander(f"📄 {doc_name}"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**Size:** {doc_info.get('size_mb', 'Unknown')} MB")
                        st.write(f"**Pages:** {doc_info.get('num_pages', 'Unknown')}")
                        st.write(f"**Added:** {doc_info.get('added_at', 'Unknown')}")
                        st.write(f"**Chunks:** {doc_info.get('num_chunks', 'Unknown')}")
                    
                    with col2:
                        if st.button(f"🗑️ Delete", key=f"delete_{doc_name}"):
                            if self._delete_document(doc_name):
                                st.success(f"Deleted {doc_name}")
                                st.rerun()
    
    def _render_settings_tab(self):
        """Render the settings tab"""
        settings = SettingsComponent(self.rag_generator)
        settings.render()
    
    def _render_status_tab(self):
        """Render system status tab"""
        st.header("System Status")
        
        # LLM Status
        st.subheader("🤖 Language Models")
        available_llms = self.rag_generator.get_available_llms()
        
        if available_llms:
            for llm in available_llms:
                st.success(f"✅ {llm.title()} - Available")
        else:
            st.error("❌ No language models available")
        
        # Vector Store Status
        st.subheader("🗄️ Vector Store")
        collection_info = self.vector_store.get_collection_info()
        
        if "error" in collection_info:
            st.error(f"❌ Error: {collection_info['error']}")
        else:
            st.info(f"📊 Storage Type: {collection_info['storage_type']}")
            st.info(f"📦 Total Chunks: {collection_info['total_chunks']}")
            st.info(f"📚 Documents: {collection_info['unique_documents']}")
            
            if collection_info['document_names']:
                st.write("**Documents in vector store:**")
                for doc in collection_info['document_names']:
                    st.write(f"- {doc}")
        
        # Storage Paths
        st.subheader("📁 Storage Paths")
        st.code(f"Upload Directory: {Config.UPLOAD_DIR}")
        st.code(f"Vector DB Path: {Config.VECTOR_DB_PATH}")
        st.code(f"Chat History: {Config.CHAT_HISTORY_DIR}")
        
        # Configuration
        st.subheader("⚙️ Configuration")
        st.json({
            "chunk_size": Config.CHUNK_SIZE,
            "chunk_overlap": Config.CHUNK_OVERLAP,
            "max_file_size_mb": Config.MAX_FILE_SIZE_MB,
            "storage_type": Config.STORAGE_TYPE,
            "embedding_model": Config.EMBEDDING_MODEL
        })
        
        # Clear data options
        st.subheader("🧹 Clear Data")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear Vector Store", type="secondary"):
                if st.checkbox("I understand this will delete all documents"):
                    if self.vector_store.clear_collection():
                        # Also clear document metadata
                        self.document_store.documents_file.write_text("{}")
                        st.success("Vector store cleared!")
                        st.rerun()
        
        with col2:
            if st.button("💬 Clear Chat History", type="secondary"):
                if self.document_store.clear_chat_history():
                    st.session_state.chat_history = []
                    st.success("Chat history cleared!")
                    st.rerun()
    
    def _delete_document(self, document_name: str) -> bool:
        """Delete a document from both vector store and metadata"""
        try:
            # Delete from vector store
            self.vector_store.delete_by_document(document_name)
            
            # Delete metadata
            self.document_store.remove_document(document_name)
            
            # Update session state
            st.session_state.documents = self.document_store.load_documents()
            
            return True
        except Exception as e:
            st.error(f"Error deleting document: {str(e)}")
            return False

def main():
    """Main entry point"""
    try:
        # Validate configuration
        if not Config.validate_config():
            st.error("❌ Configuration validation failed. Please check your settings.")
            return
        
        # Run the app
        app = RAGPipelineApp()
        app.run()
        
    except Exception as e:
        st.error(f"❌ Application error: {str(e)}")
        logger.error(f"Application error: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()