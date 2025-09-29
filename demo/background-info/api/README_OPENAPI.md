# Living Twin API - OpenAPI Documentation

This document explains the OpenAPI/Swagger representation implemented for the Living Twin Strategic Intelligence API.

## 🎯 Overview

The Living Twin API now provides comprehensive OpenAPI 3.0 documentation with:
- Rich endpoint descriptions and examples
- Detailed Pydantic model schemas with validation
- Interactive documentation via Swagger UI and ReDoc
- Client generation capabilities for TypeScript/JavaScript
- Comprehensive business context for all endpoints

## 📖 Accessing API Documentation

### Interactive Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

### Local Development
```bash
# Start the API server
cd apps/api
python -m uvicorn app.main:app --reload

# Access documentation at http://localhost:8000/docs
```

## 🚀 API Capabilities

### Strategic Intelligence (`/intelligence`)
- Generate comprehensive strategic reports from agent data
- Access strategic insights with filtering and pagination
- Manage priority communications and escalations
- Strategic alignment scorecards and metrics
- Template management for intelligence generation

### RAG System (`/query`)
- Semantic document search with AI-generated answers
- Document ingestion (text, PDF, DOCX, MD)
- Conversational AI with memory and context
- Debug capabilities for RAG pipeline analysis
- Job status tracking for async operations

### Health Monitoring (`/health`)
- Comprehensive system health checks
- Service-specific status monitoring (Neo4j, Redis, Firebase)
- System metrics and performance data
- Kubernetes-compatible health probes
- Graceful shutdown capabilities

### Testing Framework (`/strategic-test`)
- End-to-end testing for strategic intelligence
- Test data setup and scenario management
- Signal detection testing and validation
- Performance and reliability testing

## 🛠️ Client Generation

### TypeScript/JavaScript Client

Generate a TypeScript client for your frontend applications:

```bash
# Install OpenAPI Generator CLI
npm install -g @openapitools/openapi-generator-cli

# Generate OpenAPI specification
cd apps/api
python scripts/generate_openapi_spec.py

# Generate TypeScript client
npx @openapitools/openapi-generator-cli generate -c openapi-generator-config.yaml

# Client will be generated in ../admin_web/src/api/generated/
```

### Using the Generated Client

```typescript
import { Configuration, QueryApi, IntelligenceApi } from './api/generated';

// Configure client with authentication
const config = new Configuration({
  basePath: 'http://localhost:8000',
  headers: {
    'Authorization': 'Bearer ' + firebaseToken
  }
});

// Use the APIs
const queryApi = new QueryApi(config);
const intelligenceApi = new IntelligenceApi(config);

// Query documents
const response = await queryApi.query({
  queryRequestSchema: {
    question: "What are our strategic priorities?",
    k: 10
  }
});

// Generate strategic intelligence
const intelligence = await intelligenceApi.generateStrategicIntelligence({
  intelligenceRequest: {
    agent_ids: ["news_agent", "competitor_agent"],
    template_id: "ceo_briefing",
    analysis_depth: "WEEKLY"
  }
});
```

## 📋 API Features & Examples

### Document Querying
```json
POST /query
{
  "question": "What are the key risks mentioned in our quarterly report?",
  "k": 5,
  "tenantId": "acme_corp"
}
```

### Document Ingestion
```json
POST /query/ingest/text
{
  "title": "Q4 2024 Strategic Plan",
  "text": "Strategic Plan 2024\n\nExecutive Summary: ...",
  "tenantId": "acme_corp"
}
```

### Strategic Intelligence Generation
```json
POST /intelligence/generate
{
  "agent_ids": ["news_agent", "competitor_agent"],
  "template_id": "ceo_strategic_truths",
  "analysis_depth": "WEEKLY",
  "variables": {
    "industry": "technology",
    "company_size": "mid-size"
  },
  "priority": "high"
}
```

## 🔧 Configuration Details

### FastAPI Application Metadata
- **Title**: Living Twin API
- **Version**: 2.0.0
- **Description**: Comprehensive strategic intelligence platform
- **Contact**: API Support (support@livingtwin.com)
- **License**: Proprietary

### Server Environments
- **Production**: `https://api.livingtwin.com`
- **Staging**: `https://staging-api.livingtwin.com`
- **Development**: `http://localhost:8000`

### Authentication
All endpoints require Firebase JWT authentication:
```
Authorization: Bearer <firebase-jwt-token>
```

Development environments support bypass mode for testing.

## 📊 API Statistics

The API currently includes:
- **4 main endpoint groups** (Health, Intelligence, Query, Strategic Test)
- **25+ endpoints** with comprehensive documentation
- **Rich Pydantic models** with validation and examples
- **Tenant isolation** with role-based access control
- **Comprehensive error handling** with detailed error responses

## 🔍 Advanced Features

### Request/Response Examples
All endpoints include comprehensive examples showing:
- Typical request payloads
- Expected response structures
- Error response formats
- Business context and use cases

### Validation & Constraints
- Field-level validation with clear error messages
- Type safety with Pydantic models
- Range constraints and enumeration values
- Custom validation rules for business logic

### Error Handling
Standardized error responses with:
- HTTP status codes
- Error messages and details
- Request validation errors
- Business logic error conditions

## 🚦 Next Steps

1. **Review Documentation**: Visit `/docs` to explore the interactive API documentation
2. **Generate Client**: Use the provided scripts to generate TypeScript clients
3. **Integration Testing**: Import OpenAPI spec into Postman or similar tools
4. **Frontend Integration**: Use generated clients in your React/Vue/Angular applications
5. **API Monitoring**: Leverage the health endpoints for production monitoring

## 🤝 Development Workflow

### API-First Development
1. Define new endpoints with comprehensive OpenAPI documentation
2. Use Pydantic models with examples and validation
3. Generate updated TypeScript clients
4. Update frontend applications with new client code
5. Test using interactive documentation and generated clients

### Continuous Integration
- Automated OpenAPI spec generation in CI/CD pipeline
- Client generation as part of frontend build process
- API documentation deployment alongside application releases
- Contract testing between frontend and backend services

---

For questions or support, contact the API team or refer to the interactive documentation at `/docs`.
