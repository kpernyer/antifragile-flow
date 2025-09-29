# Development Environment Setup Guide

This guide covers external tool dependencies, containerization strategies, and the trade-offs between local installation vs Docker-based development for the Living Twin monorepo.

## 📋 Current External Tool Requirements

### 🔧 **Core Development Tools**

| Tool | Purpose | Can Containerize? | Notes |
|------|---------|-------------------|-------|
| **Docker & Docker Compose** | Container orchestration | ❌ Host requirement | Must be installed on host |
| **Git** | Version control | ❌ Host requirement | Must be installed on host |
| **VS Code / IDE** | Development environment | ❌ Host requirement | Must be installed on host |

### 🌐 **Backend Development**

| Tool | Purpose | Can Containerize? | Current Status |
|------|---------|-------------------|----------------|
| **Python 3.11+** | API development | ✅ **Containerized** | Available in `docker/Dockerfile.api` |
| **uv** | Python package management | ✅ **Containerized** | Used for dependency installation |
| **Neo4j** | Graph database | ✅ **Containerized** | Available in `docker-compose.yml` |
| **FastAPI** | Web framework | ✅ **Containerized** | Runs in API container |

### 🎨 **Frontend Development**

| Tool | Purpose | Can Containerize? | Current Status |
|------|---------|-------------------|----------------|
| **Node.js 20+** | React development | ⚠️ **Partial** | Can containerize, but slower dev experience |
| **pnpm** | Package management | ✅ **Containerized** | Used for dependency installation |
| **Vite** | Build tool | ⚠️ **Partial** | Can run in container with volume mounts |

### 📱 **Mobile Development (Flutter)**

| Tool | Purpose | Can Containerize? | Challenges |
|------|---------|-------------------|------------|
| **Flutter SDK** | Mobile framework | ⚠️ **Limited** | Complex setup, platform dependencies |
| **Dart SDK** | Programming language | ⚠️ **Limited** | Included with Flutter |
| **Android Studio** | Android development | ❌ **No** | GUI application, requires host |
| **Android SDK** | Android toolchain | ⚠️ **Limited** | Can containerize CLI tools only |
| **Xcode** | iOS development | ❌ **macOS only** | Cannot containerize, macOS exclusive |
| **CocoaPods** | iOS dependency management | ❌ **macOS only** | Required for iOS Flutter development |
| **iOS Simulator** | iOS testing | ❌ **macOS only** | Cannot containerize, macOS exclusive |

### 🍺 **Package Managers**

| Tool | Purpose | Can Containerize? | Notes |
|------|---------|-------------------|-------|
| **Homebrew (macOS)** | Package management | ❌ **No** | Host-level package manager |
| **apt/yum (Linux)** | Package management | ❌ **No** | Host-level package manager |

## 🐳 Containerization Strategies

### ✅ **What We've Successfully Containerized**

#### 1. **Backend Stack (Fully Containerized)**

```yaml
# docker-compose.yml
services:
  neo4j:
    image: neo4j:5.15
    # Fully containerized database

  api:
    build:
      context: .
      dockerfile: docker/Dockerfile.api
    # Python, FastAPI, all dependencies installed with uv

  admin_web:
    build: ./docker/Dockerfile.admin
    # Node.js, React, Vite (for production)
```

**Benefits:**

- ✅ Consistent environment across all developers
- ✅ No Python/Neo4j installation required
- ✅ Fast dependency installation with uv
- ✅ Easy database reset and schema management
- ✅ Production-ready containers

#### 2. **Development Database (Neo4j)**

```bash
# Before: Manual Neo4j Desktop installation
# After: One command setup
make neo4j-up && make neo4j-init
```

### ⚠️ **Partial Containerization Challenges**

#### 1. **React Development**

```dockerfile
# Possible but with trade-offs
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]
```

**Trade-offs:**

- ✅ Consistent Node.js version
- ❌ Slower hot reload (file watching through Docker)
- ❌ More complex volume mounting
- ❌ Potential permission issues

**Current Recommendation:** Local Node.js for development, containerized for production with `pnpm`.

#### 2. **Flutter Development**

```dockerfile
# Experimental Flutter container
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y \
    curl git unzip xz-utils zip libglu1-mesa
RUN git clone https://github.com/flutter/flutter.git /flutter
ENV PATH="/flutter/bin:${PATH}"
```

**Major Limitations:**

- ❌ No Android emulator support
- ❌ No iOS development (macOS required)
- ❌ Complex device connection
- ❌ GUI tools not accessible
- ❌ Slow build times

### ❌ **Cannot Containerize**

#### 1. **iOS Development**

- **Xcode**: macOS exclusive, cannot run in containers
- **iOS Simulator**: Requires macOS and Xcode
- **Code signing**: Requires macOS keychain access
- **App Store deployment**: Requires macOS tools

#### 2. **Android Emulator**

- Requires hardware acceleration (KVM/HAXM)
- GUI application needs X11 forwarding
- Complex device management

#### 3. **IDE Integration**

- VS Code extensions need local Flutter/Dart SDK
- Debugging requires local toolchain
- Hot reload performance issues

## 🎯 Recommended Setup Strategy

### 🏆 **Hybrid Approach (Current Best Practice)**

#### **Containerize:**

- ✅ **Databases** (Neo4j, PostgreSQL, Redis)
- ✅ **Backend services** (FastAPI, workers)
- ✅ **Production builds** (React, API)
- ✅ **Testing environments**

#### **Install Locally:**

- 🔧 **Flutter SDK** (for mobile development)
- 🔧 **Node.js** (for React development)
- 🔧 **Android Studio** (for Android development)
- 🔧 **Xcode** (for iOS development, macOS only)

### 📋 **Minimal Local Setup Requirements**

#### **For Backend Development Only:**

```bash
# Minimal requirements
brew install docker docker-compose git
pip install uv
# Everything else runs in containers, uv used for local dev
```

#### **For Full-Stack Development:**

```bash
# Backend + Frontend
brew install docker docker-compose git node@20
npm install -g pnpm
# React runs locally, backend in containers
```

#### **For Mobile Development:**

```bash
# Complete setup
brew install docker docker-compose git node@20
npm install -g pnpm
# Install Flutter SDK
# Install Android Studio
# Install Xcode (macOS only)
```

## 🚀 Setup Automation

### **Automated Installation Scripts**

#### **macOS Setup Script**

```bash
#!/bin/bash
# tools/scripts/setup-macos.sh

echo "🚀 Setting up Living Twin development environment..."

# Install Homebrew if not present
if ! command -v brew &> /dev/null; then
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Core tools
brew install docker docker-compose git node@20
npm install -g pnpm

# Optional: Flutter for mobile development
read -p "Install Flutter for mobile development? (y/n): " -n 1 -r
if [[ $REPLY =~ ^[Yy]$ ]]; then
    brew install --cask flutter
fi

# Optional: Android Studio
read -p "Install Android Studio? (y/n): " -n 1 -r
if [[ $REPLY =~ ^[Yy]$ ]]; then
    brew install --cask android-studio
fi

echo "✅ Setup complete!"
```

#### **Linux Setup Script**

```bash
#!/bin/bash
# tools/scripts/setup-linux.sh

echo "🚀 Setting up Living Twin development environment..."

# Update package manager
sudo apt update

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER

# Install Node.js and pnpm
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
sudo npm install -g pnpm

# Install Flutter (optional)
read -p "Install Flutter for mobile development? (y/n): " -n 1 -r
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo snap install flutter --classic
fi

echo "✅ Setup complete! Please log out and back in for Docker permissions."
```

### **Development Environment Validation**

```bash
# tools/scripts/validate-environment.sh
#!/bin/bash

echo "🔍 Validating development environment..."

# Check Docker
if command -v docker &> /dev/null; then
    echo "✅ Docker: $(docker --version)"
else
    echo "❌ Docker: Not installed"
fi

# Check Node.js
if command -v node &> /dev/null; then
    echo "✅ Node.js: $(node --version)"
else
    echo "❌ Node.js: Not installed"
fi

# Check Flutter
if command -v flutter &> /dev/null; then
    echo "✅ Flutter: $(flutter --version | head -n1)"
    flutter doctor --android-licenses
else
    echo "⚠️  Flutter: Not installed (mobile development unavailable)"
fi

# Check platform-specific tools
if [[ "$OSTYPE" == "darwin"* ]]; then
    if command -v xcodebuild &> /dev/null; then
        echo "✅ Xcode: $(xcodebuild -version | head -n1)"
    else
        echo "⚠️  Xcode: Not installed (iOS development unavailable)"
    fi
fi

echo "🎯 Environment validation complete!"
```

## 📚 Development Workflow Options

### **Option 1: Minimal Setup (Backend Only)**

```bash
# Docker and uv required
git clone <repo>
cd living_twin_monorepo
make install-deps
make api-dev
```

**Pros:** Fastest setup, consistent environment
**Cons:** No frontend/mobile development

### **Option 2: Full-Stack Setup**

```bash
# Docker, Node.js and uv required
git clone <repo>
cd living_twin_monorepo
make install-deps
make api-dev & make web-dev
```

**Pros:** Full web development capability
**Cons:** Requires local Node.js installation

### **Option 3: Complete Setup**

```bash
# All tools installed
git clone <repo>
cd living_twin_monorepo
make install-deps
make api-dev & make web-dev & make mobile-dev
# Full development capability
```

**Pros:** Complete development environment
**Cons:** Most complex setup

## 🔄 Future Containerization Possibilities

### **Emerging Solutions**

#### **1. Remote Development Containers**

```json
// .devcontainer/devcontainer.json
{
  "name": "Living Twin Dev",
  "dockerComposeFile": "../docker-compose.dev.yml",
  "service": "dev-environment",
  "workspaceFolder": "/workspace",
  "features": {
    "ghcr.io/devcontainers/features/flutter:1": {},
    "ghcr.io/devcontainers/features/node:1": {"version": "20"}
  }
}
```

#### **2. Cloud Development Environments**

- **GitHub Codespaces**: Full environment in browser
- **GitPod**: Automated development environments
- **Replit**: Collaborative development

#### **3. Flutter Web Containers**

```dockerfile
# Future: Flutter web development
FROM cirrusci/flutter:stable
WORKDIR /app
COPY pubspec.* ./
RUN flutter pub get
COPY . .
EXPOSE 3000
CMD ["flutter", "run", "-d", "web-server", "--web-port", "3000"]
```

## 🎯 Recommendations

### **For New Developers**

1. **Start minimal**: Docker + Git only
2. **Add as needed**: Node.js for frontend, Flutter for mobile
3. **Use automation**: Run setup scripts
4. **Validate environment**: Use validation scripts

### **For Teams**

1. **Document requirements**: Clear setup instructions
2. **Provide alternatives**: Multiple setup options
3. **Automate validation**: CI checks for environment
4. **Consider cloud**: Remote development options

### **For Production**

1. **Everything containerized**: No local dependencies
2. **Multi-stage builds**: Optimized containers
3. **Security scanning**: Automated vulnerability checks
4. **Consistent environments**: Dev/staging/prod parity

## 🔧 Implementation Plan

### **Phase 1: Enhanced Documentation**

- ✅ Create setup scripts for macOS/Linux
- ✅ Add environment validation
- ✅ Document trade-offs clearly

### **Phase 2: Improved Containerization**

- 🔄 Add React development container option
- 🔄 Improve Flutter web container support
- 🔄 Add remote development container config

### **Phase 3: Cloud Development**

- 🔄 GitHub Codespaces configuration
- 🔄 GitPod integration
- 🔄 Cloud-based mobile development options

The key insight is that **mobile development** (especially iOS) will always require some local setup due to platform constraints, but we can minimize and automate as much as possible while providing clear alternatives for different development needs.
