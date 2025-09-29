# GitHub Setup and Integration Guide

This guide walks you through setting up the Living Twin monorepo on GitHub with full CI/CD integration.

## 🚀 Initial GitHub Repository Setup

### 1. Create GitHub Repository

1. **Go to GitHub** and create a new repository:
   - Repository name: `living-twin-monorepo`
   - Description: "Living Twin - RAG-enabled organizational twin system"
   - Visibility: Private (recommended) or Public
   - **Do NOT** initialize with README, .gitignore, or license (we already have these)

2. **Copy the repository URL** (you'll need this for the next step)

### 2. Connect Local Repository to GitHub

```bash
# Add GitHub as remote origin
git remote add origin https://github.com/YOUR_USERNAME/living-twin-monorepo.git

# Verify remote was added
git remote -v

# Push to GitHub
git push -u origin main
```

### 3. Verify Repository Structure

After pushing, verify on GitHub that you see:

- ✅ All apps/, packages/, docs/, tools/ directories
- ✅ GitHub Actions workflows in .github/workflows/
- ✅ No .env files (secrets protected)
- ✅ .env.example file present

## 🔧 GitHub Actions Configuration

### Required Repository Secrets

Set up these secrets in **Settings > Secrets and variables > Actions**:

#### **Basic Secrets**

```bash
OPENAI_API_KEY=sk-your-openai-api-key-here
```

#### **GCP/Cloud Run Deployment Secrets**

```bash
GCP_PROJECT_ID=your-gcp-project-id
WIF_PROVIDER=projects/123456789/locations/global/workloadIdentityPools/github-pool/providers/github-provider
WIF_SERVICE_ACCOUNT=github-actions@your-project.iam.gserviceaccount.com
CLOUD_RUN_SERVICE_ACCOUNT=cloud-run-sa@your-project.iam.gserviceaccount.com
```

#### **Optional Notification Secrets**

```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
```

### GitHub Actions Workflows Overview

The repository includes 4 pre-configured workflows:

#### 1. **CI Workflow** (`.github/workflows/ci.yml`)

- **Triggers:** Push/PR to main/develop branches
- **Tests:** All apps (API, admin web, mobile)
- **Validates:** Terraform, Docker builds, security scanning
- **Runs on:** Every push and pull request

#### 2. **Cloud Run Deployment** (`.github/workflows/deploy-cloud-run.yml`)

- **Triggers:** Push to main/staging branches
- **Deploys:** API to Google Cloud Run
- **Includes:** Health checks, performance testing, security scanning
- **Environments:** Production (main) and Staging (staging)

#### 3. **Production Deployment** (`.github/workflows/deploy-prod.yml`)

- **Triggers:** Manual dispatch or tags
- **Deploys:** Full production environment
- **Includes:** Database migrations, infrastructure updates

#### 4. **Staging Deployment** (`.github/workflows/deploy-staging.yml`)

- **Triggers:** Push to develop branch
- **Deploys:** Staging environment for testing
- **Includes:** Integration tests, performance benchmarks

## 🔒 Security Setup

### 1. Branch Protection Rules

Set up branch protection in **Settings > Branches**:

**For `main` branch:**

```markdown
✅ Require a pull request before merging
✅ Require approvals (1 minimum)
✅ Dismiss stale PR approvals when new commits are pushed
✅ Require review from code owners
✅ Require status checks to pass before merging
   - Select: CI / admin-web
   - Select: CI / api
   - Select: CI / mobile
   - Select: CI / terraform
✅ Require branches to be up to date before merging
✅ Require conversation resolution before merging
✅ Restrict pushes that create files larger than 100MB
```

**For `develop` branch:**

```markdown
✅ Require a pull request before merging
✅ Require status checks to pass before merging
✅ Require branches to be up to date before merging
```

### 2. Security Alerts

Enable in **Settings > Security & analysis**:

```markdown
✅ Dependency graph
✅ Dependabot alerts
✅ Dependabot security updates
✅ Secret scanning
✅ Push protection for secret scanning
```

### 3. Code Scanning

The CI workflow includes Trivy security scanning. Results appear in the **Security** tab.

## 👥 Team Collaboration Setup

### 1. Create Teams (if organization)

In your GitHub organization:

- **@living-twin/core** - Core developers (admin access)
- **@living-twin/developers** - All developers (write access)
- **@living-twin/reviewers** - Code reviewers (triage access)

### 2. CODEOWNERS File

Create `.github/CODEOWNERS`:

```bash
# Global owners
* @living-twin/core

# API and backend
/apps/api/ @living-twin/backend-team
/packages/gcp_firebase/ @living-twin/devops-team

# Frontend applications
/apps/admin_web/ @living-twin/frontend-team
/apps/mobile/ @living-twin/mobile-team

# Infrastructure
/docker/ @living-twin/devops-team
/.github/workflows/ @living-twin/devops-team

# Documentation
/docs/ @living-twin/core
```

### 3. Issue Templates

Create `.github/ISSUE_TEMPLATE/`:

**Bug Report** (`.github/ISSUE_TEMPLATE/bug_report.md`):

```markdown
---
name: Bug report
about: Create a report to help us improve
title: '[BUG] '
labels: bug
assignees: ''
---

**Describe the bug**
A clear description of what the bug is.

**Component**
- [ ] API (FastAPI backend)
- [ ] Admin Web (React)
- [ ] Mobile (Flutter)
- [ ] Infrastructure

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. See error

**Expected behavior**
What you expected to happen.

**Environment**
- OS: [e.g. macOS, Ubuntu]
- Browser: [if applicable]
- Version: [e.g. v1.2.0]
```

**Feature Request** (`.github/ISSUE_TEMPLATE/feature_request.md`):

```markdown
---
name: Feature request
about: Suggest an idea for this project
title: '[FEATURE] '
labels: enhancement
assignees: ''
---

**Is your feature request related to a problem?**
A clear description of what the problem is.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Component**
- [ ] API (FastAPI backend)
- [ ] Admin Web (React)
- [ ] Mobile (Flutter)
- [ ] Infrastructure
- [ ] Documentation

**Additional context**
Add any other context or screenshots about the feature request here.
```

## 🚀 Deployment Environments

### Environment Strategy

- **`main`** → Production environment
- **`staging`** → Staging environment
- **`develop`** → Development environment
- **Feature branches** → CI testing only

### Environment Variables by Branch

**Production (main branch):**

```bash
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
```

**Staging (staging branch):**

```bash
ENVIRONMENT=staging
DEBUG=true
LOG_LEVEL=DEBUG
```

**Development (develop branch):**

```bash
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
```

## 📊 Monitoring and Observability

### 1. GitHub Insights

Monitor repository health in **Insights**:

- **Pulse** - Recent activity overview
- **Contributors** - Team contribution metrics
- **Traffic** - Repository views and clones
- **Dependency graph** - Package dependencies

### 2. Actions Monitoring

Track CI/CD performance:

- **Actions** tab shows all workflow runs
- Set up notifications for failed deployments
- Monitor build times and success rates

### 3. Security Monitoring

Regular security checks:

- **Security** tab for vulnerability alerts
- **Dependabot** for dependency updates
- **Code scanning** results from Trivy

## 🔄 Development Workflow

### 1. Feature Development

```bash
# Create feature branch from develop
git checkout develop
git pull origin develop
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "feat: add new feature"

# Push and create PR
git push -u origin feature/new-feature
```

### 2. Pull Request Process

1. **Create PR** targeting `develop` branch
2. **Fill PR template** with description and testing notes
3. **Wait for CI** to pass (all checks green)
4. **Request review** from appropriate team members
5. **Address feedback** and update PR
6. **Merge** once approved and CI passes

### 3. Release Process

```bash
# Create release branch from develop
git checkout develop
git pull origin develop
git checkout -b release/v1.2.0

# Update version numbers and changelog
# Commit changes
git commit -m "chore: prepare release v1.2.0"

# Create PR to main
# After merge, tag the release
git checkout main
git pull origin main
git tag -a v1.2.0 -m "Release v1.2.0"
git push origin v1.2.0
```

## 🆘 Troubleshooting

### Common Issues

#### **1. CI Fails with "No such file or directory"**

- Check that paths in workflows match monorepo structure
- Verify working-directory settings in workflow files

#### **2. Secrets Not Available in Workflows**

- Ensure secrets are set in repository settings
- Check secret names match exactly in workflow files

#### **3. Branch Protection Prevents Merge**

- Ensure all required status checks pass
- Get required approvals from code owners

#### **4. Docker Build Fails**

- Check Dockerfile paths are correct for monorepo
- Verify build context includes necessary files

### Getting Help

1. **Check workflow logs** in Actions tab
2. **Review security alerts** in Security tab
3. **Check branch protection** settings
4. **Verify secrets** are properly configured

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Branch Protection Rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches)
- [Managing Repository Security](https://docs.github.com/en/code-security)
- [Workload Identity Federation](https://cloud.google.com/iam/docs/workload-identity-federation)
