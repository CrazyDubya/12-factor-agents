/**
 * Ollama Client - Interface to local Ollama AI models
 * Handles model selection, generation, streaming, and chat
 */

class OllamaClient {
  constructor(baseURL = 'http://localhost:11434') {
    this.baseURL = baseURL;
    this.modelsCache = null;
    this.cacheExpiry = 60000; // 1 minute
    this.lastCacheUpdate = 0;
  }

  /**
   * Check if Ollama is running and accessible
   */
  async checkHealth() {
    try {
      const response = await fetch(`${this.baseURL}/api/tags`);
      return response.ok;
    } catch (error) {
      console.error('Ollama health check failed:', error);
      return false;
    }
  }

  /**
   * List all available models
   */
  async listModels() {
    const now = Date.now();
    if (this.modelsCache && now - this.lastCacheUpdate < this.cacheExpiry) {
      return this.modelsCache;
    }

    try {
      const response = await fetch(`${this.baseURL}/api/tags`);
      const data = await response.json();
      this.modelsCache = data.models || [];
      this.lastCacheUpdate = now;
      return this.modelsCache;
    } catch (error) {
      console.error('Failed to list models:', error);
      return [];
    }
  }

  /**
   * Get detailed information about a specific model
   */
  async getModelInfo(modelName) {
    try {
      const response = await fetch(`${this.baseURL}/api/show`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: modelName })
      });
      return await response.json();
    } catch (error) {
      console.error(`Failed to get model info for ${modelName}:`, error);
      return null;
    }
  }

  /**
   * Generate completion (single-turn)
   */
  async generate(model, prompt, options = {}) {
    try {
      const response = await fetch(`${this.baseURL}/api/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model,
          prompt,
          stream: false,
          options: {
            num_predict: options.num_predict || 8192, // Allow up to 8K tokens output
            temperature: options.temperature || 0.7,
            top_p: options.top_p || 0.9,
            ...options.options
          },
          ...options
        })
      });

      const data = await response.json();
      return data.response;
    } catch (error) {
      console.error('Generation failed:', error);
      throw error;
    }
  }

  /**
   * Generate with streaming (real-time output)
   */
  async streamGenerate(model, prompt, onChunk, onComplete, options = {}) {
    try {
      const response = await fetch(`${this.baseURL}/api/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model,
          prompt,
          stream: true,
          options: {
            num_predict: options.num_predict || 8192, // Allow up to 8K tokens output
            temperature: options.temperature || 0.7,
            top_p: options.top_p || 0.9,
            ...options.options
          },
          ...options
        })
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let fullResponse = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          break;
        }

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n').filter(line => line.trim());

        for (const line of lines) {
          try {
            const json = JSON.parse(line);
            if (json.response) {
              fullResponse += json.response;
              onChunk(json.response, fullResponse);
            }
            if (json.done) {
              onComplete(fullResponse, json);
            }
          } catch (_e) {
            console.warn('Failed to parse chunk:', line);
          }
        }
      }

      return fullResponse;
    } catch (error) {
      console.error('Streaming generation failed:', error);
      throw error;
    }
  }

  /**
   * Chat completion (multi-turn)
   */
  async chat(model, messages, options = {}) {
    try {
      const response = await fetch(`${this.baseURL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model,
          messages,
          stream: false,
          options: {
            num_predict: options.num_predict || 8192,
            temperature: options.temperature || 0.7,
            top_p: options.top_p || 0.9,
            ...options.options
          },
          ...options
        })
      });

      const data = await response.json();
      return data.message.content;
    } catch (error) {
      console.error('Chat failed:', error);
      throw error;
    }
  }

  /**
   * Chat with streaming
   */
  async streamChat(model, messages, onChunk, onComplete, options = {}) {
    try {
      const response = await fetch(`${this.baseURL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model,
          messages,
          stream: true,
          options: {
            num_predict: options.num_predict || 8192,
            temperature: options.temperature || 0.7,
            top_p: options.top_p || 0.9,
            ...options.options
          },
          ...options
        })
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let fullResponse = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          break;
        }

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n').filter(line => line.trim());

        for (const line of lines) {
          try {
            const json = JSON.parse(line);
            if (json.message?.content) {
              fullResponse += json.message.content;
              onChunk(json.message.content, fullResponse);
            }
            if (json.done) {
              onComplete(fullResponse, json);
            }
          } catch (_e) {
            console.warn('Failed to parse chat chunk:', line);
          }
        }
      }

      return fullResponse;
    } catch (error) {
      console.error('Streaming chat failed:', error);
      throw error;
    }
  }

  /**
   * Generate embeddings for semantic search
   */
  async embeddings(model, text) {
    try {
      const response = await fetch(`${this.baseURL}/api/embeddings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model,
          prompt: text
        })
      });

      const data = await response.json();
      return data.embedding;
    } catch (error) {
      console.error('Embeddings generation failed:', error);
      throw error;
    }
  }

  /**
   * Smart model selection based on task type
   * Based on comprehensive benchmarking and real-world testing
   * Updated to prioritize expanded models with larger context windows (32K-128K)
   */
  async selectBestModel(task, preferSpeed = false) {
    const MODEL_PREFERENCES = {
      // Prioritize expanded models with 32K-128K context windows
      readme: ['mistral-32k', 'mistral:7b', 'llama3-32k', 'llama3:8b', 'qwen-128k'], // Best for documentation
      code_analysis: ['llama3-32k', 'gemma2-32k', 'llama3:8b', 'qwen-128k', 'gemma2:9b'], // Strong reasoning
      agent_config: ['llama3-32k', 'mistral-32k', 'llama3:8b', 'mistral:7b', 'qwen-128k'], // Structured output
      todo: ['qwen-128k', 'qwen2.5:3b', 'llama32-long', 'llama3.2:3b', 'mistral:7b'], // Fast list generation
      quality: ['gemma2-32k', 'llama3-32k', 'llama3:8b', 'qwen-128k', 'gemma2:9b'], // Deep analysis
      security: ['llama3-32k', 'llama3:8b', 'qwen-128k', 'mistral-32k', 'mistral:7b'], // Pattern recognition
      dependency: ['qwen-128k', 'qwen2.5:3b', 'llama32-long', 'llama3.2:3b', 'mistral:7b'], // Structured parsing
      chat: ['llama3-32k', 'mistral-32k', 'llama3:8b', 'mistral:7b', 'qwen-128k'], // Conversational
      large_repo: ['qwen-128k', 'llama32-long', 'gemma2-32k', 'llama3-32k', 'mistral-32k'], // Large files/repos (128K context)
      quick_task: ['qwen2.5:1.5b', 'llama3.2:3b', 'smollm2:360m'], // Ultra-fast
      embedding: ['nomic-embed-text'] // Semantic search
    };

    // Task-specific generation settings - increased for expanded models
    const TASK_SETTINGS = {
      readme: { num_predict: 16384, temperature: 0.7, top_p: 0.9 }, // 16K output for comprehensive docs
      code_analysis: { num_predict: 8192, temperature: 0.5, top_p: 0.8 }, // 8K for detailed analysis
      agent_config: { num_predict: 8192, temperature: 0.6, top_p: 0.85 }, // 8K for complex configs
      todo: { num_predict: 4096, temperature: 0.4, top_p: 0.75 }, // 4K for lists
      quality: { num_predict: 8192, temperature: 0.5, top_p: 0.8 }, // 8K for thorough analysis
      security: { num_predict: 8192, temperature: 0.4, top_p: 0.8 }, // 8K for detailed security reports
      dependency: { num_predict: 4096, temperature: 0.5, top_p: 0.8 }, // 4K for dependency graphs
      chat: { num_predict: 4096, temperature: 0.8, top_p: 0.9 }, // 4K for conversations
      large_repo: { num_predict: 16384, temperature: 0.6, top_p: 0.85 }, // 16K for large context tasks
      quick_task: { num_predict: 512, temperature: 0.3, top_p: 0.7 } // 512 for quick tasks
    };

    const preferences = MODEL_PREFERENCES[task] || MODEL_PREFERENCES['chat'];
    const settings = TASK_SETTINGS[task] || TASK_SETTINGS['chat'];
    const available = await this.listModels();

    let selectedModel = null;

    if (preferSpeed) {
      // Reverse order (smaller models first)
      for (let i = preferences.length - 1; i >= 0; i--) {
        const modelName = preferences[i];
        const found = available.find(m => m.name.includes(modelName));
        if (found) {
          selectedModel = found.name;
          break;
        }
      }
    } else {
      // Quality priority (larger models first)
      for (const modelName of preferences) {
        const found = available.find(m => m.name.includes(modelName));
        if (found) {
          selectedModel = found.name;
          break;
        }
      }
    }

    // Fallback to first available model
    if (!selectedModel) {
      selectedModel = available[0]?.name || null;
    }

    return { model: selectedModel, settings };
  }

  /**
   * Get recommended settings for a task type
   */
  getTaskSettings(task) {
    const TASK_SETTINGS = {
      readme: { num_predict: 16384, temperature: 0.7, top_p: 0.9 },
      code_analysis: { num_predict: 8192, temperature: 0.5, top_p: 0.8 },
      agent_config: { num_predict: 8192, temperature: 0.6, top_p: 0.85 },
      todo: { num_predict: 4096, temperature: 0.4, top_p: 0.75 },
      quality: { num_predict: 8192, temperature: 0.5, top_p: 0.8 },
      security: { num_predict: 8192, temperature: 0.4, top_p: 0.8 },
      dependency: { num_predict: 4096, temperature: 0.5, top_p: 0.8 },
      chat: { num_predict: 4096, temperature: 0.8, top_p: 0.9 },
      large_repo: { num_predict: 16384, temperature: 0.6, top_p: 0.85 },
      quick_task: { num_predict: 512, temperature: 0.3, top_p: 0.7 }
    };

    return TASK_SETTINGS[task] || TASK_SETTINGS['chat'];
  }

  /**
   * Get fallback models if primary fails
   */
  async getFallbackModels(primaryModel) {
    const available = await this.listModels();
    return available.filter(m => m.name !== primaryModel).map(m => m.name);
  }

  /**
   * Estimate token count (rough approximation)
   */
  estimateTokens(text) {
    // Rough estimate: ~4 characters per token
    return Math.ceil(text.length / 4);
  }

  /**
   * Format prompt with template variables
   */
  formatPrompt(template, variables) {
    let formatted = template;
    for (const [key, value] of Object.entries(variables)) {
      formatted = formatted.replace(new RegExp(`{{${key}}}`, 'g'), value);
    }
    return formatted;
  }

  /**
   * Build context window from repository data
   */
  buildContextWindow(repoData, maxTokens = 4096) {
    const context = [];
    let tokenCount = 0;

    // Priority order for context inclusion
    const items = [
      { content: repoData.description || '', priority: 1 },
      { content: repoData.readme || '', priority: 2 },
      { content: JSON.stringify(repoData.package_info || {}), priority: 3 },
      { content: repoData.file_structure || '', priority: 4 }
    ];

    items.sort((a, b) => a.priority - b.priority);

    for (const item of items) {
      const itemTokens = this.estimateTokens(item.content);
      if (tokenCount + itemTokens < maxTokens) {
        context.push(item.content);
        tokenCount += itemTokens;
      } else {
        // Add truncated version
        const remaining = maxTokens - tokenCount;
        const truncated = item.content.substring(0, remaining * 4);
        context.push(truncated + '...[truncated]');
        break;
      }
    }

    return context.join('\n\n');
  }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = OllamaClient;
}
