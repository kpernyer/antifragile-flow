# Living Twin Domain Configuration

## 🌐 Domain Structure for `aprio.one`

### Production Environment
- **Primary Domain**: `dev.aprio.one`
- **API Endpoint**: `https://dev.aprio.one/api`
- **GraphQL Endpoint**: `https://dev.aprio.one/api/graphql`
- **Web Application**: `https://dev.aprio.one`
- **Admin Interface**: `https://dev.aprio.one/admin`

### Staging Environment
- **Staging Domain**: `staging.aprio.one`
- **API Endpoint**: `https://staging.aprio.one/api`
- **GraphQL Endpoint**: `https://staging.aprio.one/api/graphql`
- **Web Application**: `https://staging.aprio.one`

### Local Development
- **API Endpoint**: `http://localhost:8000`
- **GraphQL Endpoint**: `http://localhost:8000/graphql`
- **Admin Interface**: `http://localhost:5173`
- **Neo4j Browser**: `http://localhost:7474`

## 🔧 Service Architecture

```
Production (dev.aprio.one)
├── Web App (React/Next.js)     → https://dev.aprio.one
├── API (FastAPI)               → https://dev.aprio.one/api
│   ├── REST Endpoints          → https://dev.aprio.one/api/v1/*
│   ├── GraphQL                 → https://dev.aprio.one/api/graphql
│   └── OpenAPI Docs           → https://dev.aprio.one/api/docs
├── Analytics                   → https://analytics.dev.aprio.one
├── Vector Search               → https://vector.dev.aprio.one
└── Mobile App APIs            → All endpoints accessible via dev.aprio.one
```

## 📱 Mobile App Configuration

### Flutter/Dart App Endpoints
- **Local**: `make connect-local` → `http://localhost:8000`
- **Staging**: `make connect-staging` → `https://staging.aprio.one/api`
- **Production**: `make connect-prod` → `https://dev.aprio.one/api`

### Mobile App Stores
- **Google Play**: `play.google.com/store/apps` (Future)
- **Apple App Store**: `apps.apple.com` (Future)

## 🏗️ Infrastructure Services

### Database Services
- **Neo4j Production**: `neo4j://dev.aprio.one:7687`
- **Redis Production**: `redis://dev.aprio.one:6379`
- **Neo4j Local**: `bolt://localhost:7687`
- **Redis Local**: `localhost:6379`

### Authentication
- **Firebase Auth**: `firebase-aprio-one.web.app`
- **Local Firebase Emulator**: `http://localhost:9099`

### External APIs
- **OpenAI Production**: `api.openai.com`
- **Local LLM (Ollama)**: `http://localhost:11434`

## 🔐 DNS Configuration Required

### A Records
```
dev.aprio.one           → [Production Server IP]
staging.aprio.one       → [Staging Server IP]
analytics.dev.aprio.one → [Analytics Server IP]
vector.dev.aprio.one    → [Vector Search Server IP]
```

### CNAME Records (Alternative)
```
www.dev.aprio.one       → dev.aprio.one
api.aprio.one          → dev.aprio.one  (if preferred)
```

## 🚀 Deployment Checklist

- [ ] Configure DNS records for `dev.aprio.one`
- [ ] Setup SSL certificates (Let's Encrypt via Certbot)
- [ ] Configure Google Cloud Run for API
- [ ] Setup Vercel for web frontend
- [ ] Configure Firebase Auth domain
- [ ] Setup Google Cloud Neo4j instance
- [ ] Configure Redis Memorystore
- [ ] Update mobile app configs
- [ ] Test all endpoints
- [ ] Setup monitoring and analytics

## 🔄 Migration Commands

### Update Mobile App Configs
```bash
cd ../living-twin-mobile
make connect-prod  # Points to dev.aprio.one
make connect-staging  # Points to staging.aprio.one
```

### Update Environment Variables
```bash
# Production
export API_BASE_URL="https://dev.aprio.one/api"
export GRAPHQL_URL="https://dev.aprio.one/api/graphql"

# Staging
export API_BASE_URL="https://staging.aprio.one/api"
export GRAPHQL_URL="https://staging.aprio.one/api/graphql"
```

---

*Domain configuration updated: $(date)*
*Ready for deployment to aprio.one infrastructure*
