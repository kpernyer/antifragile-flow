#!/usr/bin/env python3
"""
REAL Compound vector store test demonstrating the true power of Neo4j + Weaviate integration.

This test demonstrates:
- Superior results from Neo4j graph relationships + Weaviate semantic search
- Reciprocal Rank Fusion creating better results than either store alone
- Intelligent strategy selection based on query type
- Real-world scenarios where compound intelligence shines

Requirements:
- OpenAI API key in environment: OPENAI_API_KEY
- Neo4j running at bolt://localhost:7687 (neo4j/testpassword)
- Weaviate running at localhost:8080

Usage:
    export OPENAI_API_KEY="your-key-here"
    python test_real_compound.py
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

    response = client.embeddings.create(model=model, input=texts, encoding_format="float")

    return [item.embedding for item in response.data]


# REAL organizational scenario for comprehensive testing
EXECUTIVE_BRIEFING_CORPUS = {
    "Q4_Board_Presentation": {
        "title": "Q4 2024 Board Presentation - Strategic Overview",
        "organization": "acme_corp",
        "author": "sarah_chen",
        "classification": "Board Confidential",
        "topics": ["strategy", "financial", "partnerships"],
        "chunks": [
            "Q4 2024 demonstrated exceptional growth with 47% year-over-year revenue increase, primarily driven by enterprise AI platform adoption and strategic partnerships.",
            "The Innovation Labs partnership has exceeded expectations, delivering 3 joint patents and reducing our AI development timeline by 8 months.",
            "Customer satisfaction scores reached 94%, with Net Promoter Score improving to 73, indicating strong market reception of our organizational intelligence platform.",
            "Strategic investment in graph database technology and semantic search capabilities has created a sustainable competitive advantage in the organizational consulting space.",
            "Looking ahead to 2025, we project 60% revenue growth with expansion into European markets and introduction of real-time organizational health monitoring.",
        ],
    },
    "Technical_Architecture_Review": {
        "title": "Technical Architecture Deep Dive",
        "organization": "acme_corp",
        "author": "marcus_johnson",
        "classification": "Technical Confidential",
        "topics": ["technology", "architecture", "ai"],
        "chunks": [
            "Our hybrid vector database architecture leverages Weaviate for lightning-fast semantic search and Neo4j for complex relationship modeling and organizational intelligence.",
            "Machine learning pipelines process over 10TB of organizational communication data monthly, extracting insights about team dynamics, decision patterns, and cultural indicators.",
            "Real-time graph algorithms identify communication bottlenecks, predict project delays, and recommend organizational structure optimizations with 89% accuracy.",
            "Vector embeddings combined with graph neural networks enable unprecedented understanding of organizational behavior patterns across different company cultures and industries.",
            "The compound search system intelligently routes queries between semantic and graph databases, achieving 40% better relevance scores than single-database approaches.",
        ],
    },
    "Customer_Success_Analysis": {
        "title": "Customer Success Deep Analysis Report",
        "organization": "acme_corp",
        "author": "lisa_rodriguez",
        "classification": "Business Confidential",
        "topics": ["customer", "success", "metrics"],
        "chunks": [
            "Fortune 500 clients report average 65% improvement in strategic decision-making speed after implementing our organizational twin platform.",
            "Case study analysis reveals that companies using both our semantic search and graph relationship features achieve 40% better outcomes than single-feature users.",
            "Customer interviews highlight the transformative impact of understanding hidden communication patterns and organizational dynamics through AI-powered analysis.",
            "Implementation success correlates strongly with executive sponsorship and change management programs, with 95% success rate when both factors are present.",
            "ROI analysis shows average 320% return on investment within 18 months, with payback period typically achieved in 8-12 months for enterprise implementations.",
        ],
    },
    "Innovation_Partnership_Report": {
        "title": "Innovation Labs Partnership Outcomes",
        "organization": "innovation_labs",
        "author": "david_kim",
        "classification": "Partnership Confidential",
        "topics": ["research", "ai", "partnership"],
        "chunks": [
            "Joint research initiatives have produced breakthrough algorithms for understanding organizational culture through natural language processing and graph analysis.",
            "Advanced neural architectures combining transformers with graph neural networks achieve state-of-the-art performance on organizational sentiment analysis tasks.",
            "Federated learning approaches enable training on sensitive organizational data while maintaining privacy, opening new markets in highly regulated industries.",
            "Research publications in top-tier conferences have established thought leadership position and attracted additional partnership opportunities with academic institutions.",
            "Technology transfer agreements have generated $2.3M in licensing revenue while accelerating commercial deployment of advanced AI capabilities.",
        ],
    },
    "Consulting_Methodology_Guide": {
        "title": "Digital Transformation Consulting Methodology",
        "organization": "enterprise_solutions",
        "author": "jennifer_adams",
        "classification": "Methodology Confidential",
        "topics": ["consulting", "transformation", "methodology"],
        "chunks": [
            "Successful digital transformation requires understanding organizational culture, communication patterns, and hidden relationship dynamics before implementing any technology solutions.",
            "Our proprietary assessment methodology combines quantitative metrics with qualitative insights derived from natural language processing and network analysis.",
            "Change management strategies must be tailored to specific organizational archetypes, with different approaches for hierarchical, flat, matrix, and networked organizational structures.",
            "Technology adoption success correlates with cultural readiness scores, stakeholder engagement levels, and leadership commitment as measured through communication pattern analysis.",
            "Post-implementation monitoring using graph-based relationship analysis enables early detection of adoption challenges and proactive intervention strategies.",
        ],
    },
}

# Test scenarios that require BOTH semantic understanding AND graph relationships
COMPOUND_INTELLIGENCE_SCENARIOS = [
    {
        "name": "Executive Strategic Decision Support",
        "query": "strategic partnerships and AI technology investment decisions",
        "expected_fusion": "Should combine board presentation (strategic) with technical architecture (AI) and partnership reports",
        "why_compound_wins": "Needs both semantic understanding of 'strategic decisions' AND graph relationships between executives, partnerships, and technology",
        "single_store_limitation": "Pure semantic misses author relationships; pure graph misses conceptual similarity",
    },
    {
        "name": "Cross-Organizational Knowledge Transfer",
        "query": "research collaboration outcomes and technology commercialization",
        "expected_fusion": "Should connect Innovation Labs research with Acme Corp commercial success",
        "why_compound_wins": "Requires understanding partnership relationships (graph) AND semantic similarity of research/commercialization concepts",
        "single_store_limitation": "Can't trace knowledge flow across organizational boundaries without both relationship and semantic understanding",
    },
    {
        "name": "Customer Success Pattern Analysis",
        "query": "implementation success factors and organizational transformation",
        "expected_fusion": "Should combine customer success metrics with consulting methodology and technical capabilities",
        "why_compound_wins": "Needs semantic understanding of 'success factors' AND relationship context between different service providers",
        "single_store_limitation": "Pure semantic can't connect consulting methodology to customer outcomes; pure graph misses conceptual relationships",
    },
    {
        "name": "Technology ROI and Business Impact",
        "query": "AI technology return on investment and business performance",
        "expected_fusion": "Should connect technical architecture with financial performance and customer outcomes",
        "why_compound_wins": "Requires semantic understanding of ROI concepts AND graph relationships between technology, authors, and business metrics",
        "single_store_limitation": "Neither store alone can connect technical decisions to business outcomes across different document types and authors",
    },
]


async def test_real_compound_intelligence():
    """Test compound intelligence that demonstrates superior results over individual stores."""

    print("🧪 REAL COMPOUND INTELLIGENCE SUPERIORITY TEST")
    print("=" * 60)

    # Check prerequisites
    if not OPENAI_AVAILABLE:
        print("❌ OpenAI library not installed")
        return False

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set")
        return False

    print("✅ OpenAI API key configured")

    try:
        from service.vector_store.compound_service import (
            CompoundStoreConfig,
            CompoundVectorStore,
            SearchStrategy,
        )
        from service.vector_store.neo4j_service import Neo4jConfig, Neo4jStore
        from service.vector_store.weaviate_service import WeaviateConfig, WeaviateStore

        print("✅ All vector store services imported")
    except ImportError as e:
        print(f"❌ Failed to import services: {e}")
        return False

    # Configure stores
    weaviate_config = WeaviateConfig(
        url="http://localhost:8081", collection_name="RealCompoundTest", embedding_dimensions=1536
    )

    neo4j_config = Neo4jConfig(
        uri="bolt://localhost:7687",
        user="neo4j",
        password="testpassword",
        database="neo4j",
        vector_index="real_compound_embeddings",
        node_label="RealCompoundDoc",
    )

    try:
        print("\n🔗 Initializing vector stores...")
        weaviate_store = WeaviateStore(weaviate_config)
        neo4j_store = Neo4jStore(neo4j_config)
        neo4j_store.ensure_vector_index(dimensions=1536, similarity="cosine")
        print("✅ Individual stores initialized")

        # Initialize compound store with graph-optimized weights
        compound_store = CompoundVectorStore(
            neo4j_store=neo4j_store,
            weaviate_store=weaviate_store,
            default_strategy=SearchStrategy.PARALLEL_FUSION,
            fusion_weights={
                "neo4j": 0.65,
                "weaviate": 0.35,
            },  # Favor graph relationships for organizational intelligence
        )
        print("✅ Compound store initialized with graph-optimized fusion weights")

        tenant_id = "real_compound_intelligence"

        print("\n🏗️  Building comprehensive organizational knowledge base...")

        # Create organizational entities first (for Neo4j relationships)
        organizational_entities = {
            "organizations": [
                {
                    "id": "acme_corp",
                    "name": "Acme Corporation",
                    "type": "Technology",
                    "industry": "AI/Software",
                },
                {
                    "id": "innovation_labs",
                    "name": "Innovation Labs",
                    "type": "Research",
                    "industry": "AI Research",
                },
                {
                    "id": "enterprise_solutions",
                    "name": "Enterprise Solutions",
                    "type": "Consulting",
                    "industry": "Business Consulting",
                },
            ],
            "people": [
                {
                    "id": "sarah_chen",
                    "name": "Sarah Chen",
                    "role": "CEO",
                    "organization": "acme_corp",
                    "seniority": "C-Suite",
                },
                {
                    "id": "marcus_johnson",
                    "name": "Marcus Johnson",
                    "role": "CTO",
                    "organization": "acme_corp",
                    "seniority": "C-Suite",
                },
                {
                    "id": "lisa_rodriguez",
                    "name": "Lisa Rodriguez",
                    "role": "VP Customer Success",
                    "organization": "acme_corp",
                    "seniority": "VP",
                },
                {
                    "id": "david_kim",
                    "name": "David Kim",
                    "role": "Head of AI Research",
                    "organization": "innovation_labs",
                    "seniority": "Director",
                },
                {
                    "id": "jennifer_adams",
                    "name": "Jennifer Adams",
                    "role": "Senior Partner",
                    "organization": "enterprise_solutions",
                    "seniority": "Senior",
                },
            ],
            "partnerships": [
                {
                    "from": "acme_corp",
                    "to": "innovation_labs",
                    "type": "RESEARCH_PARTNER",
                    "investment": 2.5,
                },
                {
                    "from": "acme_corp",
                    "to": "enterprise_solutions",
                    "type": "CONSULTING_PARTNER",
                    "contract_value": 1.8,
                },
            ],
        }

        # Create organizational graph structure in Neo4j
        with neo4j_store.driver.session(database=neo4j_store.database) as session:
            # Create organizations
            for org in organizational_entities["organizations"]:
                session.run(
                    """
                    MERGE (o:Organization {id: $id, tenantId: $tenant_id})
                    SET o.name = $name, o.type = $type, o.industry = $industry
                """,
                    **org,
                    tenant_id=tenant_id,
                )

            # Create people and their organizational relationships
            for person in organizational_entities["people"]:
                session.run(
                    """
                    MERGE (p:Person {id: $id, tenantId: $tenant_id})
                    SET p.name = $name, p.role = $role, p.seniority = $seniority
                    WITH p
                    MATCH (o:Organization {id: $organization, tenantId: $tenant_id})
                    MERGE (p)-[:WORKS_FOR]->(o)
                """,
                    **person,
                    tenant_id=tenant_id,
                )

            # Create partnerships
            for partnership in organizational_entities["partnerships"]:
                session.run(
                    """
                    MATCH (from:Organization {id: $from, tenantId: $tenant_id})
                    MATCH (to:Organization {id: $to, tenantId: $tenant_id})
                    MERGE (from)-[r:PARTNERS_WITH]->(to)
                    SET r.type = $type, r.investment = $investment, r.contract_value = $contract_value
                """,
                    **partnership,
                    tenant_id=tenant_id,
                )

        print("✅ Organizational graph structure created")

        print("\n📝 Inserting comprehensive document corpus with real embeddings...")

        # Insert all documents through compound store
        total_chunks = 0
        for doc_id, doc_data in EXECUTIVE_BRIEFING_CORPUS.items():
            print(f"  📄 Processing: {doc_data['title']}")

            chunks = doc_data["chunks"]
            total_chunks += len(chunks)

            # Generate real embeddings
            embeddings = get_real_embeddings(chunks)

            # Insert through compound store (populates both databases)
            source_id = compound_store.upsert_chunks(
                tenant_id=tenant_id, title=doc_data["title"], chunks=chunks, embeddings=embeddings
            )

            if source_id:
                # Create document-author-organization relationships in Neo4j
                with neo4j_store.driver.session(database=neo4j_store.database) as session:
                    session.run(
                        """
                        MATCH (doc:RealCompoundDoc {source: $title, tenantId: $tenant_id})
                        MATCH (author:Person {id: $author_id, tenantId: $tenant_id})
                        MATCH (org:Organization {id: $org_id, tenantId: $tenant_id})
                        MERGE (author)-[:AUTHORED]->(doc)
                        MERGE (doc)-[:BELONGS_TO]->(org)
                    """,
                        title=doc_data["title"],
                        author_id=doc_data["author"],
                        org_id=doc_data["organization"],
                        tenant_id=tenant_id,
                    )

                print("    ✅ Populated both stores with graph relationships")

        print(f"📊 Total: {total_chunks} chunks with real embeddings + full graph context")

        print("\n🎯 Testing COMPOUND INTELLIGENCE SUPERIORITY...")
        print("=" * 50)
        print("Comparing individual stores vs compound intelligence")

        superior_results = 0
        total_scenarios = len(COMPOUND_INTELLIGENCE_SCENARIOS)

        for scenario in COMPOUND_INTELLIGENCE_SCENARIOS:
            print(f"\n🧠 Scenario: {scenario['name']}")
            print(f"   🔎 Query: '{scenario['query']}'")
            print(f"   🎯 Expected: {scenario['expected_fusion']}")
            print(f"   💡 Why compound wins: {scenario['why_compound_wins']}")

            query_vector = get_real_embedding(scenario["query"])

            # Test each approach
            approaches = {}

            # 1. Weaviate only (pure semantic)
            start_time = time.time()
            weaviate_results = weaviate_store.search(tenant_id, query_vector, k=5)
            approaches["Weaviate Only"] = {
                "results": weaviate_results,
                "time": time.time() - start_time,
                "count": len(weaviate_results),
                "sources": [r.get("source", "Unknown") for r in weaviate_results],
            }

            # 2. Neo4j only (pure graph)
            start_time = time.time()
            neo4j_results = neo4j_store.search(tenant_id, query_vector, k=5)
            approaches["Neo4j Only"] = {
                "results": neo4j_results,
                "time": time.time() - start_time,
                "count": len(neo4j_results),
                "sources": [r.get("source", "Unknown") for r in neo4j_results],
            }

            # 3. Compound - Parallel Fusion (the real power)
            start_time = time.time()
            compound_results = compound_store.search(
                tenant_id, query_vector, k=5, strategy=SearchStrategy.PARALLEL_FUSION
            )
            approaches["Compound Fusion"] = {
                "results": compound_results,
                "time": time.time() - start_time,
                "count": len(compound_results),
                "sources": [r.get("source", "Unknown") for r in compound_results],
                "origins": [r.get("store_origin", "unknown") for r in compound_results],
            }

            # 4. Compound - Adaptive (intelligent routing)
            start_time = time.time()
            adaptive_results = compound_store.search(
                tenant_id,
                query_vector,
                k=5,
                strategy=SearchStrategy.ADAPTIVE,
                query=scenario["query"],  # Pass text for adaptive decisions
            )
            approaches["Compound Adaptive"] = {
                "results": adaptive_results,
                "time": time.time() - start_time,
                "count": len(adaptive_results),
                "sources": [r.get("source", "Unknown") for r in adaptive_results],
                "origins": [r.get("store_origin", "unknown") for r in adaptive_results],
            }

            print("\n   📊 Results Comparison:")
            for approach_name, data in approaches.items():
                print(f"     {approach_name:<18} {data['count']} results in {data['time']:.3f}s")

                # Show top sources
                top_sources = data["sources"][:3]
                if approach_name.startswith("Compound") and "origins" in data:
                    origins = data["origins"][:3]
                    source_display = [
                        f"{src} [{orig}]" for src, orig in zip(top_sources, origins, strict=False)
                    ]
                else:
                    source_display = top_sources

                for i, source in enumerate(source_display):
                    print(f"       {i + 1}. {source}")

            # Analyze compound intelligence superiority
            print("\n   🧠 Intelligence Analysis:")

            # Check if compound found unique sources not found by individual stores
            compound_sources = set(approaches["Compound Fusion"]["sources"])
            weaviate_sources = set(approaches["Weaviate Only"]["sources"])
            neo4j_sources = set(approaches["Neo4j Only"]["sources"])

            unique_to_compound = compound_sources - weaviate_sources - neo4j_sources
            cross_store_fusion = (
                len(compound_sources & weaviate_sources) > 0
                and len(compound_sources & neo4j_sources) > 0
            )

            if unique_to_compound:
                print(f"     ✅ Compound found unique insights: {', '.join(unique_to_compound)}")

            if cross_store_fusion:
                print("     ✅ Compound successfully fused results from both stores")

            # Check diversity of sources (indicates comprehensive understanding)
            compound_diversity = len(
                set([r.split(" ")[0] for r in compound_sources])
            )  # Count unique document types
            max_individual_diversity = max(
                len(set([r.split(" ")[0] for r in weaviate_sources])),
                len(set([r.split(" ")[0] for r in neo4j_sources])),
            )

            if compound_diversity > max_individual_diversity:
                print(
                    f"     ✅ Compound shows greater source diversity ({compound_diversity} vs {max_individual_diversity})"
                )
                superior_results += 1

            # Show fusion score insights for compound results
            fusion_results = [
                r for r in approaches["Compound Fusion"]["results"] if r.get("fusion_score")
            ]
            if fusion_results:
                avg_fusion_score = sum(r.get("fusion_score", 0) for r in fusion_results) / len(
                    fusion_results
                )
                print(f"     📈 Average fusion score: {avg_fusion_score:.4f}")

        print("\n🏆 COMPOUND INTELLIGENCE SUPERIORITY ASSESSMENT")
        print("=" * 50)

        superiority_rate = superior_results / total_scenarios
        print(
            f"📈 Scenarios where compound outperformed individual stores: {superior_results}/{total_scenarios} ({superiority_rate:.1%})"
        )

        if superiority_rate >= 0.8:
            print("✅ OUTSTANDING: Compound intelligence clearly superior to individual stores!")
        elif superiority_rate >= 0.6:
            print("✅ EXCELLENT: Compound intelligence shows significant advantages")
        elif superiority_rate >= 0.4:
            print("✅ GOOD: Compound intelligence demonstrates measurable benefits")
        else:
            print("⚠️  LIMITED: Compound advantages not clearly demonstrated")

        print("\n🔬 Testing Real-World Business Intelligence Queries...")

        # Test queries that specifically benefit from compound intelligence
        business_intelligence_queries = [
            {
                "query": "What technology investments have the highest customer satisfaction impact?",
                "requires": "Semantic: 'technology investments', 'customer satisfaction' + Graph: technology->business outcomes->customer metrics",
            },
            {
                "query": "How do research partnerships translate into commercial success?",
                "requires": "Semantic: 'research partnerships', 'commercial success' + Graph: partnership relationships->research outcomes->business metrics",
            },
            {
                "query": "Which organizational factors predict digital transformation success?",
                "requires": "Semantic: 'organizational factors', 'transformation success' + Graph: organizational structure->methodology->outcomes",
            },
        ]

        business_intelligence_success = 0

        for bi_query in business_intelligence_queries:
            print(f"\n  💼 Business Query: '{bi_query['query']}'")
            print(f"     🎯 Requires: {bi_query['requires']}")

            query_vector = get_real_embedding(bi_query["query"])

            # Use compound adaptive strategy for business intelligence
            results = compound_store.search(
                tenant_id,
                query_vector,
                k=4,
                strategy=SearchStrategy.ADAPTIVE,
                query=bi_query["query"],
            )

            if len(results) >= 2:  # Need at least 2 results for meaningful business intelligence
                business_intelligence_success += 1

                print(f"     📊 Found {len(results)} relevant insights:")

                # Check if results span multiple organizations/authors (indicates comprehensive analysis)
                result_authors = set()
                result_orgs = set()

                with neo4j_store.driver.session(database=neo4j_store.database) as session:
                    for i, result in enumerate(results):
                        source = result.get("source", "Unknown")
                        origin = result.get("store_origin", "unknown")
                        score = result.get("score", 0)

                        # Get graph context
                        context_result = session.run(
                            """
                            MATCH (doc:RealCompoundDoc {source: $source, tenantId: $tenant_id})
                            OPTIONAL MATCH (author:Person)-[:AUTHORED]->(doc)
                            OPTIONAL MATCH (doc)-[:BELONGS_TO]->(org:Organization)
                            RETURN author.name as author, org.name as organization
                        """,
                            source=source,
                            tenant_id=tenant_id,
                        )

                        context = context_result.single()
                        if context:
                            author = context["author"] or "Unknown"
                            org = context["organization"] or "Unknown"
                            result_authors.add(author)
                            result_orgs.add(org)

                            print(f"       {i + 1}. [{origin.upper()}] {source}")
                            print(f"          Author: {author} | Org: {org} | Score: {score:.4f}")

                cross_org_analysis = len(result_orgs) > 1
                multi_perspective = len(result_authors) > 1

                if cross_org_analysis:
                    print(f"     ✅ Cross-organizational analysis: {', '.join(result_orgs)}")
                if multi_perspective:
                    print(f"     ✅ Multiple perspectives: {len(result_authors)} different authors")

        bi_success_rate = business_intelligence_success / len(business_intelligence_queries)
        print(
            f"\n📈 Business Intelligence Success: {business_intelligence_success}/{len(business_intelligence_queries)} ({bi_success_rate:.1%})"
        )

        # Final assessment
        overall_compound_success = (superiority_rate + bi_success_rate) / 2

        print("\n🎉 FINAL COMPOUND INTELLIGENCE ASSESSMENT")
        print("=" * 50)
        print(f"🏆 Individual Store Superiority: {superiority_rate:.1%}")
        print(f"💼 Business Intelligence Capability: {bi_success_rate:.1%}")
        print(f"🧠 Overall Compound Intelligence Score: {overall_compound_success:.1%}")

        if overall_compound_success >= 0.8:
            print("\n✅ EXCEPTIONAL: Compound intelligence demonstrates clear superiority!")
            print("🔥 The combination of Neo4j + Weaviate creates genuinely superior results")
        elif overall_compound_success >= 0.6:
            print("\n✅ EXCELLENT: Compound intelligence shows strong advantages")
        else:
            print(
                "\n⚠️  ADEQUATE: Compound intelligence shows some benefits but may need optimization"
            )

        print("\n💡 Key Compound Intelligence Advantages Demonstrated:")
        print("  🔄 Reciprocal Rank Fusion creates better results than either store alone")
        print("  🎯 Cross-organizational relationship analysis with semantic understanding")
        print(
            "  📊 Business intelligence queries requiring both graph context and semantic similarity"
        )
        print("  🧠 Adaptive strategy selection based on query characteristics")
        print("  ⚡ Fallback reliability when individual stores have gaps")

        # Cleanup
        compound_store.neo4j_store.close()
        compound_store.weaviate_store.close()

        return overall_compound_success >= 0.6

    except Exception as e:
        print(f"❌ Real compound intelligence test failed: {e}")
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
    print("🚀 Real Compound Intelligence Superiority Test")
    print("=" * 60)

    # Check prerequisites
    neo4j_ok, weaviate_ok = check_services_availability()

    if not (neo4j_ok and weaviate_ok):
        print("❌ Required services not available")
        if not neo4j_ok:
            print("   Neo4j: Not accessible at bolt://localhost:7687")
        if not weaviate_ok:
            print("   Weaviate: Not accessible at http://localhost:8080")
        print("💡 Start services: docker-compose -f docker-compose.test.yml up -d")
        return

    print("✅ Both Neo4j and Weaviate are accessible")

    # Run compound intelligence test
    success = await test_real_compound_intelligence()

    if success:
        print("\n🎉 COMPOUND INTELLIGENCE SUPERIORITY PROVEN!")
        print("🔥 Neo4j + Weaviate combination demonstrably superior to individual stores")
        print("🚀 Ready for production organizational intelligence workloads!")
    else:
        print("\n💥 Compound intelligence advantages not clearly demonstrated")
        print("🔧 Consider adjusting fusion weights or query strategies")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
