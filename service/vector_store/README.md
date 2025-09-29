# Vector Store Services

Comprehensive vector store services for the Antifragile Flow organizational twin system, supporting both Neo4j graph-based relationships and Weaviate semantic search.

## Architecture

The vector store system provides three separate services that can work independently or together:

### 🌐 **Weaviate Service** (`weaviate_service.py`)
- **Fast semantic search** with HNSW indexing
- **Hybrid search** combining vector + keyword matching
- **Optimized for chunking** and document retrieval
- **Multi-tenant support** with proper isolation

### 🕸️ **Neo4j Service** (`neo4j_service.py`)
- **Graph-based vector search** with relationship context
- **Organizational intelligence** through connected data
- **Document relationships** and entity linking
- **Perfect for organizational twin** knowledge graphs

### 🧠 **Compound Service** (`compound_service.py`)
- **Intelligent orchestration** between Neo4j and Weaviate
- **Multiple search strategies** (semantic-first, graph-first, parallel fusion)
- **Reciprocal Rank Fusion** for optimal result combination
- **Adaptive routing** based on query characteristics

## Quick Start

### 1. Basic Weaviate Usage

```python
from service.vector_store import WeaviateStore, WeaviateConfig

# Configure Weaviate
config = WeaviateConfig(
    url="http://localhost:8080",
    collection_name="AntifragileDoc",
    embedding_dimensions=1536
)

# Initialize store
weaviate_store = WeaviateStore(config)

# Insert document chunks
embeddings = get_embeddings(chunks)  # Your embedding function
source_id = weaviate_store.upsert_chunks(
    tenant_id="org_123",
    title="Strategic Plan 2024",
    chunks=chunks,
    embeddings=embeddings
)

# Search for similar content
query_vector = get_embedding("organizational strategy")
results = weaviate_store.search(
    tenant_id="org_123",
    query_vector=query_vector,
    k=5
)

# Hybrid search (vector + keyword)
hybrid_results = weaviate_store.hybrid_search(
    tenant_id="org_123",
    query="strategic planning process",
    query_vector=query_vector,
    k=5,
    alpha=0.7  # 70% vector, 30% keyword
)
```

### 2. Basic Neo4j Usage

```python
from service.vector_store import Neo4jStore, Neo4jConfig

# Configure Neo4j
config = Neo4jConfig(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password",
    database="neo4j",
    vector_index="document_embeddings"
)

# Initialize store
neo4j_store = Neo4jStore(config)

# Ensure vector index exists
neo4j_store.ensure_vector_index(dimensions=1536, similarity="cosine")

# Insert with relationships
source_id = neo4j_store.upsert_chunks(
    tenant_id="org_123",
    title="Board Meeting Minutes",
    chunks=chunks,
    embeddings=embeddings
)

# Create organizational context
neo4j_store.create_organizational_relationships(
    tenant_id="org_123",
    document_id=source_id,
    organization_data={
        "name": "Acme Corp",
        "type": "Technology",
        "industry": "Software",
        "size": 500
    }
)

# Search with graph context
results = neo4j_store.search(
    tenant_id="org_123",
    query_vector=query_vector,
    k=5
)
```

### 3. Compound Store Usage (Recommended)

```python
from service.vector_store import (
    CompoundVectorStore,
    SearchStrategy,
    WeaviateStore,
    Neo4jStore
)

# Initialize both stores
weaviate_store = WeaviateStore(weaviate_config)
neo4j_store = Neo4jStore(neo4j_config)

# Create compound store
compound_store = CompoundVectorStore(
    neo4j_store=neo4j_store,
    weaviate_store=weaviate_store,
    default_strategy=SearchStrategy.PARALLEL_FUSION,
    fusion_weights={"neo4j": 0.6, "weaviate": 0.4}
)

# Insert to both stores automatically
source_id = compound_store.upsert_chunks(
    tenant_id="org_123",
    title="Quarterly Report",
    chunks=chunks,
    embeddings=embeddings
)

# Intelligent search with multiple strategies
results = compound_store.search(
    tenant_id="org_123",
    query_vector=query_vector,
    k=5,
    strategy=SearchStrategy.ADAPTIVE  # Chooses best strategy
)

# Hybrid search across both stores
hybrid_results = compound_store.hybrid_search(
    tenant_id="org_123",
    query="organizational transformation",
    query_vector=query_vector,
    k=5
)
```

## Search Strategies

The compound store supports multiple search strategies:

### `SEMANTIC_FIRST`
- Use Weaviate for fast semantic search first
- Supplement with Neo4j if more results needed
- Best for: General document retrieval

### `GRAPH_FIRST`
- Use Neo4j for relationship-aware search first
- Supplement with Weaviate for completeness
- Best for: Organizational context queries

### `PARALLEL_FUSION`
- Query both stores simultaneously
- Combine results using Reciprocal Rank Fusion
- Best for: Comprehensive search results

### `ADAPTIVE`
- Automatically choose strategy based on query
- Long queries → semantic-first
- Short queries → parallel fusion
- Best for: General-purpose applications

## Integration with Document Processing

### Example Activity Integration

```python
from activity.document_activities import DocumentInfo, DocumentSummaryResult
from service.vector_store import CompoundVectorStore, SearchStrategy

async def enhanced_document_analysis(
    document_info: DocumentInfo,
    compound_store: CompoundVectorStore
) -> DocumentSummaryResult:
    """
    Enhanced document analysis using both semantic and graph context.
    """

    # Extract and chunk document
    content = await extract_document_content(document_info)
    chunks = chunk_document(content)
    embeddings = await get_embeddings(chunks)

    # Store in both vector stores
    source_id = compound_store.upsert_chunks(
        tenant_id=document_info.tenant_id,
        title=document_info.file_name,
        chunks=chunks,
        embeddings=embeddings
    )

    # Search for related content using hybrid approach
    query_vector = await get_embedding(f"similar to {document_info.file_name}")
    related_docs = compound_store.search(
        tenant_id=document_info.tenant_id,
        query_vector=query_vector,
        k=10,
        strategy=SearchStrategy.GRAPH_FIRST  # Prioritize organizational context
    )

    # Generate summary with context
    context = "\n".join([doc["text"] for doc in related_docs])
    summary = await generate_contextual_summary(content, context)

    return DocumentSummaryResult(
        document_info=document_info,
        short_summary=summary,
        key_takeaways=extract_takeaways(content, context),
        main_topics=identify_topics(content),
        markdown_report=generate_report(content, related_docs),
        confidence_score=calculate_confidence(related_docs)
    )
```

## Dependencies

### Required
```bash
pip install neo4j  # For Neo4j service
pip install weaviate-client  # For Weaviate service
```

### Optional (automatically detected)
- Services gracefully handle missing dependencies
- Will raise ImportError with helpful message if needed

## Configuration

### Environment Variables
```bash
# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password
NEO4J_DATABASE=neo4j

# Weaviate
WEAVIATE_URL=http://localhost:8080
WEAVIATE_API_KEY=your-api-key  # Optional for local
WEAVIATE_COLLECTION=AntifragileDoc
```

## Best Practices

### 1. **Use Compound Store for Production**
- Combines the best of both worlds
- Automatic fallback handling
- Intelligent result fusion

### 2. **Choose Strategy Based on Use Case**
- `GRAPH_FIRST`: Organizational queries, relationship-heavy content
- `SEMANTIC_FIRST`: General document search, content discovery
- `PARALLEL_FUSION`: When you need the most comprehensive results
- `ADAPTIVE`: General-purpose, let the system decide

### 3. **Optimize for Your Data**
- Adjust fusion weights based on your content type
- Neo4j weight higher for relationship-heavy domains
- Weaviate weight higher for semantic similarity tasks

### 4. **Monitor Performance**
- Use store_origin in results to understand which store is performing better
- Adjust strategies based on query patterns
- Consider caching for frequently accessed content

## Future Enhancements

- **Vector index optimization** for different embedding models
- **Dynamic fusion weight adjustment** based on query performance
- **Advanced organizational relationship modeling** from the knowledge-representation project
- **Real-time similarity threshold tuning**
- **Multi-modal support** for images and documents

This vector store system provides the foundation for sophisticated organizational intelligence, combining the speed of Weaviate with the relationship intelligence of Neo4j.
