#!/bin/bash

# Branch Cleanup Script for Prison Project
# This script helps manage and clean up experimental and feature branches

set -e

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

# Function to get branch age in days
get_branch_age() {
    local branch=$1
    local last_commit_date=$(git log -1 --format=%ct $branch 2>/dev/null || echo "0")
    local current_date=$(date +%s)
    local age_seconds=$((current_date - last_commit_date))
    local age_days=$((age_seconds / 86400))
    echo $age_days
}

# Function to check if branch is merged
is_branch_merged() {
    local branch=$1
    local target=${2:-develop}
    git merge-base --is-ancestor $branch $target 2>/dev/null
}

# Function to list experimental branches
list_experimental_branches() {
    echo "🔬 Experimental Branches:"
    echo "========================="
    
    local found_experimental=false
    
    for branch in $(git branch | grep -E "(experiment|research|spike)/" | sed 's/^[* ] //'); do
        found_experimental=true
        local age=$(get_branch_age $branch)
        local status="Active"
        
        if [ $age -gt 90 ]; then
            status="${RED}Stale (${age} days)${NC}"
        elif [ $age -gt 60 ]; then
            status="${YELLOW}Old (${age} days)${NC}"
        elif [ $age -gt 30 ]; then
            status="${BLUE}Aging (${age} days)${NC}"
        else
            status="${GREEN}Recent (${age} days)${NC}"
        fi
        
        echo -e "  📋 $branch - $status"
    done
    
    if [ "$found_experimental" = false ]; then
        echo "  No experimental branches found."
    fi
    echo ""
}

# Function to list feature branches
list_feature_branches() {
    echo "🚀 Feature Branches:"
    echo "==================="
    
    local found_features=false
    
    for branch in $(git branch | grep "feature/" | sed 's/^[* ] //'); do
        found_features=true
        local age=$(get_branch_age $branch)
        local merged_status=""
        
        if is_branch_merged $branch develop; then
            merged_status="${GREEN}[MERGED]${NC}"
        else
            merged_status="${YELLOW}[UNMERGED]${NC}"
        fi
        
        echo -e "  🌟 $branch - ${age} days old $merged_status"
    done
    
    if [ "$found_features" = false ]; then
        echo "  No feature branches found."
    fi
    echo ""
}

# Function to clean up merged branches
cleanup_merged_branches() {
    print_status "Cleaning up merged feature branches..."
    
    local cleaned=false
    
    for branch in $(git branch --merged develop | grep -v -E "(main|develop|staging|\*)" | sed 's/^[* ] //'); do
        if [[ $branch == feature/* ]]; then
            print_status "Deleting merged feature branch: $branch"
            git branch -d $branch
            cleaned=true
        fi
    done
    
    if [ "$cleaned" = false ]; then
        print_success "No merged feature branches to clean up."
    else
        print_success "Cleaned up merged feature branches."
    fi
}

# Function to clean up stale experimental branches
cleanup_stale_experimental() {
    print_status "Checking for stale experimental branches (90+ days old)..."
    
    local found_stale=false
    
    for branch in $(git branch | grep -E "(experiment|research|spike)/" | sed 's/^[* ] //'); do
        local age=$(get_branch_age $branch)
        
        if [ $age -gt 90 ]; then
            found_stale=true
            print_warning "Stale experimental branch found: $branch (${age} days old)"
            
            read -p "Delete this branch? [y/N]: " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                git branch -D $branch
                print_success "Deleted $branch"
            else
                print_status "Kept $branch"
            fi
        fi
    done
    
    if [ "$found_stale" = false ]; then
        print_success "No stale experimental branches found."
    fi
}

# Function to prune remote tracking branches
prune_remote_branches() {
    print_status "Pruning remote tracking branches..."
    
    if git remote | grep -q "^origin$"; then
        git remote prune origin
        print_success "Pruned remote tracking branches."
    else
        print_warning "No 'origin' remote found to prune."
    fi
}

# Function to show branch statistics
show_branch_stats() {
    echo "📊 Branch Statistics:"
    echo "===================="
    
    local total_branches=$(git branch | wc -l | tr -d ' ')
    local feature_count=$(git branch | grep -c "feature/" || echo "0")
    local experiment_count=$(git branch | grep -c -E "(experiment|research|spike)/" || echo "0")
    local hotfix_count=$(git branch | grep -c "hotfix/" || echo "0")
    
    echo "  Total branches: $total_branches"
    echo "  Feature branches: $feature_count"
    echo "  Experimental branches: $experiment_count"
    echo "  Hotfix branches: $hotfix_count"
    echo ""
}

# Main menu
show_menu() {
    echo "🧹 Git Branch Cleanup Tool"
    echo "=========================="
    echo ""
    echo "1. List all experimental branches"
    echo "2. List all feature branches"
    echo "3. Show branch statistics"
    echo "4. Clean up merged feature branches"
    echo "5. Clean up stale experimental branches (90+ days)"
    echo "6. Prune remote tracking branches"
    echo "7. Full cleanup (merged features + stale experiments + prune)"
    echo "8. Exit"
    echo ""
}

# Main script logic
if [ $# -eq 0 ]; then
    # Interactive mode
    while true; do
        show_menu
        read -p "Choose an option [1-8]: " choice
        echo ""
        
        case $choice in
            1)
                list_experimental_branches
                ;;
            2)
                list_feature_branches
                ;;
            3)
                show_branch_stats
                ;;
            4)
                cleanup_merged_branches
                ;;
            5)
                cleanup_stale_experimental
                ;;
            6)
                prune_remote_branches
                ;;
            7)
                cleanup_merged_branches
                cleanup_stale_experimental
                prune_remote_branches
                print_success "Full cleanup completed!"
                ;;
            8)
                print_success "Goodbye!"
                exit 0
                ;;
            *)
                print_error "Invalid option. Please choose 1-8."
                ;;
        esac
        
        echo ""
        read -p "Press Enter to continue..."
        echo ""
    done
else
    # Command line mode
    case $1 in
        --list-experimental)
            list_experimental_branches
            ;;
        --list-features)
            list_feature_branches
            ;;
        --stats)
            show_branch_stats
            ;;
        --cleanup-merged)
            cleanup_merged_branches
            ;;
        --cleanup-stale)
            cleanup_stale_experimental
            ;;
        --prune)
            prune_remote_branches
            ;;
        --full-cleanup)
            cleanup_merged_branches
            cleanup_stale_experimental
            prune_remote_branches
            ;;
        --help)
            echo "Usage: $0 [option]"
            echo ""
            echo "Options:"
            echo "  --list-experimental  List all experimental branches"
            echo "  --list-features      List all feature branches"
            echo "  --stats              Show branch statistics"
            echo "  --cleanup-merged     Clean up merged feature branches"
            echo "  --cleanup-stale      Clean up stale experimental branches"
            echo "  --prune              Prune remote tracking branches"
            echo "  --full-cleanup       Perform full cleanup"
            echo "  --help               Show this help message"
            echo ""
            echo "Run without arguments for interactive mode."
            ;;
        *)
            print_error "Unknown option: $1"
            print_status "Use --help for usage information."
            exit 1
            ;;
    esac
fi