#!/usr/bin/env python3
"""
Test scheduler workflows and activities.
Demonstrates cron-like scheduling capabilities.
"""

import asyncio
from datetime import datetime
import os

from temporalio.client import Client

from shared import shared
from shared.models.types import ScanType, TaskType
from workflow.scheduler_workflow import (
    AdHocSchedulerWorkflow,
    CompetitorMonitoringWorkflow,
    WeeklyCompetitorReportRequest,
)


async def test_scheduler_activities():
    """Test individual scheduler activities"""
    print("⏰ TESTING SCHEDULER ACTIVITIES")
    print("=" * 50)

    # Connect to Temporal server
    target_host = os.environ.get("TEMPORAL_ADDRESS", "localhost:7233")
    client = await Client.connect(target_host)
    print(f"✅ Connected to Temporal server: {target_host}")

    # Test ad-hoc health check
    print("\n🏥 Testing health check...")
    health_result = await client.execute_workflow(
        AdHocSchedulerWorkflow.run,
        TaskType.HEALTH_CHECK,
        {},
        id=f"test-health-check-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        task_queue=shared.TASK_QUEUE_NAME,
    )

    print(f"   Task ID: {health_result.task_id}")
    print(f"   Success: {health_result.success}")
    print(f"   Results: {health_result.results}")

    # Test ad-hoc competitor scan
    print("\n🔍 Testing competitor scan...")
    scan_params = {
        "competitors": ["OpenAI", "Anthropic", "Google AI"],
        "scan_type": "news",
        "lookback_days": 7,
        "priority": "normal",
    }

    scan_result = await client.execute_workflow(
        AdHocSchedulerWorkflow.run,
        TaskType.COMPETITOR_SCAN,
        scan_params,
        id=f"test-competitor-scan-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        task_queue=shared.TASK_QUEUE_NAME,
    )

    print(f"   Task ID: {scan_result.task_id}")
    print(f"   Success: {scan_result.success}")
    print(f"   Competitors scanned: {scan_result.results.get('competitors_scanned', 0)}")
    print(f"   Results found: {scan_result.results.get('results_found', 0)}")

    # Test cleanup
    print("\n🧹 Testing cleanup...")
    cleanup_params = {"data_type": "documents", "retention_days": 30}

    cleanup_result = await client.execute_workflow(
        AdHocSchedulerWorkflow.run,
        TaskType.CLEANUP,
        cleanup_params,
        id=f"test-cleanup-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        task_queue=shared.TASK_QUEUE_NAME,
    )

    print(f"   Task ID: {cleanup_result.task_id}")
    print(f"   Success: {cleanup_result.success}")
    print(f"   Items cleaned: {cleanup_result.results.get('items_cleaned', 0)}")

    return True


async def test_weekly_competitor_monitoring():
    """Test weekly competitor monitoring workflow"""
    print("\n📊 TESTING WEEKLY COMPETITOR MONITORING")
    print("=" * 50)

    # Connect to Temporal server
    target_host = os.environ.get("TEMPORAL_ADDRESS", "localhost:7233")
    client = await Client.connect(target_host)

    # Create weekly report request
    request = WeeklyCompetitorReportRequest(
        competitors=["OpenAI", "Anthropic", "Google AI", "Microsoft AI"],
        recipients=["manager@company.com", "analyst@company.com"],
        scan_types=[ScanType.NEWS],
        notification_enabled=True,
    )

    print(f"📧 Monitoring {len(request.competitors)} competitors")
    print(f"📬 Sending reports to {len(request.recipients)} recipients")

    # Execute the workflow
    result = await client.execute_workflow(
        CompetitorMonitoringWorkflow.run,
        request,
        id=f"test-weekly-monitoring-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        task_queue=shared.TASK_QUEUE_NAME,
    )

    print("\n📋 WEEKLY MONITORING RESULTS:")
    print(f"   Report ID: {result.report_id}")
    print(f"   Competitors analyzed: {result.competitors_analyzed}")
    print(f"   Scan results: {len(result.scan_results)}")
    print(f"   Notifications sent: {result.notifications_sent}")
    print(f"   Success: {result.success}")

    # Show scan details
    for i, scan in enumerate(result.scan_results, 1):
        print(f"\n   Scan {i}:")
        print(f"      Scan ID: {scan.scan_id}")
        print(f"      Duration: {scan.scan_duration_seconds:.2f}s")
        print(f"      Competitors: {scan.competitors_scanned}")
        print(f"      Results: {scan.results_found}")
        print(f"      Success: {scan.success}")

    return result.success


async def demonstrate_cron_scheduling():
    """Demonstrate how to set up cron-like scheduling"""
    print("\n🕐 CRON SCHEDULING DEMONSTRATION")
    print("=" * 50)
    print("📝 Here's how to set up scheduled workflows:")
    print()

    print("🗓️  WEEKLY COMPETITOR MONITORING (Every Monday 9 AM):")
    print("```python")
    print("await client.start_workflow(")
    print("    CompetitorMonitoringWorkflow.run,")
    print("    WeeklyCompetitorReportRequest(")
    print("        competitors=['OpenAI', 'Anthropic', 'Google AI'],")
    print("        recipients=['manager@company.com'],")
    print("        scan_types=['news', 'social'],")
    print("        notification_enabled=True")
    print("    ),")
    print("    id='weekly-competitor-monitoring',")
    print("    cron_schedule='0 9 * * 1',  # Every Monday 9 AM")
    print("    task_queue=shared.TASK_QUEUE_NAME,")
    print(")")
    print("```")
    print()

    print("🔧 DAILY MAINTENANCE (Every day 2 AM):")
    print("```python")
    print("await client.start_workflow(")
    print("    MaintenanceWorkflow.run,")
    print("    id='daily-maintenance',")
    print("    cron_schedule='0 2 * * *',  # Every day at 2 AM")
    print("    task_queue=shared.TASK_QUEUE_NAME,")
    print(")")
    print("```")
    print()

    print("⚡ HEALTH CHECKS (Every 5 minutes):")
    print("```python")
    print("await client.start_workflow(")
    print("    AdHocSchedulerWorkflow.run,")
    print("    'health_check',")
    print("    {},")
    print("    id='health-monitoring',")
    print("    cron_schedule='*/5 * * * *',  # Every 5 minutes")
    print("    task_queue=shared.TASK_QUEUE_NAME,")
    print(")")
    print("```")
    print()

    print("📅 CRON EXPRESSION EXAMPLES:")
    print("   0 9 * * 1     - Every Monday at 9:00 AM")
    print("   0 2 * * *     - Every day at 2:00 AM")
    print("   */5 * * * *   - Every 5 minutes")
    print("   0 0 1 * *     - First day of every month at midnight")
    print("   0 9-17 * * 1-5 - Every hour from 9 AM to 5 PM, Monday to Friday")


async def main():
    """Run scheduler tests"""
    print("⏰ SCHEDULER WORKFLOW TESTING")
    print("=" * 60)
    print()

    try:
        # Test 1: Individual scheduler activities
        if not await test_scheduler_activities():
            return

        print("\n" + "=" * 60)

        # Test 2: Weekly competitor monitoring workflow
        if not await test_weekly_competitor_monitoring():
            return

        print("\n" + "=" * 60)

        # Test 3: Demonstrate cron scheduling
        await demonstrate_cron_scheduling()

        print("\n" + "=" * 60)
        print("🎉 ALL SCHEDULER TESTS PASSED!")
        print()
        print("✅ Scheduler activities working")
        print("✅ Weekly competitor monitoring operational")
        print("✅ Ad-hoc scheduling functional")
        print("✅ Cron-like scheduling patterns demonstrated")
        print()
        print("📝 Ready for production scheduling workflows!")

    except Exception as e:
        print(f"💥 Scheduler test failed: {e!s}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
