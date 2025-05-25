import streamlit as st
import logging
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class FileUploadComponent:
    """Handle PDF file upload and processing"""
    
    def __init__(self, pdf_processor, text_chunker, vector_store, document_store):
        self.pdf_processor = pdf_processor
        self.text_chunker = text_chunker
        self.vector_store = vector_store
        self.document_store = document_store
    
    def render(self):
        """Render the file upload interface"""
        st.subheader("📤 Upload PDF Documents")
        
        # File uploader
        uploaded_files = st.file_uploader(
            "Choose PDF files",
            type=['pdf'],
            accept_multiple_files=True,
            help="Upload one or more PDF files to add to your knowledge base"
        )
        
        if uploaded_files:
            # Process button
            if st.button("🔄 Process Documents", type="primary"):
                self._process_uploaded_files(uploaded_files)
    
    def _process_uploaded_files(self, uploaded_files):
        """Process uploaded PDF files"""
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total_files = len(uploaded_files)
        processed_count = 0
        
        for i, uploaded_file in enumerate(uploaded_files):
            try:
                status_text.text(f"Processing {uploaded_file.name}...")
                progress_bar.progress((i) / total_files)
                
                # Check if document already exists
                existing_docs = self.document_store.load_documents()
                if uploaded_file.name in existing_docs:
                    st.warning(f"⚠️ {uploaded_file.name} already exists. Skipping.")
                    continue
                
                # Extract text from PDF
                text = self.pdf_processor.extract_text_from_uploaded_file(uploaded_file)
                
                if not text:
                    st.error(f"❌ Failed to extract text from {uploaded_file.name}")
                    continue
                
                # Save file to uploads directory
                saved_path = self.pdf_processor.save_uploaded_file(uploaded_file)
                
                if not saved_path:
                    st.error(f"❌ Failed to save {uploaded_file.name}")
                    continue
                
                # Chunk the text
                chunks = self.text_chunker.chunk_document(
                    text=text,
                    document_name=uploaded_file.name,
                    file_path=str(saved_path)
                )
                
                if not chunks:
                    st.error(f"❌ Failed to chunk {uploaded_file.name}")
                    continue
                
                # Add to vector store
                if self.vector_store.add_documents(chunks):
                    # Save document metadata
                    file_info = self.pdf_processor.get_file_info(saved_path)
                    doc_metadata = {
                        "name": uploaded_file.name,
                        "file_path": str(saved_path),
                        "size_mb": round(uploaded_file.size / (1024 * 1024), 2),
                        "num_pages": file_info.get("num_pages", 0),
                        "num_chunks": len(chunks),
                        "chunk_size": self.text_chunker.chunk_size,
                        "chunk_overlap": self.text_chunker.chunk_overlap
                    }
                    
                    if self.document_store.save_document_metadata(doc_metadata):
                        processed_count += 1
                        st.success(f"✅ Processed {uploaded_file.name} ({len(chunks)} chunks)")
                    else:
                        st.error(f"❌ Failed to save metadata for {uploaded_file.name}")
                else:
                    st.error(f"❌ Failed to add {uploaded_file.name} to vector store")
                
            except Exception as e:
                st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
                logger.error(f"Error processing {uploaded_file.name}: {str(e)}")
        
        # Final status
        progress_bar.progress(1.0)
        status_text.text(f"Completed! Processed {processed_count}/{total_files} files.")
        
        if processed_count > 0:
            # Update session state
            st.session_state.documents = self.document_store.load_documents()
            st.balloons()
        
        # Auto-refresh after 2 seconds
        if processed_count > 0:
            st.rerun()