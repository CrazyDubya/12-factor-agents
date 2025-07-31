import express from 'express';
import { TwelveFactorAgent, AgentState } from './agent';
import { OllamaService } from './ollama-service';

export class AgentServer {
  private app: express.Application;
  private agents: Map<string, TwelveFactorAgent> = new Map();
  private ollamaService: OllamaService;

  constructor() {
    this.app = express();
    this.app.use(express.json());
    
    const ollamaBaseUrl = process.env.OLLAMA_BASE_URL || 'http://localhost:11434';
    this.ollamaService = new OllamaService(ollamaBaseUrl);
    
    this.setupRoutes();
  }

  private setupRoutes(): void {
    // Health check
    this.app.get('/health', async (req, res) => {
      const ollamaHealthy = await this.ollamaService.checkHealth();
      res.json({
        status: 'ok',
        ollama: ollamaHealthy ? 'connected' : 'disconnected',
        timestamp: new Date().toISOString()
      });
    });

    // Factor 6: Launch/Pause/Resume with simple APIs
    // Create new conversation thread
    this.app.post('/thread', async (req, res) => {
      try {
        const { message, model } = req.body;
        
        if (!message) {
          return res.status(400).json({ error: 'Message is required' });
        }

        const threadId = `thread-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        const currentModel = model || process.env.SELECTED_MODEL || 'llama3.1:8b';
        
        // Factor 5: Unify execution state and business state
        const state: AgentState = {
          threadId,
          currentModel,
          context: [],
          ollamaBaseUrl: process.env.OLLAMA_BASE_URL || 'http://localhost:11434'
        };

        const agent = new TwelveFactorAgent(state);
        this.agents.set(threadId, agent);

        // Process the initial message
        const nextStep = await agent.determineNextStep(message);
        const result = await agent.executeToolCall(nextStep);

        res.json({
          thread_id: threadId,
          model: currentModel,
          next_step: nextStep,
          result,
          state: agent.getState()
        });

      } catch (error) {
        res.status(500).json({ 
          error: error instanceof Error ? error.message : 'Unknown error' 
        });
      }
    });

    // Continue conversation in existing thread
    this.app.post('/thread/:threadId/continue', async (req, res) => {
      try {
        const { threadId } = req.params;
        const { message } = req.body;

        if (!message) {
          return res.status(400).json({ error: 'Message is required' });
        }

        const agent = this.agents.get(threadId);
        if (!agent) {
          return res.status(404).json({ error: 'Thread not found' });
        }

        const nextStep = await agent.determineNextStep(message);
        const result = await agent.executeToolCall(nextStep);

        res.json({
          thread_id: threadId,
          next_step: nextStep,
          result,
          state: agent.getState()
        });

      } catch (error) {
        res.status(500).json({ 
          error: error instanceof Error ? error.message : 'Unknown error' 
        });
      }
    });

    // Get thread state
    this.app.get('/thread/:threadId', (req, res) => {
      const { threadId } = req.params;
      const agent = this.agents.get(threadId);
      
      if (!agent) {
        return res.status(404).json({ error: 'Thread not found' });
      }

      res.json({
        thread_id: threadId,
        state: agent.getState()
      });
    });

    // List available models
    this.app.get('/models', async (req, res) => {
      try {
        const models = await this.ollamaService.listModels();
        const recommendations = this.ollamaService.getRecommendedModels();
        
        res.json({
          models: models.map(model => ({
            name: model.name,
            size: model.size,
            display: this.ollamaService.formatModelForDisplay(model),
            details: model.details
          })),
          recommendations
        });
      } catch (error) {
        res.status(500).json({ 
          error: error instanceof Error ? error.message : 'Failed to fetch models' 
        });
      }
    });

    // Change model for a thread
    this.app.post('/thread/:threadId/model', async (req, res) => {
      try {
        const { threadId } = req.params;
        const { model } = req.body;

        if (!model) {
          return res.status(400).json({ error: 'Model name is required' });
        }

        const agent = this.agents.get(threadId);
        if (!agent) {
          return res.status(404).json({ error: 'Thread not found' });
        }

        // Verify model exists
        const models = await this.ollamaService.listModels();
        const modelExists = models.some(m => m.name === model);
        
        if (!modelExists) {
          return res.status(400).json({ 
            error: `Model '${model}' not found`,
            available_models: models.map(m => m.name)
          });
        }

        // Update model through agent
        const selectResult = await agent.executeToolCall({
          intent: 'select_model',
          model_name: model
        });

        res.json({
          thread_id: threadId,
          result: selectResult,
          state: agent.getState()
        });

      } catch (error) {
        res.status(500).json({ 
          error: error instanceof Error ? error.message : 'Failed to change model' 
        });
      }
    });

    // Factor 11: Single-command execution endpoint
    this.app.post('/execute', async (req, res) => {
      try {
        const { command, model } = req.body;
        
        if (!command) {
          return res.status(400).json({ error: 'Command is required' });
        }

        // Create temporary agent for single execution
        const tempThreadId = `temp-${Date.now()}`;
        const currentModel = model || process.env.SELECTED_MODEL || 'llama3.1:8b';
        
        const state: AgentState = {
          threadId: tempThreadId,
          currentModel,
          context: [],
          ollamaBaseUrl: process.env.OLLAMA_BASE_URL || 'http://localhost:11434'
        };

        const agent = new TwelveFactorAgent(state);
        
        const nextStep = await agent.determineNextStep(command);
        const result = await agent.executeToolCall(nextStep);

        res.json({
          command,
          model: currentModel,
          next_step: nextStep,
          result
        });

      } catch (error) {
        res.status(500).json({ 
          error: error instanceof Error ? error.message : 'Execution failed' 
        });
      }
    });

    // List active threads
    this.app.get('/threads', (req, res) => {
      const threads = Array.from(this.agents.keys()).map(threadId => {
        const agent = this.agents.get(threadId)!;
        const state = agent.getState();
        return {
          thread_id: threadId,
          model: state.currentModel,
          context_length: state.context.length
        };
      });

      res.json({ threads });
    });

    // Delete thread
    this.app.delete('/thread/:threadId', (req, res) => {
      const { threadId } = req.params;
      
      if (this.agents.has(threadId)) {
        this.agents.delete(threadId);
        res.json({ message: 'Thread deleted successfully' });
      } else {
        res.status(404).json({ error: 'Thread not found' });
      }
    });
  }

  public start(port: number = 3000): void {
    this.app.listen(port, () => {
      console.log(`🦙 12-Factor Agents Ollama Demo Server running on port ${port}`);
      console.log(`📡 Ollama Base URL: ${process.env.OLLAMA_BASE_URL || 'http://localhost:11434'}`);
      console.log(`🔗 API Endpoints:`);
      console.log(`   GET  /health                    - Health check`);
      console.log(`   GET  /models                    - List available models`);
      console.log(`   POST /thread                    - Create new conversation`);
      console.log(`   POST /thread/:id/continue       - Continue conversation`);
      console.log(`   GET  /thread/:id                - Get thread state`);
      console.log(`   POST /thread/:id/model          - Change model for thread`);
      console.log(`   POST /execute                   - Single command execution`);
      console.log(`   GET  /threads                   - List active threads`);
      console.log(`   DELETE /thread/:id              - Delete thread`);
    });
  }

  public getApp(): express.Application {
    return this.app;
  }
}