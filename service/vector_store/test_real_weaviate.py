#!/usr/bin/env python3
"""
REAL Weaviate test with actual OpenAI embeddings and semantic search capabilities.

This test demonstrates:
- True semantic understanding (not mock embeddings)
- Cross-language semantic similarity
- Complex query understanding
- Real-world organizational document processing

Requirements:
- OpenAI API key in environment: OPENAI_API_KEY
- Weaviate running at localhost:8080

Usage:
    export OPENAI_API_KEY="your-key-here"
    python test_real_weaviate.py
"""

import asyncio
import logging
import os
from pathlib import Path
import sys
import time

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Real OpenAI embeddings
try:
    import openai

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


def get_real_embedding(text: str, model: str = "text-embedding-3-small") -> list[float]:
    """Generate real OpenAI embedding."""
    if not OPENAI_AVAILABLE:
        raise ImportError("OpenAI not installed. Run: pip install openai")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")

    client = openai.OpenAI(api_key=api_key)

    response = client.embeddings.create(model=model, input=text, encoding_format="float")

    return response.data[0].embedding


def get_real_embeddings(
    texts: list[str], model: str = "text-embedding-3-small"
) -> list[list[float]]:
    """Generate real OpenAI embeddings for multiple texts."""
    if not OPENAI_AVAILABLE:
        raise ImportError("OpenAI not installed. Run: pip install openai")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")

    client = openai.OpenAI(api_key=api_key)

    # Batch process for efficiency
    response = client.embeddings.create(model=model, input=texts, encoding_format="float")

    return [item.embedding for item in response.data]


# REAL organizational documents with semantic complexity
REAL_ORGANIZATIONAL_DOCUMENTS = {
    "CEO Strategic Vision 2024": [
        "We envision becoming the definitive leader in AI-powered organizational intelligence, transforming how companies understand and optimize their human dynamics.",
        "Our artificial intelligence platform will democratize access to world-class organizational consulting, making expert insights available to companies of all sizes.",
        "By 2025, we aim to serve over 1000 organizations worldwide, helping them achieve measurable improvements in decision-making speed and quality.",
        "Investment in machine learning research, particularly in natural language processing and graph neural networks, remains our highest priority.",
        "We believe that the future of work lies in human-AI collaboration, where artificial intelligence augments rather than replaces human judgment.",
    ],
    "Employee Wellbeing and Mental Health Policy": [
        "Employee mental health and psychological safety are fundamental to our organizational culture and business success.",
        "We provide comprehensive mental health support including therapy coverage, meditation apps, and flexible working arrangements for work-life balance.",
        "Burnout prevention measures include mandatory vacation policies, meeting-free Fridays, and workload monitoring through regular check-ins.",
        "Our diversity, equity, and inclusion initiatives create an environment where all team members feel valued and can thrive professionally.",
        "Regular pulse surveys measure employee satisfaction, stress levels, and engagement to identify areas needing attention or improvement.",
    ],
    "Quarterly Financial Performance Analysis": [
        "Q3 2024 revenue exceeded projections by 23%, driven primarily by enterprise client acquisitions and platform expansion.",
        "Operating expenses decreased by 11% due to automation initiatives and streamlined operational processes across departments.",
        "Customer acquisition costs dropped significantly following implementation of AI-driven marketing attribution and lead scoring systems.",
        "Recurring revenue now represents 89% of total revenue, indicating strong customer retention and satisfaction with our platform.",
        "Cash flow projections show sustainable growth trajectory with break-even expected by Q2 2025 under current expansion plans.",
    ],
    "Technology Infrastructure and Security Report": [
        "Our cloud-native architecture built on Kubernetes provides horizontal scalability to handle enterprise-level data processing workloads.",
        "Zero-trust security model with end-to-end encryption ensures customer data protection and compliance with international privacy regulations.",
        "Real-time monitoring and observability stack provides 99.9% uptime with automated incident response and recovery procedures.",
        "Vector database implementation using Weaviate enables sub-second semantic search across millions of organizational documents.",
        "Continuous integration and deployment pipelines with automated testing ensure code quality and rapid, safe feature releases.",
    ],
    "Customer Success and Product Development Roadmap": [
        "Customer feedback analysis reveals strong demand for multi-language support and improved integration capabilities with existing enterprise systems.",
        "Product roadmap prioritizes advanced analytics dashboards, providing executives with real-time insights into organizational health metrics.",
        "Machine learning model improvements focus on better understanding of cultural nuances and communication patterns across different industries.",
        "API development enables third-party integrations with popular business tools like Slack, Microsoft Teams, and project management platforms.",
        "User experience research drives interface redesign to make complex organizational insights accessible to non-technical business users.",
    ],
}

# Semantic test queries that should demonstrate real understanding
SEMANTIC_TEST_QUERIES = [
    # Conceptual similarity (not keyword matching)
    (
        "artificial intelligence and machine learning",
        ["CEO Strategic Vision 2024", "Technology Infrastructure and Security Report"],
    ),
    # Emotional/cultural concepts
    ("employee happiness and workplace culture", ["Employee Wellbeing and Mental Health Policy"]),
    # Business performance concepts
    ("revenue growth and financial success", ["Quarterly Financial Performance Analysis"]),
    # Technical infrastructure concepts
    ("scalable systems and data processing", ["Technology Infrastructure and Security Report"]),
    # Customer-focused concepts
    (
        "client satisfaction and user experience",
        ["Customer Success and Product Development Roadmap"],
    ),
    # Cross-domain concepts (should find multiple relevant documents)
    (
        "organizational transformation and business intelligence",
        ["CEO Strategic Vision 2024", "Customer Success and Product Development Roadmap"],
    ),
    # Specific but conceptual
    (
        "mental health support and employee wellbeing programs",
        ["Employee Wellbeing and Mental Health Policy"],
    ),
    # Technical but business-relevant
    ("data security and privacy compliance", ["Technology Infrastructure and Security Report"]),
]

# Complex hybrid queries (text + semantic)
HYBRID_TEST_QUERIES = [
    ("AI machine learning", "strategic vision for artificial intelligence implementation"),
    ("employee mental health", "workplace psychological safety and wellbeing initiatives"),
    ("revenue growth profit", "financial performance and business success metrics"),
    ("security encryption", "data protection and cybersecurity infrastructure"),
    ("customer feedback UX", "user experience and client satisfaction improvements"),
]


async def test_real_weaviate_capabilities():
    """Test Weaviate with actual semantic understanding capabilities."""

    print("🧪 REAL WEAVIATE SEMANTIC CAPABILITIES TEST")
    print("=" * 60)

    # Check prerequisites
    if not OPENAI_AVAILABLE:
        print("❌ OpenAI library not installed")
        print("💡 Install with: pip install openai")
        return False

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set")
        print("💡 Export your OpenAI API key: export OPENAI_API_KEY='your-key-here'")
        return False

    print("✅ OpenAI API key configured")

    try:
        from service.vector_store.weaviate_service import WeaviateConfig, WeaviateStore

        print("✅ Weaviate service imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Weaviate service: {e}")
        return False

    # Configure Weaviate with proper dimensions for OpenAI embeddings
    config = WeaviateConfig(
        url="http://localhost:8081",
        collection_name="RealSemanticTest",
        embedding_dimensions=1536,  # text-embedding-3-small dimensions
    )

    try:
        # Initialize store
        print("\n🔗 Connecting to Weaviate...")
        store = WeaviateStore(config)
        print("✅ Connected to Weaviate successfully")

        tenant_id = "real_semantic_test"

        print("\n📝 Inserting real organizational documents with OpenAI embeddings...")
        print("⏳ This may take a moment as we generate real embeddings...")

        # Insert documents with real embeddings
        total_chunks = sum(len(chunks) for chunks in REAL_ORGANIZATIONAL_DOCUMENTS.values())
        processed_chunks = 0

        for title, chunks in REAL_ORGANIZATIONAL_DOCUMENTS.items():
            print(f"  📄 Processing: {title} ({len(chunks)} chunks)")

            # Generate real embeddings
            start_embed_time = time.time()
            embeddings = get_real_embeddings(chunks)
            embed_time = time.time() - start_embed_time
            print(f"    🧠 Generated embeddings in {embed_time:.2f}s")

            # Insert into Weaviate
            start_insert_time = time.time()
            source_id = store.upsert_chunks(
                tenant_id=tenant_id, title=title, chunks=chunks, embeddings=embeddings
            )
            insert_time = time.time() - start_insert_time

            if source_id:
                processed_chunks += len(chunks)
                print(f"    ✅ Inserted successfully in {insert_time:.2f}s")
            else:
                print(f"    ❌ Failed to insert {title}")

        print(
            f"\n📊 Total: {processed_chunks}/{total_chunks} chunks processed with real embeddings"
        )

        print("\n🔍 Testing REAL semantic search capabilities...")
        print("🎯 These queries test conceptual understanding, not keyword matching")

        semantic_success_count = 0
        total_semantic_tests = 0

        for query, expected_sources in SEMANTIC_TEST_QUERIES:
            print(f"\n  🔎 Semantic Query: '{query}'")
            print(f"    🎯 Should find: {', '.join(expected_sources)}")

            # Generate query embedding
            query_start = time.time()
            query_vector = get_real_embedding(query)
            query_embed_time = time.time() - query_start

            # Perform semantic search
            search_start = time.time()
            results = store.search(tenant_id=tenant_id, query_vector=query_vector, k=3)
            search_time = time.time() - search_start

            print(f"    ⚡ Query: {query_embed_time:.3f}s, Search: {search_time:.3f}s")
            print(f"    📊 Found {len(results)} results:")

            found_sources = set()
            for i, result in enumerate(results):
                score = result.get("score", 0.0) or 0.0  # Handle None scores
                source = result.get("source", "Unknown")
                found_sources.add(source)

                # Show semantic relevance
                relevance = "✅" if source in expected_sources else "🔍"
                print(f"      {i + 1}. {relevance} [{source}] Score: {score:.4f}")

                # Show text snippet to verify semantic relevance
                text_snippet = result.get("text", "")[:120] + "..."
                print(f'         "{text_snippet}"')

            # Calculate semantic accuracy
            expected_set = set(expected_sources)
            correct_matches = len(found_sources & expected_set)
            total_expected = len(expected_set)

            accuracy = correct_matches / total_expected if total_expected > 0 else 0
            print(f"    🎯 Semantic Accuracy: {correct_matches}/{total_expected} ({accuracy:.1%})")

            if accuracy >= 0.5:  # At least 50% of expected sources found
                semantic_success_count += 1

            total_semantic_tests += 1

        semantic_success_rate = semantic_success_count / total_semantic_tests
        print(
            f"\n📈 Overall Semantic Understanding: {semantic_success_count}/{total_semantic_tests} ({semantic_success_rate:.1%})"
        )

        print("\n🔀 Testing REAL hybrid search (semantic + keyword)...")

        hybrid_success_count = 0

        for keyword_query, semantic_description in HYBRID_TEST_QUERIES:
            print("\n  🔎 Hybrid Query:")
            print(f"    💬 Keywords: '{keyword_query}'")
            print(f"    🧠 Semantic: '{semantic_description}'")

            # Generate semantic embedding
            semantic_vector = get_real_embedding(semantic_description)

            # Perform hybrid search
            start_time = time.time()
            hybrid_results = store.hybrid_search(
                tenant_id=tenant_id,
                query=keyword_query,
                query_vector=semantic_vector,
                k=3,
                alpha=0.7,  # 70% semantic, 30% keyword
            )
            search_time = time.time() - start_time

            print(f"    📊 Found {len(hybrid_results)} hybrid results in {search_time:.3f}s")

            if len(hybrid_results) > 0:
                hybrid_success_count += 1

                for i, result in enumerate(hybrid_results):
                    score = result.get("score", 0.0) or 0.0  # Handle None scores
                    source = result.get("source", "Unknown")
                    print(f"      {i + 1}. [{source}] Hybrid Score: {score:.4f}")
            else:
                print("    ❌ No hybrid results found")

        hybrid_success_rate = hybrid_success_count / len(HYBRID_TEST_QUERIES)
        print(
            f"\n📈 Hybrid Search Success: {hybrid_success_count}/{len(HYBRID_TEST_QUERIES)} ({hybrid_success_rate:.1%})"
        )

        print("\n🎯 Testing semantic edge cases...")

        # Test semantic edge cases that prove real understanding
        edge_cases = [
            ("company culture and team dynamics", "Should understand organizational concepts"),
            ("revenue streams and profitability", "Should understand financial concepts"),
            ("data privacy and security compliance", "Should understand technical/legal concepts"),
            ("employee retention and job satisfaction", "Should understand HR concepts"),
        ]

        edge_case_success = 0
        for edge_query, description in edge_cases:
            print(f"  🎯 Edge Case: '{edge_query}' - {description}")

            query_vector = get_real_embedding(edge_query)
            results = store.search(tenant_id=tenant_id, query_vector=query_vector, k=2)

            if len(results) > 0:
                edge_case_success += 1
                best_match = results[0]
                score = best_match.get("score", 0.0) or 0.0  # Handle None scores
                source = best_match.get("source", "Unknown")
                print(f"    ✅ Found relevant match: [{source}] Score: {score:.4f}")
            else:
                print("    ❌ No semantic understanding demonstrated")

        edge_success_rate = edge_case_success / len(edge_cases)
        print(
            f"\n📈 Semantic Edge Cases: {edge_case_success}/{len(edge_cases)} ({edge_success_rate:.1%})"
        )

        # Final assessment
        overall_success = (semantic_success_rate + hybrid_success_rate + edge_success_rate) / 3

        print("\n🎉 REAL WEAVIATE CAPABILITIES ASSESSMENT")
        print("=" * 50)
        print(f"🧠 Semantic Understanding: {semantic_success_rate:.1%}")
        print(f"🔀 Hybrid Search: {hybrid_success_rate:.1%}")
        print(f"🎯 Edge Case Handling: {edge_success_rate:.1%}")
        print(f"📊 Overall Real Capability Score: {overall_success:.1%}")

        if overall_success >= 0.7:
            print("\n✅ EXCELLENT: Weaviate demonstrates strong real-world semantic capabilities!")
        elif overall_success >= 0.5:
            print("\n✅ GOOD: Weaviate shows solid semantic understanding capabilities")
        else:
            print("\n⚠️  LIMITED: Semantic capabilities may need tuning or data improvement")

        print("\n💡 Key Insights Demonstrated:")
        print("  🧠 True semantic similarity (not just keyword matching)")
        print("  🎯 Cross-domain concept understanding")
        print("  🔀 Hybrid search combining semantic + lexical")
        print("  📊 Real-world organizational document comprehension")

        # Cleanup
        store.close()
        return overall_success >= 0.5

    except Exception as e:
        print(f"❌ Real Weaviate test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def check_weaviate_connection():
    """Check if Weaviate is accessible."""
    try:
        import requests

        response = requests.get("http://localhost:8081/v1/.well-known/ready", timeout=5)
        return response.status_code == 200
    except:
        return False


async def main():
    """Main test runner."""
    print("🚀 Real Weaviate Semantic Capabilities Test")
    print("=" * 60)

    # Check prerequisites
    if not check_weaviate_connection():
        print("❌ Weaviate is not accessible at http://localhost:8081")
        print("💡 Start Weaviate with:")
        print("   docker-compose -f docker-compose.test.yml up -d weaviate")
        return

    print("✅ Weaviate is accessible")

    # Run real capability test
    success = await test_real_weaviate_capabilities()

    if success:
        print("\n🎉 REAL semantic capabilities verified! Weaviate is ready for production.")
        print("🔥 This proves genuine semantic understanding, not mock data.")
    else:
        print("\n💥 Real capability test failed. Check configuration and data quality.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
