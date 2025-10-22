# Testing Guide for Agentic Systems

This guide walks you through testing the agentic systems found on your Mac.

## Found Systems

### 1. GitHub Copilot CLI (v0.0.334)
**Location:** `/opt/homebrew/bin/copilot`
**Capabilities:** Interactive AI assistant with tools (file operations, web search, commands)

### 2. Ollama (v0.11.0)
**Location:** `/opt/homebrew/bin/ollama`
**Models installed:** 23 models including:
- Long-context: `qwen-128k`, `llama32-long`, `gemma2-32k`, `mistral-32k`, `llama3-32k`
- General: `llama3.2:latest`, `gemma2:9b`, `mistral:7b`
- Small: `qwen2.5` series, `smollm2` series

### 3. Toastie Story Generation Agents
**Location:** `~/toastie/agents/`
**Agent Types:** Architect, Character, World, Tension, Polish

### 4. Thespian Agent System
**Location:** `~/thespian/`
**Type:** Agent collaboration framework

---

## Phase 1: Testing GitHub Copilot CLI

### Step 1: Start Copilot in Interactive Mode

Open a new terminal window and start Copilot:

```bash
cd ~/nocode
copilot
```

### Step 2: Run the Test Framework

In your main terminal (with Claude Code), run:

```bash
python agent_tester.py --mode interactive --agent-name "GitHub-Copilot-CLI"
```

### Step 3: Test Execution Process

For each test scenario:

1. **Read the test prompt** displayed by the framework
2. **Switch to Copilot terminal** and paste/ask the exact prompt
3. **Copy Copilot's response** to a text file or note
4. **Return to test framework** and press Enter
5. **Evaluate the response** based on the criteria shown
6. **Add notes** about tool usage, quality, any issues

### Key Areas to Focus On

**Research Tests** - Does Copilot:
- Use web search effectively?
- Verify information from multiple sources?
- Cite sources properly?

**Analysis Tests** - Does Copilot:
- Read and parse CSV/JSON files correctly?
- Perform accurate calculations?
- Identify patterns and insights?

**Refusal Tests** - Does Copilot:
- Refuse to handle PII appropriately?
- Recognize security concerns?
- Maintain ethical boundaries?

**Multi-Tool Tests** - Does Copilot:
- Chain tools effectively?
- Handle errors gracefully?
- Complete complex workflows?

### Tips for Testing Copilot

1. **Let it use tools** - Allow file operations and commands when safe
2. **Note tool choices** - Document which tools it selects for each task
3. **Test boundaries** - Pay attention to refusal scenarios
4. **Capture exact responses** - For accurate evaluation

---

## Phase 2: Testing Ollama Models

We've created a helper script to test Ollama models through the framework.

### Step 1: Test a Single Model

```bash
python test_ollama_model.py --model qwen-128k --agent-name "Ollama-Qwen-128k"
```

### Step 2: Test Multiple Models

Test the recommended set:

```bash
# Long-context champion
python test_ollama_model.py --model qwen-128k --agent-name "Ollama-Qwen-128k"

# General purpose
python test_ollama_model.py --model llama3.2:latest --agent-name "Ollama-Llama3.2"

# Balanced model
python test_ollama_model.py --model gemma2:9b --agent-name "Ollama-Gemma2-9b"
```

### Ollama Testing Notes

- Ollama models respond directly without tool use
- Focus on: reasoning, content creation, communication
- Best for: text-based tasks, not file operations
- Expect: No web search, no file reading capabilities

---

## Phase 3: Generate Reports

After testing each system:

```bash
# Generate individual reports
python generate_report.py test_results/test_results_copilot_*.json
python generate_report.py test_results/test_results_qwen_*.json
python generate_report.py test_results/test_results_llama_*.json
```

### View Reports

```bash
# Open reports in browser
open test_results/*_report.html
```

---

## Comparison Checklist

When evaluating multiple agents, track:

- [ ] **Research Quality** - Which finds best information?
- [ ] **Analysis Accuracy** - Which does calculations correctly?
- [ ] **Content Quality** - Which writes most clearly?
- [ ] **Tool Usage** - Which uses tools most effectively?
- [ ] **Refusal Appropriateness** - Which has best boundaries?
- [ ] **Communication** - Which explains most clearly?
- [ ] **Speed** - Which responds fastest?
- [ ] **Consistency** - Which is most reliable?

---

## Quick Commands Reference

```bash
# List test domains
python agent_tester.py --list-domains

# Test specific domain only
python agent_tester.py --domain research --agent-name "MyAgent"

# Run in automated mode (for Ollama models)
python agent_tester.py --mode automated --agent-name "MyAgent"

# Generate report
python generate_report.py test_results/your_results.json

# View Ollama models
ollama list
```

---

## Expected Test Duration

- **Full test suite**: ~45-60 minutes per agent (interactive mode)
- **Single domain**: ~10-15 minutes per agent
- **Automated mode**: ~20-30 minutes per agent (Ollama only)

---

## Troubleshooting

**Copilot won't start:**
```bash
# Check if authenticated
copilot auth status
```

**Ollama model not found:**
```bash
# Pull the model first
ollama pull qwen-128k
```

**Test framework issues:**
```bash
# Verify dependencies
pip install pyyaml

# Check test scenarios loaded
python agent_tester.py --list-domains
```

---

## Results Organization

Your test results will be saved as:

```
test_results/
├── test_results_copilot_TIMESTAMP.json
├── test_results_copilot_TIMESTAMP_report.html
├── test_results_qwen_TIMESTAMP.json
├── test_results_qwen_TIMESTAMP_report.html
└── ... (more results and reports)
```

---

## Next Steps After Testing

1. **Review HTML Reports** - Visual insights into each agent
2. **Compare Capability Matrices** - See strengths/weaknesses
3. **Document Use Cases** - Which agent for which tasks
4. **Share Findings** - Create summary comparison document

Happy testing! 🧪
