#!/bin/bash

# Git Setup Script for Prison Project
# This script sets up the complete Git workflow with all necessary branches and configurations

set -e

echo "🚀 Setting up Git workflow for Prison Project..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    print_error "Not in a Git repository. Please run 'git init' first."
    exit 1
fi

print_status "Checking current Git configuration..."

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)
print_status "Current branch: $CURRENT_BRANCH"

# Create core branches if they don't exist
print_status "Setting up core branches..."

# Ensure we're on main branch
if [ "$CURRENT_BRANCH" != "main" ]; then
    print_status "Switching to main branch..."
    git checkout main 2>/dev/null || {
        print_warning "Main branch doesn't exist, creating it..."
        git checkout -b main
    }
fi

# Create develop branch
if ! git show-ref --verify --quiet refs/heads/develop; then
    print_status "Creating develop branch..."
    git checkout -b develop
    git checkout main
    print_success "Created develop branch"
else
    print_success "Develop branch already exists"
fi

# Create staging branch
if ! git show-ref --verify --quiet refs/heads/staging; then
    print_status "Creating staging branch..."
    git checkout -b staging
    git checkout main
    print_success "Created staging branch"
else
    print_success "Staging branch already exists"
fi

# Set up branch tracking
print_status "Setting up branch tracking..."

# Check if origin remote exists
if git remote | grep -q "^origin$"; then
    print_status "Setting up remote tracking branches..."
    
    # Push all branches to origin if they don't exist remotely
    for branch in main develop staging; do
        if ! git ls-remote --heads origin $branch | grep -q $branch; then
            print_status "Pushing $branch to origin..."
            git push -u origin $branch
        else
            print_success "Remote $branch already exists"
        fi
    done
else
    print_warning "No 'origin' remote found. You'll need to add a remote and push branches manually."
    print_status "To add a remote: git remote add origin <repository-url>"
fi

# Set up Git configuration for the project
print_status "Setting up Git configuration..."

# Set up merge strategy
git config merge.ours.driver true

# Set up pull strategy
git config pull.rebase false

# Set up default push behavior
git config push.default simple

print_success "Git configuration updated"

# Create initial commit if repository is empty
if [ $(git rev-list --all --count) -eq 0 ]; then
    print_status "Repository is empty, creating initial commit..."
    git add .
    git commit -m "Initial commit: Set up project structure and Git workflow"
    print_success "Created initial commit"
fi

# Display branch structure
print_status "Current branch structure:"
git branch -a

print_success "Git workflow setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Review the GIT_WORKFLOW.md file for detailed workflow instructions"
echo "2. Set up branch protection rules in your Git hosting service"
echo "3. Configure CI/CD pipelines for automated testing and deployment"
echo "4. Start developing by creating feature branches from 'develop'"
echo ""
echo "🌟 Quick commands to get started:"
echo "  Create a feature branch:     git checkout develop && git checkout -b feature/my-feature"
echo "  Create an experiment branch: git checkout develop && git checkout -b experiment/my-experiment"
echo "  Create a hotfix branch:      git checkout main && git checkout -b hotfix/urgent-fix"