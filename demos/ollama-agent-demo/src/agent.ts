// The `baml_client` module is generated code. Ensure it is created as part of the build process.
let b;
try {
  b = require('../baml_client');
} catch (error) {
  console.error("Error: The 'baml_client' module is missing. Ensure it is generated before running the application.");
  process.exit(1); // Exit the application if the module is missing
}
import { OllamaService, OllamaModel } from './ollama-service';

export interface AgentState {
  threadId: string;
  currentModel: string;
  context: string[];
  ollamaBaseUrl: string;
}

export class TwelveFactorAgent {
  private ollamaService: OllamaService;
  private state: AgentState;

  constructor(state: AgentState) {
    this.state = state;
    this.ollamaService = new OllamaService(state.ollamaBaseUrl);
  }

  /**
   * Factor 1: Natural Language to Tool Calls
   * Convert user input to structured tool calls
   */
  async determineNextStep(userInput: string): Promise<any> {
    // Add user input to context (Factor 3: Own your context window)
    this.addToContext('user_input', userInput);
    
    const thread = this.formatContextAsXML();
    
    try {
      // Set the model for this request
      process.env.SELECTED_MODEL = this.state.currentModel;
      process.env.OLLAMA_BASE_URL = this.state.ollamaBaseUrl;
      
      const result = await b.DetermineNextStep(thread, this.state.currentModel);
      this.addToContext('tool_call', JSON.stringify(result));
      
      return result;
    } catch (error) {
      console.error('Error determining next step:', error);
      // Factor 9: Compact Errors into Context Window
      const errorMsg = this.compactError(error);
      this.addToContext('error', errorMsg);
      
      return {
        intent: 'request_more_information',
        message: 'I encountered an issue processing your request. Could you please rephrase or try again?'
      };
    }
  }

  /**
   * Factor 4: Tools are just structured outputs
   * Execute tool calls and return results
   */
  async executeToolCall(toolCall: any): Promise<any> {
    switch (toolCall.intent) {
      case 'add':
        return this.handleCalculation(toolCall.a, toolCall.b, (a, b) => a + b, 'addition');
      
      case 'subtract':
        return this.handleCalculation(toolCall.a, toolCall.b, (a, b) => a - b, 'subtraction');
      
      case 'multiply':
        return this.handleCalculation(toolCall.a, toolCall.b, (a, b) => a * b, 'multiplication');
      
      case 'divide':
        return this.handleCalculation(toolCall.a, toolCall.b, (a, b) => {
          if (b === 0) throw new Error('Division by zero');
          return a / b;
        }, 'division');
      
      case 'list_models':
        return await this.handleListModels();
      
      case 'select_model':
        return await this.handleSelectModel(toolCall.model_name);
      
      case 'request_more_information':
        return {
          type: 'clarification_needed',
          message: toolCall.message
        };
      
      case 'done_for_now':
        return {
          type: 'final_response',
          message: toolCall.message
        };
      
      default:
        throw new Error(`Unknown tool: ${toolCall.intent}`);
    }
  }

  /**
   * Factor 3: Own your context window
   * Format context in a structured way
   */
  private formatContextAsXML(): string {
    return this.state.context.map(entry => {
      const [type, content] = entry.split(':', 2);
      return `<${type}>\n${content}\n</${type}>`;
    }).join('\n\n');
  }

  /**
   * Add entry to context with proper formatting
   */
  private addToContext(type: string, content: string): void {
    this.state.context.push(`${type}:${content}`);
    
    // Factor 3: Keep context window manageable
    if (this.state.context.length > 20) {
      this.state.context = this.state.context.slice(-15); // Keep last 15 entries
    }
  }

  /**
   * Factor 9: Compact Errors into Context Window
   */
  private compactError(error: any): string {
    const errorStr = error?.message || String(error);
    // Keep only essential error information
    return errorStr.length > 200 ? errorStr.substring(0, 200) + '...' : errorStr;
  }

  /**
   * Handle calculator operations
   */
  private async handleCalculation(
    a: number, 
    b: number, 
    operation: (a: number, b: number) => number,
    operationName: string
  ): Promise<any> {
    try {
      const result = operation(a, b);
      const response = {
        type: 'calculation_result',
        operation: operationName,
        inputs: { a, b },
        result,
        message: `The ${operationName} of ${a} and ${b} is ${result}.`
      };
      
      this.addToContext('tool_response', JSON.stringify(response));
      return response;
    } catch (error) {
      throw new Error(`Failed to perform ${operationName}: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  /**
   * Handle model listing
   */
  private async handleListModels(): Promise<any> {
    try {
      const models = await this.ollamaService.listModels();
      const recommendations = this.ollamaService.getRecommendedModels();
      
      const response = {
        type: 'model_list',
        models: models.map(model => ({
          name: model.name,
          size: model.size,
          display: this.ollamaService.formatModelForDisplay(model)
        })),
        recommendations,
        current_model: this.state.currentModel,
        message: `Found ${models.length} available models. Current model: ${this.state.currentModel}`
      };
      
      this.addToContext('tool_response', JSON.stringify(response));
      return response;
    } catch (error) {
      throw new Error(`Failed to list models: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  /**
   * Handle model selection
   */
  private async handleSelectModel(modelName: string): Promise<any> {
    try {
      // Verify model exists
      const models = await this.ollamaService.listModels();
      const modelExists = models.some(model => model.name === modelName);
      
      if (!modelExists) {
        throw new Error(`Model '${modelName}' not found. Available models: ${models.map(m => m.name).join(', ')}`);
      }
      
      const previousModel = this.state.currentModel;
      this.state.currentModel = modelName;
      
      const response = {
        type: 'model_selected',
        previous_model: previousModel,
        new_model: modelName,
        message: `Successfully switched from '${previousModel}' to '${modelName}'. The new model will be used for subsequent interactions.`
      };
      
      this.addToContext('tool_response', JSON.stringify(response));
      return response;
    } catch (error) {
      throw new Error(`Failed to select model: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  /**
   * Factor 12: Make your agent a stateless reducer
   * Get current state
   */
  getState(): AgentState {
    return { ...this.state };
  }

  /**
   * Factor 12: Make your agent a stateless reducer
   * Create new agent instance with updated state
   */
  static fromState(state: AgentState): TwelveFactorAgent {
    return new TwelveFactorAgent(state);
  }

  /**
   * Check if Ollama is accessible
   */
  async checkOllamaHealth(): Promise<boolean> {
    return await this.ollamaService.checkHealth();
  }
}