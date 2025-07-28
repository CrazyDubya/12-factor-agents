# Git Workflow and Branching Strategy

## Overview

This project uses a Git Flow-inspired branching strategy with dedicated branches for different environments and clear guidelines for experimental work.

## Core Branches

### 1. Production Branch (`main`)
- **Purpose**: Production-ready code
- **Protection**: Protected branch, requires PR reviews
- **Deployment**: Automatically deploys to production
- **Merges from**: `staging` branch only
- **Direct commits**: Not allowed

### 2. Staging Branch (`staging`)
- **Purpose**: Pre-production testing and validation
- **Protection**: Protected branch, requires PR reviews
- **Deployment**: Automatically deploys to staging environment
- **Merges from**: `develop` branch and hotfix branches
- **Testing**: Full integration and user acceptance testing

### 3. Development Branch (`develop`)
- **Purpose**: Integration branch for ongoing development
- **Protection**: Semi-protected, requires PR reviews
- **Merges from**: Feature branches, experimental branches
- **Testing**: Continuous integration testing

## Supporting Branches

### Feature Branches
- **Naming**: `feature/description` or `feature/ticket-number`
- **Purpose**: New features and enhancements
- **Branched from**: `develop`
- **Merged to**: `develop`
- **Lifetime**: Until feature is complete

### Hotfix Branches
- **Naming**: `hotfix/description` or `hotfix/ticket-number`
- **Purpose**: Critical production fixes
- **Branched from**: `main`
- **Merged to**: `main` and `develop` (and `staging` if needed)
- **Lifetime**: Until fix is deployed

### Release Branches
- **Naming**: `release/version-number`
- **Purpose**: Prepare releases, final testing, and bug fixes
- **Branched from**: `develop`
- **Merged to**: `main` and `develop`
- **Lifetime**: Until release is complete

## Experimental Branch Management

### Experimental Branch Types

#### 1. Research Branches (`research/`)
- **Naming**: `research/topic-name`
- **Purpose**: Proof of concepts, technology evaluation
- **Branched from**: `develop` or specific feature branch
- **Lifetime**: Variable, can be long-lived
- **Cleanup**: Regular review and cleanup of stale branches

#### 2. Spike Branches (`spike/`)
- **Naming**: `spike/investigation-topic`
- **Purpose**: Time-boxed investigations and prototypes
- **Branched from**: `develop`
- **Lifetime**: Short-lived (1-2 weeks max)
- **Cleanup**: Automatic cleanup after spike completion

#### 3. Experimental Feature Branches (`experiment/`)
- **Naming**: `experiment/feature-name`
- **Purpose**: Experimental implementations of features
- **Branched from**: `develop`
- **Lifetime**: Until experiment conclusion
- **Cleanup**: Convert to feature branch or delete

### Experimental Branch Guidelines

1. **Documentation**: All experimental branches must have a README explaining:
   - Purpose and goals
   - Expected timeline
   - Success/failure criteria
   - Dependencies and risks

2. **Regular Reviews**: Weekly review of experimental branches:
   - Progress assessment
   - Decision on continuation
   - Cleanup of abandoned experiments

3. **Branch Naming Convention**:
   ```
   experiment/[type]-[description]
   research/[topic]-[focus-area]
   spike/[investigation-name]
   ```

4. **Merge Strategy**:
   - Successful experiments → Convert to feature branch
   - Failed experiments → Document learnings, then delete
   - Partial success → Extract useful parts to feature branches

## Workflow Procedures

### Starting New Work

1. **Feature Development**:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/new-feature-name
   ```

2. **Experimental Work**:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b experiment/new-experiment-name
   # Create experiment documentation
   echo "# Experiment: New Experiment Name" > EXPERIMENT.md
   ```

3. **Hotfix**:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b hotfix/critical-fix
   ```

### Merging and Integration

1. **Feature to Develop**:
   ```bash
   # Create PR from feature branch to develop
   # After approval and CI passes:
   git checkout develop
   git merge --no-ff feature/feature-name
   git branch -d feature/feature-name
   ```

2. **Develop to Staging**:
   ```bash
   # Create PR from develop to staging
   # After approval:
   git checkout staging
   git merge --no-ff develop
   ```

3. **Staging to Main**:
   ```bash
   # Create PR from staging to main
   # After approval and testing:
   git checkout main
   git merge --no-ff staging
   git tag -a v1.0.0 -m "Release version 1.0.0"
   ```

## Branch Protection Rules

### Main Branch
- Require PR reviews (2 reviewers)
- Require status checks to pass
- Require branches to be up to date
- Restrict pushes to administrators only
- Require signed commits

### Staging Branch
- Require PR reviews (1 reviewer)
- Require status checks to pass
- Require branches to be up to date

### Develop Branch
- Require PR reviews (1 reviewer)
- Require status checks to pass

## Cleanup and Maintenance

### Regular Cleanup Tasks

1. **Weekly Branch Review**:
   ```bash
   # List all experimental branches
   git branch -r | grep -E "(experiment|research|spike)/"
   
   # Review each branch for:
   # - Last commit date
   # - Progress status
   # - Continued relevance
   ```

2. **Monthly Cleanup**:
   ```bash
   # Delete merged feature branches
   git branch --merged develop | grep -v develop | xargs -n 1 git branch -d
   
   # Delete remote tracking branches for deleted remotes
   git remote prune origin
   ```

3. **Quarterly Review**:
   - Review all experimental branches
   - Document learnings from completed experiments
   - Archive or delete stale research branches

### Automated Cleanup

Set up automated cleanup for:
- Merged feature branches (delete after 30 days)
- Stale experimental branches (notify after 60 days, delete after 90 days)
- Old release branches (archive after 6 months)

## Environment Management

### Development Environment
- **Branch**: `develop`
- **Auto-deploy**: On push to develop
- **Testing**: Unit tests, integration tests
- **Database**: Development database with test data

### Staging Environment
- **Branch**: `staging`
- **Auto-deploy**: On push to staging
- **Testing**: Full test suite, performance tests, security scans
- **Database**: Production-like data (anonymized)

### Production Environment
- **Branch**: `main`
- **Deploy**: Manual trigger after staging validation
- **Testing**: Smoke tests, monitoring
- **Database**: Production database

## Emergency Procedures

### Critical Production Issue
1. Create hotfix branch from `main`
2. Implement fix
3. Test in staging environment
4. Deploy to production
5. Merge back to `develop` and `staging`

### Rollback Procedure
1. Identify last known good commit
2. Create rollback branch
3. Deploy rollback
4. Investigate and fix root cause

## Tools and Automation

### Recommended Tools
- **CI/CD**: GitHub Actions, GitLab CI, or Jenkins
- **Code Review**: GitHub PR, GitLab MR, or Bitbucket PR
- **Branch Management**: Git hooks, automated cleanup scripts
- **Monitoring**: Branch age monitoring, merge conflict detection

### Git Hooks
- Pre-commit: Code formatting, linting
- Pre-push: Run tests
- Post-merge: Cleanup notifications

## Best Practices

1. **Commit Messages**: Use conventional commit format
2. **PR Descriptions**: Include purpose, changes, and testing notes
3. **Branch Naming**: Follow established conventions
4. **Regular Syncing**: Keep branches up to date with their base branches
5. **Documentation**: Update relevant docs with each change
6. **Testing**: Ensure all tests pass before merging
7. **Code Review**: All code must be reviewed before merging

## Troubleshooting

### Common Issues
- Merge conflicts: Resolve by rebasing feature branch on latest develop
- Stale branches: Regular cleanup and communication
- Large PRs: Break down into smaller, focused changes
- Failed deployments: Rollback and investigate

### Getting Help
- Check this documentation first
- Ask in team chat for quick questions
- Create an issue for process improvements
- Schedule a meeting for complex workflow discussions