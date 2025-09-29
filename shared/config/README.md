# 🔧 Centralized Configuration Management

Comprehensive configuration system that provides consistent default values across Python backend and TypeScript frontend components.

## 🎯 Philosophy

**"Single Source of Truth for Cross-Language Configuration"**

All ports, URLs, credentials, and service endpoints are defined in one place and kept in sync across:
- **Python Backend**: `shared/config/defaults.py`
- **TypeScript Frontend**: `frontend/src/config/defaults.ts`

## 📁 Configuration Files

### Core Configuration Files

#### `defaults.py` - Python Backend Defaults
```python
from shared.config.defaults import PORTS, URLS, QUEUES, get_temporal_address

# Use centralized values
client = await Client.connect(get_temporal_address())
workflow_url = get_temporal_ui_url(workflow_id)
```

#### `defaults.ts` - TypeScript Frontend Defaults
```typescript
import { DEFAULT_PORTS, getApiUrl, getTemporalUIUrl } from '../config/defaults';

// Use centralized values
const apiEndpoint = getApiUrl();
const monitoringUrl = getTemporalUIUrl(workflowId);
```

### Advanced Configuration (Ready for Integration)

#### `settings.py` - Comprehensive Settings Management
- Environment-based configuration
- Production/development/testing profiles
- Validation and type safety
- Integration with all other config modules

#### `ai_config.py` - AI Service Configuration
- OpenAI API settings
- Model configurations
- Rate limiting and retry policies

#### `database_config.py` - Database Configuration
- PostgreSQL, Redis, MongoDB settings
- Connection pooling configuration
- Environment-specific connection strings

#### `../temporal_client/config.py` - Temporal Configuration
- Multi-environment Temporal settings
- Task queue management
- Security and TLS configuration

## 🔗 Cross-Language Synchronization

### Synchronized Values

| Category | Python Location | TypeScript Location | Example Values |
|----------|----------------|-------------------|---------------|
| **Temporal Ports** | `PORTS.TEMPORAL_SERVER` | `DEFAULT_PORTS.TEMPORAL_SERVER` | `7233` |
| **Web URLs** | `URLS.FRONTEND_LOCAL` | `DEFAULT_URLS.FRONTEND_LOCAL` | `http://localhost:3000` |
| **GraphQL Port** | `PORTS.GRAPHQL_SERVER` | `DEFAULT_PORTS.GRAPHQL_SERVER` | `4000` |
| **GraphQL Endpoint** | `URLS.GRAPHQL_ENDPOINT` | `DEFAULT_URLS.GRAPHQL_ENDPOINT` | `http://localhost:4000/graphql` |
| **GraphQL Playground** | `URLS.GRAPHQL_PLAYGROUND` | `DEFAULT_URLS.GRAPHQL_PLAYGROUND` | `http://localhost:4000/playground` |
| **GraphQL WebSocket** | `URLS.GRAPHQL_SUBSCRIPTIONS` | `DEFAULT_URLS.GRAPHQL_SUBSCRIPTIONS` | `ws://localhost:4000/graphql` |
| **Task Queues** | `QUEUES.DEFAULT` | `TASK_QUEUES.DEFAULT` | `"hackathon"` |

### Environment Variables

| Variable | Purpose | Default | Used By |
|----------|---------|---------|---------|
| `TEMPORAL_ADDRESS` | Temporal server | `localhost:7233` | Python Backend |
| `REACT_APP_TEMPORAL_ADDRESS` | Temporal server | `localhost:7233` | React Frontend |
| `REACT_APP_API_URL` | Backend API | `http://localhost:8080` | React Frontend |
| `GRAPHQL_URL` | GraphQL server | `http://localhost:4000` | Python Backend |
| `GRAPHQL_ENDPOINT` | GraphQL endpoint | `http://localhost:4000/graphql` | Python Backend |
| `REACT_APP_GRAPHQL_URL` | GraphQL server | `http://localhost:4000` | React Frontend |
| `REACT_APP_GRAPHQL_ENDPOINT` | GraphQL endpoint | `http://localhost:4000/graphql` | React Frontend |
| `REACT_APP_GRAPHQL_SUBSCRIPTIONS` | GraphQL WebSocket | `ws://localhost:4000/graphql` | React Frontend |

## 🚀 Current Usage Patterns

### Python Backend
```python
# Recommended pattern (using centralized defaults)
from shared.config.defaults import get_temporal_address, get_temporal_ui_url

client = await Client.connect(get_temporal_address())
monitor_url = get_temporal_ui_url(workflow_id)
```

### TypeScript Frontend
```typescript
// Recommended pattern (using centralized defaults)
import {
  getApiUrl,
  getTemporalUIUrl,
  getGraphQLEndpoint,
  getGraphQLSubscriptionsUrl
} from '../config/defaults';

const apiClient = new ApiClient(getApiUrl());
const graphqlClient = new ApolloClient({ uri: getGraphQLEndpoint() });
const subscriptionClient = new SubscriptionClient(getGraphQLSubscriptionsUrl());
const workflowMonitorUrl = getTemporalUIUrl(workflowId);
```

## 📋 Migration Path

### Current State
- ✅ **Centralized defaults created** in both Python and TypeScript
- ⏳ **Legacy hardcoded values** still exist in 20+ files
- ⏳ **Environment variables** partially implemented

### Phase 1: Replace Hardcoded Values (Immediate)
```bash
# Files with hardcoded localhost:7233 (17 locations)
./test/simple_test_starter.py
./actor/ceo/starter.py
./worker/onboarding_worker.py
# ... and 14 more
```

### Phase 2: Standardize Environment Variables
```bash
# Ensure consistent env var names across Python/TypeScript
TEMPORAL_ADDRESS=localhost:7233
REACT_APP_TEMPORAL_ADDRESS=localhost:7233
REACT_APP_API_URL=http://localhost:8080
```

### Phase 3: Integrate Advanced Configuration
```python
# Future: Use comprehensive settings system
from shared.config import get_settings
settings = get_settings()
client = await get_temporal_client()  # Managed client
```

## 🔧 Development Guidelines

### Adding New Configuration Values

1. **Add to Python defaults**:
   ```python
   # shared/config/defaults.py
   NEW_SERVICE_PORT = 9999
   NEW_SERVICE_URL = f"http://{DefaultHosts.LOCAL}:{NEW_SERVICE_PORT}"
   ```

2. **Add to TypeScript defaults**:
   ```typescript
   // frontend/src/config/defaults.ts
   NEW_SERVICE_PORT: 9999,
   NEW_SERVICE_URL: `http://${DEFAULT_HOSTS.LOCAL}:9999`,
   ```

3. **Update documentation** in this README

### Environment Variable Naming
- **Python Backend**: `SERVICE_ADDRESS`, `SERVICE_PORT`
- **React Frontend**: `REACT_APP_SERVICE_ADDRESS`, `REACT_APP_SERVICE_PORT`

### Testing Configuration
```python
# Python
def test_temporal_connection():
    address = get_temporal_address()
    assert address in ["localhost:7233", "production.temporal.com:7233"]
```

```typescript
// TypeScript
test('temporal address configuration', () => {
  const address = getTemporalAddress();
  expect(address).toMatch(/localhost:7233|\.temporal\.com:7233/);
});
```

## 🎯 Benefits

### ✅ **Consistency**
- Same port numbers across all services
- Synchronized URLs between frontend/backend
- Standardized naming conventions

### ✅ **Maintainability**
- Single place to update service endpoints
- Environment-aware configuration
- Type-safe configuration values

### ✅ **Development Experience**
- Clear documentation of all services
- Easy local development setup
- Obvious environment variable patterns

### ✅ **Production Readiness**
- Environment-based overrides
- Secure credential management
- Professional configuration architecture

## 🔄 Synchronization Checklist

When updating configuration values:

- [ ] Update Python `defaults.py`
- [ ] Update TypeScript `defaults.ts`
- [ ] Update environment variable documentation
- [ ] Test both backend and frontend with new values
- [ ] Update this README if adding new categories

---

This configuration system ensures that port numbers, URLs, and service endpoints remain consistent across the entire Antifragile Flow application stack.
