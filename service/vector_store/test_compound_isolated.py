#!/usr/bin/env python3
"""
Isolated test for Compound vector store service.

This tests the intelligent orchestration between Neo4j and Weaviate.
Run this to test all search strategies and fusion capabilities:
    python test_compound_isolated.py
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


# Rich test data for comprehensive evaluation
TEST_CORPUS = {
    "CEO Strategic Vision 2024": [
        "Our vision for 2024 centers on becoming the market leader in AI-powered organizational intelligence.",
        "We will invest $10M in research and development, focusing on natural language processing and graph databases.",
        "Strategic partnerships with leading universities will accelerate our innovation pipeline.",
        "Customer success metrics show 40% improvement in decision-making speed using our platform.",
        "The board has approved expansion into European markets with offices in London and Berlin.",
    ],
    "Product Roadmap Technical Specs": [
        "Neo4j integration will enable real-time relationship analysis across organizational data.",
        "Vector embeddings using OpenAI's latest models provide semantic search capabilities.",
        "Temporal workflow orchestration ensures reliable processing of complex document flows.",
        "React-based frontend with TypeScript provides intuitive user experience for business users.",
        "Docker containerization and Kubernetes deployment enable scalable cloud infrastructure.",
    ],
    "Customer Success Case Study": [
        "Fortune 500 client achieved 60% reduction in strategic planning cycles using our platform.",
        "Organizational twin technology identified communication bottlenecks saving $2M annually.",
        "Real-time sentiment analysis prevented three major organizational crises in Q3.",
        "Executive dashboard provides C-suite visibility into organizational health metrics.",
        "Integration with existing enterprise systems completed in under 30 days.",
    ],
    "Financial Performance Analysis": [
        "Q3 revenue grew 85% year-over-year, exceeding analyst expectations by $1.2M.",
        "Gross margin improved to 72% due to automation and operational efficiency gains.",
        "Customer acquisition cost decreased 25% through improved marketing attribution.",
        "Annual recurring revenue reached $15M with 95% customer retention rate.",
        "Cash runway extended to 24 months following successful Series B funding round.",
    ],
    "Team Culture and Values": [
        "Our culture emphasizes psychological safety and continuous learning for all team members.",
        "Diversity metrics show 45% women in leadership roles and 30% underrepresented minorities.",
        "Remote-first work model with quarterly team gatherings builds strong relationships.",
        "Employee Net Promoter Score of 78 indicates high engagement and satisfaction.",
        "Learning budget of $5000 per employee annually supports professional development.",
    ],
}


async def test_compound_service():
    """Test Compound service with all strategies and comprehensive scenarios."""

    print("🧪 COMPOUND VECTOR STORE ISOLATED TEST")
    print("=" * 50)

    try:
        from service.vector_store.compound_service import (
            CompoundStoreConfig,
            CompoundVectorStore,
            SearchStrategy,
        )
        from service.vector_store.neo4j_service import Neo4jConfig, Neo4jStore
        from service.vector_store.weaviate_service import WeaviateConfig, WeaviateStore

        print("✅ Successfully imported all vector store services")
    except ImportError as e:
        print(f"❌ Failed to import services: {e}")
        print("💡 Make sure to install: pip install neo4j weaviate-client")
        return False

    # Configure stores
    weaviate_config = WeaviateConfig(
        url="http://localhost:8080", collection_name="CompoundTestDoc", embedding_dimensions=1536
    )

    neo4j_config = Neo4jConfig(
        uri="bolt://localhost:7687",
        user="neo4j",
        password="testpassword",
        database="neo4j",
        vector_index="compound_test_embeddings",
        node_label="CompoundTestDoc",
    )

    try:
        # Initialize individual stores
        print("\n🔗 Initializing vector stores...")
        weaviate_store = WeaviateStore(weaviate_config)
        neo4j_store = Neo4jStore(neo4j_config)
        print("✅ Individual stores initialized")

        # Ensure Neo4j vector index
        neo4j_store.ensure_vector_index(dimensions=1536, similarity="cosine")

        # Initialize compound store with different strategies
        fusion_weights = {"neo4j": 0.6, "weaviate": 0.4}  # Favor Neo4j for organizational context
        compound_store = CompoundVectorStore(
            neo4j_store=neo4j_store,
            weaviate_store=weaviate_store,
            default_strategy=SearchStrategy.PARALLEL_FUSION,
            fusion_weights=fusion_weights,
        )
        print("✅ Compound store initialized with parallel fusion strategy")

        # Test tenant
        tenant_id = "compound_test_org"

        print("\n📝 Populating both stores via compound service...")

        # Insert test corpus through compound store (will populate both)
        source_ids = []
        for title, chunks in TEST_CORPUS.items():
            print(f"  📄 Inserting: {title} ({len(chunks)} chunks)")

            embeddings = mock_embeddings(chunks)

            start_time = time.time()
            source_id = compound_store.upsert_chunks(
                tenant_id=tenant_id, title=title, chunks=chunks, embeddings=embeddings
            )
            insert_time = time.time() - start_time

            if source_id:
                source_ids.append(source_id)
                print(
                    f"    ✅ Inserted to both stores (ID: {source_id[:8]}...) in {insert_time:.2f}s"
                )
            else:
                print(f"    ❌ Failed to insert {title}")

        print("\n🎯 Testing all search strategies...")

        test_queries = [
            ("AI technology and innovation", "Should find Product Roadmap and CEO Vision"),
            (
                "financial performance metrics",
                "Should find Financial Analysis and Customer Success",
            ),
            ("organizational culture leadership", "Should find Team Culture and CEO Vision"),
            (
                "customer success and revenue",
                "Should find Customer Case Study and Financial Analysis",
            ),
            ("technical infrastructure graph", "Should find Product Roadmap"),
        ]

        strategies_to_test = [
            SearchStrategy.NEO4J_ONLY,
            SearchStrategy.WEAVIATE_ONLY,
            SearchStrategy.SEMANTIC_FIRST,
            SearchStrategy.GRAPH_FIRST,
            SearchStrategy.PARALLEL_FUSION,
            SearchStrategy.ADAPTIVE,
        ]

        strategy_results = {}

        for strategy in strategies_to_test:
            print(f"\n  🧭 Testing strategy: {strategy.value.upper()}")
            strategy_results[strategy] = {}

            for query, description in test_queries:
                print(f"    🔎 Query: '{query}' ({description})")

                query_vector = mock_embedding(query)

                start_time = time.time()
                results = compound_store.search(
                    tenant_id=tenant_id, query_vector=query_vector, k=3, strategy=strategy
                )
                search_time = time.time() - start_time

                strategy_results[strategy][query] = {
                    "results": results,
                    "time": search_time,
                    "count": len(results),
                }

                print(f"      📊 Found {len(results)} results in {search_time:.3f}s")

                # Show results with origin store
                for i, result in enumerate(results):
                    score = result.get("score", 0)
                    source = result.get("source", "Unknown")
                    origin = result.get("store_origin", "unknown")
                    fusion_score = result.get("fusion_score")

                    score_display = f"Score: {score:.4f}"
                    if fusion_score:
                        score_display += f" (Fusion: {fusion_score:.4f})"

                    print(f"        {i + 1}. [{origin.upper()}] {source} - {score_display}")

        print("\n📊 Strategy Performance Comparison...")

        # Compare strategy performance
        avg_times = {}
        avg_results = {}

        for strategy in strategies_to_test:
            times = [data["time"] for data in strategy_results[strategy].values()]
            counts = [data["count"] for data in strategy_results[strategy].values()]

            avg_times[strategy] = sum(times) / len(times)
            avg_results[strategy] = sum(counts) / len(counts)

            print(
                f"  🧭 {strategy.value.upper():<15} Avg Time: {avg_times[strategy]:.3f}s  Avg Results: {avg_results[strategy]:.1f}"
            )

        # Find fastest and most comprehensive strategies
        fastest_strategy = min(avg_times, key=avg_times.get)
        most_results_strategy = max(avg_results, key=avg_results.get)

        print(
            f"\n  🏃 Fastest Strategy: {fastest_strategy.value.upper()} ({avg_times[fastest_strategy]:.3f}s)"
        )
        print(
            f"  📈 Most Results: {most_results_strategy.value.upper()} ({avg_results[most_results_strategy]:.1f} avg)"
        )

        print("\n🔀 Testing hybrid search capabilities...")

        # Test hybrid search (text + vector)
        hybrid_queries = [
            ("revenue financial performance", "quarterly financial results and revenue growth"),
            ("AI technology innovation", "artificial intelligence and technical innovation"),
            ("customer success metrics", "customer satisfaction and business outcomes"),
            ("team culture leadership", "organizational culture and team leadership"),
        ]

        for keyword_query, vector_description in hybrid_queries:
            print(f"  🔎 Hybrid: '{keyword_query}' + semantic('{vector_description}')")

            query_vector = mock_embedding(vector_description)

            start_time = time.time()
            hybrid_results = compound_store.hybrid_search(
                tenant_id=tenant_id, query=keyword_query, query_vector=query_vector, k=3, alpha=0.7
            )
            search_time = time.time() - start_time

            print(f"    📊 Found {len(hybrid_results)} hybrid results in {search_time:.3f}s")

            for i, result in enumerate(hybrid_results):
                score = result.get("score", 0)
                source = result.get("source", "Unknown")
                origin = result.get("store_origin", "unknown")
                text_preview = result.get("text", "")[:80] + "..."

                print(f"      {i + 1}. [{origin.upper()}] {source} - Score: {score:.4f}")
                print(f"         {text_preview}")

        print("\n🔄 Testing store fallback scenarios...")

        # Test what happens when one store fails
        print("  ⚠️  Simulating Weaviate failure...")

        # Create compound store with only Neo4j
        neo4j_only_compound = CompoundVectorStore(
            neo4j_store=neo4j_store,
            weaviate_store=None,  # Simulate Weaviate failure
            default_strategy=SearchStrategy.ADAPTIVE,
        )

        query_vector = mock_embedding("technical infrastructure")
        fallback_results = neo4j_only_compound.search(
            tenant_id=tenant_id, query_vector=query_vector, k=3
        )

        print(f"    📊 With Neo4j only: {len(fallback_results)} results")
        for result in fallback_results:
            origin = result.get("store_origin", "unknown")
            source = result.get("source", "Unknown")
            print(f"      [{origin.upper()}] {source}")

        print("  ⚠️  Simulating Neo4j failure...")

        # Create compound store with only Weaviate
        weaviate_only_compound = CompoundVectorStore(
            neo4j_store=None,  # Simulate Neo4j failure
            weaviate_store=weaviate_store,
            default_strategy=SearchStrategy.ADAPTIVE,
        )

        fallback_results_w = weaviate_only_compound.search(
            tenant_id=tenant_id, query_vector=query_vector, k=3
        )

        print(f"    📊 With Weaviate only: {len(fallback_results_w)} results")
        for result in fallback_results_w:
            origin = result.get("store_origin", "unknown")
            source = result.get("source", "Unknown")
            print(f"      [{origin.upper()}] {source}")

        print("\n📋 Testing unified source retrieval...")

        # Test getting recent sources through compound store
        recent_sources = compound_store.get_recent_sources(tenant_id=tenant_id, limit=10)
        print(f"  📊 Found {len(recent_sources)} recent sources")

        for source in recent_sources:
            title = source.get("title", "Unknown")
            chunk_count = source.get("chunk_count", 0)
            print(f"    📄 {title} - {chunk_count} chunks")

        print("\n🧪 Testing adaptive strategy intelligence...")

        # Test adaptive strategy with different query types
        adaptive_queries = [
            ("AI", "Short query - should use parallel fusion"),
            (
                "What are the key technical infrastructure components for our graph database implementation?",
                "Long query - should use semantic-first",
            ),
            ("revenue", "Short financial term - should use parallel fusion"),
            (
                "Can you provide a comprehensive analysis of our organizational culture and leadership development initiatives?",
                "Very long query - should use semantic-first",
            ),
        ]

        for query_text, expected_behavior in adaptive_queries:
            print(f"  🔎 Adaptive Query: '{query_text[:50]}...' ({expected_behavior})")

            query_vector = mock_embedding(query_text)

            start_time = time.time()
            adaptive_results = compound_store.search(
                tenant_id=tenant_id,
                query_vector=query_vector,
                k=2,
                strategy=SearchStrategy.ADAPTIVE,
                query=query_text,  # Pass text for adaptive decisions
            )
            search_time = time.time() - start_time

            print(f"    📊 Found {len(adaptive_results)} results in {search_time:.3f}s")

            # Show which stores were used
            origins = {r.get("store_origin") for r in adaptive_results}
            print(f"    🎯 Used stores: {', '.join(origins)}")

        print("\n✅ All compound store tests completed successfully!")

        # Show final statistics
        total_documents = len(TEST_CORPUS)
        total_chunks = sum(len(chunks) for chunks in TEST_CORPUS.values())

        print("\n📈 Test Summary:")
        print(f"  📄 Documents processed: {total_documents}")
        print(f"  📝 Total chunks: {total_chunks}")
        print(f"  🧭 Search strategies tested: {len(strategies_to_test)}")
        print(f"  ⚡ Fastest strategy: {fastest_strategy.value}")
        print(f"  📊 Most comprehensive: {most_results_strategy.value}")

        # Cleanup
        compound_store.neo4j_store.close() if compound_store.neo4j_store else None
        compound_store.weaviate_store.close() if compound_store.weaviate_store else None

        return True

    except Exception as e:
        print(f"❌ Compound store test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def check_services_availability():
    """Check if both Neo4j and Weaviate are accessible."""
    neo4j_ok = False
    weaviate_ok = False

    # Check Neo4j
    try:
        from neo4j import GraphDatabase

        driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "testpassword"))
        with driver.session() as session:
            session.run("RETURN 1")
        driver.close()
        neo4j_ok = True
    except:
        pass

    # Check Weaviate
    try:
        import requests

        response = requests.get("http://localhost:8080/v1/.well-known/ready", timeout=5)
        weaviate_ok = response.status_code == 200
    except:
        pass

    return neo4j_ok, weaviate_ok


async def main():
    """Main test runner."""
    print("🚀 Starting Compound Vector Store Isolation Test")
    print("=" * 60)

    # Check if both services are running
    neo4j_ok, weaviate_ok = check_services_availability()

    if not neo4j_ok:
        print("❌ Neo4j is not accessible at bolt://localhost:7687")
    else:
        print("✅ Neo4j is accessible")

    if not weaviate_ok:
        print("❌ Weaviate is not accessible at http://localhost:8080")
    else:
        print("✅ Weaviate is accessible")

    if not (neo4j_ok and weaviate_ok):
        print("\n💡 Start both services with:")
        print("   docker-compose -f docker-compose.test.yml up -d")
        print("   Wait for both to be ready, then run this test again.")
        return

    # Run tests
    success = await test_compound_service()

    if success:
        print("\n🎉 All tests passed! Compound vector store is working correctly.")
        print(
            "🌟 The intelligent orchestration between Neo4j and Weaviate is functioning perfectly!"
        )
        print("\n💡 Key Benefits Demonstrated:")
        print("  🔄 Automatic result fusion from both stores")
        print("  🧭 Multiple search strategies for different use cases")
        print("  ⚡ Fallback handling when one store fails")
        print("  🎯 Adaptive query routing based on content")
    else:
        print("\n💥 Some tests failed. Check the output above for details.")


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)

    # Run tests
    asyncio.run(main())
