#!/bin/bash

# =============================================================================
# Full Agent Comparison Test Suite
#
# Runs tests on multiple agentic systems and generates comparison reports
# =============================================================================

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}=================================${NC}"
echo -e "${CYAN}Full Agent Comparison Test Suite${NC}"
echo -e "${CYAN}=================================${NC}"
echo ""

# Check dependencies
echo -e "${BLUE}Checking dependencies...${NC}"
python3 --version > /dev/null 2>&1 || { echo "Error: Python 3 not found"; exit 1; }
ollama --version > /dev/null 2>&1 || { echo "Error: Ollama not found"; exit 1; }
echo -e "${GREEN}✓ Dependencies OK${NC}"
echo ""

# Select test mode
echo -e "${YELLOW}Select agents to test:${NC}"
echo "1. Quick Test (2 agents: Copilot CLI + qwen-128k) - ~2 hours"
echo "2. Recommended (4 agents: Copilot + 3 Ollama models) - ~4 hours"
echo "3. Comprehensive (6 agents: Copilot + 5 Ollama models) - ~6 hours"
echo "4. Ollama Only (3 models) - ~2 hours"
echo "5. Custom Selection"
echo ""
read -p "Enter choice (1-5): " CHOICE

case $CHOICE in
    1)
        echo -e "\n${GREEN}Quick Test Mode${NC}"
        AGENTS=("copilot" "qwen-128k")
        ;;
    2)
        echo -e "\n${GREEN}Recommended Mode${NC}"
        AGENTS=("copilot" "qwen-128k" "llama3.2:latest" "gemma2:9b")
        ;;
    3)
        echo -e "\n${GREEN}Comprehensive Mode${NC}"
        AGENTS=("copilot" "qwen-128k" "llama3.2:latest" "gemma2:9b" "mistral:7b" "qwen2.5:3b")
        ;;
    4)
        echo -e "\n${GREEN}Ollama Only Mode${NC}"
        AGENTS=("qwen-128k" "llama3.2:latest" "gemma2:9b")
        ;;
    5)
        echo -e "\n${YELLOW}Custom Selection${NC}"
        echo "Available agents:"
        echo "  - copilot (GitHub Copilot CLI)"
        echo "  - qwen-128k (long-context)"
        echo "  - llama3.2:latest (general purpose)"
        echo "  - gemma2:9b (balanced)"
        echo "  - mistral:7b (strong reasoning)"
        echo "  - qwen2.5:3b (small efficient)"
        echo ""
        read -p "Enter agent names (space-separated): " -a AGENTS
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo -e "${BLUE}Will test ${#AGENTS[@]} agents:${NC}"
for agent in "${AGENTS[@]}"; do
    echo "  - $agent"
done
echo ""

read -p "Continue? (y/n): " CONFIRM
if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

# Create results directory
mkdir -p test_results

# Test each agent
for agent in "${AGENTS[@]}"; do
    echo ""
    echo -e "${CYAN}=================================${NC}"
    echo -e "${CYAN}Testing: $agent${NC}"
    echo -e "${CYAN}=================================${NC}"
    echo ""

    if [ "$agent" == "copilot" ]; then
        echo -e "${YELLOW}INSTRUCTIONS FOR COPILOT CLI:${NC}"
        echo "1. Open a new terminal window"
        echo "2. Run: copilot"
        echo "3. Return here and press Enter to start the test framework"
        echo ""
        read -p "Press Enter when Copilot is ready..."

        python3 agent_tester.py --mode interactive --agent-name "GitHub-Copilot-CLI"
    else
        # Check if Ollama model is available
        if ! ollama list | grep -q "$agent"; then
            echo -e "${YELLOW}Model $agent not found locally.${NC}"
            read -p "Pull model now? (y/n): " PULL
            if [[ $PULL =~ ^[Yy]$ ]]; then
                ollama pull "$agent"
            else
                echo "Skipping $agent"
                continue
            fi
        fi

        python3 test_ollama_model.py --model "$agent" --agent-name "Ollama-$(echo $agent | sed 's/:/-/g')"
    fi

    echo ""
    echo -e "${GREEN}✓ Completed testing: $agent${NC}"
    echo ""
done

# Generate individual reports
echo ""
echo -e "${CYAN}=================================${NC}"
echo -e "${CYAN}Generating Individual Reports${NC}"
echo -e "${CYAN}=================================${NC}"
echo ""

for result_file in test_results/test_results_*.json; do
    if [ -f "$result_file" ]; then
        echo "Generating report for: $(basename $result_file)"
        python3 generate_report.py "$result_file"
    fi
done

# Generate comparison report
echo ""
echo -e "${CYAN}=================================${NC}"
echo -e "${CYAN}Generating Comparison Report${NC}"
echo -e "${CYAN}=================================${NC}"
echo ""

RESULT_FILES=(test_results/test_results_*.json)
if [ ${#RESULT_FILES[@]} -ge 2 ]; then
    python3 compare_agents.py test_results/test_results_*.json
    echo ""
    echo -e "${GREEN}✓ Comparison report generated${NC}"
else
    echo -e "${YELLOW}Not enough results for comparison (need at least 2)${NC}"
fi

# Summary
echo ""
echo -e "${CYAN}=================================${NC}"
echo -e "${CYAN}Testing Complete!${NC}"
echo -e "${CYAN}=================================${NC}"
echo ""
echo -e "${GREEN}Results:${NC}"
ls -lh test_results/*_report.html 2>/dev/null | awk '{print "  " $9}'
echo ""
echo -e "${BLUE}View reports:${NC}"
echo "  open test_results/comparison_report_*.html"
echo ""
echo -e "${GREEN}All done! 🎉${NC}"
