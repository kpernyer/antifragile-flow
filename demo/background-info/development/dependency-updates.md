# Dependency Update Guide for Living Twin Monorepo

## Python Backend (apps/api) - Using UV

### Installation Commands
```bash
cd apps/api

# Install UV if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies with UV
uv sync

# Or install specific groups
uv pip install -e .
uv pip install -e ".[dev]"
```

### New Dependencies Added
- `redis[hiredis]>=5.0.0` - Redis with C parser for performance
- `slowapi>=0.1.9` - Rate limiting
- `psutil>=5.9.0` - System metrics for health checks

## JavaScript/TypeScript (apps/admin_web) - Using PNPM

### Installation Commands
```bash
# From monorepo root
pnpm install

# Or specifically for admin_web
cd apps/admin_web
pnpm install
```

### Dependencies to Add (if needed for monitoring)
```json
{
  "dependencies": {
    "@sentry/react": "^7.100.0"
  }
}
```

## Flutter/Dart (apps/mobile)

### Installation Commands
```bash
cd apps/mobile

# Get dependencies
flutter pub get

# Run build runner for code generation
flutter pub run build_runner build --delete-conflicting-outputs
```

### Dependencies Already Configured
All the following dependencies are already in pubspec.yaml:
- `flutter_secure_storage: ^9.0.0` - Encrypted storage
- `dio: ^5.4.0` - HTTP client with interceptors
- `rxdart: ^0.27.7` - Reactive extensions for debouncing
- `shared_preferences: ^2.2.2` - Simple key-value storage
- `sqflite: ^2.3.0` - SQLite for local caching
- `get_it: ^7.6.4` - Dependency injection
- `injectable: ^2.3.2` - DI code generation
- `freezed: ^2.4.6` - Immutable models
- `sentry_flutter: ^7.14.0` - Crash reporting

## Docker Compose Services

### Redis Service Configuration
```yaml
# docker-compose.yml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  redis_data:
```

## Environment Variables

### Python API (.env)
```bash
# Redis Configuration
REDIS_URL=redis://localhost:6379
REDIS_MAX_CONNECTIONS=50

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_DEFAULT="100 per minute"
RATE_LIMIT_BURST="20 per second"

# Neo4j Connection Pool
NEO4J_MAX_CONNECTIONS=50
NEO4J_CONNECTION_TIMEOUT=30.0
NEO4J_RETRY_TIME=30.0

# Health Check
HEALTH_CHECK_INTERVAL=30
API_VERSION=1.0.0
```

### Flutter Mobile (.env)
```bash
# API Configuration
API_BASE_URL=http://localhost:8000
API_TIMEOUT=30000
API_RETRY_ATTEMPTS=3

# Security
PIN_REQUIRED=false
BIOMETRIC_ENABLED=true
SECURE_STORAGE_ENABLED=true

# Caching
CACHE_MEMORY_SIZE=100
CACHE_DISK_SIZE_MB=50
CACHE_TTL_HOURS=24
```

## Running Everything

### 1. Start Infrastructure
```bash
# From monorepo root
docker-compose up -d redis neo4j
```

### 2. Install All Dependencies
```bash
# Python API
cd apps/api && uv sync && cd ../..

# Admin Web
pnpm install

# Mobile
cd apps/mobile && flutter pub get && cd ../..
```

### 3. Run Services
```bash
# Terminal 1: Python API
cd apps/api && uv run uvicorn app.main:app --reload --port 8000

# Terminal 2: Admin Web
pnpm --filter admin_web dev

# Terminal 3: Mobile (iOS Simulator)
cd apps/mobile && flutter run -d ios

# Terminal 4: Mobile (Android)
cd apps/mobile && flutter run -d android
```

## Verification Commands

### Python API Health Check
```bash
curl http://localhost:8000/api/health/ready
```

### Redis Connection Test
```bash
redis-cli ping
# Should return: PONG
```

### Neo4j Connection Test
```bash
curl http://localhost:7474
# Should show Neo4j browser
```

## Troubleshooting

### UV Issues
```bash
# Clear UV cache
uv cache clean

# Reinstall
uv pip install --force-reinstall -e .
```

### PNPM Issues
```bash
# Clear cache
pnpm store prune

# Reinstall
pnpm install --force
```

### Flutter Issues
```bash
# Clean build
flutter clean

# Clear pub cache
flutter pub cache clean

# Reinstall
flutter pub get
```

## CI/CD Integration

### GitHub Actions Example
```yaml
name: CI

on: [push, pull_request]

jobs:
  python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: astral-sh/setup-uv@v2
      - run: cd apps/api && uv sync && uv run pytest

  javascript:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: pnpm/action-setup@v2
        with:
          version: 8
      - run: pnpm install --frozen-lockfile
      - run: pnpm test

  flutter:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.16.0'
      - run: cd apps/mobile && flutter pub get
      - run: cd apps/mobile && flutter test
```

## Performance Monitoring

### Expected Metrics After Implementation
- **API Response Time**: < 100ms (p95)
- **Redis Cache Hit Rate**: > 80%
- **Neo4j Connection Pool Utilization**: < 70%
- **Rate Limit Violations**: < 1%
- **Health Check Latency**: < 50ms
- **Mobile App Cache Hit Rate**: > 60%
- **Flutter Network Retry Success**: > 95%

## Security Checklist

- [x] Rate limiting enabled on all endpoints
- [x] Redis configured with password (production)
- [x] Neo4j using encrypted connections (production)
- [x] Flutter secure storage for sensitive data
- [x] SSL pinning configured in mobile app
- [x] API authentication required
- [x] Health endpoints protected (production)
- [x] Sentry configured for error tracking
