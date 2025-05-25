# ui/components/chat_interface.py
import streamlit as st
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ChatInterface:
    """Handle chat interface for RAG conversations"""
    
    def __init__(self, rag_generator):
        self.rag_generator = rag_generator
    
    def render(self):
        """Render the chat interface"""
        # Chat settings in sidebar
        with st.sidebar:
            st.subheader("💬 Chat Settings")
            
            # LLM selection
            available_llms = self.rag_generator.get_available_llms()
            if available_llms:
                selected_llm = st.selectbox(
                    "Choose Language Model",
                    available_llms,
                    index=0 if available_llms else None,
                    format_func=lambda x: x.title()
                )
                st.session_state.current_llm = selected_llm
            else:
                st.error("No LLMs available")
                return
            
            # Retrieval settings
            st.subheader("🔍 Retrieval Settings")
            k_chunks = st.slider(
                "Number of chunks to retrieve",
                min_value=1,
                max_value=20,
                value=5,
                help="More chunks = more context but slower response"
            )
            
            # Clear chat button
            if st.button("🗑️ Clear Chat History"):
                st.session_state.chat_history = []
                st.rerun()
        
        # Display chat history
        self._display_chat_history()
        
        # Chat input
        self._handle_chat_input(k_chunks)
    
    def _display_chat_history(self):
        """Display the chat conversation"""
        if not st.session_state.chat_history:
            st.info("👋 Ask me anything about your documents!")
            return
        
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.write(message["content"])
            
            elif message["role"] == "assistant":
                with st.chat_message("assistant"):
                    st.write(message["content"])
                    
                    # Show sources if available
                    if message.get("sources"):
                        with st.expander("📚 Sources"):
                            for source in message["sources"]:
                                st.write(f"• {source}")
                    
                    # Show chunks info if available
                    if message.get("chunks_info"):
                        chunks_info = message["chunks_info"]
                        st.caption(f"📊 Retrieved {len(chunks_info)} chunks")
    
    def _handle_chat_input(self, k_chunks: int):
        """Handle user input and generate responses"""
        # Chat input
        if prompt := st.chat_input("Ask a question about your documents..."):
            # Add user message to history
            st.session_state.chat_history.append({
                "role": "user",
                "content": prompt
            })
            
            # Display user message immediately
            with st.chat_message("user"):
                st.write(prompt)
            
            # Generate response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = self.rag_generator.generate_response(
                        query=prompt,
                        llm_name=st.session_state.current_llm,
                        k=k_chunks
                    )
                
                # Display response
                if response.get("error"):
                    st.error(f"❌ {response['answer']}")
                else:
                    st.write(response["answer"])
                    
                    # Show sources
                    if response.get("sources"):
                        with st.expander("📚 Sources"):
                            for source in response["sources"]:
                                st.write(f"• {source}")
                    
                    # Show additional info
                    if response.get("chunks"):
                        chunks_count = len(response["chunks"])
                        st.caption(f"📊 Retrieved {chunks_count} relevant chunks")
                        
                        # Optional: Show chunk details
                        if chunks_count > 0:
                            with st.expander("🔍 Retrieved Chunks (Debug)"):
                                for i, chunk in enumerate(response["chunks"]):
                                    st.write(f"**Chunk {i+1}** (from {chunk.get('source', 'Unknown')}):")
                                    st.write(chunk["text"][:200] + "..." if len(chunk["text"]) > 200 else chunk["text"])
                                    if chunk.get("distance") is not None:
                                        st.caption(f"Similarity: {1 - chunk['distance']:.3f}")
                                    st.divider()
                
                # Add assistant response to history
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response["answer"],
                    "sources": response.get("sources", []),
                    "chunks_info": response.get("chunks", [])
                })