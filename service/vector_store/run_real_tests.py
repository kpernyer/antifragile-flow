#!/usr/bin/env python3
"""
REAL vector store capability test runner - NO MOCKS!

This runs comprehensive tests using actual:
- OpenAI embeddings (requires API key)
- Neo4j graph relationships and complex queries
- Weaviate semantic search and hybrid capabilities
- Compound intelligence demonstrating superiority over individual stores

Prerequisites:
- OPENAI_API_KEY environment variable
- Docker services running (Neo4j + Weaviate)

Usage:
    export OPENAI_API_KEY="your-key-here"
    python run_real_tests.py
"""

import asyncio
import os
from pathlib import Path
import sys


async def check_prerequisites():
    """Check all prerequisites for real testing."""
    print("🔍 Checking Prerequisites...")

    # Check OpenAI API key
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("❌ OPENAI_API_KEY environment variable not set")
        print("💡 Get your key at: https://platform.openai.com/api-keys")
        print("💡 Export it: export OPENAI_API_KEY='your-key-here'")
        return False
    elif len(openai_key) < 20:
        print("❌ OPENAI_API_KEY appears to be invalid (too short)")
        return False
    else:
        print(f"✅ OpenAI API key configured ({openai_key[:8]}...)")

    # Check OpenAI library
    try:
        import openai

        print("✅ OpenAI library available")
    except ImportError:
        print("❌ OpenAI library not installed")
        print("💡 Install with: pip install openai")
        return False

    # Check Docker services
    neo4j_ok = check_neo4j_health()
    weaviate_ok = check_weaviate_health()

    if not neo4j_ok:
        print("❌ Neo4j not accessible at bolt://localhost:7687")
    else:
        print("✅ Neo4j accessible and healthy")

    if not weaviate_ok:
        print("❌ Weaviate not accessible at http://localhost:8081")
    else:
        print("✅ Weaviate accessible and healthy")

    if not (neo4j_ok and weaviate_ok):
        print("\n💡 Start services with:")
        print("   docker-compose -f docker-compose.test.yml up -d")
        return False

    return True


def check_neo4j_health():
    """Check if Neo4j is healthy."""
    try:
        from neo4j import GraphDatabase

        driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "testpassword"))
        with driver.session() as session:
            session.run("RETURN 1")
        driver.close()
        return True
    except:
        return False


def check_weaviate_health():
    """Check if Weaviate is healthy."""
    try:
        import requests

        response = requests.get("http://localhost:8081/v1/.well-known/ready", timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"    Debug: Weaviate health check failed: {e}")
        return False


async def run_real_test_script(script_name: str, description: str):
    """Run a real test script and return success status."""
    print(f"\n{'=' * 70}")
    print(f"🔥 {description} - REAL CAPABILITIES TEST")
    print(f"{'=' * 70}")

    script_path = Path(__file__).parent / script_name

    try:
        process = await asyncio.create_subprocess_exec(
            sys.executable,
            str(script_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            env={**os.environ},  # Pass through environment variables including OPENAI_API_KEY
        )

        stdout, _ = await process.communicate()

        # Print output
        output = stdout.decode()
        print(output)

        success = process.returncode == 0

        if success:
            print(f"\n✅ {description} - REAL CAPABILITIES VERIFIED")
        else:
            print(f"\n❌ {description} - REAL CAPABILITIES TEST FAILED")

        return success

    except Exception as e:
        print(f"❌ Error running {script_name}: {e}")
        return False


async def estimate_api_costs():
    """Estimate OpenAI API costs for the test suite."""
    print("\n💰 OpenAI API Cost Estimate:")

    # Rough estimates based on test data
    test_estimates = {
        "Weaviate Test": {"chunks": 25, "queries": 15, "total_tokens": 8000, "cost_usd": 0.01},
        "Neo4j Test": {"chunks": 30, "queries": 20, "total_tokens": 10000, "cost_usd": 0.013},
        "Compound Test": {"chunks": 35, "queries": 25, "total_tokens": 12000, "cost_usd": 0.015},
    }

    total_cost = sum(test["cost_usd"] for test in test_estimates.values())
    total_tokens = sum(test["total_tokens"] for test in test_estimates.values())

    for test_name, estimate in test_estimates.items():
        print(
            f"  {test_name:<15} ~{estimate['chunks']} chunks, ~{estimate['queries']} queries → ~${estimate['cost_usd']:.3f}"
        )

    print(f"\n  📊 Total Estimated Cost: ~${total_cost:.3f} USD")
    print(f"  📊 Total Tokens: ~{total_tokens:,}")
    print("  💡 Using text-embedding-3-small ($0.00002/1K tokens)")

    print("\n✅ Proceeding with real API testing...")
    return True


async def main():
    """Main real test orchestrator."""
    print("🔥 ANTIFRAGILE FLOW - REAL VECTOR STORE CAPABILITIES TEST")
    print("=" * 70)
    print("This test suite uses:")
    print("  🧠 Real OpenAI embeddings (requires API key & costs ~$0.04)")
    print("  🕸️  Real Neo4j graph relationships and complex queries")
    print("  🌐 Real Weaviate semantic search and hybrid capabilities")
    print("  🏆 Real compound intelligence superiority demonstration")
    print("=" * 70)

    # Check prerequisites
    if not await check_prerequisites():
        print("\n❌ Prerequisites not met. Please fix the above issues and try again.")
        return

    print("\n✅ All prerequisites satisfied!")

    # Estimate costs
    if not await estimate_api_costs():
        print("Test cancelled by user.")
        return

    print("\n🚀 Starting REAL capability tests...")

    # Run all real tests
    test_results = {}

    real_tests = [
        ("test_real_weaviate.py", "Weaviate Real Semantic Intelligence"),
        ("test_real_neo4j.py", "Neo4j Real Graph Intelligence"),
        ("test_real_compound.py", "Compound Real Intelligence Superiority"),
    ]

    for script, description in real_tests:
        print(f"\n⏳ Preparing to run {description}...")
        print("   This will use real OpenAI API calls and may take several minutes...")

        success = await run_real_test_script(script, description)
        test_results[description] = success

        if success:
            print(f"🎉 {description} - PASSED")
        else:
            print(f"💥 {description} - FAILED")

        # Brief pause between tests
        await asyncio.sleep(2)

    # Final assessment
    print("\n" + "=" * 70)
    print("🏆 REAL VECTOR STORE CAPABILITIES - FINAL ASSESSMENT")
    print("=" * 70)

    passed = sum(test_results.values())
    total = len(test_results)

    for test_name, success in test_results.items():
        status = "✅ REAL CAPABILITIES VERIFIED" if success else "❌ CAPABILITIES FAILED"
        print(f"  {test_name:<35} {status}")

    print(f"\nOverall: {passed}/{total} real capability tests passed")

    if passed == total:
        print("\n🎉 ALL REAL CAPABILITIES VERIFIED!")
        print("🔥 Your vector store services demonstrate genuine intelligence:")
        print("   🧠 True semantic understanding (not keyword matching)")
        print("   🕸️  Complex graph relationship analysis")
        print("   🏆 Compound intelligence superior to individual stores")
        print("   📊 Ready for production organizational intelligence workloads!")

        print("\n🚀 Next Steps:")
        print("  1. Integrate into your DocumentProcessing workflows")
        print("  2. Configure production embeddings (consider fine-tuning)")
        print("  3. Import knowledge-representation data for enhanced relationships")
        print("  4. Set up monitoring and observability")
        print("  5. Implement real-time organizational intelligence features")

    elif passed >= 2:
        print(f"\n✅ STRONG CAPABILITIES DEMONSTRATED ({passed}/{total})")
        print(
            "Most real capabilities are working. Check failed tests for optimization opportunities."
        )

    else:
        print(f"\n⚠️  LIMITED REAL CAPABILITIES ({passed}/{total})")
        print("Some fundamental issues need to be resolved.")

    print("\n🔗 Service Access:")
    print("  Neo4j Browser: http://localhost:7474 (neo4j/testpassword)")
    print("  Weaviate API: http://localhost:8081/v1")


if __name__ == "__main__":
    asyncio.run(main())
