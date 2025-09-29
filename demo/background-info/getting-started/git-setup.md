# Git Repository Setup Guide

This guide helps you initialize and maintain the Living Twin monorepo with proper secret management and Git best practices.

## 🚀 Initial Repository Setup

### 1. Initialize Git Repository

```bash
# Initialize the repository
git init

# Add all files (secrets are protected by .gitignore)
git add .

# Create initial commit
git commit -m "feat: initial Living Twin monorepo setup

- Complete monorepo structure with apps/, packages/, docs/
- FastAPI backend with hexagonal architecture
- React admin interface with Vite
- Flutter mobile app with environment-aware configuration
- Comprehensive documentation in docs/
- Docker setup for local development
- Terraform infrastructure as code
- Proper secret management with .gitignore"
```

### 2. Connect to Remote Repository

```bash
# Add your remote repository
git remote add origin https://github.com/your-username/living-twin-monorepo.git

# Push to remote
git push -u origin main
```

## 🔒 Secret Management

### Protected Files (Never Committed)

The `.gitignore` file protects these sensitive files:

- `.env` - Contains real API keys and secrets
- `.env.local` - Local development overrides
- `*.key`, `*.pem` - Certificate files
- `service-account*.json` - Firebase/GCP credentials
- `terraform.tfvars` - Terraform variable files with secrets

### Safe Files (Can Be Committed)

- `.env.example` - Template with placeholder values
- `firebase.json` - Firebase configuration (no secrets)
- `terraform/*.tf` - Infrastructure code (no secrets)
- All application code and documentation

### Environment Setup for New Developers

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-username/living-twin-monorepo.git
   cd living-twin-monorepo
   ```

2. **Set up environment:**

   ```bash
   # Copy environment template
   cp .env.example .env

   # Edit .env with your actual values
   nano .env  # or your preferred editor
   ```

3. **Install dependencies:**

   ```bash
   # Python backend
   python3.11 -m venv .venv
   source .venv/bin/activate
   make install

   # React admin
   make node-setup

   # Flutter mobile (optional)
   cd apps/mobile && flutter pub get
   ```

## 🔍 Pre-Commit Checks

### Verify No Secrets Are Staged

Before committing, always check:

```bash
# Check what files are staged
git status

# Verify no .env files are staged
git ls-files --cached | grep -E '\.(env|key|pem|json)$' | grep -v '.example'

# If any secret files are found, unstage them:
git reset HEAD .env .env.local *.key
```

### Automated Secret Detection

Consider adding a pre-commit hook:

```bash
# Create .git/hooks/pre-commit
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Check for potential secrets
if git diff --cached --name-only | grep -qE '\.(env|key|pem)$' && ! git diff --cached --name-only | grep -q '\.example$'; then
    echo "❌ Error: Attempting to commit secret files!"
    echo "Files:"
    git diff --cached --name-only | grep -E '\.(env|key|pem)$'
    echo "Use 'git reset HEAD <file>' to unstage"
    exit 1
fi

# Check for hardcoded API keys
if git diff --cached | grep -qE '(sk-[a-zA-Z0-9]{48}|AIza[a-zA-Z0-9]{35})'; then
    echo "❌ Error: Potential API key found in staged changes!"
    echo "Please remove hardcoded secrets and use environment variables"
    exit 1
fi

echo "✅ Pre-commit checks passed"
EOF

chmod +x .git/hooks/pre-commit
```

## 📝 Commit Message Conventions

Use conventional commits for better changelog generation:

```bash
# Feature additions
git commit -m "feat(api): add conversation memory system"
git commit -m "feat(mobile): implement voice recognition"

# Bug fixes
git commit -m "fix(admin): resolve authentication redirect loop"

# Documentation
git commit -m "docs: update deployment guide with Cloud Run steps"

# Refactoring
git commit -m "refactor(api): extract vector store interface"

# Configuration changes
git commit -m "config: update Docker compose for production"
```

## 🌿 Branch Strategy

### Main Branches

- `main` - Production-ready code
- `develop` - Integration branch for features
- `staging` - Pre-production testing

### Feature Branches

```bash
# Create feature branch
git checkout -b feature/conversation-memory
git checkout -b fix/auth-redirect-bug
git checkout -b docs/api-documentation

# Work on feature...
git add .
git commit -m "feat: implement conversation memory storage"

# Push and create PR
git push -u origin feature/conversation-memory
```

## 🚀 Release Process

### 1. Prepare Release

```bash
# Switch to develop branch
git checkout develop
git pull origin develop

# Create release branch
git checkout -b release/v1.2.0

# Update version numbers in:
# - apps/api/pyproject.toml
# - apps/admin_web/package.json
# - apps/mobile/pubspec.yaml

# Commit version updates
git commit -m "chore: bump version to v1.2.0"
```

### 2. Deploy and Test

```bash
# Deploy to staging
make deploy-staging

# Run tests
make test-all

# If issues found, fix and commit
git commit -m "fix: resolve staging deployment issue"
```

### 3. Merge to Main

```bash
# Merge to main
git checkout main
git merge release/v1.2.0

# Tag release
git tag -a v1.2.0 -m "Release v1.2.0: Conversation memory and voice features"

# Push to remote
git push origin main --tags

# Deploy to production
make deploy-production
```

## 🔧 Maintenance Commands

### Clean Up Branches

```bash
# List merged branches
git branch --merged main

# Delete merged feature branches
git branch -d feature/old-feature

# Clean up remote tracking branches
git remote prune origin
```

### Repository Health Check

```bash
# Check for large files
git ls-files | xargs ls -la | sort -k5 -rn | head -10

# Check repository size
du -sh .git

# Verify .gitignore is working
git status --ignored
```

## 🆘 Emergency Procedures

### If Secrets Were Accidentally Committed

```bash
# Remove from last commit (if not pushed yet)
git reset --soft HEAD~1
git reset HEAD .env
git commit -m "fix: remove accidentally committed secrets"

# If already pushed, contact team immediately
# Consider rotating all exposed secrets
```

### Repository Corruption Recovery

```bash
# Verify repository integrity
git fsck --full

# If issues found, clone fresh copy
git clone https://github.com/your-username/living-twin-monorepo.git living-twin-backup
```

## 📚 Additional Resources

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/)
- [Semantic Versioning](https://semver.org/)
- [GitHub Flow](https://guides.github.com/introduction/flow/)
