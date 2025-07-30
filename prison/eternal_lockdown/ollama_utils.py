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

    def send_message(self, messages: List[Dict], model: Optional[str] = None, **kwargs) -> Dict:
        """
        Send messages to Ollama API in OpenAI-compatible format
        """
        # Use provided model or default
        model_to_use = model or self.model
        
        # Create cache key
        cache_key = json.dumps({
            "messages": messages,
            "model": model_to_use,
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens)
        }, sort_keys=True)
        
        # Check cache first
        if self.cache_api_calls and cache_key in self.api_cache:
            logger.debug("Returning cached response")
            return self.api_cache[cache_key]
        
        try:
            # Convert messages to Ollama prompt format
            prompt = self._convert_messages_to_prompt(messages)
            
            # Prepare Ollama request
            ollama_request = {
                "model": model_to_use,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", self.temperature),
                    "num_predict": kwargs.get("max_tokens", self.max_tokens)
                }
            }
            
            # Make request to Ollama
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=ollama_request,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                ollama_response = response.json()
                openai_response = self._convert_ollama_to_openai_response(ollama_response, messages)
                
                # Cache the response
                if self.cache_api_calls:
                    self.api_cache[cache_key] = openai_response
                    self._save_cache()
                
                return openai_response
            else:
                error_msg = f"Ollama API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {
                    "choices": [{
                        "message": {"role": "assistant", "content": f"Error: {error_msg}"},
                        "finish_reason": "error"
                    }]
                }
                
        except Exception as e:
            error_msg = f"Error calling Ollama API: {str(e)}"
            logger.error(error_msg)
            return {
                "choices": [{
                    "message": {"role": "assistant", "content": f"Error: {error_msg}"},
                    "finish_reason": "error"
                }]
            }
    
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
        
        # Add specific JSON formatting instruction for TinyTroupe compatibility
        prompt_parts.append("""
Assistant: I must respond with a valid JSON object in the exact format expected by TinyTroupe. My response must be ONLY valid JSON, no additional text or explanations.

The JSON format must be:
{
  "action": {
    "type": "ACTION_TYPE",
    "content": "action description",
    "target": "target_name_or_empty"
  },
  "cognitive_state": {
    "goals": ["goal1", "goal2"],
    "context": ["context1", "context2"],
    "attention": "what I'm focusing on",
    "emotions": "how I'm feeling"
  }
}

Valid action types: TALK, DONE, THINK, MOVE, WORK, OBSERVE, INTERACT

JSON response:""")
        
        return "\n\n".join(prompt_parts)
    
    def _convert_ollama_to_openai_response(self, ollama_response: Dict, original_messages: List[Dict]) -> Dict:
        """Convert Ollama response to OpenAI-compatible format"""
        content = ollama_response.get("response", "")
        
        # Create OpenAI-compatible response that TinyTroupe expects
        openai_response = {
            "role": "assistant",
            "content": content,
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
                "total_tokens": self._estimate_tokens(str(original_messages)) + self._estimate_tokens(content)
            }
        }
        
        return openai_response
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text"""
        try:
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
        except:
            # Fallback: rough estimate
            return len(text.split()) * 1.3
    
    def get_embedding(self, text: str, model: Optional[str] = None, **kwargs) -> Dict:
        """
        Get embeddings from Ollama (if supported by model)
        """
        # Note: Not all Ollama models support embeddings
        # This is a placeholder implementation
        return {
            "data": [{
                "embedding": [0.0] * 1536,  # Placeholder embedding
                "index": 0
            }],
            "usage": {
                "prompt_tokens": self._estimate_tokens(text),
                "total_tokens": self._estimate_tokens(text)
            }
        }

###########################################################################
# Global client instance
###########################################################################

_client = None

def client():
    """Get or create global OllamaClient instance"""
    global _client
    if _client is None:
        _client = OllamaClient()
    return _client

def send_message(messages, **kwargs):
    """Send message using global client"""
    return client().send_message(messages, **kwargs)

def get_embedding(text, **kwargs):
    """Get embedding using global client"""
    return client().get_embedding(text, **kwargs)

def setup_ollama_for_tinytroupe():
    """
    Configure TinyTroupe to use Ollama instead of OpenAI
    This replaces the OpenAI API calls with Ollama calls
    """
    try:
        import tinytroupe.openai_utils as openai_utils
        
        def ollama_send_message(messages, model=None, **kwargs):
            """Replace OpenAI send_message with Ollama version"""
            ollama_client = client()
            return ollama_client.send_message(messages, model=model, **kwargs)
        
        def ollama_send_message_with_retries(messages, model=None, **kwargs):
            """Replace OpenAI send_message with retries"""
            return ollama_send_message(messages, model=model, **kwargs)
        
        # Replace the functions in openai_utils
        openai_utils.send_message = ollama_send_message
        openai_utils.send_message_with_retries = ollama_send_message_with_retries
        
        print("TinyTroupe configured to use Ollama LLMs")
        return True
        
    except ImportError as e:
        print(f"Could not configure TinyTroupe for Ollama: {e}")
        return False
    except Exception as e:
        print(f"Error setting up Ollama for TinyTroupe: {e}")
        return False