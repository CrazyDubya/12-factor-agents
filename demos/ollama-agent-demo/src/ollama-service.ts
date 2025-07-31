import axios from 'axios';

export interface OllamaModel {
  name: string;
  model: string;
  modified_at: string;
  size: number;
  digest: string;
  details?: {
    parent_model?: string;
    format?: string;
    family?: string;
    families?: string[];
    parameter_size?: string;
    quantization_level?: string;
  };
}

export interface OllamaModelResponse {
  models: OllamaModel[];
}

export class OllamaService {
  private baseUrl: string;

  constructor(baseUrl: string = 'http://localhost:11434') {
    this.baseUrl = baseUrl;
  }

  /**
   * List all available models from Ollama
   */
  async listModels(): Promise<OllamaModel[]> {
    try {
      const response = await axios.get<OllamaModelResponse>(`${this.baseUrl}/api/tags`);
      return response.data.models || [];
    } catch (error) {
      console.error('Failed to fetch models from Ollama:', error);
      throw new Error(`Failed to connect to Ollama at ${this.baseUrl}. Make sure Ollama is running.`);
    }
  }

  /**
   * Check if Ollama is running and accessible
   */
  async checkHealth(): Promise<boolean> {
    try {
      await axios.get(`${this.baseUrl}/api/tags`);
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Get model info
   */
  async getModelInfo(modelName: string): Promise<any> {
    try {
      const response = await axios.post(`${this.baseUrl}/api/show`, {
        name: modelName
      });
      return response.data;
    } catch (error) {
      console.error(`Failed to get info for model ${modelName}:`, error);
      throw new Error(`Model ${modelName} not found or not accessible`);
    }
  }

  /**
   * Format model for display
   */
  formatModelForDisplay(model: OllamaModel): string {
    const sizeGB = (model.size / (1024 * 1024 * 1024)).toFixed(1);
    const family = model.details?.family || 'unknown';
    return `${model.name} (${family}, ${sizeGB}GB)`;
  }

  /**
   * Get recommended models for different use cases
   */
  getRecommendedModels(): { [key: string]: string[] } {
    return {
      'General Chat': ['llama3.1:8b', 'llama3.1:70b', 'mistral:7b'],
      'Code Generation': ['codellama:7b', 'codellama:13b', 'deepseek-coder:6.7b'],
      'Math & Logic': ['llama3.1:8b', 'llama3.1:70b'],
      'Fast Response': ['llama3.1:8b', 'mistral:7b', 'phi3:mini'],
      'High Quality': ['llama3.1:70b', 'llama3.1:405b']
    };
  }
}