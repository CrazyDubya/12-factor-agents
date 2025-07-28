# Contributing to Prison Project

Thank you for your interest in contributing to the Prison Project! This document provides guidelines and instructions for contributing to this repository.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Branch Management](#branch-management)
- [Code Standards](#code-standards)
- [Pull Request Process](#pull-request-process)
- [Experimental Work](#experimental-work)
- [Testing](#testing)
- [Documentation](#documentation)

## Getting Started

### Prerequisites

1. Git installed and configured
2. Access to the repository
3. Understanding of our [Git Workflow](./GIT_WORKFLOW.md)

### Initial Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd prison
   ```

2. Run the setup script:
   ```bash
   ./scripts/git-setup.sh
   ```

3. Familiarize yourself with the project structure and documentation

## Development Workflow

### 1. Choose Your Work Type

- **Feature Development**: New functionality or enhancements
- **Bug Fixes**: Fixing existing issues
- **Experimental Work**: Research, prototypes, or proof of concepts
- **Hotfixes**: Critical production issues

### 2. Create a Branch

Use our branch creation script:

```bash
# For features
./scripts/create-branch.sh feature my-new-feature "Description of the feature"

# For experiments
./scripts/create-branch.sh experiment new-approach "Testing a new approach"

# For research
./scripts/create-branch.sh research performance-study "Investigating performance options"

# For hotfixes
./scripts/create-branch.sh hotfix critical-bug "Fix critical security issue"
```

### 3. Development Process

1. **Write Tests First** (when applicable)
   - Unit tests for new functionality
   - Integration tests for complex features
   - Update existing tests as needed

2. **Implement Changes**
   - Follow coding standards
   - Make small, focused commits
   - Write clear commit messages

3. **Document Your Work**
   - Update relevant documentation
   - Add inline comments for complex logic
   - Update README if needed

## Branch Management

### Branch Types and Naming

- `feature/description` - New features
- `experiment/description` - Experimental work
- `research/topic` - Research and investigation
- `spike/investigation` - Time-boxed spikes
- `hotfix/description` - Critical fixes
- `release/version` - Release preparation

### Branch Lifecycle

1. **Creation**: Branch from appropriate base (`develop` or `main`)
2. **Development**: Regular commits with clear messages
3. **Testing**: Ensure all tests pass
4. **Review**: Create pull request for code review
5. **Integration**: Merge into target branch
6. **Cleanup**: Delete branch after successful merge

## Code Standards

### Commit Messages

Use conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Maintenance tasks

Examples:
```
feat(auth): add user authentication system
fix(api): resolve timeout issue in user endpoint
docs(readme): update installation instructions
```

### Code Style

- Follow language-specific style guides
- Use consistent indentation (spaces vs tabs)
- Write self-documenting code
- Add comments for complex logic
- Keep functions small and focused

## Pull Request Process

### Before Creating a PR

1. **Update Your Branch**:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout your-branch
   git rebase develop
   ```

2. **Run Tests**:
   ```bash
   # Run your test suite
   npm test  # or appropriate test command
   ```

3. **Check Code Quality**:
   ```bash
   # Run linting and formatting
   npm run lint  # or appropriate lint command
   ```

### Creating a Pull Request

1. **Title**: Clear, descriptive title
2. **Description**: Include:
   - What changes were made
   - Why the changes were necessary
   - How to test the changes
   - Any breaking changes
   - Screenshots (if UI changes)

3. **Reviewers**: Assign appropriate reviewers
4. **Labels**: Add relevant labels
5. **Linked Issues**: Reference related issues

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update
- [ ] Experimental work

## Testing
- [ ] Tests pass locally
- [ ] New tests added (if applicable)
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No merge conflicts
```

## Experimental Work

### Guidelines for Experiments

1. **Documentation**: Always create experiment documentation
2. **Time Boxing**: Set clear time limits
3. **Success Criteria**: Define measurable goals
4. **Regular Reviews**: Schedule progress check-ins
5. **Knowledge Sharing**: Document learnings

### Experiment Lifecycle

1. **Planning**: Define hypothesis and approach
2. **Implementation**: Build and test
3. **Evaluation**: Assess against success criteria
4. **Decision**: Continue, pivot, or abandon
5. **Documentation**: Record learnings and outcomes

### Converting Experiments

Successful experiments can be converted to feature branches:

```bash
# Create feature branch from experiment
git checkout experiment/my-experiment
git checkout -b feature/my-feature
# Clean up experimental code and documentation
# Follow standard feature development process
```

## Testing

### Test Types

1. **Unit Tests**: Test individual components
2. **Integration Tests**: Test component interactions
3. **End-to-End Tests**: Test complete user workflows
4. **Performance Tests**: Test system performance
5. **Security Tests**: Test for vulnerabilities

### Test Guidelines

- Write tests before implementing features (TDD)
- Maintain high test coverage
- Test both happy path and edge cases
- Use descriptive test names
- Keep tests independent and isolated

## Documentation

### Required Documentation

1. **Code Comments**: For complex logic
2. **API Documentation**: For public interfaces
3. **README Updates**: For new features
4. **Architecture Docs**: For significant changes
5. **Experiment Docs**: For experimental work

### Documentation Standards

- Use clear, concise language
- Include examples where helpful
- Keep documentation up to date
- Use consistent formatting
- Link related documentation

## Getting Help

### Resources

- [Git Workflow Documentation](./GIT_WORKFLOW.md)
- Project README
- Team chat channels
- Code review comments

### Asking Questions

1. **Check Documentation**: Review existing docs first
2. **Search Issues**: Look for similar questions
3. **Ask in Chat**: For quick questions
4. **Create Issue**: For complex problems
5. **Schedule Meeting**: For architectural discussions

## Branch Cleanup

Regular cleanup helps maintain a healthy repository:

```bash
# Interactive cleanup tool
./scripts/branch-cleanup.sh

# Command line options
./scripts/branch-cleanup.sh --cleanup-merged
./scripts/branch-cleanup.sh --cleanup-stale
./scripts/branch-cleanup.sh --full-cleanup
```

## Release Process

### Preparing a Release

1. Create release branch from `develop`
2. Update version numbers
3. Update changelog
4. Final testing and bug fixes
5. Merge to `main` and `develop`
6. Tag the release
7. Deploy to production

### Hotfix Process

1. Create hotfix branch from `main`
2. Implement fix
3. Test thoroughly
4. Merge to `main`, `staging`, and `develop`
5. Deploy immediately
6. Monitor for issues

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow
- Follow project guidelines
- Communicate clearly and professionally

## Questions?

If you have questions about contributing, please:

1. Check this documentation
2. Review the [Git Workflow](./GIT_WORKFLOW.md)
3. Ask in team chat
4. Create an issue for process improvements

Thank you for contributing to the Prison Project! 🚀