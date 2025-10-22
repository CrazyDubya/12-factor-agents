# Agentic Systems Test Matrix

## Testable CLI-Based Agents

| System | Type | CLI Tool | Test Capability | Notes |
|--------|------|----------|----------------|-------|
| **GitHub Copilot CLI** | Commercial | `copilot` | ✅ Full | Interactive agent with tools |
| **Ollama: qwen-128k** | Open Source | `ollama` | ✅ Text-only | Best long-context (128k tokens) |
| **Ollama: llama3.2** | Open Source | `ollama` | ✅ Text-only | Latest Llama, general purpose |
| **Ollama: gemma2:9b** | Open Source | `ollama` | ✅ Text-only | Balanced size/performance |
| **Ollama: mistral:7b** | Open Source | `ollama` | ✅ Text-only | Strong reasoning |
| **Ollama: qwen2.5:3b** | Open Source | `ollama` | ✅ Text-only | Efficient small model |
| **Claude Code CLI** | Commercial | `claude` | ⚠️ Self-test | Current system |

## GUI-Only Editors (Manual Testing Required)

| System | Version | AI Feature | Test Method |
|--------|---------|------------|-------------|
| **Cursor** | 1.7.28 | Cursor Tab, Chat | Manual GUI interaction |
| **Windsurf** | 1.99.3 | Cascade, Chat | Manual GUI interaction |

## Test Domain Capabilities Matrix

| Domain | Copilot CLI | Ollama Models | Notes |
|--------|-------------|---------------|-------|
| **Research** | ✅ Web search | ❌ No tools | Copilot has advantage |
| **Analysis** | ✅ Can read files | ❌ No file access | Copilot has advantage |
| **Content** | ✅ Full | ✅ Full | Both capable |
| **Planning** | ✅ Full | ✅ Full | Both capable |
| **Multi-Tool** | ✅ Full | ❌ No tools | Copilot only |
| **Reasoning** | ✅ Full | ✅ Full | Both capable |
| **Refusals** | ✅ Full | ✅ Full | Both have boundaries |
| **Communication** | ✅ Full | ✅ Full | Both capable |

## Testing Priority

### Phase 1: Tool-Capable Agents
1. **GitHub Copilot CLI** - Complete test suite (all 61 scenarios)
   - Can test: All domains including file operations and web search
   - Estimated time: 45-60 minutes

### Phase 2: Text-Only Models (Selected Scenarios)
2. **Ollama: qwen-128k** - Text-based scenarios (~40 tests)
   - Focus: Reasoning, content, communication, planning
   - Skip: File operations, web search, multi-tool
   - Estimated time: 30-40 minutes

3. **Ollama: llama3.2** - Text-based scenarios (~40 tests)
   - Same focus as qwen-128k
   - Estimated time: 30-40 minutes

4. **Ollama: gemma2:9b** - Text-based scenarios (~40 tests)
   - Same focus as qwen-128k
   - Estimated time: 30-40 minutes

### Phase 3: Optional Additional Models
5. **Ollama: mistral:7b** - If time permits
6. **Ollama: qwen2.5:3b** - Small model baseline
7. **Claude Code** - Self-testing experiment

## Test Execution Commands

### Copilot CLI Testing
```bash
# Full suite (interactive mode)
python agent_tester.py --mode interactive --agent-name "GitHub-Copilot-CLI"
```

### Ollama Model Testing
```bash
# Long-context champion
python test_ollama_model.py --model qwen-128k --agent-name "Ollama-Qwen-128k"

# General purpose
python test_ollama_model.py --model llama3.2:latest --agent-name "Ollama-Llama3.2"

# Balanced model
python test_ollama_model.py --model gemma2:9b --agent-name "Ollama-Gemma2-9b"

# Strong reasoning
python test_ollama_model.py --model mistral:7b --agent-name "Ollama-Mistral-7b"

# Small efficient
python test_ollama_model.py --model qwen2.5:3b --agent-name "Ollama-Qwen2.5-3b"
```

### Generate Comparison Report
```bash
# After testing multiple agents
python compare_agents.py test_results/test_results_*.json
```

## Comparison Dimensions

### Quantitative Metrics
- **Overall Success Rate** - Pass + (Partial × 0.5) / Total
- **Domain Performance** - Success rate by domain
- **Speed** - Average response time
- **Refusal Accuracy** - Appropriate refusals vs inappropriate ones

### Qualitative Assessment
- **Response Quality** - Depth, accuracy, clarity
- **Tool Usage** - Effectiveness of tool selection (Copilot only)
- **Boundary Recognition** - How well they handle edge cases
- **Communication Style** - Clarity, tone, structure

## Expected Strengths by Agent

### GitHub Copilot CLI
- ✅ Excellent tool integration
- ✅ Web search capabilities
- ✅ File operations
- ✅ Multi-step workflows
- ⚠️ May be less conversational

### Ollama: qwen-128k
- ✅ Exceptional long-context handling
- ✅ Strong Chinese-English bilingual
- ✅ Fast inference
- ❌ No tool use
- ❌ No web access

### Ollama: llama3.2
- ✅ Latest Meta model
- ✅ Balanced performance
- ✅ Good instruction following
- ❌ No tool use

### Ollama: gemma2:9b
- ✅ Excellent reasoning
- ✅ Code understanding
- ✅ Balanced size
- ❌ No tool use

## Results Organization

```
test_results/
├── test_results_copilot_TIMESTAMP.json
├── test_results_copilot_TIMESTAMP_report.html
├── test_results_qwen_128k_TIMESTAMP.json
├── test_results_qwen_128k_TIMESTAMP_report.html
├── test_results_llama3_2_TIMESTAMP.json
├── test_results_llama3_2_TIMESTAMP_report.html
├── test_results_gemma2_9b_TIMESTAMP.json
├── test_results_gemma2_9b_TIMESTAMP_report.html
└── comparison_report_TIMESTAMP.html  ← Multi-agent comparison
```

## Success Criteria

A comprehensive evaluation should include:
- [ ] At least 1 tool-capable agent (Copilot CLI)
- [ ] At least 2 text-only models (different sizes/architectures)
- [ ] Full domain coverage (all 8 domains tested)
- [ ] Refusal scenarios validated
- [ ] HTML reports generated for all agents
- [ ] Cross-agent comparison report created

## Time Investment

- **Minimal** (2 agents): ~2 hours
  - Copilot CLI + qwen-128k

- **Recommended** (4 agents): ~3-4 hours
  - Copilot CLI + qwen-128k + llama3.2 + gemma2:9b

- **Comprehensive** (6+ agents): ~5-6 hours
  - All above + mistral + qwen2.5:3b + additional testing

## Next Steps

1. **Start with Copilot CLI** - Most comprehensive testing
2. **Add Ollama models** - For text-only comparison
3. **Generate individual reports** - Understand each agent
4. **Run comparison analysis** - See relative strengths
5. **Document findings** - Use cases per agent
