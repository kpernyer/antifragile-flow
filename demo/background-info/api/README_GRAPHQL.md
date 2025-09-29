# Living Twin API - GraphQL Integration

This document explains the GraphQL implementation added to the Living Twin Strategic Intelligence Platform.

## 🎯 Overview

We've implemented GraphQL as a **facade layer** over the existing FastAPI REST API using Strawberry GraphQL. This provides:
- **Flexible data fetching** for complex dashboard queries
- **Type-safe operations** with modern Python async/await
- **Single endpoint** aggregation for multiple REST calls
- **Rich introspection** and development tools

## 🚀 GraphQL Endpoints

### **GraphiQL Interface (Development)**
- **URL**: `http://localhost:8000/graphql`
- **Features**: Interactive query builder, schema exploration, documentation

### **GraphQL API Endpoint**
- **URL**: `http://localhost:8000/graphql`
- **Methods**: POST (queries/mutations), GET (GraphiQL)

## 📊 Key Use Cases

### 1. **Strategic Intelligence Dashboard**
Single query to get comprehensive dashboard data:

```graphql
query StrategicDashboard {
  strategicIntelligenceDashboard {
    recentTruths {
      id
      statement
      confidence
      impactLevel
      category
      createdAt
    }
    pendingCommunications {
      id
      topic
      priority
      type
      createdAt
    }
    alignmentScorecard {
      overallAlignmentScore
      alignmentZone
      strategicVelocity
      riskIndicators
      priorityInterventions
    }
    systemHealth {
      status
      uptime_seconds
      services
    }
    totalTruths
    queueLength
  }
}
```

### 2. **Flexible Truth Querying**
Filter and paginate organizational truths:

```graphql
query FilteredTruths {
  truths(
    filter: {
      categories: [MARKET, COMPETITIVE]
      impactLevels: [HIGH, CRITICAL]
      confidenceMin: 0.8
      limit: 10
    }
  ) {
    id
    statement
    confidence
    category
    impactLevel
    strategicGoals
    relatedTruths
  }
}
```

### 3. **Document Querying with RAG**
Semantic search across documents:

```graphql
query QueryDocuments {
  queryDocuments(
    input: {
      question: "What are our key strategic risks?"
      k: 5
    }
  ) {
    answer
    confidence
    sources
    queryId
  }
}
```

### 4. **Communications Management**
Get priority communications with filtering:

```graphql
query PendingCommunications {
  communications(
    filter: {
      acknowledged: false
      priorityMin: 7
      types: [ALERT, RECOMMENDATION]
    }
  ) {
    id
    topic
    content
    priority
    type
    createdAt
    relatedTruths
  }
}
```

## 🔧 GraphQL Schema

### **Core Types**

#### **OrganizationalTruth**
Strategic insights and organizational knowledge:
```graphql
type OrganizationalTruth {
  id: String!
  statement: String!
  confidence: Float!
  evidenceCount: Int!
  category: TruthCategory!
  impactLevel: ImpactLevel!
  strategicGoals: [String!]!
  relatedTruths: [String!]!
  createdAt: DateTime!
}
```

#### **CommunicationQueue**
Priority communications and alerts:
```graphql
type CommunicationQueue {
  id: String!
  topic: String!
  content: String!
  type: CommunicationType!
  priority: Int!
  acknowledged: Boolean!
  relatedTruths: [String!]!
}
```

#### **StrategicAlignmentScorecard**
Strategic alignment metrics:
```graphql
type StrategicAlignmentScorecard {
  overallAlignmentScore: Float!
  alignmentZone: StrategicAlignmentZone!
  strategicVelocity: Float!
  riskIndicators: [String!]!
  priorityInterventions: [String!]!
}
```

### **Enums**
- `TruthCategory`: MARKET, COMPETITIVE, TECHNOLOGY, REGULATORY, ORGANIZATIONAL, FINANCIAL
- `ImpactLevel`: LOW, MEDIUM, HIGH, CRITICAL
- `CommunicationType`: INSIGHT, ALERT, RECOMMENDATION, BRIEFING
- `AnalysisDepth`: DAILY, WEEKLY, MONTHLY, QUARTERLY

## 🛠️ Implementation Details

### **Architecture**
- **Strawberry GraphQL**: Modern Python GraphQL library with async support
- **Facade Pattern**: GraphQL resolvers call existing domain services
- **Type Safety**: Full type checking with Python type hints
- **Context Integration**: Firebase authentication context passed to resolvers

### **File Structure**
```
apps/api/app/graphql/
├── __init__.py          # GraphQL module
├── types.py             # GraphQL type definitions
├── resolvers.py         # Query/mutation resolvers
└── schema.py            # Schema configuration
```

### **Key Features**
1. **Authentication Integration**: Uses existing Firebase JWT middleware
2. **Tenant Isolation**: Automatic tenant context in all queries
3. **Error Handling**: Graceful error propagation from domain services
4. **Development Tools**: GraphiQL interface for testing and exploration

## 🔍 Development Workflow

### **Testing GraphQL Queries**
1. Start the development server: `uvicorn app.main:app --reload`
2. Navigate to `http://localhost:8000/graphql`
3. Use GraphiQL interface to build and test queries
4. View schema documentation in the right panel

### **Adding New Resolvers**
1. Define GraphQL types in `types.py`
2. Implement resolver logic in `resolvers.py`
3. Add to Query or Mutation classes
4. Test with GraphiQL interface

### **Frontend Integration**
Use generated TypeScript clients or libraries like Apollo Client:

```typescript
import { ApolloClient, InMemoryCache, gql } from '@apollo/client';

const client = new ApolloClient({
  uri: 'http://localhost:8000/graphql',
  cache: new InMemoryCache(),
  headers: {
    'Authorization': `Bearer ${firebaseToken}`
  }
});

const GET_DASHBOARD = gql`
  query GetDashboard {
    strategicIntelligenceDashboard {
      recentTruths { id statement confidence }
      pendingCommunications { id topic priority }
      systemHealth { status }
    }
  }
`;

const { data } = await client.query({ query: GET_DASHBOARD });
```

## 🚦 Benefits Over REST

### **For Dashboard Aggregation**
- **Single Request**: One GraphQL query vs multiple REST calls
- **Flexible Data**: Request only needed fields
- **Reduced Over-fetching**: Mobile-optimized responses

### **For Development**
- **Type Safety**: Full typing with TypeScript generation
- **Self-Documenting**: Schema serves as API documentation
- **Powerful Tooling**: GraphiQL for exploration and testing

### **For Production**
- **Efficient Queries**: Reduced network overhead
- **Caching**: Built-in query caching capabilities
- **Monitoring**: Detailed query analytics and performance metrics

## 🔗 REST vs GraphQL Usage

### **Use GraphQL For:**
- Complex dashboard queries requiring multiple data types
- Mobile applications needing optimized payloads
- Frontend applications with varying data requirements
- Exploratory data analysis and reporting

### **Keep REST For:**
- File uploads and downloads
- Simple CRUD operations
- External integrations and webhooks
- Health checks and monitoring

## 📈 Performance Considerations

- **N+1 Query Problem**: Resolved through domain service aggregation
- **Query Complexity**: Built-in depth limiting and timeout handling
- **Caching**: Leverages existing Redis caching from REST services
- **Rate Limiting**: Same rate limiting as REST endpoints

The GraphQL implementation provides a modern, flexible interface while maintaining all the reliability and performance characteristics of the underlying REST API.
