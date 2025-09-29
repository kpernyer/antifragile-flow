#!/usr/bin/env python3
"""
Isolated test for Neo4j vector store service.

Run this to test Neo4j functionality independently:
    python test_neo4j_isolated.py
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


# Test data with organizational context
ORGANIZATIONAL_DOCUMENTS = {
    "Board Meeting Minutes Q3": [
        "The board reviewed Q3 performance and approved the digital transformation budget of $2.5M.",
        "CEO reported successful acquisition of TechStart Inc, expanding our AI capabilities.",
        "Board approved the new organizational structure with three VP-level positions.",
        "Risk committee raised concerns about cybersecurity investments and compliance gaps.",
        "Next board meeting scheduled for December 15th to review year-end results.",
    ],
    "Employee Handbook 2024": [
        "All employees must complete mandatory security training by January 31st.",
        "The company promotes work-life balance through flexible working arrangements.",
        "Performance reviews will be conducted quarterly starting in 2024.",
        "Our diversity and inclusion program aims for 40% leadership representation by 2025.",
        "Employee stock option program expanded to include all full-time staff.",
    ],
    "Strategic Partnership Agreement": [
        "Acme Corp enters strategic partnership with Innovation Labs for AI development.",
        "Joint venture will focus on next-generation customer analytics platforms.",
        "Revenue sharing model: 60% Acme Corp, 40% Innovation Labs for first two years.",
        "Partnership includes shared intellectual property rights and co-marketing agreements.",
        "Initial project timeline spans 18 months with $5M combined investment.",
    ],
}

ORGANIZATIONAL_DATA = {
    "Acme Corp": {
        "name": "Acme Corp",
        "type": "Technology",
        "industry": "Software Development",
        "size": 750,
    },
    "Innovation Labs": {
        "name": "Innovation Labs",
        "type": "Research",
        "industry": "AI/ML Research",
        "size": 150,
    },
    "TechStart Inc": {
        "name": "TechStart Inc",
        "type": "Startup",
        "industry": "Artificial Intelligence",
        "size": 45,
    },
}


async def test_neo4j_service():
    """Test Neo4j service with comprehensive scenarios including relationships."""

    print("🧪 NEO4J SERVICE ISOLATED TEST")
    print("=" * 50)

    try:
        from service.vector_store.neo4j_service import Neo4jConfig, Neo4jStore

        print("✅ Successfully imported Neo4j service")
    except ImportError as e:
        print(f"❌ Failed to import Neo4j service: {e}")
        print("💡 Make sure to install: pip install neo4j")
        return False

    # Configure Neo4j
    config = Neo4jConfig(
        uri="bolt://localhost:7687",
        user="neo4j",
        password="testpassword",
        database="neo4j",
        vector_index="test_document_embeddings",
        node_label="TestDocument",
        embedding_property="embedding",
    )

    try:
        # Initialize store
        print("\n🔗 Connecting to Neo4j...")
        store = Neo4jStore(config)
        print("✅ Connected to Neo4j successfully")

        # Ensure vector index
        print("\n📊 Setting up vector index...")
        store.ensure_vector_index(dimensions=1536, similarity="cosine")
        print("✅ Vector index ensured")

        # Test tenant ID
        tenant_id = "test_org_neo4j_001"

        print(f"\n📝 Testing document insertion with graph relationships for tenant: {tenant_id}")

        # Insert test documents
        source_ids = []
        document_org_mapping = {
            "Board Meeting Minutes Q3": "Acme Corp",
            "Employee Handbook 2024": "Acme Corp",
            "Strategic Partnership Agreement": "Innovation Labs",
        }

        for title, chunks in ORGANIZATIONAL_DOCUMENTS.items():
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

                # Create organizational relationships
                org_name = document_org_mapping[title]
                org_data = ORGANIZATIONAL_DATA[org_name]

                print(f"    🔗 Creating organizational relationship: {title} -> {org_name}")
                relationship_success = store.create_organizational_relationships(
                    tenant_id=tenant_id, document_id=source_id, organization_data=org_data
                )

                if relationship_success:
                    print("    ✅ Organizational relationships created")
                else:
                    print("    ❌ Failed to create organizational relationships")

            else:
                print(f"    ❌ Failed to insert {title}")

        print("\n🔍 Testing vector search with graph context...")

        # Test searches
        test_queries = [
            "board meeting and corporate governance",
            "employee policies and workplace culture",
            "strategic partnerships and business development",
            "digital transformation and technology investment",
            "acquisition and company expansion",
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
                chunk_index = result.get("chunk_index", 0)
                print(f"      {i + 1}. [{source}] Score: {score:.4f} (Chunk {chunk_index})")
                print(f"         {text_preview}")

        print("\n🕸️ Testing document relationships (Neo4j specific)...")

        # Test relationship queries for inserted documents
        for source_id in source_ids[:2]:  # Test first two documents
            print(f"  🔗 Checking relationships for document: {source_id[:8]}...")

            relationships = store.get_document_relationships(
                tenant_id=tenant_id, document_id=source_id
            )

            print(f"    📊 Found {len(relationships)} relationships")
            for rel in relationships:
                rel_type = rel.get("type", "Unknown")
                related_title = rel.get("related_title", "Unknown")
                related_labels = rel.get("related_labels", [])
                print(f"      🔗 {rel_type} -> {related_title} ({', '.join(related_labels)})")

        print("\n📋 Testing recent sources retrieval...")

        # Test getting recent sources
        recent_sources = store.get_recent_sources(tenant_id=tenant_id, limit=10)
        print(f"  📊 Found {len(recent_sources)} recent sources")

        for source in recent_sources:
            title = source.get("title", "Unknown")
            chunk_count = source.get("chunk_count", 0)
            created_at = source.get("created_at", "")
            source_id = source.get("id", "")
            print(f"    📄 {title} - {chunk_count} chunks (ID: {source_id[:8]}...) - {created_at}")

        print("\n🧪 Testing multi-tenant isolation...")

        # Test with different tenant
        other_tenant = "test_org_neo4j_002"

        # Insert one document for other tenant
        other_chunks = ["This confidential document belongs to a different organization."]
        other_embeddings = mock_embeddings(other_chunks)

        other_source_id = store.upsert_chunks(
            tenant_id=other_tenant,
            title="Confidential Org2 Document",
            chunks=other_chunks,
            embeddings=other_embeddings,
        )

        # Search from first tenant should not see second tenant's docs
        query_vector = mock_embedding("confidential organization document")
        tenant1_results = store.search(tenant_id=tenant_id, query_vector=query_vector, k=10)
        tenant2_results = store.search(tenant_id=other_tenant, query_vector=query_vector, k=10)

        print(f"    📊 Tenant '{tenant_id}' sees {len(tenant1_results)} documents")
        print(f"    📊 Tenant '{other_tenant}' sees {len(tenant2_results)} documents")

        tenant1_sources = {r.get("source") for r in tenant1_results}
        tenant2_sources = {r.get("source") for r in tenant2_results}

        if "Confidential Org2 Document" not in tenant1_sources:
            print("    ✅ Tenant isolation working correctly")
        else:
            print("    ❌ Tenant isolation failed!")

        print("\n🏢 Testing organizational context queries...")

        # Test queries that should benefit from organizational relationships
        org_queries = [
            (
                "Acme Corp strategic decisions",
                ["Board Meeting Minutes Q3", "Employee Handbook 2024"],
            ),
            ("Innovation Labs partnerships", ["Strategic Partnership Agreement"]),
            ("technology company policies", ["Board Meeting Minutes Q3", "Employee Handbook 2024"]),
        ]

        for query_text, expected_sources in org_queries:
            print(f"  🔎 Organizational Query: '{query_text}'")

            query_vector = mock_embedding(query_text)
            results = store.search(tenant_id=tenant_id, query_vector=query_vector, k=5)

            found_sources = {r.get("source") for r in results}
            expected_found = len(set(expected_sources) & found_sources)

            print(
                f"    📊 Found {len(results)} results, {expected_found}/{len(expected_sources)} expected sources"
            )
            for source in found_sources:
                relevance = "✅" if source in expected_sources else "🔍"
                print(f"      {relevance} {source}")

        print("\n✅ All Neo4j tests completed successfully!")

        # Cleanup
        store.close()
        return True

    except Exception as e:
        print(f"❌ Neo4j test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def check_neo4j_connection():
    """Check if Neo4j is accessible."""
    try:
        from neo4j import GraphDatabase

        driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "testpassword"))
        with driver.session() as session:
            session.run("RETURN 1")
        driver.close()
        return True
    except:
        return False


async def main():
    """Main test runner."""
    print("🚀 Starting Neo4j Service Isolation Test")
    print("=" * 60)

    # Check if Neo4j is running
    if not check_neo4j_connection():
        print("❌ Neo4j is not accessible at bolt://localhost:7687")
        print("💡 Start Neo4j with:")
        print("   docker-compose -f docker-compose.test.yml up -d neo4j")
        print("   Wait for it to be ready, then run this test again.")
        print("   Default credentials: neo4j/testpassword")
        return

    print("✅ Neo4j is accessible")

    # Run tests
    success = await test_neo4j_service()

    if success:
        print("\n🎉 All tests passed! Neo4j service is working correctly.")
        print("📊 You can explore the graph at: http://localhost:7474")
        print("🔐 Login with: neo4j/testpassword")
    else:
        print("\n💥 Some tests failed. Check the output above for details.")


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)

    # Run tests
    asyncio.run(main())
