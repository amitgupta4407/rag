
# src/models/llm_handler.py
import logging
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod
import requests
import json
from src.config import Config
from openai import OpenAI
import os


# OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')

logger = logging.getLogger(__name__)

class BaseLLMHandler(ABC):
    """Base class for LLM handlers"""
    
    @abstractmethod
    def generate_response(self, prompt: str, context: str = "", **kwargs) -> Optional[str]:
        """Generate response from the LLM"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the LLM is available"""
        pass




class OpenAIHandler(BaseLLMHandler):
    """Handle OPENROUTER/OpenAI API interactions"""
    
    def __init__(self):
        self.api_key = Config.OPENROUTER_API_KEY
        self.base_url = "https://openrouter.ai/api/v1",
    
    def generate_response(self, prompt: str, context: str = "", **kwargs) -> Optional[str]:
        """Generate response using OpenAI/openrouter API"""
        if not self.is_available():
            logger.error("Openrouter/OpenAI API key not configured")
            return None
        
        try:

            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.api_key,
                )
            completion = client.chat.completions.create(
            # model="moonshotai/kimi-dev-72b:free",
            model="google/gemini-2.0-flash-exp:free",
            messages=[
                        {
                        "role": "user",
                        "content": self._build_prompt(context, prompt)
                        }
                    ]
            )

            if completion.choices[0].message.content:
                return completion.choices[0].message.content
                
            else:
                logger.error("Empty response from OpenAi/Openrouter")
                return None
                
        except Exception as e:
            logger.error(f"Error with OpenAI/openrouter API: {str(e)}")
            return None
    
    def is_available(self) -> bool:
        """Check if OPENROUTER API is configured"""
        return bool(self.api_key)
    
    def _build_prompt(self, context: str, question: str) -> str:
        """Build the prompt for OpenAi"""
        if context:
            return f"""You are a helpful assistant that answers questions based on the provided context.

                    Context:
                    {context}

                    Question: {question}

                    Please provide a comprehensive answer based on the context above. If the context doesn't contain relevant information, please say so."""
        else:
            return question

class OllamaHandler(BaseLLMHandler):
    """Handle Ollama API interactions"""
    
    def __init__(self):
        self.base_url = Config.OLLAMA_BASE_URL
        self.model = Config.OLLAMA_MODEL
    
    def generate_response(self, prompt: str, context: str = "", **kwargs) -> Optional[str]:
        """Generate response using Ollama API"""
        if not self.is_available():
            logger.error("Ollama not available")
            return None
        
        try:
            # Build the full prompt
            full_prompt = self._build_prompt(context, prompt)
            
            # Make API request
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error with Ollama API: {str(e)}")
            return None
    
    def is_available(self) -> bool:
        """Check if Ollama is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_available_models(self) -> List[str]:
        """Get list of available models from Ollama"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [model["name"] for model in models]
            return []
        except:
            return []
    
    def _build_prompt(self, context: str, question: str) -> str:
        """Build the prompt for Ollama"""
        if context:
            return f"""You are a helpful assistant that answers questions based on the provided context.
Context:
{context}

Question: {question}

Please provide a comprehensive answer based on the context above. If the context doesn't contain relevant information, please say so."""
        else:
            return question

class LLMManager:
    """Manage multiple LLM handlers"""
    
    def __init__(self):
        self.handlers = {
            "openAi": OpenAIHandler(),
            "ollama": OllamaHandler()
        }
        self.default_handler = None
        self._initialize_default()
    
    def _initialize_default(self):
        """Initialize default handler based on availability"""
        for name, handler in self.handlers.items():
            if handler.is_available():
                self.default_handler = name
                logger.info(f"Default LLM set to: {name}")
                break
        
        if not self.default_handler:
            logger.warning("No LLM handlers available")
    
    def generate_response(self, prompt: str, context: str = "", handler_name: str = None, **kwargs) -> Optional[str]:
        """Generate response using specified or default handler"""
        handler_name = handler_name or self.default_handler
        
        if not handler_name:
            logger.error("No LLM handler available")
            return None
        
        if handler_name not in self.handlers:
            logger.error(f"Unknown handler: {handler_name}")
            return None
        
        handler = self.handlers[handler_name]
        
        if not handler.is_available():
            logger.error(f"Handler {handler_name} not available")
            return None
        
        return handler.generate_response(prompt, context, **kwargs)
    
    def get_available_handlers(self) -> List[str]:
        """Get list of available handlers"""
        return [name for name, handler in self.handlers.items() if handler.is_available()]
    
    def is_any_available(self) -> bool:
        """Check if any handler is available"""
        return len(self.get_available_handlers()) > 0
    
    def set_default_handler(self, handler_name: str) -> bool:
        """Set default handler"""
        if handler_name in self.handlers and self.handlers[handler_name].is_available():
            self.default_handler = handler_name
            logger.info(f"Default handler set to: {handler_name}")
            return True
        return False
