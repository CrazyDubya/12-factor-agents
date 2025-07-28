#!/bin/bash

# Create Branch Script for Prison Project
# This script helps create properly named branches following our conventions

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "🌿 Branch Creation Tool"
    echo "======================"
    echo ""
    echo "Usage: $0 <type> <name> [description]"
    echo ""
    echo "Branch Types:"
    echo "  feature     - New features and enhancements"
    echo "  experiment  - Experimental implementations"
    echo "  research    - Research and proof of concepts"
    echo "  spike       - Time-boxed investigations"
    echo "  hotfix      - Critical production fixes"
    echo "  release     - Release preparation"
    echo ""
    echo "Examples:"
    echo "  $0 feature user-authentication"
    echo "  $0 experiment new-ui-framework"
    echo "  $0 research performance-optimization"
    echo "  $0 spike database-migration-strategy"
    echo "  $0 hotfix critical-security-patch"
    echo ""
}

# Function to create experiment documentation
create_experiment_docs() {
    local branch_name=$1
    local description=$2
    
    cat > "EXPERIMENT_${branch_name}.md" << EOF
# Experiment: ${branch_name}

## Overview
${description:-"Brief description of the experiment"}

## Goals
- [ ] Define specific, measurable goals
- [ ] List success criteria
- [ ] Identify failure conditions

## Timeline
- **Start Date**: $(date +%Y-%m-%d)
- **Expected Duration**: [Define timeline]
- **Review Date**: [Set review milestone]

## Hypothesis
[What do you expect to learn or achieve?]

## Approach
[Describe the experimental approach]

## Dependencies
- [ ] List any dependencies
- [ ] Identify potential blockers
- [ ] Note required resources

## Risks
- [ ] Technical risks
- [ ] Timeline risks
- [ ] Resource risks

## Success Metrics
- [ ] Define measurable success criteria
- [ ] Identify key performance indicators
- [ ] Set acceptance thresholds

## Progress Log
### $(date +%Y-%m-%d)
- Experiment started
- Initial setup completed

## Results
[Document findings as the experiment progresses]

## Conclusion
[Final assessment and recommendations]

## Next Steps
- [ ] Actions based on results
- [ ] Follow-up experiments
- [ ] Implementation plans
EOF

    print_success "Created experiment documentation: EXPERIMENT_${branch_name}.md"
}

# Function to create research documentation
create_research_docs() {
    local branch_name=$1
    local description=$2
    
    cat > "RESEARCH_${branch_name}.md" << EOF
# Research: ${branch_name}

## Research Question
${description:-"Define the research question or problem"}

## Background
[Provide context and background information]

## Objectives
- [ ] Primary research objectives
- [ ] Secondary objectives
- [ ] Learning goals

## Methodology
[Describe research approach and methods]

## Resources
- [ ] Documentation to review
- [ ] Tools to evaluate
- [ ] People to consult

## Timeline
- **Start Date**: $(date +%Y-%m-%d)
- **Milestones**: [Define key milestones]
- **Completion Target**: [Set target date]

## Findings
[Document discoveries and insights]

## Recommendations
[Based on research findings]

## References
[List sources and references]
EOF

    print_success "Created research documentation: RESEARCH_${branch_name}.md"
}

# Main script logic
if [ $# -lt 2 ]; then
    show_usage
    exit 1
fi

BRANCH_TYPE=$1
BRANCH_NAME=$2
DESCRIPTION=$3

# Validate branch type
case $BRANCH_TYPE in
    feature|experiment|research|spike|hotfix|release)
        ;;
    *)
        print_error "Invalid branch type: $BRANCH_TYPE"
        show_usage
        exit 1
        ;;
esac

# Validate branch name (no spaces, lowercase, hyphens allowed)
if [[ ! $BRANCH_NAME =~ ^[a-z0-9-]+$ ]]; then
    print_error "Invalid branch name. Use lowercase letters, numbers, and hyphens only."
    exit 1
fi

# Determine base branch
case $BRANCH_TYPE in
    hotfix)
        BASE_BRANCH="main"
        ;;
    *)
        BASE_BRANCH="develop"
        ;;
esac

# Create full branch name
FULL_BRANCH_NAME="${BRANCH_TYPE}/${BRANCH_NAME}"

print_status "Creating branch: $FULL_BRANCH_NAME"
print_status "Base branch: $BASE_BRANCH"

# Check if branch already exists
if git show-ref --verify --quiet refs/heads/$FULL_BRANCH_NAME; then
    print_error "Branch $FULL_BRANCH_NAME already exists!"
    exit 1
fi

# Switch to base branch and update
print_status "Switching to $BASE_BRANCH and updating..."
git checkout $BASE_BRANCH
git pull origin $BASE_BRANCH 2>/dev/null || print_warning "Could not pull from origin (remote may not exist)"

# Create new branch
print_status "Creating new branch: $FULL_BRANCH_NAME"
git checkout -b $FULL_BRANCH_NAME

# Create documentation for experimental branches
case $BRANCH_TYPE in
    experiment)
        create_experiment_docs $BRANCH_NAME "$DESCRIPTION"
        git add "EXPERIMENT_${BRANCH_NAME}.md"
        ;;
    research)
        create_research_docs $BRANCH_NAME "$DESCRIPTION"
        git add "RESEARCH_${BRANCH_NAME}.md"
        ;;
    spike)
        echo "# Spike: $BRANCH_NAME" > "SPIKE_${BRANCH_NAME}.md"
        echo "" >> "SPIKE_${BRANCH_NAME}.md"
        echo "**Investigation**: ${DESCRIPTION:-"Time-boxed investigation"}" >> "SPIKE_${BRANCH_NAME}.md"
        echo "**Start Date**: $(date +%Y-%m-%d)" >> "SPIKE_${BRANCH_NAME}.md"
        echo "**Time Box**: [Define time limit]" >> "SPIKE_${BRANCH_NAME}.md"
        echo "" >> "SPIKE_${BRANCH_NAME}.md"
        echo "## Questions to Answer" >> "SPIKE_${BRANCH_NAME}.md"
        echo "- [ ] [List specific questions]" >> "SPIKE_${BRANCH_NAME}.md"
        echo "" >> "SPIKE_${BRANCH_NAME}.md"
        echo "## Findings" >> "SPIKE_${BRANCH_NAME}.md"
        echo "[Document findings here]" >> "SPIKE_${BRANCH_NAME}.md"
        
        git add "SPIKE_${BRANCH_NAME}.md"
        print_success "Created spike documentation: SPIKE_${BRANCH_NAME}.md"
        ;;
esac

# Make initial commit if documentation was created
if git diff --cached --quiet; then
    print_success "Branch $FULL_BRANCH_NAME created successfully!"
else
    git commit -m "docs: Initialize ${BRANCH_TYPE} branch ${BRANCH_NAME}

${DESCRIPTION:+"Description: $DESCRIPTION"}"
    print_success "Branch $FULL_BRANCH_NAME created with initial documentation!"
fi

print_status "You are now on branch: $FULL_BRANCH_NAME"
print_status "Ready to start working!"

echo ""
echo "📋 Next steps:"
case $BRANCH_TYPE in
    experiment)
        echo "1. Fill out the experiment documentation in EXPERIMENT_${BRANCH_NAME}.md"
        echo "2. Define clear success/failure criteria"
        echo "3. Set up regular progress reviews"
        ;;
    research)
        echo "1. Complete the research documentation in RESEARCH_${BRANCH_NAME}.md"
        echo "2. Gather and review relevant resources"
        echo "3. Document findings as you progress"
        ;;
    spike)
        echo "1. Define specific questions in SPIKE_${BRANCH_NAME}.md"
        echo "2. Set a strict time limit for investigation"
        echo "3. Focus on answering key questions quickly"
        ;;
    feature)
        echo "1. Break down the feature into smaller tasks"
        echo "2. Write tests for the new functionality"
        echo "3. Implement the feature incrementally"
        ;;
    hotfix)
        echo "1. Identify and fix the critical issue"
        echo "2. Test the fix thoroughly"
        echo "3. Prepare for immediate deployment"
        ;;
esac

echo ""
echo "🔄 When ready to merge:"
echo "  git checkout $BASE_BRANCH"
echo "  git pull origin $BASE_BRANCH"
echo "  git checkout $FULL_BRANCH_NAME"
echo "  git rebase $BASE_BRANCH"
echo "  # Create pull request to merge into $BASE_BRANCH"