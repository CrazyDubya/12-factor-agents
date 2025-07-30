# Quick Start Guide - Git Workflow

## 🚀 Get Started in 5 Minutes

### 1. Understand the Branch Structure
```
main (production) ← staging ← develop ← feature/experiment branches
```

### 2. Create Your First Branch
```bash
# For a new feature
./scripts/create-branch.sh feature user-login "Add user authentication"

# For an experiment
./scripts/create-branch.sh experiment react-migration "Test React migration"

# For research
./scripts/create-branch.sh research performance-optimization "Study performance options"
```

### 3. Daily Workflow
```bash
# Start work
git checkout develop
git pull origin develop
git checkout -b feature/my-feature

# Make changes
git add .
git commit -m "feat: add new functionality"

# Push and create PR
git push origin feature/my-feature
# Create PR in your Git hosting service
```

### 4. Manage Branches
```bash
# Interactive cleanup
./scripts/branch-cleanup.sh

# Quick cleanup
./scripts/branch-cleanup.sh --cleanup-merged
```

## 📋 Branch Types Quick Reference

| Type | Purpose | Base Branch | Lifetime |
|------|---------|-------------|----------|
| `feature/` | New features | `develop` | Until merged |
| `experiment/` | Experimental work | `develop` | Variable |
| `research/` | Investigation | `develop` | Long-lived |
| `spike/` | Time-boxed study | `develop` | 1-2 weeks |
| `hotfix/` | Critical fixes | `main` | Until deployed |
| `release/` | Release prep | `develop` | Until released |

## 🔄 Merge Flow

1. **Feature** → `develop` → `staging` → `main`
2. **Hotfix** → `main` + `develop` + `staging`
3. **Experiment** → Convert to feature or delete

## 📚 Key Files

- `GIT_WORKFLOW.md` - Complete workflow documentation
- `CONTRIBUTING.md` - Contribution guidelines
- `scripts/create-branch.sh` - Create properly named branches
- `scripts/branch-cleanup.sh` - Manage and clean branches
- `scripts/git-setup.sh` - Initial repository setup

## 🎯 Next Steps

1. Read the full [Git Workflow](./GIT_WORKFLOW.md) documentation
2. Review [Contributing Guidelines](./CONTRIBUTING.md)
3. Set up your development environment
4. Create your first branch and start coding!

Happy coding! 🎉