# 🦙 12-Factor Agents Ollama Demo

This demo showcases the **12-factor agent principles** using Ollama for local LLM inference. Users can select from available Ollama models and interact with an agent that follows the twelve factors for reliable LLM applications.

## 🌟 12-Factor Principles Demonstrated

This demo implements all 12 factors:

1. **Natural Language to Tool Calls** - Converts user input to structured tool calls
2. **Own your prompts** - Prompts are defined in BAML files
3. **Own your context window** - Context formatted as structured XML
4. **Tools are just structured outputs** - Calculator and model management tools
5. **Unify execution state and business state** - Unified AgentState interface
6. **Launch/Pause/Resume with simple APIs** - Stateless design supports this
7. **Contact humans with tool calls** - Clarification requests as tool calls
8. **Own your control flow** - Custom agent loop implementation
9. **Compact Errors into Context Window** - Error handling with context preservation
10. **Small, Focused Agents** - Single-purpose agent for math and model management
11. **Trigger from anywhere, meet users where they are** - CLI and single-command modes
12. **Make your agent a stateless reducer** - State-based agent design

## 🚀 Quick Start

### Prerequisites

1. **Install Ollama**: Visit [ollama.ai](https://ollama.ai) and install Ollama
2. **Start Ollama**: Run `ollama serve` in your terminal
3. **Pull a model**: Run `ollama pull llama3.1:8b` (or your preferred model)

### Installation

```bash
# Navigate to the demo directory
cd demos/ollama-agent-demo

# Install dependencies
npm install

# Build the project
npm run build
```

### Usage

#### Interactive Mode

```bash
npm run dev
```

This starts an interactive CLI where you can:
- Perform calculations: "add 5 and 3", "multiply 10 by 7"
- List available models: "list models"
- Select different models: "use mistral:7b"
- Get help: "help"
- Exit: "exit" or Ctrl+C

#### Single Command Mode

```bash
npm run dev "add 15 and 27"
npm run dev "list models"
npm run dev "multiply 8 by 9"
```

## 🔧 Configuration

### Environment Variables

- `OLLAMA_BASE_URL`: Ollama server URL (default: `http://localhost:11434`)
- `SELECTED_MODEL`: Default model to use (default: `llama3.1:8b`)

### Example

```bash
export OLLAMA_BASE_URL=http://localhost:11434
export SELECTED_MODEL=mistral:7b
npm run dev
```

## 🎯 Features

### Calculator Operations
- Addition, subtraction, multiplication, division
- Error handling for edge cases (e.g., division by zero)
- Context-aware multi-step calculations

### Model Management
- List all available Ollama models
- Display model information (size, family)
- Switch between models during conversation
- Recommended models by use case

### 12-Factor Implementation
- **Structured Context**: XML-formatted conversation history
- **Error Compaction**: Intelligent error summarization
- **Stateless Design**: Easy to scale and resume
- **Tool-based Architecture**: All actions as structured outputs

## 🔍 Example Interaction

```
🦙 12-Factor Agents Ollama Demo
=================================

✅ Connected to Ollama successfully!
📝 Current model: llama3.1:8b

Available commands:
  • Ask math questions: "add 5 and 3", "multiply 10 by 7"
  • List models: "list models" or "show available models"
  • Select model: "use llama3.1:8b" or "select mistral:7b"
  • Help: "help"
  • Exit: "exit" or "quit"

You: add 15 and 27
🤖 Processing...
📋 Next step: add
🧮 The addition of 15 and 27 is 42.
   Operation: addition
   Inputs: 15, 27
   Result: 42

You: list models
🤖 Processing...
📋 Next step: list_models
🦙 Available Ollama Models:
==========================
1. llama3.1:8b (llama, 4.7GB) 👈 (current)
2. mistral:7b (mistral, 4.1GB)
3. codellama:7b (llama, 3.8GB)

📋 Recommended by Category:
  General Chat: llama3.1:8b, llama3.1:70b, mistral:7b
  Code Generation: codellama:7b, codellama:13b, deepseek-coder:6.7b
  Math & Logic: llama3.1:8b, llama3.1:70b
  Fast Response: llama3.1:8b, mistral:7b, phi3:mini
  High Quality: llama3.1:70b, llama3.1:405b

You: use mistral:7b
🤖 Processing...
📋 Next step: select_model
🔄 Model switched successfully!
   Previous: llama3.1:8b
   Current: mistral:7b
```

## 🏗️ Architecture

### File Structure

```
demos/ollama-agent-demo/
├── src/
│   ├── agent.ts           # Main agent implementation
│   ├── cli.ts            # CLI interface
│   ├── index.ts          # Entry point
│   └── ollama-service.ts # Ollama API client
├── baml_src/
│   ├── agent.baml        # Agent prompts and types
│   ├── calculator.baml   # Calculator tool definitions
│   └── clients.baml      # Ollama client configuration
├── package.json
├── tsconfig.json
└── README.md
```

### Key Components

- **TwelveFactorAgent**: Core agent implementing all 12 factors
- **OllamaService**: Service for interacting with Ollama API
- **CLI**: Interactive command-line interface
- **BAML Configuration**: Structured prompts and client setup

## 🧪 Testing

The project includes type checking and build validation:

```bash
npm run build  # Type checking and compilation
npm run test   # Unit tests (if available)
```

## 🤝 Contributing

This demo is part of the 12-factor-agents project. Contributions are welcome!

1. Follow the existing code patterns
2. Maintain the 12-factor principles
3. Add appropriate error handling
4. Update documentation

## 📚 Learn More

- [12-Factor Agents Guide](https://github.com/humanlayer/12-factor-agents)
- [Ollama Documentation](https://ollama.ai/docs)
- [BAML Documentation](https://docs.boundaryml.com)

## 🐛 Troubleshooting

### Ollama Connection Issues

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama if not running
ollama serve

# Pull a model if none available
ollama pull llama3.1:8b
```

### Missing Models

```bash
# List installed models
ollama list

# Install recommended models
ollama pull llama3.1:8b
ollama pull mistral:7b
```

### TypeScript Errors

```bash
# Clean build
rm -rf dist/ baml_client/
npx baml-cli generate
npm run build
```