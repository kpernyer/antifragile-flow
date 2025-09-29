# Vector Store Services - Testing Guide

Complete testing suite for isolated validation of Neo4j, Weaviate, and Compound vector store services.

## 🚀 Quick Start

### Option 1: Automated Setup & Test
```bash
cd service/vector_store
./setup_and_test.sh
```

This single script will:
- ✅ Check dependencies
- 🐳 Start Docker services
- ⏳ Wait for services to be ready
- 🧪 Run all tests automatically
- 📊 Show comprehensive results

### Option 2: Manual Setup
```bash
# 1. Start services
docker-compose -f docker-compose.test.yml up -d

# 2. Wait for services (check health at URLs below)
# Neo4j: http://localhost:7474 (neo4j/testpassword)
# Weaviate: http://localhost:8080/v1/.well-known/ready

# 3. Install dependencies
pip install neo4j weaviate-client requests

# 4. Run master test suite
python run_all_tests.py
```

### Option 3: Individual Tests
```bash
# Test Weaviate service only
python test_weaviate_isolated.py

# Test Neo4j service only
python test_neo4j_isolated.py

# Test Compound service only (requires both databases)
python test_compound_isolated.py
```

## 🧪 Test Coverage

### Weaviate Service Test (`test_weaviate_isolated.py`)
- ✅ **Connection & Schema Creation**: Verifies Weaviate connectivity and collection setup
- ✅ **Document Insertion**: Tests batch chunk insertion with embeddings
- ✅ **Vector Search**: Semantic similarity search with configurable K
- ✅ **Hybrid Search**: Combined vector + keyword search with alpha weighting
- ✅ **Multi-Tenant Isolation**: Ensures tenant data separation
- ✅ **Recent Sources**: Retrieval of recently ingested documents
- ✅ **Performance Metrics**: Insertion and search timing

**Sample Test Data:**
- Strategic planning documents
- Financial reports
- Organizational restructuring memos

### Neo4j Service Test (`test_neo4j_isolated.py`)
- ✅ **Graph Database Connection**: Neo4j driver connectivity and auth
- ✅ **Vector Index Creation**: Automated vector index setup with optimal config
- ✅ **Document Storage**: Graph-based document chunk storage
- ✅ **Organizational Relationships**: Entity relationship creation and modeling
- ✅ **Graph-Aware Search**: Vector search with relationship context
- ✅ **Relationship Queries**: Document-to-organization relationship traversal
- ✅ **Multi-Tenant Graph Isolation**: Tenant separation in graph queries
- ✅ **Organizational Intelligence**: Context-aware search results

**Sample Test Data:**
- Board meeting minutes with organizational context
- Employee handbooks linked to company entities
- Partnership agreements with relationship modeling

### Compound Service Test (`test_compound_isolated.py`)
- ✅ **Multi-Store Orchestration**: Coordinated Neo4j + Weaviate operations
- ✅ **Search Strategy Testing**: All 6 strategic routing approaches
- ✅ **Reciprocal Rank Fusion**: Advanced result combination algorithm
- ✅ **Performance Comparison**: Strategy benchmarking and optimization
- ✅ **Adaptive Query Routing**: Intelligent strategy selection
- ✅ **Hybrid Search Orchestration**: Cross-store hybrid search capabilities
- ✅ **Fallback Scenarios**: Graceful degradation when stores fail
- ✅ **Fusion Weight Optimization**: Configurable result weighting

**Search Strategies Tested:**
1. **NEO4J_ONLY**: Pure graph-based search
2. **WEAVIATE_ONLY**: Pure semantic search
3. **SEMANTIC_FIRST**: Weaviate primary, Neo4j supplement
4. **GRAPH_FIRST**: Neo4j primary, Weaviate supplement
5. **PARALLEL_FUSION**: Simultaneous query with RRF combination
6. **ADAPTIVE**: Automatic strategy selection based on query characteristics

## 📊 Expected Results

### Performance Benchmarks
- **Weaviate**: ~0.050s average search time (semantic)
- **Neo4j**: ~0.100s average search time (with relationships)
- **Compound Parallel Fusion**: ~0.150s (comprehensive results)
- **Compound Semantic First**: ~0.075s (fast with fallback)

### Accuracy Metrics
- **Multi-tenant isolation**: 100% separation
- **Relationship accuracy**: Organizational context preserved
- **Result fusion**: Eliminates duplicates, ranks relevance
- **Fallback reliability**: Graceful degradation to available store

## 🔧 Troubleshooting

### Common Issues

**"Connection refused" errors:**
```bash
# Check if services are running
docker-compose -f docker-compose.test.yml ps

# Restart services
docker-compose -f docker-compose.test.yml restart

# Check logs
docker-compose -f docker-compose.test.yml logs neo4j
docker-compose -f docker-compose.test.yml logs weaviate
```

**"Import errors" for neo4j or weaviate:**
```bash
# Install missing dependencies
pip install neo4j weaviate-client

# Or install all project dependencies
pip install -r ../../requirements.txt  # if exists
```

**Services slow to start:**
```bash
# Give services more time (especially on slower machines)
sleep 60

# Check service health manually
curl http://localhost:8080/v1/.well-known/ready
docker exec antifragile-neo4j-test cypher-shell -u neo4j -p testpassword "RETURN 1"
```

**Port conflicts:**
```bash
# Check what's using the ports
lsof -i :7474  # Neo4j HTTP
lsof -i :7687  # Neo4j Bolt
lsof -i :8080  # Weaviate

# Stop conflicting services or modify docker-compose.test.yml ports
```

### Service Access

**Neo4j Browser:** http://localhost:7474
- Username: `neo4j`
- Password: `testpassword`
- Explore graph relationships and run Cypher queries

**Weaviate Console:** http://localhost:8080/v1
- No authentication required for local testing
- API documentation and schema exploration

### Data Persistence

Test data is ephemeral by design:
- **Docker volumes**: Cleared between test runs
- **Collections/Indexes**: Recreated each test
- **Test data**: Synthetic organizational documents

For persistent testing, modify `docker-compose.test.yml` to use named volumes.

## 🎯 Integration Examples

### Using in DocumentProcessing Workflow

```python
from service.vector_store import CompoundVectorStore, SearchStrategy

async def enhanced_document_processing():
    # Initialize compound store (inject via DI in production)
    compound_store = CompoundVectorStore(
        neo4j_store=neo4j_store,
        weaviate_store=weaviate_store,
        default_strategy=SearchStrategy.GRAPH_FIRST  # Organizational focus
    )

    # Process document with organizational intelligence
    source_id = await compound_store.upsert_chunks(
        tenant_id="acme_corp_2024",
        title="Strategic Plan Q4",
        chunks=document_chunks,
        embeddings=embeddings
    )

    # Search for related organizational context
    context_results = await compound_store.search(
        tenant_id="acme_corp_2024",
        query_vector=query_embedding,
        k=10,
        strategy=SearchStrategy.PARALLEL_FUSION
    )

    return enhanced_analysis_with_context(document, context_results)
```

## 🔮 Next Steps

After successful testing:

1. **Production Configuration**: Replace test credentials and URLs
2. **Real Embeddings**: Integrate OpenAI, HuggingFace, or custom embeddings
3. **Monitoring**: Add logging, metrics, and health checks
4. **Workflow Integration**: Connect to DocumentProcessing activities
5. **Performance Tuning**: Optimize fusion weights for your domain
6. **Knowledge Graph Import**: Use aprio-one knowledge-representation data

The test suite validates that your vector store architecture is ready for production organizational intelligence workflows!
