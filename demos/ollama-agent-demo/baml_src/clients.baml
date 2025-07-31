// Ollama Client Configuration
// Using OpenAI-compatible API since Ollama supports this format
// Learn more about clients at https://docs.boundaryml.com/docs/snippets/clients/overview

client<llm> OllamaLocal {
  provider openai
  options {
    model env.SELECTED_MODEL
    api_key "ollama" // Ollama doesn't require real auth
    base_url env.OLLAMA_BASE_URL
  }
}

client<llm> OllamaDefault {
  provider openai
  options {
    model "llama3.1:8b"
    api_key "ollama"
    base_url env.OLLAMA_BASE_URL
  }
}

// Simple fallback for demo
client<llm> OllamaFallback {
  provider fallback
  options {
    // This will try the clients in order until one succeeds
    strategy [OllamaLocal, OllamaDefault]
  }
}

// https://docs.boundaryml.com/docs/snippets/clients/retry
retry_policy Constant {
  max_retries 3
  // Strategy is optional
  strategy {
    type constant_delay
    delay_ms 200
  }
}

retry_policy Exponential {
  max_retries 2
  // Strategy is optional
  strategy {
    type exponential_backoff
    delay_ms 300
    multiplier 1.5
    max_delay_ms 10000
  }
}