# 🚀 GraphQL Knowledge Base Server Setup

Complete setup guide for the Knowledge Base GraphQL server with centralized configuration management.

## 🎯 Overview

The GraphQL server provides a unified API for the Knowledge Base, offering:
- **Document search and retrieval**
- **Real-time subscriptions** for live updates
- **Full-text and semantic search**
- **Document processing workflows**
- **Integration with Temporal workflows**

## 📊 Configuration

### Default Values (Synchronized Across Languages)

| Service | Port | URL | Purpose |
|---------|------|-----|---------|
| **GraphQL Server** | `4000` | `http://localhost:4000` | Main GraphQL server |
| **GraphQL Endpoint** | `4000` | `http://localhost:4000/graphql` | GraphQL queries/mutations |
| **GraphQL Playground** | `4000` | `http://localhost:4000/playground` | Interactive schema explorer |
| **GraphQL Subscriptions** | `4000` | `ws://localhost:4000/graphql` | Real-time WebSocket |

### Environment Variables

```bash
# GraphQL Server Configuration
GRAPHQL_HOST=localhost
GRAPHQL_PORT=4000
GRAPHQL_URL=http://localhost:4000
GRAPHQL_ENDPOINT=http://localhost:4000/graphql
GRAPHQL_PLAYGROUND=http://localhost:4000/playground
GRAPHQL_SUBSCRIPTIONS=ws://localhost:4000/graphql

# Knowledge Base Features
KB_FULL_TEXT_SEARCH=true
KB_SEMANTIC_SEARCH=true
KB_SEARCH_LIMIT=50
KB_SEMANTIC_THRESHOLD=0.7
KB_DATABASE_BACKEND=postgresql
KB_VECTOR_DATABASE=pinecone

# Frontend Environment Variables (React)
REACT_APP_GRAPHQL_URL=http://localhost:4000
REACT_APP_GRAPHQL_ENDPOINT=http://localhost:4000/graphql
REACT_APP_GRAPHQL_SUBSCRIPTIONS=ws://localhost:4000/graphql
```

## 🐍 Python Backend Setup

### Basic Configuration

```python
from shared.config.defaults import get_graphql_endpoint, get_graphql_subscriptions_url
from shared.config.graphql_config import get_graphql_server_config, get_knowledge_base_config

# Get configuration
graphql_config = get_graphql_server_config("local")
kb_config = get_knowledge_base_config()

# Server URLs
graphql_endpoint = get_graphql_endpoint()  # http://localhost:4000/graphql
subscriptions_url = get_graphql_subscriptions_url()  # ws://localhost:4000/graphql

print(f"GraphQL server starting on {graphql_config.get_server_url()}")
print(f"Playground available at {graphql_config.get_playground_url()}")
```

### Server Implementation Example

```python
import asyncio
from ariadne import make_executable_schema, QueryType, SubscriptionType
from ariadne.asgi import GraphQL
from shared.config.graphql_config import get_graphql_server_config

# Initialize GraphQL server
config = get_graphql_server_config()

# Define your schema
type_defs = """
    type Query {
        searchDocuments(query: String!, limit: Int): [Document]
        getDocument(id: ID!): Document
    }

    type Subscription {
        documentUpdated(id: ID!): Document
    }

    type Document {
        id: ID!
        title: String!
        content: String!
        createdAt: String!
    }
"""

# Create executable schema
query = QueryType()
subscription = SubscriptionType()

@query.field("searchDocuments")
def resolve_search_documents(_, info, query: str, limit: int = 50):
    # Implement search logic using kb_config
    pass

@subscription.source("documentUpdated")
async def document_updated_generator(_, info, id: str):
    # Implement real-time updates
    pass

schema = make_executable_schema(type_defs, query, subscription)
app = GraphQL(schema, debug=config.debug)
```

### Database Integration

```python
from shared.config.graphql_config import get_knowledge_base_config
from shared.config.defaults import URLS

kb_config = get_knowledge_base_config()

# Database configuration
if kb_config.database_backend == "postgresql":
    DATABASE_URL = URLS.POSTGRES_LOCAL
elif kb_config.database_backend == "mongodb":
    DATABASE_URL = URLS.MONGODB_LOCAL

# Vector database for semantic search
if kb_config.vector_database == "pinecone":
    # Initialize Pinecone client
    pass
```

## ⚛️ TypeScript Frontend Setup

### Apollo Client Configuration

```typescript
import { ApolloClient, InMemoryCache, createHttpLink, split } from '@apollo/client';
import { WebSocketLink } from '@apollo/client/link/ws';
import { getMainDefinition } from '@apollo/client/utilities';
import {
  getGraphQLEndpoint,
  getGraphQLSubscriptionsUrl
} from '../config/defaults';

// HTTP link for queries and mutations
const httpLink = createHttpLink({
  uri: getGraphQLEndpoint(), // http://localhost:4000/graphql
});

// WebSocket link for subscriptions
const wsLink = new WebSocketLink({
  uri: getGraphQLSubscriptionsUrl(), // ws://localhost:4000/graphql
  options: {
    reconnect: true,
  },
});

// Split link based on operation type
const splitLink = split(
  ({ query }) => {
    const definition = getMainDefinition(query);
    return (
      definition.kind === 'OperationDefinition' &&
      definition.operation === 'subscription'
    );
  },
  wsLink,
  httpLink,
);

// Create Apollo Client
const client = new ApolloClient({
  link: splitLink,
  cache: new InMemoryCache(),
  defaultOptions: {
    watchQuery: {
      errorPolicy: 'all',
    },
  },
});

export default client;
```

### React Hook Examples

```typescript
import { useQuery, useMutation, useSubscription } from '@apollo/client';
import { gql } from '@apollo/client';

// Search documents
const SEARCH_DOCUMENTS = gql`
  query SearchDocuments($query: String!, $limit: Int) {
    searchDocuments(query: $query, limit: $limit) {
      id
      title
      content
      createdAt
    }
  }
`;

// Real-time document updates
const DOCUMENT_UPDATED = gql`
  subscription DocumentUpdated($id: ID!) {
    documentUpdated(id: $id) {
      id
      title
      content
      createdAt
    }
  }
`;

// React component
export const DocumentSearch: React.FC = () => {
  const { data, loading, error } = useQuery(SEARCH_DOCUMENTS, {
    variables: { query: "AI workflows", limit: 20 }
  });

  const { data: updateData } = useSubscription(DOCUMENT_UPDATED, {
    variables: { id: "doc-123" }
  });

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      {data?.searchDocuments?.map((doc) => (
        <div key={doc.id}>
          <h3>{doc.title}</h3>
          <p>{doc.content}</p>
        </div>
      ))}
    </div>
  );
};
```

## 🚀 Development Workflow

### 1. Start GraphQL Server

```bash
# Set environment variables
export GRAPHQL_PORT=4000
export KB_FULL_TEXT_SEARCH=true
export KB_SEMANTIC_SEARCH=true

# Start the GraphQL server
uv run python knowledge_base/graphql_server.py
```

### 2. Access GraphQL Playground

Visit `http://localhost:4000/playground` to:
- Explore the schema
- Test queries and mutations
- Debug GraphQL operations

### 3. Frontend Development

```bash
# In frontend directory
npm start

# Frontend will connect to GraphQL server automatically using centralized config
```

## 🔧 Configuration Management

### Environment-Specific Configs

```python
# Local development
config = get_graphql_server_config("local")
# - Debug mode enabled
# - Playground enabled
# - Introspection enabled
# - No rate limiting

# Production
config = get_graphql_server_config("production")
# - Debug mode disabled
# - Playground disabled
# - Introspection disabled
# - Rate limiting enabled
```

### Custom Configuration

```python
from shared.config.graphql_config import GraphQLServerConfig

custom_config = GraphQLServerConfig(
    host="0.0.0.0",
    port=4000,
    enable_playground=True,
    max_query_depth=20,
    cors_origins=["http://localhost:3000", "https://myapp.com"],
)
```

## 🧪 Testing

### Unit Tests

```python
def test_graphql_config():
    config = get_graphql_server_config("local")
    assert config.port == 4000
    assert config.enable_playground is True
    assert "http://localhost:3000" in config.cors_origins

def test_knowledge_base_config():
    kb_config = get_knowledge_base_config()
    assert kb_config.enable_full_text_search is True
    assert kb_config.search_results_limit == 50
```

### Integration Tests

```python
async def test_graphql_endpoint():
    import httpx
    from shared.config.defaults import get_graphql_endpoint

    async with httpx.AsyncClient() as client:
        response = await client.post(
            get_graphql_endpoint(),
            json={"query": "{ __schema { types { name } } }"}
        )
        assert response.status_code == 200
        assert "types" in response.json()["data"]["__schema"]
```

## 📊 Monitoring and Performance

### Metrics Configuration

```python
config = get_graphql_server_config()
if config.enable_metrics:
    # Prometheus metrics available at /metrics
    print(f"Metrics endpoint: {config.get_server_url()}/metrics")
```

### Query Performance

```python
kb_config = get_knowledge_base_config()
search_config = kb_config.get_search_config()

# Optimize based on configuration
if search_config["semantic_enabled"]:
    # Use vector database for semantic search
    pass
if search_config["full_text_enabled"]:
    # Use full-text search with boost factor
    pass
```

## 🔄 Integration with Temporal

### Workflow Integration

```python
from temporalio import activity
from shared.config.defaults import get_graphql_endpoint

@activity.defn
async def index_document_in_knowledge_base(document_id: str) -> bool:
    """Activity to index document in GraphQL Knowledge Base"""
    graphql_endpoint = get_graphql_endpoint()

    # Send GraphQL mutation to index document
    mutation = """
        mutation IndexDocument($id: ID!) {
            indexDocument(id: $id) {
                success
                message
            }
        }
    """

    # Implementation here...
    return True
```

## 🎯 Next Steps

1. **Implement GraphQL server** using the configuration system
2. **Set up schema and resolvers** for Knowledge Base operations
3. **Integrate with vector database** for semantic search
4. **Add real-time subscriptions** for live document updates
5. **Connect frontend** using Apollo Client with centralized URLs
6. **Set up monitoring and metrics** using the provided configuration

All configuration is now centralized and synchronized between Python backend and TypeScript frontend!
