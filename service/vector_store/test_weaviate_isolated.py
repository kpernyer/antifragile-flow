#!/usr/bin/env python3
"""
Isolated test for Weaviate vector store service.

Run this to test Weaviate functionality independently:
    python test_weaviate_isolated.py
"""

import asyncio
import logging
from pathlib import Path
import random
import sys
import time

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


# Mock embeddings for testing (replace with real embeddings in production)
def mock_embedding(text: str, dimensions: int = 1536) -> list[float]:
    """Generate a mock embedding vector for testing."""
    # Create a pseudo-random but consistent embedding based on text
    random.seed(hash(text) % (2**32))
    return [random.uniform(-1, 1) for _ in range(dimensions)]


def mock_embeddings(texts: list[str], dimensions: int = 1536) -> list[list[float]]:
    """Generate mock embeddings for a list of texts."""
    return [mock_embedding(text, dimensions) for text in texts]


# Test data
SAMPLE_DOCUMENTS = {
    "Strategic Plan 2024": [
        "Our company's strategic vision for 2024 focuses on digital transformation and market expansion.",
        "Key initiatives include cloud migration, AI integration, and customer experience enhancement.",
        "We aim to increase market share by 25% through innovative product development.",
        "Investment in talent acquisition and retention remains a top priority.",
        "Sustainability goals include carbon neutrality by 2025 and renewable energy adoption.",
    ],
    "Q3 Financial Report": [
        "Revenue for Q3 2024 exceeded expectations with a 15% growth over the previous quarter.",
        "Operating expenses decreased by 8% due to efficiency improvements and cost optimization.",
        "Cash flow remains strong with improved working capital management.",
        "Investment in R&D increased by 12% to support innovation initiatives.",
        "Earnings per share grew to $2.85, beating analyst estimates by $0.15.",
    ],
    "Team Restructuring Memo": [
        "Effective immediately, we are implementing a new organizational structure.",
        "Three new cross-functional teams will be established to improve collaboration.",
        "The Product Development team will report directly to the CTO.",
        "Marketing and Sales teams will be consolidated under a unified Revenue Operations leader.",
        "All team leads are expected to complete transition planning by month-end.",
    ],
}


async def test_weaviate_service():
    """Test Weaviate service with comprehensive scenarios."""

    print("🧪 WEAVIATE SERVICE ISOLATED TEST")
    print("=" * 50)

    try:
        from service.vector_store.weaviate_service import WeaviateConfig, WeaviateStore

        print("✅ Successfully imported Weaviate service")
    except ImportError as e:
        print(f"❌ Failed to import Weaviate service: {e}")
        print("💡 Make sure to install: pip install weaviate-client")
        return False

    # Configure Weaviate
    config = WeaviateConfig(
        url="http://localhost:8080", collection_name="AntifragileTestDoc", embedding_dimensions=1536
    )

    try:
        # Initialize store
        print("\n🔗 Connecting to Weaviate...")
        store = WeaviateStore(config)
        print("✅ Connected to Weaviate successfully")

        # Test tenant ID
        tenant_id = "test_org_001"

        print(f"\n📝 Testing document insertion for tenant: {tenant_id}")

        # Insert test documents
        source_ids = []
        for title, chunks in SAMPLE_DOCUMENTS.items():
            print(f"  📄 Inserting: {title} ({len(chunks)} chunks)")

            # Generate embeddings
            embeddings = mock_embeddings(chunks)

            # Insert chunks
            start_time = time.time()
            source_id = store.upsert_chunks(
                tenant_id=tenant_id, title=title, chunks=chunks, embeddings=embeddings
            )
            insert_time = time.time() - start_time

            if source_id:
                source_ids.append(source_id)
                print(
                    f"    ✅ Inserted successfully (ID: {source_id[:8]}...) in {insert_time:.2f}s"
                )
            else:
                print(f"    ❌ Failed to insert {title}")

        print("\n🔍 Testing vector search...")

        # Test searches
        test_queries = [
            "strategic planning and market expansion",
            "financial performance and revenue growth",
            "team restructuring and organizational changes",
            "digital transformation initiatives",
            "sustainability and environmental goals",
        ]

        for query in test_queries:
            print(f"  🔎 Query: '{query}'")

            # Generate query vector
            query_vector = mock_embedding(query)

            # Perform search
            start_time = time.time()
            results = store.search(tenant_id=tenant_id, query_vector=query_vector, k=3)
            search_time = time.time() - start_time

            print(f"    📊 Found {len(results)} results in {search_time:.3f}s")

            # Display top results
            for i, result in enumerate(results):
                score = result.get("score", 0)
                text_preview = result.get("text", "")[:100] + "..."
                source = result.get("source", "Unknown")
                print(f"      {i + 1}. [{source}] Score: {score:.4f}")
                print(f"         {text_preview}")

        print("\n🔀 Testing hybrid search...")

        # Test hybrid search (vector + keyword)
        hybrid_queries = [
            ("financial growth revenue", "quarterly financial results"),
            ("team restructuring organization", "organizational changes and team structure"),
            ("strategic digital transformation", "digital strategy and innovation"),
        ]

        for keyword_query, vector_query in hybrid_queries:
            print(f"  🔎 Hybrid Query: '{keyword_query}' + vector('{vector_query}')")

            query_vector = mock_embedding(vector_query)

            start_time = time.time()
            results = store.hybrid_search(
                tenant_id=tenant_id,
                query=keyword_query,
                query_vector=query_vector,
                k=2,
                alpha=0.7,  # 70% vector, 30% keyword
            )
            search_time = time.time() - start_time

            print(f"    📊 Found {len(results)} hybrid results in {search_time:.3f}s")

            for i, result in enumerate(results):
                score = result.get("score", 0)
                source = result.get("source", "Unknown")
                text_preview = result.get("text", "")[:80] + "..."
                print(f"      {i + 1}. [{source}] Score: {score:.4f} - {text_preview}")

        print("\n📋 Testing recent sources retrieval...")

        # Test getting recent sources
        recent_sources = store.get_recent_sources(tenant_id=tenant_id, limit=10)
        print(f"  📊 Found {len(recent_sources)} recent sources")

        for source in recent_sources:
            title = source.get("title", "Unknown")
            chunk_count = source.get("chunk_count", 0)
            created_at = source.get("created_at", "")
            doc_type = source.get("document_type", "")
            print(f"    📄 {title} - {chunk_count} chunks ({doc_type}) - {created_at}")

        print("\n🧪 Testing multi-tenant isolation...")

        # Test with different tenant
        other_tenant = "test_org_002"

        # Insert one document for other tenant
        other_chunks = ["This is a document for a different organization."]
        other_embeddings = mock_embeddings(other_chunks)

        other_source_id = store.upsert_chunks(
            tenant_id=other_tenant,
            title="Other Org Document",
            chunks=other_chunks,
            embeddings=other_embeddings,
        )

        # Search from first tenant should not see second tenant's docs
        query_vector = mock_embedding("organization document")
        tenant1_results = store.search(tenant_id=tenant_id, query_vector=query_vector, k=10)
        tenant2_results = store.search(tenant_id=other_tenant, query_vector=query_vector, k=10)

        print(f"    📊 Tenant '{tenant_id}' sees {len(tenant1_results)} documents")
        print(f"    📊 Tenant '{other_tenant}' sees {len(tenant2_results)} documents")

        tenant1_sources = {r.get("source") for r in tenant1_results}
        tenant2_sources = {r.get("source") for r in tenant2_results}

        if "Other Org Document" not in tenant1_sources:
            print("    ✅ Tenant isolation working correctly")
        else:
            print("    ❌ Tenant isolation failed!")

        print("\n✅ All Weaviate tests completed successfully!")

        # Cleanup
        store.close()
        return True

    except Exception as e:
        print(f"❌ Weaviate test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def check_weaviate_connection():
    """Check if Weaviate is accessible."""
    try:
        import requests

        response = requests.get("http://localhost:8080/v1/.well-known/ready", timeout=5)
        return response.status_code == 200
    except:
        return False


async def main():
    """Main test runner."""
    print("🚀 Starting Weaviate Service Isolation Test")
    print("=" * 60)

    # Check if Weaviate is running
    if not check_weaviate_connection():
        print("❌ Weaviate is not accessible at http://localhost:8080")
        print("💡 Start Weaviate with:")
        print("   docker-compose -f docker-compose.test.yml up -d weaviate")
        print("   Wait for it to be ready, then run this test again.")
        return

    print("✅ Weaviate is accessible")

    # Run tests
    success = await test_weaviate_service()

    if success:
        print("\n🎉 All tests passed! Weaviate service is working correctly.")
    else:
        print("\n💥 Some tests failed. Check the output above for details.")


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)

    # Run tests
    asyncio.run(main())
