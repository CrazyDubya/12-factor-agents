"""
Ollama integration utilities for TinyTroupe
Replaces OpenAI API calls with Ollama local API calls
"""

import os
import requests
import json
import time
import pickle
import logging
import configparser
from typing import Union, Dict, List, Any, Optional
import tiktoken

from tinytroupe import utils
from tinytroupe.control import transactional
from tinytroupe import default
from tinytroupe import config_manager

logger = logging.getLogger("tinytroupe")

# Configuration
config = utils.read_config_file()

###########################################################################
# Ollama Client class
###########################################################################

class OllamaClient:
    """
    A utility class for interacting with the Ollama API.
    Provides OpenAI-compatible interface for TinyTroupe.
    """

    def __init__(self, cache_api_calls=default["cache_api_calls"], cache_file_name=default["cache_file_name"]) -> None:
        logger.debug("Initializing OllamaClient")
        
        # Ollama configuration
        self.base_url = config.get("Ollama", "BASE_URL", fallback="http://localhost:11434")
        self.model = config.get("Ollama", "MODEL", fallback="llama2:latest")
        self.timeout = int(config.get("Ollama", "TIMEOUT", fallback="480"))
        
        # Model parameters
        self.temperature = float(config.get("Ollama", "TEMPERATURE", fallback="1.1"))
        self.max_tokens = int(config.get("Ollama", "MAX_TOKENS", fallback="16000"))
        
        # Caching setup
        self.set_api_cache(cache_api_calls, cache_file_name)
        
        # Test connection
        self._test_connection()
    
    def _test_connection(self):
        """Test connection to Ollama server"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get("models", [])
                available_models = [m["name"] for m in models]
                logger.info(f"Connected to Ollama. Available models: {available_models}")
                
                # Check if our configured model is available
                if self.model not in available_models:
                    logger.warning(f"Configured model '{self.model}' not found. Available: {available_models}")
                    if available_models:
                        self.model = available_models[0]
                        logger.info(f"Using first available model: {self.model}")
            else:
                logger.error(f"Failed to connect to Ollama: {response.status_code}")
        except Exception as e:
            logger.error(f"Error connecting to Ollama: {e}")
    
    def set_api_cache(self, cache_api_calls, cache_file_name=default["cache_file_name"]):
        """
        Enables or disables the caching of API calls.
        """
        self.cache_api_calls = cache_api_calls
        self.cache_file_name = cache_file_name.replace("openai_api_cache", "ollama_api_cache")
        if self.cache_api_calls:
            self.api_cache = self._load_cache()
    
    def _load_cache(self):
        """Load API call cache from file"""
        try:
            if os.path.exists(self.cache_file_name):
                with open(self.cache_file_name, 'rb') as f:
                    return pickle.load(f)
        except Exception as e:
            logger.warning(f"Could not load cache: {e}")
        return {}
    
    def _save_cache(self):
        """Save API call cache to file"""
        if self.cache_api_calls:
            try:
                with open(self.cache_file_name, 'wb') as f:
                    pickle.dump(self.api_cache, f)
            except Exception as e:
                logger.warning(f"Could not save cache: {e}")
    
    def _get_cache_key(self, messages, **kwargs):
        """Generate cache key for API call"""
        # Create a hashable representation of the request
        key_data = {
            "messages": str(messages),
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            **kwargs
        }
        return str(hash(str(sorted(key_data.items()))))
    
    def send_message(self, messages: List[Dict], model: Optional[str] = None, **kwargs) -> Dict:
        """
        Send messages to Ollama API with OpenAI-compatible interface
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model name (optional, uses default if not provided)
            **kwargs: Additional parameters
            
        Returns:
            Response dictionary compatible with OpenAI format
        """
        if model is None:
            model = self.model
            
        # Check cache first
        cache_key = None
        if self.cache_api_calls:
            cache_key = self._get_cache_key(messages, model=model, **kwargs)
            if cache_key in self.api_cache:
                logger.debug("Using cached response")
                return self.api_cache[cache_key]
        
        # Convert messages to Ollama format
        prompt = self._convert_messages_to_prompt(messages)
        
        # Prepare request
        request_data = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", self.temperature),
                "num_predict": kwargs.get("max_tokens", self.max_tokens),
            }
        }
        
        # Handle response format (for structured output)
        response_format = kwargs.get("response_format")
        if response_format:
            # For structured output, we'll add instructions to the prompt
            if hasattr(response_format, 'model_json_schema'):
                schema = response_format.model_json_schema()
                request_data["prompt"] += f"\n\nPlease respond with valid JSON matching this schema: {json.dumps(schema)}"
        
        try:
            # Make API call
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=request_data,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            ollama_response = response.json()
            
            # Convert to OpenAI-compatible format
            openai_response = self._convert_ollama_to_openai_response(ollama_response, messages)
            
            # Cache the response
            if self.cache_api_calls and cache_key:
                self.api_cache[cache_key] = openai_response
                self._save_cache()
            
            return openai_response
            
        except Exception as e:
            logger.error(f"Error calling Ollama API: {e}")
            raise
    
    def _convert_messages_to_prompt(self, messages: List[Dict]) -> str:
        """Convert OpenAI messages format to a single prompt for Ollama"""
        prompt_parts = []
        
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"Human: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
            else:
                prompt_parts.append(f"{role}: {content}")
        
        # Add final prompt for assistant response
        prompt_parts.append("Assistant:")
        
        return "\n\n".join(prompt_parts)
    
    def _convert_ollama_to_openai_response(self, ollama_response: Dict, original_messages: List[Dict]) -> Dict:
        """Convert Ollama response to OpenAI-compatible format"""
        content = ollama_response.get("response", "")
        
        # Create OpenAI-compatible response
        openai_response = {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": content
                },
                "finish_reason": "stop",
                "index": 0
            }],
            "usage": {
                "prompt_tokens": self._estimate_tokens(str(original_messages)),
                "completion_tokens": self._estimate_tokens(content),
                "total_tokens": 0  # Will be calculated below
            },
            "model": ollama_response.get("model", self.model),
            "object": "chat.completion",
            "created": int(time.time())
        }
        
        # Calculate total tokens
        openai_response["usage"]["total_tokens"] = (
            openai_response["usage"]["prompt_tokens"] + 
            openai_response["usage"]["completion_tokens"]
        )
        
        return openai_response
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text (rough approximation)"""
        # Simple estimation: ~4 characters per token
        return max(1, len(text) // 4)
    
    def get_embedding(self, text: str, model: Optional[str] = None) -> List[float]:
        """
        Get text embedding from Ollama
        Note: Not all Ollama models support embeddings
        """
        if model is None:
            model = config.get("Ollama", "EMBEDDING_MODEL", fallback=self.model)
        
        try:
            response = requests.post(
                f"{self.base_url}/api/embeddings",
                json={
                    "model": model,
                    "prompt": text
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get("embedding", [])
            
        except Exception as e:
            logger.warning(f"Embedding not available, using dummy embedding: {e}")
            # Return dummy embedding if not supported
            return [0.0] * 384  # Common embedding dimension

# Global client instance
_client = None

def client():
    """Get the global Ollama client instance"""
    global _client
    if _client is None:
        _client = OllamaClient()
    return _client

# Compatibility functions to match OpenAI utils interface
def send_message(messages, **kwargs):
    """Send message using global client"""
    return client().send_message(messages, **kwargs)

def get_embedding(text, **kwargs):
    """Get embedding using global client"""
    return client().get_embedding(text, **kwargs)