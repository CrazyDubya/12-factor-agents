# AutoGen Installation Guide for Eternal Lockdown

## Quick Installation

```bash
# Install AutoGen
pip install pyautogen

# Or with all optional dependencies
pip install "pyautogen[teachable,lmm,graph]"
```

## Detailed Setup

### 1. Install AutoGen

```bash
# Basic installation
pip install pyautogen>=0.2.0

# With additional features
pip install pyautogen[teachable]  # For teachable agents
pip install pyautogen[lmm]        # For large multimodal models
pip install pyautogen[graph]      # For graph-based conversations
```

### 2. Verify Installation

```python
import autogen
print(f"AutoGen version: {autogen.__version__}")
```

### 3. Configure for Ollama

AutoGen works with Ollama through OpenAI-compatible API:

```python
llm_config = {
    "config_list": [{
        "model": "llama2:latest",
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama",  # Dummy key for Ollama
        "api_type": "openai"
    }],
    "temperature": 0.7,
    "timeout": 120,
}
```

### 4. Test Configuration

```python
import autogen

# Create test agent
agent = autogen.ConversableAgent(
    name="TestAgent",
    system_message="You are a helpful assistant.",
    llm_config=llm_config,
    human_input_mode="NEVER"
)

# Test response
response = agent.generate_reply(
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response)
```

## Common Issues and Solutions

### Issue: "No module named 'autogen'"
**Solution**: Install AutoGen
```bash
pip install pyautogen
```

### Issue: "Connection refused to localhost:11434"
**Solution**: Start Ollama server
```bash
ollama serve
```

### Issue: "Model not found"
**Solution**: Pull the required model
```bash
ollama pull llama2
```

### Issue: "API key required"
**Solution**: Use dummy key for Ollama
```python
"api_key": "ollama"  # Any string works for Ollama
```

## Advanced Configuration

### Multiple Models
```python
llm_config = {
    "config_list": [
        {
            "model": "llama2:latest",
            "base_url": "http://localhost:11434/v1",
            "api_key": "ollama"
        },
        {
            "model": "llama3:latest", 
            "base_url": "http://localhost:11434/v1",
            "api_key": "ollama"
        }
    ],
    "temperature": 0.7
}
```

### Custom Timeout and Retries
```python
llm_config = {
    "config_list": [...],
    "timeout": 300,        # 5 minutes
    "retry_wait_time": 10, # Wait 10 seconds between retries
    "max_retries": 3       # Retry up to 3 times
}
```

### Caching Responses
```python
llm_config = {
    "config_list": [...],
    "cache_seed": 42,      # Enable caching with seed
    "temperature": 0       # Use 0 temperature for consistent caching
}
```

## Integration with Eternal Lockdown

### 1. Import Prison Agents
```python
from autogen_integration.autogen_prison_agents import (
    PrisonInmateAgent, 
    PrisonGuardAgent, 
    WardenAgent
)
```

### 2. Create Prison Scenario
```python
# Create agents
inmate = PrisonInmateAgent(
    name="Marcus Johnson",
    crime_type="Drug possession",
    sentence_length="5 years"
)

guard = PrisonGuardAgent(
    name="Officer Martinez",
    rank="Correctional Officer II",
    years_experience=8
)

# Start conversation
result = inmate.initiate_chat(
    guard,
    message="Officer, I'd like to ask about the GED program."
)
```

### 3. Run Scenarios
```python
from autogen_integration.prison_scenarios import scenario_manager

# List available scenarios
scenarios = scenario_manager.list_scenarios()
print(scenarios)

# Run specific scenario
result = scenario_manager.run_scenario("education_inquiry")
```

## Performance Tips

1. **Use appropriate models**: Smaller models (7B) for simple conversations, larger models (13B+) for complex scenarios
2. **Adjust temperature**: Lower (0.3-0.7) for consistent responses, higher (0.8-1.0) for creative conversations
3. **Set reasonable timeouts**: 60-120 seconds for most conversations
4. **Enable caching**: For repeated scenarios or testing
5. **Limit conversation rounds**: Use `max_consecutive_auto_reply` to prevent infinite loops

## Troubleshooting

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Ollama Status
```bash
curl http://localhost:11434/api/tags
```

### Test Ollama API
```bash
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama2:latest",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

## Resources

- [AutoGen Documentation](https://microsoft.github.io/autogen/)
- [AutoGen GitHub](https://github.com/microsoft/autogen)
- [Ollama Documentation](https://ollama.ai/docs)
- [OpenAI API Compatibility](https://platform.openai.com/docs/api-reference)