#!/usr/bin/env python3
"""
Direct testing of AI agents without Temporal workflows.
Fastest way to test individual AI activities.
"""

import asyncio
from pathlib import Path


# Test document creation
def create_test_document():
    """Create a simple test document for AI testing"""
    test_file = Path("test_document.txt")
    test_content = """
    QUARTERLY BUSINESS REPORT - Q3 2024

    Executive Summary:
    Our company achieved strong growth in Q3 2024 with revenue increasing 15%
    compared to the previous quarter. Key highlights include:

    - Revenue: $2.5M (up 15% from Q2)
    - New customer acquisitions: 150 accounts
    - Product launches: 2 major features released
    - Team expansion: Hired 8 new employees

    Key Challenges:
    - Supply chain delays affecting delivery times
    - Increased competition in the market
    - Rising operational costs

    Future Outlook:
    Q4 2024 looks promising with several large deals in the pipeline
    and continued product development initiatives.
    """

    test_file.write_text(test_content.strip())
    return str(test_file.absolute())


async def test_document_processing():
    """Test document processing activities directly"""
    print("🧪 TESTING DOCUMENT PROCESSING ACTIVITIES")
    print("=" * 50)

    try:
        # Import activities
        from activity.document_activities import process_document_upload
        from agent_activity.ai_activities import analyze_document_content, generate_document_summary

        # Create test document
        test_file = create_test_document()
        print(f"📄 Created test document: {test_file}")

        # Test 1: Pure technical activity
        print("\n1️⃣ Testing technical document upload...")
        document_info = await process_document_upload(test_file)
        print(f"✅ Document processed: {document_info.file_name}")
        print(f"   Size: {document_info.file_size} bytes")
        print(f"   Type: {document_info.file_type}")
        print(f"   Text length: {len(document_info.extracted_text)} chars")

        # Test 2: AI-powered analysis
        print("\n2️⃣ Testing AI document analysis...")
        analysis_result = await analyze_document_content(document_info)
        print(f"✅ Analysis completed with confidence: {analysis_result.confidence_score}")
        print(f"   Summary: {analysis_result.short_summary}")
        print(f"   Key takeaways: {len(analysis_result.key_takeaways)} items")
        print(f"   Main topics: {analysis_result.main_topics}")

        # Test 3: Quick summary (combines both)
        print("\n3️⃣ Testing quick document summary...")
        summary_result = await generate_document_summary(test_file)
        print(f"✅ Quick summary completed: {summary_result.file_name}")
        print(f"   Success: {summary_result.success}")
        print(f"   Summary: {summary_result.summary_text}")

        # Cleanup
        Path(test_file).unlink()
        print("\n🧹 Cleaned up test file")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        # Cleanup on error
        if Path("test_document.txt").exists():
            Path("test_document.txt").unlink()


async def test_research_activity():
    """Test research activity directly"""
    print("\n🔍 TESTING RESEARCH ACTIVITY")
    print("=" * 50)

    try:
        from agent_activity.ai_activities import perform_simple_research

        # Test research
        query = "What are the key benefits of workflow orchestration?"
        context = "Software development context"

        print(f"🔍 Testing research query: '{query}'")
        research_result = await perform_simple_research(query, context)

        print("✅ Research completed")
        print(f"   Success: {research_result.success}")
        print(f"   Confidence: {research_result.confidence_score}")
        print(f"   Findings length: {len(research_result.findings)} chars")
        print(f"   Key insights: {len(research_result.key_insights)} items")

        if research_result.key_insights:
            print("   First insight:", research_result.key_insights[0])

    except Exception as e:
        print(f"❌ Research test failed: {e}")


async def test_agent_core():
    """Test core agent functionality"""
    print("\n🤖 TESTING CORE AGENT")
    print("=" * 50)

    try:
        from agent_activity.core.writer_agent import new_writer_agent
        from agents import RunConfig, Runner, gen_trace_id, trace

        # Create agent
        writer_agent = new_writer_agent()
        print("✅ Writer agent created")

        # Test simple prompt
        run_config = RunConfig(trace_id=gen_trace_id())
        prompt = "Write a brief summary of the benefits of AI in business."

        print("🤖 Testing agent with simple prompt...")
        with trace("test_agent", run_config.trace_id):
            result = await Runner.run(writer_agent, prompt, run_config=run_config)

            if result.final_output:
                print("✅ Agent execution successful")
                report_data = result.final_output
                print(
                    f"   Content length: {len(getattr(report_data, 'content', 'No content'))} chars"
                )
            else:
                print("❌ Agent execution failed: No output generated")

    except Exception as e:
        print(f"❌ Core agent test failed: {e}")


async def main():
    """Run all AI agent tests"""
    print("🧪 AI AGENT TESTING SUITE")
    print("=" * 60)

    # Test document processing
    await test_document_processing()

    # Test research
    await test_research_activity()

    # Test core agent
    await test_agent_core()

    print("\n🎯 TESTING COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
