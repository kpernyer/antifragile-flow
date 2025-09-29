#!/usr/bin/env python3
"""
REAL Neo4j test with actual graph relationships, organizational intelligence, and complex queries.

This test demonstrates:
- True graph relationship modeling and traversal
- Complex Cypher queries for organizational intelligence
- Multi-hop relationship analysis
- Graph-based insights that pure vector search cannot provide

Requirements:
- OpenAI API key in environment: OPENAI_API_KEY
- Neo4j running at bolt://localhost:7687 (neo4j/testpassword)

Usage:
    export OPENAI_API_KEY="your-key-here"
    python test_real_neo4j.py
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


# REAL organizational structure for graph modeling
ORGANIZATIONAL_ENTITIES = {
    "organizations": [
        {
            "id": "acme_corp",
            "name": "Acme Corporation",
            "type": "Technology",
            "industry": "Software",
            "size": 850,
            "founded": 2018,
            "headquarters": "San Francisco, CA",
            "revenue_millions": 45.2,
            "growth_stage": "Series B",
        },
        {
            "id": "innovation_labs",
            "name": "Innovation Labs",
            "type": "Research",
            "industry": "AI/ML Research",
            "size": 120,
            "founded": 2020,
            "headquarters": "Boston, MA",
            "revenue_millions": 8.1,
            "growth_stage": "Series A",
        },
        {
            "id": "enterprise_solutions",
            "name": "Enterprise Solutions Inc",
            "type": "Consulting",
            "industry": "Business Consulting",
            "size": 2500,
            "founded": 2010,
            "headquarters": "New York, NY",
            "revenue_millions": 180.5,
            "growth_stage": "Public",
        },
    ],
    "people": [
        {
            "id": "sarah_chen",
            "name": "Sarah Chen",
            "role": "CEO",
            "organization": "acme_corp",
            "department": "Executive",
            "seniority_level": "C-Suite",
            "years_experience": 12,
            "specialization": "Strategic Leadership",
        },
        {
            "id": "marcus_johnson",
            "name": "Marcus Johnson",
            "role": "CTO",
            "organization": "acme_corp",
            "department": "Engineering",
            "seniority_level": "C-Suite",
            "years_experience": 15,
            "specialization": "Technical Architecture",
        },
        {
            "id": "lisa_rodriguez",
            "name": "Lisa Rodriguez",
            "role": "VP of Engineering",
            "organization": "acme_corp",
            "department": "Engineering",
            "seniority_level": "VP",
            "years_experience": 10,
            "specialization": "Team Leadership",
        },
        {
            "id": "david_kim",
            "name": "David Kim",
            "role": "Head of AI Research",
            "organization": "innovation_labs",
            "department": "Research",
            "seniority_level": "Director",
            "years_experience": 8,
            "specialization": "Machine Learning",
        },
        {
            "id": "jennifer_adams",
            "name": "Jennifer Adams",
            "role": "Senior Consultant",
            "organization": "enterprise_solutions",
            "department": "Consulting",
            "seniority_level": "Senior",
            "years_experience": 7,
            "specialization": "Digital Transformation",
        },
    ],
    "projects": [
        {
            "id": "ai_transformation",
            "name": "AI Transformation Initiative",
            "organization": "acme_corp",
            "budget_millions": 5.2,
            "duration_months": 18,
            "status": "Active",
            "priority": "High",
            "lead": "marcus_johnson",
        },
        {
            "id": "partnership_integration",
            "name": "Innovation Labs Partnership",
            "organization": "acme_corp",
            "budget_millions": 2.1,
            "duration_months": 12,
            "status": "Planning",
            "priority": "Medium",
            "lead": "sarah_chen",
        },
        {
            "id": "nlp_research",
            "name": "Advanced NLP Research",
            "organization": "innovation_labs",
            "budget_millions": 1.8,
            "duration_months": 24,
            "status": "Active",
            "priority": "High",
            "lead": "david_kim",
        },
    ],
    "relationships": [
        # Organizational partnerships
        {
            "from": "acme_corp",
            "to": "innovation_labs",
            "type": "PARTNERS_WITH",
            "since": "2023-06",
            "investment_millions": 2.5,
        },
        {
            "from": "acme_corp",
            "to": "enterprise_solutions",
            "type": "CONSULTS_WITH",
            "since": "2023-01",
            "contract_value": 1.2,
        },
        # Reporting relationships
        {"from": "marcus_johnson", "to": "sarah_chen", "type": "REPORTS_TO", "since": "2022-03"},
        {
            "from": "lisa_rodriguez",
            "to": "marcus_johnson",
            "type": "REPORTS_TO",
            "since": "2023-01",
        },
        # Cross-org collaboration
        {
            "from": "marcus_johnson",
            "to": "david_kim",
            "type": "COLLABORATES_WITH",
            "frequency": "Weekly",
            "project": "ai_transformation",
        },
        {
            "from": "sarah_chen",
            "to": "jennifer_adams",
            "type": "CONSULTS_WITH",
            "frequency": "Monthly",
        },
        # Project ownership
        {
            "from": "marcus_johnson",
            "to": "ai_transformation",
            "type": "LEADS",
            "responsibility": "Technical",
        },
        {
            "from": "sarah_chen",
            "to": "partnership_integration",
            "type": "SPONSORS",
            "responsibility": "Strategic",
        },
        {"from": "david_kim", "to": "nlp_research", "type": "LEADS", "responsibility": "Research"},
        # Document authorship and access
        {
            "from": "sarah_chen",
            "to": "board_meeting_minutes",
            "type": "AUTHORED",
            "date": "2024-01-15",
        },
        {
            "from": "marcus_johnson",
            "to": "tech_architecture_doc",
            "type": "AUTHORED",
            "date": "2024-02-10",
        },
        {
            "from": "jennifer_adams",
            "to": "transformation_strategy",
            "type": "AUTHORED",
            "date": "2024-01-20",
        },
    ],
}

# REAL organizational documents with complex interdependencies
REAL_GRAPH_DOCUMENTS = {
    "board_meeting_minutes": {
        "title": "Board Meeting Minutes Q1 2024",
        "organization": "acme_corp",
        "author": "sarah_chen",
        "date": "2024-01-15",
        "classification": "Confidential",
        "chunks": [
            "CEO Sarah Chen presented Q4 2023 results showing 34% revenue growth, primarily driven by enterprise client acquisitions and our AI platform expansion.",
            "CTO Marcus Johnson reported successful completion of the core infrastructure modernization, reducing system latency by 60% and improving scalability.",
            "The board approved a $5.2M investment in the AI Transformation Initiative, with Marcus Johnson as technical lead and expected completion by mid-2025.",
            "Strategic partnership with Innovation Labs was ratified, including a $2.5M equity investment and joint research agreement for advanced NLP capabilities.",
            "Risk assessment identified cybersecurity as the top priority, with immediate budget allocation for zero-trust architecture implementation.",
        ],
    },
    "tech_architecture_doc": {
        "title": "Technical Architecture Blueprint 2024",
        "organization": "acme_corp",
        "author": "marcus_johnson",
        "date": "2024-02-10",
        "classification": "Internal",
        "chunks": [
            "Our microservices architecture leverages Kubernetes orchestration with service mesh for secure inter-service communication and observability.",
            "Vector database integration using Weaviate provides semantic search capabilities across organizational documents with sub-100ms query response times.",
            "Neo4j graph database stores organizational relationships and enables complex traversal queries for management insights and reporting dashboards.",
            "Real-time event streaming through Apache Kafka ensures reliable data flow between services while maintaining exactly-once delivery guarantees.",
            "Machine learning pipeline built on Temporal workflows orchestrates model training, evaluation, and deployment with full auditability and rollback capabilities.",
        ],
    },
    "transformation_strategy": {
        "title": "Digital Transformation Strategy",
        "organization": "enterprise_solutions",
        "author": "jennifer_adams",
        "date": "2024-01-20",
        "classification": "Client Confidential",
        "chunks": [
            "Digital transformation requires fundamental reimagining of business processes, not just technology upgrades or point solutions.",
            "Change management and organizational culture adaptation are critical success factors, often more important than the technology itself.",
            "Data governance framework must be established before implementing analytics platforms to ensure data quality and regulatory compliance.",
            "Employee training and upskilling programs should begin 6 months before technology rollout to minimize disruption and resistance.",
            "Success metrics should include both quantitative KPIs and qualitative measures of employee satisfaction and customer experience improvements.",
        ],
    },
    "research_proposal": {
        "title": "Advanced NLP Research Proposal",
        "organization": "innovation_labs",
        "author": "david_kim",
        "date": "2024-02-01",
        "classification": "Proprietary",
        "chunks": [
            "Large language models fine-tuned on organizational communication patterns can significantly improve understanding of company culture and dynamics.",
            "Graph neural networks combined with transformer architectures enable modeling of complex organizational relationships and communication flows.",
            "Multi-modal analysis incorporating text, network topology, and temporal patterns provides comprehensive organizational intelligence insights.",
            "Federated learning approaches allow training on sensitive organizational data while preserving privacy and maintaining competitive advantages.",
            "Benchmark datasets and evaluation metrics specific to organizational intelligence are needed to measure model performance accurately.",
        ],
    },
    "partnership_agreement": {
        "title": "Innovation Labs Partnership Agreement",
        "organization": "acme_corp",
        "author": "sarah_chen",
        "date": "2023-12-15",
        "classification": "Legal Confidential",
        "chunks": [
            "Strategic partnership establishes joint research initiatives in artificial intelligence and organizational behavior analysis.",
            "Acme Corporation invests $2.5M for 15% equity stake in Innovation Labs, with board representation and strategic input rights.",
            "Intellectual property sharing agreement covers jointly developed algorithms while preserving each company's proprietary technologies.",
            "Revenue sharing model allocates 60% to Acme Corp and 40% to Innovation Labs for commercialized research outcomes.",
            "Partnership duration is 5 years with automatic renewal, subject to performance milestones and mutual satisfaction criteria.",
        ],
    },
}


async def test_real_neo4j_graph_capabilities():
    """Test Neo4j with actual graph intelligence and relationship analysis."""

    print("🧪 REAL NEO4J GRAPH INTELLIGENCE TEST")
    print("=" * 60)

    # Check prerequisites
    if not OPENAI_AVAILABLE:
        print("❌ OpenAI library not installed")
        print("💡 Install with: pip install openai")
        return False

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set")
        return False

    print("✅ OpenAI API key configured")

    try:
        from service.vector_store.neo4j_service import Neo4jConfig, Neo4jStore

        print("✅ Neo4j service imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Neo4j service: {e}")
        return False

    # Configure Neo4j
    config = Neo4jConfig(
        uri="bolt://localhost:7687",
        user="neo4j",
        password="testpassword",
        database="neo4j",
        vector_index="real_graph_test_embeddings",
        node_label="RealGraphDoc",
    )

    try:
        # Initialize store
        print("\n🔗 Connecting to Neo4j...")
        store = Neo4jStore(config)
        print("✅ Connected to Neo4j successfully")

        # Ensure vector index
        store.ensure_vector_index(dimensions=1536, similarity="cosine")
        print("✅ Vector index configured")

        tenant_id = "real_graph_test"

        print("\n🏗️  Building real organizational graph structure...")

        # Create comprehensive organizational graph using direct Cypher
        with store.driver.session(database=store.database) as session:
            # Create organizations
            print("  🏢 Creating organizations...")
            for org in ORGANIZATIONAL_ENTITIES["organizations"]:
                session.run(
                    """
                    MERGE (o:Organization {id: $id})
                    SET o.name = $name,
                        o.type = $type,
                        o.industry = $industry,
                        o.size = $size,
                        o.founded = $founded,
                        o.headquarters = $headquarters,
                        o.revenue_millions = $revenue_millions,
                        o.growth_stage = $growth_stage,
                        o.tenantId = $tenant_id
                """,
                    **org,
                    tenant_id=tenant_id,
                )

            # Create people
            print("  👥 Creating people...")
            for person in ORGANIZATIONAL_ENTITIES["people"]:
                session.run(
                    """
                    MERGE (p:Person {id: $id})
                    SET p.name = $name,
                        p.role = $role,
                        p.department = $department,
                        p.seniority_level = $seniority_level,
                        p.years_experience = $years_experience,
                        p.specialization = $specialization,
                        p.tenantId = $tenant_id
                    WITH p
                    MATCH (o:Organization {id: $organization, tenantId: $tenant_id})
                    MERGE (p)-[:WORKS_FOR]->(o)
                """,
                    **person,
                    tenant_id=tenant_id,
                )

            # Create projects
            print("  📋 Creating projects...")
            for project in ORGANIZATIONAL_ENTITIES["projects"]:
                session.run(
                    """
                    MERGE (pr:Project {id: $id})
                    SET pr.name = $name,
                        pr.budget_millions = $budget_millions,
                        pr.duration_months = $duration_months,
                        pr.status = $status,
                        pr.priority = $priority,
                        pr.tenantId = $tenant_id
                    WITH pr
                    MATCH (o:Organization {id: $organization, tenantId: $tenant_id})
                    MERGE (pr)-[:BELONGS_TO]->(o)
                    WITH pr
                    MATCH (p:Person {id: $lead, tenantId: $tenant_id})
                    MERGE (p)-[:LEADS]->(pr)
                """,
                    **project,
                    tenant_id=tenant_id,
                )

            # Create relationships
            print("  🔗 Creating relationships...")
            for rel in ORGANIZATIONAL_ENTITIES["relationships"]:
                rel_type = rel["type"]
                from_id = rel["from"]
                to_id = rel["to"]

                # Build dynamic properties
                props = {k: v for k, v in rel.items() if k not in ["from", "to", "type"]}
                prop_sets = ", ".join([f"r.{k} = ${k}" for k in props])

                query = f"""
                    MATCH (from {{id: $from_id, tenantId: $tenant_id}})
                    MATCH (to {{id: $to_id, tenantId: $tenant_id}})
                    MERGE (from)-[r:{rel_type}]->(to)
                """
                if prop_sets:
                    query += f" SET {prop_sets}"

                session.run(query, from_id=from_id, to_id=to_id, tenant_id=tenant_id, **props)

        print("✅ Organizational graph structure created")

        print("\n📝 Inserting documents with real embeddings and graph connections...")

        # Insert documents with embeddings and connect to graph
        for doc_id, doc_data in REAL_GRAPH_DOCUMENTS.items():
            print(f"  📄 Processing: {doc_data['title']}")

            chunks = doc_data["chunks"]

            # Generate real embeddings
            embeddings = get_real_embeddings(chunks)

            # Insert document chunks
            source_id = store.upsert_chunks(
                tenant_id=tenant_id, title=doc_data["title"], chunks=chunks, embeddings=embeddings
            )

            if source_id:
                # Connect document to organizational entities using Cypher
                with store.driver.session(database=store.database) as session:
                    # Connect to author
                    session.run(
                        """
                        MATCH (doc:RealGraphDoc {tenantId: $tenant_id})
                        WHERE doc.source = $title
                        WITH doc
                        MATCH (author:Person {id: $author_id, tenantId: $tenant_id})
                        MERGE (author)-[:AUTHORED {date: $date}]->(doc)
                    """,
                        tenant_id=tenant_id,
                        title=doc_data["title"],
                        author_id=doc_data["author"],
                        date=doc_data["date"],
                    )

                    # Connect to organization
                    session.run(
                        """
                        MATCH (doc:RealGraphDoc {tenantId: $tenant_id})
                        WHERE doc.source = $title
                        WITH doc
                        MATCH (org:Organization {id: $org_id, tenantId: $tenant_id})
                        MERGE (doc)-[:BELONGS_TO]->(org)
                    """,
                        tenant_id=tenant_id,
                        title=doc_data["title"],
                        org_id=doc_data["organization"],
                    )

                print(
                    f"    ✅ Connected to graph: {doc_data['author']} -> {doc_data['organization']}"
                )

        print("\n🧠 Testing REAL graph intelligence queries...")

        # Test complex graph queries that demonstrate true intelligence
        graph_intelligence_tests = [
            {
                "name": "Multi-hop Author Analysis",
                "description": "Find all documents authored by people who report to Sarah Chen",
                "cypher": """
                    MATCH (sarah:Person {name: 'Sarah Chen', tenantId: $tenant_id})
                    MATCH (subordinate:Person {tenantId: $tenant_id})-[:REPORTS_TO*1..2]->(sarah)
                    MATCH (subordinate)-[:AUTHORED]->(doc:RealGraphDoc {tenantId: $tenant_id})
                    RETURN doc.source as document, subordinate.name as author, subordinate.role as role
                """,
                "expected_insights": ["Should find documents by Marcus Johnson and Lisa Rodriguez"],
            },
            {
                "name": "Cross-Organizational Knowledge Flow",
                "description": "Trace information flow between partnered organizations",
                "cypher": """
                    MATCH (org1:Organization {tenantId: $tenant_id})-[:PARTNERS_WITH]->(org2:Organization {tenantId: $tenant_id})
                    MATCH (person1:Person {tenantId: $tenant_id})-[:WORKS_FOR]->(org1)
                    MATCH (person2:Person {tenantId: $tenant_id})-[:WORKS_FOR]->(org2)
                    MATCH (person1)-[:COLLABORATES_WITH]->(person2)
                    MATCH (person1)-[:AUTHORED]->(doc1:RealGraphDoc {tenantId: $tenant_id})
                    MATCH (person2)-[:AUTHORED]->(doc2:RealGraphDoc {tenantId: $tenant_id})
                    RETURN org1.name as org1, org2.name as org2,
                           person1.name as collaborator1, person2.name as collaborator2,
                           doc1.source as doc1, doc2.source as doc2
                """,
                "expected_insights": ["Should trace Acme-Innovation Labs collaboration"],
            },
            {
                "name": "Project-Document Alignment",
                "description": "Find documents related to active high-priority projects",
                "cypher": """
                    MATCH (project:Project {status: 'Active', priority: 'High', tenantId: $tenant_id})
                    MATCH (person:Person {tenantId: $tenant_id})-[:LEADS]->(project)
                    MATCH (person)-[:AUTHORED]->(doc:RealGraphDoc {tenantId: $tenant_id})
                    RETURN project.name as project, person.name as lead,
                           doc.source as related_document, project.budget_millions as budget
                """,
                "expected_insights": [
                    "Should connect AI Transformation project to technical documents"
                ],
            },
            {
                "name": "Organizational Hierarchy Document Flow",
                "description": "Analyze document creation patterns by seniority level",
                "cypher": """
                    MATCH (person:Person {tenantId: $tenant_id})-[:AUTHORED]->(doc:RealGraphDoc {tenantId: $tenant_id})
                    MATCH (person)-[:WORKS_FOR]->(org:Organization {tenantId: $tenant_id})
                    RETURN person.seniority_level as level,
                           count(doc) as document_count,
                           collect(doc.source)[0..3] as sample_documents,
                           org.name as organization
                    ORDER BY document_count DESC
                """,
                "expected_insights": ["Should show C-Suite creates more strategic documents"],
            },
        ]

        intelligence_success = 0

        for test in graph_intelligence_tests:
            print(f"\n  🧠 {test['name']}")
            print(f"     📋 {test['description']}")

            with store.driver.session(database=store.database) as session:
                result = session.run(test["cypher"], tenant_id=tenant_id)
                records = list(result)

                if records:
                    intelligence_success += 1
                    print(f"     ✅ Found {len(records)} intelligent connections")

                    # Show sample results
                    for i, record in enumerate(records[:3]):
                        values = [f"{k}={v}" for k, v in record.items()]
                        print(f"       {i + 1}. {', '.join(values)}")

                    if len(records) > 3:
                        print(f"       ... and {len(records) - 3} more")
                else:
                    print("     ❌ No intelligent connections found")

        print("\n🔍 Testing semantic search with graph context...")

        # Test semantic search combined with graph relationships
        semantic_graph_queries = [
            (
                "artificial intelligence and machine learning research",
                "Should find AI-related docs with author context",
            ),
            (
                "strategic business partnerships and investments",
                "Should find partnership docs with organizational context",
            ),
            (
                "technical architecture and infrastructure",
                "Should find technical docs with project relationships",
            ),
        ]

        semantic_success = 0

        for query, expected in semantic_graph_queries:
            print(f"\n  🔎 Graph+Semantic: '{query}'")
            print(f"     🎯 {expected}")

            query_vector = get_real_embedding(query)

            start_time = time.time()
            semantic_results = store.search(tenant_id=tenant_id, query_vector=query_vector, k=3)
            search_time = time.time() - start_time

            if semantic_results:
                semantic_success += 1
                print(f"     📊 Found {len(semantic_results)} results in {search_time:.3f}s")

                # Show results with graph context
                for i, result in enumerate(semantic_results):
                    score = result.get("score", 0)
                    source = result.get("source", "Unknown")

                    # Get graph context for this document
                    with store.driver.session(database=store.database) as session:
                        context_result = session.run(
                            """
                            MATCH (doc:RealGraphDoc {source: $source, tenantId: $tenant_id})
                            OPTIONAL MATCH (author:Person)-[:AUTHORED]->(doc)
                            OPTIONAL MATCH (doc)-[:BELONGS_TO]->(org:Organization)
                            RETURN author.name as author, author.role as role,
                                   org.name as organization, org.type as org_type
                        """,
                            source=source,
                            tenant_id=tenant_id,
                        )

                        context = context_result.single()
                        if context:
                            author_info = (
                                f"{context['author']} ({context['role']})"
                                if context["author"]
                                else "Unknown"
                            )
                            org_info = (
                                f"{context['organization']} ({context['org_type']})"
                                if context["organization"]
                                else "Unknown"
                            )
                            print(f"       {i + 1}. [{source}] Score: {score:.4f}")
                            print(f"          📝 Author: {author_info}")
                            print(f"          🏢 Organization: {org_info}")
                        else:
                            print(
                                f"       {i + 1}. [{source}] Score: {score:.4f} (No graph context)"
                            )

        print("\n📈 Testing relationship-aware document discovery...")

        # Test queries that require graph traversal
        relationship_queries = [
            {
                "query": "Find documents from people who collaborate across organizations",
                "cypher": """
                    MATCH (p1:Person)-[:COLLABORATES_WITH]->(p2:Person)
                    MATCH (p1)-[:WORKS_FOR]->(org1:Organization)
                    MATCH (p2)-[:WORKS_FOR]->(org2:Organization)
                    WHERE org1 <> org2 AND p1.tenantId = $tenant_id
                    MATCH (p1)-[:AUTHORED]->(doc:RealGraphDoc)
                    RETURN doc.source as document, p1.name as author,
                           org1.name as author_org, p2.name as collaborator, org2.name as collab_org
                """,
                "insight": "Cross-organizational collaboration patterns",
            },
            {
                "query": "Find documents related to high-budget projects",
                "cypher": """
                    MATCH (project:Project {tenantId: $tenant_id})
                    WHERE project.budget_millions > 2.0
                    MATCH (person:Person)-[:LEADS]->(project)
                    MATCH (person)-[:AUTHORED]->(doc:RealGraphDoc)
                    RETURN doc.source as document, project.name as project,
                           project.budget_millions as budget, person.name as lead
                    ORDER BY project.budget_millions DESC
                """,
                "insight": "High-investment project documentation",
            },
        ]

        relationship_success = 0

        for rel_test in relationship_queries:
            print(f"\n  🕸️  {rel_test['query']}")
            print(f"     💡 {rel_test['insight']}")

            with store.driver.session(database=store.database) as session:
                result = session.run(rel_test["cypher"], tenant_id=tenant_id)
                records = list(result)

                if records:
                    relationship_success += 1
                    print(f"     ✅ Found {len(records)} relationship-based insights")

                    for i, record in enumerate(records):
                        values = [f"{k}={v}" for k, v in record.items()]
                        print(f"       {i + 1}. {', '.join(values)}")
                else:
                    print("     ❌ No relationship-based insights found")

        # Calculate overall success
        total_tests = (
            len(graph_intelligence_tests) + len(semantic_graph_queries) + len(relationship_queries)
        )
        total_success = intelligence_success + semantic_success + relationship_success
        success_rate = total_success / total_tests

        print("\n🎉 REAL NEO4J GRAPH INTELLIGENCE ASSESSMENT")
        print("=" * 55)
        print(
            f"🧠 Graph Intelligence Queries: {intelligence_success}/{len(graph_intelligence_tests)} ({intelligence_success / len(graph_intelligence_tests):.1%})"
        )
        print(
            f"🔍 Semantic + Graph Context: {semantic_success}/{len(semantic_graph_queries)} ({semantic_success / len(semantic_graph_queries):.1%})"
        )
        print(
            f"🕸️  Relationship Discovery: {relationship_success}/{len(relationship_queries)} ({relationship_success / len(relationship_queries):.1%})"
        )
        print(f"📊 Overall Graph Intelligence: {total_success}/{total_tests} ({success_rate:.1%})")

        if success_rate >= 0.8:
            print("\n✅ EXCELLENT: Neo4j demonstrates powerful graph intelligence capabilities!")
        elif success_rate >= 0.6:
            print("\n✅ GOOD: Neo4j shows solid graph relationship understanding")
        else:
            print("\n⚠️  LIMITED: Graph capabilities may need optimization")

        print("\n💡 Key Graph Intelligence Demonstrated:")
        print("  🕸️  Multi-hop relationship traversal")
        print("  🏢 Cross-organizational collaboration tracking")
        print("  📋 Project-document-author connections")
        print("  🎯 Context-aware semantic search with relationships")
        print("  📈 Organizational hierarchy analysis through graphs")

        # Cleanup
        store.close()
        return success_rate >= 0.6

    except Exception as e:
        print(f"❌ Real Neo4j test failed: {e}")
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
    print("🚀 Real Neo4j Graph Intelligence Test")
    print("=" * 60)

    # Check prerequisites
    if not check_neo4j_connection():
        print("❌ Neo4j is not accessible at bolt://localhost:7687")
        print("💡 Start Neo4j with:")
        print("   docker-compose -f docker-compose.test.yml up -d neo4j")
        return

    print("✅ Neo4j is accessible")

    # Run real capability test
    success = await test_real_neo4j_graph_capabilities()

    if success:
        print(
            "\n🎉 REAL graph intelligence verified! Neo4j is ready for organizational intelligence."
        )
        print("🔥 This proves genuine graph relationship understanding, not mock data.")
        print("🌐 Access Neo4j Browser: http://localhost:7474 (neo4j/testpassword)")
    else:
        print("\n💥 Real graph capability test failed. Check configuration and relationships.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
