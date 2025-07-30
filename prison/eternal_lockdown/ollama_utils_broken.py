

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
