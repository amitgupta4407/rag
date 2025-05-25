# src/config.py
import os
from pathlib import Path
from typing import Literal
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Central configuration management"""
    
    # Project paths
    PROJECT_ROOT = Path(__file__).parent.parent
    DATA_DIR = PROJECT_ROOT / "data"
    UPLOAD_DIR = DATA_DIR / "uploads"
    VECTOR_DB_PATH = DATA_DIR / "vector_db"
    CHAT_HISTORY_DIR = DATA_DIR / "chat_history"
    
    # LLM Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")
    
    # Storage Configuration
    STORAGE_TYPE: Literal["memory", "local"] = os.getenv("STORAGE_TYPE", "local")
    
    # Processing Configuration
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    
    # UI Configuration
    PAGE_TITLE = os.getenv("PAGE_TITLE", "RAG PDF Pipeline")
    PAGE_ICON = os.getenv("PAGE_ICON", "📚")
    
    # Embedding Configuration
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Default ChromaDB embedding
    
    @classmethod
    def create_directories(cls):
        """Create necessary directories if they don't exist"""
        directories = [
            cls.DATA_DIR,
            cls.UPLOAD_DIR,
            cls.VECTOR_DB_PATH,
            cls.CHAT_HISTORY_DIR
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            
        # Create .gitkeep files
        for directory in [cls.UPLOAD_DIR, cls.VECTOR_DB_PATH, cls.CHAT_HISTORY_DIR]:
            gitkeep = directory / ".gitkeep"
            if not gitkeep.exists():
                gitkeep.touch()
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate configuration settings"""
        errors = []
        
        # Check if at least one LLM is configured
        if not cls.GEMINI_API_KEY and not cls._is_ollama_available():
            errors.append("No LLM configured. Please set GEMINI_API_KEY or ensure Ollama is running.")
        
        # Check storage type
        if cls.STORAGE_TYPE not in ["memory", "local"]:
            errors.append(f"Invalid STORAGE_TYPE: {cls.STORAGE_TYPE}. Must be 'memory' or 'local'.")
        
        # Check numeric values
        if cls.CHUNK_SIZE <= 0:
            errors.append("CHUNK_SIZE must be positive.")
        
        if cls.CHUNK_OVERLAP < 0:
            errors.append("CHUNK_OVERLAP must be non-negative.")
        
        if cls.MAX_FILE_SIZE_MB <= 0:
            errors.append("MAX_FILE_SIZE_MB must be positive.")
            
        if errors:
            print("Configuration errors:")
            for error in errors:
                print(f"  - {error}")
            return False
            
        return True
    
    @classmethod
    def _is_ollama_available(cls) -> bool:
        """Check if Ollama is available"""
        try:
            import requests
            response = requests.get(f"{cls.OLLAMA_BASE_URL}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    @classmethod
    def get_available_llms(cls) -> list:
        """Get list of available LLMs"""
        available = []
        
        if cls.GEMINI_API_KEY:
            available.append("gemini")
            
        if cls._is_ollama_available():
            available.append("ollama")
            
        return available

# Initialize configuration on import
Config.create_directories()