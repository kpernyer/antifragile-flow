#!/usr/bin/env python3
"""
Master test runner for all vector store services.

This script runs comprehensive isolated tests for:
- Weaviate service
- Neo4j service
- Compound service (orchestration)

Usage:
    python run_all_tests.py
"""

import asyncio
from pathlib import Path
import subprocess
import sys


async def check_docker_services():
    """Check if required Docker services are running."""
    print("🐳 Checking Docker services...")

    # Check if docker-compose is available
    try:
        result = subprocess.run(
            ["docker-compose", "--version"], capture_output=True, text=True, check=True
        )
        print("✅ Docker Compose is available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker Compose not found. Please install Docker Compose.")
        return False

    # Check if services are running
    compose_file = Path(__file__).parent / "docker-compose.test.yml"

    try:
        result = subprocess.run(
            ["docker-compose", "-f", str(compose_file), "ps", "-q"],
            capture_output=True,
            text=True,
            check=True,
        )

        running_services = result.stdout.strip().split("\n") if result.stdout.strip() else []

        if len(running_services) >= 2:  # neo4j + weaviate at minimum
            print(f"✅ Found {len(running_services)} running services")
            return True
        else:
            print(f"⚠️  Only {len(running_services)} services running")
            return False

    except subprocess.CalledProcessError:
        print("❌ Could not check service status")
        return False


async def start_docker_services():
    """Start the required Docker services."""
    print("\n🚀 Starting Docker services...")
    compose_file = Path(__file__).parent / "docker-compose.test.yml"

    try:
        process = subprocess.Popen(
            ["docker-compose", "-f", str(compose_file), "up", "-d"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        stdout, stderr = process.communicate()

        if process.returncode == 0:
            print("✅ Docker services started successfully")
            print("\n⏳ Waiting for services to be ready...")

            # Wait for services to be healthy
            for i in range(30):  # Wait up to 30 seconds
                await asyncio.sleep(1)

                # Check health
                neo4j_ready = check_neo4j_health()
                weaviate_ready = check_weaviate_health()

                if neo4j_ready and weaviate_ready:
                    print("✅ All services are ready!")
                    return True

                if i % 5 == 0:  # Print status every 5 seconds
                    neo_status = "✅" if neo4j_ready else "⏳"
                    weaviate_status = "✅" if weaviate_ready else "⏳"
                    print(f"   Neo4j: {neo_status}  Weaviate: {weaviate_status}")

            print("⚠️  Services started but may not be fully ready")
            return True

        else:
            print(f"❌ Failed to start services: {stderr}")
            return False

    except Exception as e:
        print(f"❌ Error starting services: {e}")
        return False


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

        response = requests.get("http://localhost:8080/v1/.well-known/ready", timeout=2)
        return response.status_code == 200
    except:
        return False


async def run_test_script(script_name: str, description: str):
    """Run a test script and return success status."""
    print(f"\n{'=' * 60}")
    print(f"🧪 {description}")
    print(f"{'=' * 60}")

    script_path = Path(__file__).parent / script_name

    try:
        process = await asyncio.create_subprocess_exec(
            sys.executable,
            str(script_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        stdout, _ = await process.communicate()

        # Print output in real-time style
        output = stdout.decode()
        print(output)

        success = process.returncode == 0

        if success:
            print(f"\n✅ {description} PASSED")
        else:
            print(f"\n❌ {description} FAILED")

        return success

    except Exception as e:
        print(f"❌ Error running {script_name}: {e}")
        return False


async def main():
    """Main test orchestrator."""
    print("🚀 ANTIFRAGILE FLOW - VECTOR STORE TEST SUITE")
    print("=" * 60)
    print("Testing isolated vector store services:")
    print("  🌐 Weaviate Service (semantic search)")
    print("  🕸️  Neo4j Service (graph relationships)")
    print("  🧠 Compound Service (intelligent orchestration)")
    print("=" * 60)

    # Check if services are already running
    services_running = await check_docker_services()

    if not services_running:
        print("\n📋 Starting required services...")
        started = await start_docker_services()
        if not started:
            print("❌ Could not start services. Exiting.")
            return

    # Final health check
    print("\n🏥 Final health check...")
    neo4j_ready = check_neo4j_health()
    weaviate_ready = check_weaviate_health()

    print(f"  Neo4j (bolt://localhost:7687): {'✅ Ready' if neo4j_ready else '❌ Not ready'}")
    print(f"  Weaviate (http://localhost:8080): {'✅ Ready' if weaviate_ready else '❌ Not ready'}")

    if not (neo4j_ready and weaviate_ready):
        print("\n⚠️  Some services are not ready. Tests may fail.")
        print("💡 You can:")
        print("  1. Wait a few more minutes for services to start")
        print("  2. Check Docker logs: docker-compose -f docker-compose.test.yml logs")
        print("  3. Restart services: docker-compose -f docker-compose.test.yml restart")

        response = input("\nContinue anyway? (y/N): ").strip().lower()
        if response != "y":
            print("Exiting.")
            return

    # Run all tests
    test_results = {}

    tests = [
        ("test_weaviate_isolated.py", "Weaviate Service Test"),
        ("test_neo4j_isolated.py", "Neo4j Service Test"),
        ("test_compound_isolated.py", "Compound Service Test"),
    ]

    for script, description in tests:
        success = await run_test_script(script, description)
        test_results[description] = success

    # Summary
    print("\n" + "=" * 60)
    print("🎯 TEST SUITE SUMMARY")
    print("=" * 60)

    passed = sum(test_results.values())
    total = len(test_results)

    for test_name, success in test_results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"  {test_name:<30} {status}")

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Your vector store services are working perfectly!")
        print("\n💡 Next Steps:")
        print("  1. Integrate services into your DocumentProcessing workflow")
        print("  2. Set up proper embedding generation (replace mock embeddings)")
        print("  3. Configure production databases")
        print("  4. Add monitoring and observability")

        print("\n🔗 Service Access:")
        print("  Neo4j Browser: http://localhost:7474 (neo4j/testpassword)")
        print("  Weaviate API: http://localhost:8080/v1")

    else:
        print(f"\n💥 {total - passed} test(s) failed. Check the output above for details.")

        print("\n🔧 Troubleshooting:")
        print("  1. Check service logs: docker-compose -f docker-compose.test.yml logs")
        print("  2. Restart services: docker-compose -f docker-compose.test.yml restart")
        print("  3. Check port conflicts (7474, 7687, 8080)")
        print("  4. Ensure sufficient Docker resources (memory/CPU)")


if __name__ == "__main__":
    asyncio.run(main())
