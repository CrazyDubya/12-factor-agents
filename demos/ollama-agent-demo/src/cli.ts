import * as readline from 'readline';
import { TwelveFactorAgent, AgentState } from './agent';
import { OllamaService } from './ollama-service';

export class CLI {
  private rl: readline.Interface;
  private agent: TwelveFactorAgent;
  private ollamaService: OllamaService;

  constructor() {
    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });

    const ollamaBaseUrl = process.env.OLLAMA_BASE_URL || 'http://localhost:11434';
    
    // Factor 5: Unify execution state and business state
    const initialState: AgentState = {
      threadId: `thread-${Date.now()}`,
      currentModel: process.env.SELECTED_MODEL || 'llama3.1:8b',
      context: [],
      ollamaBaseUrl
    };

    this.agent = new TwelveFactorAgent(initialState);
    this.ollamaService = new OllamaService(ollamaBaseUrl);
  }

  async start(): Promise<void> {
    console.log('🦙 12-Factor Agents Ollama Demo');
    console.log('=================================');
    console.log('');
    console.log('This demo showcases the 12-factor agent principles using Ollama models.');
    console.log('');

    // Check Ollama connectivity
    const isHealthy = await this.agent.checkOllamaHealth();
    if (!isHealthy) {
      console.log('❌ Cannot connect to Ollama. Please make sure Ollama is running.');
      console.log(`   Expected URL: ${this.agent.getState().ollamaBaseUrl}`);
      console.log('   Start Ollama with: ollama serve');
      console.log('');
      process.exit(1);
    }

    console.log('✅ Connected to Ollama successfully!');
    
    // Show current model
    const state = this.agent.getState();
    console.log(`📝 Current model: ${state.currentModel}`);
    console.log('');

    this.showHelp();
    this.startConversationLoop();
  }

  private showHelp(): void {
    console.log('Available commands:');
    console.log('  • Ask math questions: "add 5 and 3", "multiply 10 by 7"');
    console.log('  • List models: "list models" or "show available models"');
    console.log('  • Select model: "use llama3.1:8b" or "select mistral:7b"');
    console.log('  • Help: "help"');
    console.log('  • Exit: "exit" or "quit"');
    console.log('');
  }

  private async startConversationLoop(): Promise<void> {
    while (true) {
      const input = await this.prompt('You: ');
      
      if (input.toLowerCase().trim() === 'exit' || input.toLowerCase().trim() === 'quit') {
        console.log('Goodbye! 👋');
        break;
      }

      if (input.toLowerCase().trim() === 'help') {
        this.showHelp();
        continue;
      }

      if (input.trim() === '') {
        continue;
      }

      await this.processInput(input);
    }

    this.rl.close();
  }

  private async processInput(input: string): Promise<void> {
    try {
      console.log('🤖 Processing...');
      
      // Factor 1: Natural Language to Tool Calls
      const nextStep = await this.agent.determineNextStep(input);
      console.log(`📋 Next step: ${nextStep.intent}`);
      
      // Factor 4: Tools are just structured outputs
      const result = await this.agent.executeToolCall(nextStep);
      
      this.displayResult(result);
      
    } catch (error) {
      console.log(`❌ Error: ${error instanceof Error ? error.message : String(error)}`);
    }
    
    console.log('');
  }

  private displayResult(result: any): void {
    switch (result.type) {
      case 'calculation_result':
        console.log(`🧮 ${result.message}`);
        console.log(`   Operation: ${result.operation}`);
        console.log(`   Inputs: ${result.inputs.a}, ${result.inputs.b}`);
        console.log(`   Result: ${result.result}`);
        break;

      case 'model_list':
        console.log('🦙 Available Ollama Models:');
        console.log('==========================');
        result.models.forEach((model: any, index: number) => {
          const indicator = model.name === result.current_model ? '👈 (current)' : '';
          console.log(`${index + 1}. ${model.display} ${indicator}`);
        });
        console.log('');
        console.log('📋 Recommended by Category:');
        Object.entries(result.recommendations).forEach(([category, models]) => {
          console.log(`  ${category}: ${(models as string[]).join(', ')}`);
        });
        break;

      case 'model_selected':
        console.log(`🔄 Model switched successfully!`);
        console.log(`   Previous: ${result.previous_model}`);
        console.log(`   Current: ${result.new_model}`);
        break;

      case 'clarification_needed':
        console.log(`❓ ${result.message}`);
        break;

      case 'final_response':
        console.log(`✅ ${result.message}`);
        break;

      default:
        console.log(`📄 ${JSON.stringify(result, null, 2)}`);
    }
  }

  private prompt(question: string): Promise<string> {
    return new Promise((resolve) => {
      this.rl.question(question, resolve);
    });
  }

  /**
   * Factor 11: Trigger from anywhere, meet users where they are
   * Support different input methods
   */
  static async runSingleCommand(command: string): Promise<void> {
    const cli = new CLI();
    
    // Check Ollama connectivity
    const isHealthy = await cli.agent.checkOllamaHealth();
    if (!isHealthy) {
      console.log('❌ Cannot connect to Ollama. Please make sure Ollama is running.');
      return;
    }

    console.log(`🦙 Processing command: "${command}"`);
    await cli.processInput(command);
  }
}

/**
 * Start the CLI application
 */
export async function startCLI(args: string[]): Promise<void> {
  if (args.length > 0) {
    // Factor 11: Single command mode
    const command = args.join(' ');
    await CLI.runSingleCommand(command);
  } else {
    // Interactive mode
    const cli = new CLI();
    await cli.start();
  }
}