# ui/components/settings.py
import streamlit as st
import logging
import os
from src.config import Config

logger = logging.getLogger(__name__)

class SettingsComponent:
    """Handle application settings and configuration"""
    
    def __init__(self, rag_generator):
        self.rag_generator = rag_generator
    
    def render(self):
        """Render the settings interface"""
        st.header("⚙️ Settings")
        
        # LLM Configuration
        self._render_llm_settings()
        
        st.divider()
        
        # Processing Settings
        self._render_processing_settings()
        
        st.divider()
        
        # Storage Settings
        self._render_storage_settings()
        
        st.divider()
        
        # Advanced Settings
        self._render_advanced_settings()
    
    def _render_llm_settings(self):
        """Render LLM configuration settings"""
        st.subheader("🤖 Language Model Configuration")
        
        # Gemini Settings
        with st.expander("🔹 Gemini Configuration"):
            st.write("**Current Status:**")
            if Config.GEMINI_API_KEY:
                st.success("✅ API Key configured")
            else:
                st.warning("⚠️ No API Key configured")
            
            gemini_key = st.text_input(
                "Gemini API Key",
                value=Config.GEMINI_API_KEY[:20] + "..." if Config.GEMINI_API_KEY else "",
                type="password",
                help="Get your API key from Google AI Studio"
            )
            
            if st.button("Test Gemini Connection"):
                if gemini_key and gemini_key != Config.GEMINI_API_KEY[:20] + "...":
                    # Update config temporarily
                    original_key = Config.GEMINI_API_KEY
                    Config.GEMINI_API_KEY = gemini_key
                    
                    # Test connection
                    from src.models.llm_handler import GeminiHandler
                    handler = GeminiHandler()
                    if handler.is_available():
                        st.success("✅ Gemini connection successful!")
                    else:
                        st.error("❌ Failed to connect to Gemini")
                        Config.GEMINI_API_KEY = original_key
                else:
                    st.info("Please enter a new API key to test")
        
        # Ollama Settings
        with st.expander("🔹 Ollama Configuration"):
            st.write("**Current Status:**")
            ollama_handler = self.rag_generator.llm_manager.handlers["ollama"]
            if ollama_handler.is_available():
                st.success("✅ Ollama is running")
                
                # Show available models
                models = ollama_handler.get_available_models()
                if models:
                    st.write("**Available Models:**")
                    for model in models:
                        if model == Config.OLLAMA_MODEL:
                            st.write(f"• {model} ⭐ (current)")
                        else:
                            st.write(f"• {model}")
                
                # Model selection
                if models:
                    selected_model = st.selectbox(
                        "Select Model",
                        models,
                        index=models.index(Config.OLLAMA_MODEL) if Config.OLLAMA_MODEL in models else 0
                    )
                    
                    if st.button("Set as Default Model"):
                        Config.OLLAMA_MODEL = selected_model
                        st.success(f"Default model set to: {selected_model}")
            else:
                st.error("❌ Ollama not available")
                st.info("Make sure Ollama is installed and running on your system")
            
            st.code(f"Base URL: {Config.OLLAMA_BASE_URL}")
            st.code(f"Current Model: {Config.OLLAMA_MODEL}")
        
        # Default LLM Selection
        available_llms = self.rag_generator.get_available_llms()
        if available_llms:
            st.subheader("Default Language Model")
            current_default = getattr(self.rag_generator.llm_manager, 'default_handler', None)
            
            selected_default = st.selectbox(
                "Choose default LLM",
                available_llms,
                index=available_llms.index(current_default) if current_default in available_llms else 0,
                format_func=lambda x: x.title()
            )
            
            if st.button("Set Default LLM"):
                if self.rag_generator.set_default_llm(selected_default):
                    st.success(f"Default LLM set to: {selected_default.title()}")
                else:
                    st.error("Failed to set default LLM")
    
    def _render_processing_settings(self):
        """Render text processing settings"""
        st.subheader("📝 Text Processing Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            chunk_size = st.number_input(
                "Chunk Size",
                min_value=100,
                max_value=2000,
                value=Config.CHUNK_SIZE,
                step=50,
                help="Number of characters per chunk"
            )
        
        with col2:
            chunk_overlap = st.number_input(
                "Chunk Overlap",
                min_value=0,
                max_value=500,
                value=Config.CHUNK_OVERLAP,
                step=10,
                help="Character overlap between chunks"
            )
        
        max_file_size = st.number_input(
            "Max File Size (MB)",
            min_value=1,
            max_value=500,
            value=Config.MAX_FILE_SIZE_MB,
            help="Maximum allowed PDF file size"
        )
        
        if st.button("Apply Processing Settings"):
            Config.CHUNK_SIZE = chunk_size
            Config.CHUNK_OVERLAP = chunk_overlap
            Config.MAX_FILE_SIZE_MB = max_file_size
            st.success("Processing settings updated!")
    
    def _render_storage_settings(self):
        """Render storage configuration settings"""
        st.subheader("🗄️ Storage Settings")
        
        # Storage type
        storage_type = st.radio(
            "Storage Type",
            options=["local", "memory"],
            index=0 if Config.STORAGE_TYPE == "local" else 1,
            help="Local: Persistent storage, Memory: Temporary (lost on restart)"
        )
        
        if storage_type != Config.STORAGE_TYPE:
            st.warning("⚠️ Changing storage type requires restart")
        
        # Storage paths
        st.write("**Storage Paths:**")
        st.code(f"Upload Directory: {Config.UPLOAD_DIR}")
        st.code(f"Vector Database: {Config.VECTOR_DB_PATH}")
        st.code(f"Chat History: {Config.CHAT_HISTORY_DIR}")
        
        # Embedding model info
        st.write("**Embedding Model:**")
        st.info(f"Using: {Config.EMBEDDING_MODEL} (ChromaDB default)")
    
    def _render_advanced_settings(self):
        """Render advanced configuration options"""
        st.subheader("🔧 Advanced Settings")
        
        # Environment variables
        with st.expander("Environment Variables"):
            st.write("**Current Environment:**")
            env_vars = [
                "GEMINI_API_KEY",
                "OLLAMA_BASE_URL", 
                "OLLAMA_MODEL",
                "STORAGE_TYPE",
                "CHUNK_SIZE",
                "CHUNK_OVERLAP"
            ]
            
            for var in env_vars:
                value = os.getenv(var, "Not set")
                if "KEY" in var and value != "Not set":
                    value = value[:10] + "..." if len(value) > 10 else value
                st.code(f"{var}: {value}")
        
        # Configuration validation
        with st.expander("Configuration Validation"):
            if st.button("Validate Configuration"):
                if Config.validate_config():
                    st.success("✅ Configuration is valid")
                else:
                    st.error("❌ Configuration has issues")
        
        # Reset to defaults
        with st.expander("Reset Settings", expanded=False):
            st.warning("⚠️ This will reset all settings to default values")
            if st.button("Reset to Defaults", type="secondary"):
                if st.checkbox("I understand this will reset all settings"):
                    self._reset_to_defaults()
    
    def _reset_to_defaults(self):
        """Reset configuration to default values"""
        Config.CHUNK_SIZE = 500
        Config.CHUNK_OVERLAP = 50
        Config.MAX_FILE_SIZE_MB = 50
        Config.STORAGE_TYPE = "local"
        st.success("Settings reset to defaults!")
        st.info("Some changes may require application restart")