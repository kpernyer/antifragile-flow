"""
Scheduler workflows for automated and cron-based operations.
Demonstrates how to implement scheduled tasks using Temporal.
"""

from dataclasses import dataclass
from datetime import datetime

from temporalio import workflow

from activity.scheduler_activities import (
    CompetitorScanRequest,
    CompetitorScanResult,
    ScheduledTaskResult,
    cleanup_old_data,
    health_check_external_services,
    schedule_competitor_scan,
    send_scheduled_notification,
)


@dataclass
class WeeklyCompetitorReportRequest:
    """Request for weekly competitor monitoring report"""

    competitors: list[str]
    recipients: list[str]
    scan_types: list[str] = None
    notification_enabled: bool = True


@dataclass
class WeeklyCompetitorReportResult:
    """Result from weekly competitor monitoring"""

    report_id: str
    report_date: datetime
    competitors_analyzed: int
    scan_results: list[CompetitorScanResult]
    notifications_sent: int
    success: bool


@workflow.defn
class CompetitorMonitoringWorkflow:
    """
    Weekly competitor monitoring workflow.
    Scheduled to run every Monday morning at 9 AM.

    Usage:
        # Start cron workflow
        await client.start_workflow(
            CompetitorMonitoringWorkflow.run,
            request,
            id="weekly-competitor-monitoring",
            cron_schedule="0 9 * * 1",  # Every Monday 9 AM
            task_queue=shared.TASK_QUEUE_NAME,
        )
    """

    @workflow.run
    async def run(self, request: WeeklyCompetitorReportRequest) -> WeeklyCompetitorReportResult:
        """Execute weekly competitor monitoring"""

        workflow.logger.info(
            f"Starting weekly competitor monitoring for {len(request.competitors)} competitors"
        )

        report_id = f"competitor-report-{datetime.now().strftime('%Y%m%d')}"
        scan_results = []
        notifications_sent = 0

        try:
            # Step 1: Scan each competitor
            for scan_type in request.scan_types or ["news"]:
                scan_request = CompetitorScanRequest(
                    competitors=request.competitors,
                    scan_type=scan_type,
                    lookback_days=7,  # Last week
                    priority="normal",
                )

                scan_result = await workflow.execute_activity(
                    schedule_competitor_scan,
                    scan_request,
                    start_to_close_timeout=workflow.timedelta(minutes=10),
                    retry_policy=workflow.RetryPolicy(
                        initial_interval=workflow.timedelta(seconds=5),
                        maximum_attempts=3,
                    ),
                )

                scan_results.append(scan_result)

            # Step 2: Send notifications if enabled
            if request.notification_enabled and scan_results:
                successful_scans = [r for r in scan_results if r.success]
                total_findings = sum(r.results_found for r in successful_scans)

                # Create summary message
                summary = f"Weekly Competitor Report ({report_id})\\n"
                summary += f"Competitors monitored: {len(request.competitors)}\\n"
                summary += f"Total findings: {total_findings}\\n"
                summary += f"Scan types: {', '.join(request.scan_types or ['news'])}\\n\\n"

                for result in successful_scans:
                    summary += f"- {result.competitors_scanned} competitors scanned, {result.results_found} results found\\n"

                # Send to each recipient
                for recipient in request.recipients:
                    notification_result = await workflow.execute_activity(
                        send_scheduled_notification,
                        recipient,
                        f"Weekly Competitor Report - {datetime.now().strftime('%Y-%m-%d')}",
                        summary,
                        "email",
                        start_to_close_timeout=workflow.timedelta(minutes=2),
                    )

                    if notification_result.success:
                        notifications_sent += 1

            workflow.logger.info(f"Weekly competitor monitoring completed: {report_id}")

            return WeeklyCompetitorReportResult(
                report_id=report_id,
                report_date=datetime.now(),
                competitors_analyzed=len(request.competitors),
                scan_results=scan_results,
                notifications_sent=notifications_sent,
                success=True,
            )

        except Exception as e:
            workflow.logger.error(f"Weekly competitor monitoring failed: {e}")

            return WeeklyCompetitorReportResult(
                report_id=report_id,
                report_date=datetime.now(),
                competitors_analyzed=len(request.competitors),
                scan_results=scan_results,
                notifications_sent=notifications_sent,
                success=False,
            )


@workflow.defn
class MaintenanceWorkflow:
    """
    Daily maintenance workflow for system cleanup and health checks.
    Scheduled to run every day at 2 AM.

    Usage:
        # Start cron workflow
        await client.start_workflow(
            MaintenanceWorkflow.run,
            id="daily-maintenance",
            cron_schedule="0 2 * * *",  # Every day at 2 AM
            task_queue=shared.TASK_QUEUE_NAME,
        )
    """

    @workflow.run
    async def run(self) -> list[ScheduledTaskResult]:
        """Execute daily maintenance tasks"""

        workflow.logger.info("Starting daily maintenance workflow")

        results = []

        try:
            # Task 1: Health check of external services
            health_result = await workflow.execute_activity(
                health_check_external_services,
                start_to_close_timeout=workflow.timedelta(minutes=5),
            )
            results.append(health_result)

            # Task 2: Cleanup old documents (keep 30 days)
            doc_cleanup_result = await workflow.execute_activity(
                cleanup_old_data,
                "documents",
                30,
                start_to_close_timeout=workflow.timedelta(minutes=10),
            )
            results.append(doc_cleanup_result)

            # Task 3: Cleanup old reports (keep 90 days)
            report_cleanup_result = await workflow.execute_activity(
                cleanup_old_data,
                "reports",
                90,
                start_to_close_timeout=workflow.timedelta(minutes=5),
            )
            results.append(report_cleanup_result)

            # Task 4: Cleanup cache data (keep 7 days)
            cache_cleanup_result = await workflow.execute_activity(
                cleanup_old_data,
                "cache",
                7,
                start_to_close_timeout=workflow.timedelta(minutes=5),
            )
            results.append(cache_cleanup_result)

            # Send summary notification if any task failed
            failed_tasks = [r for r in results if not r.success]
            if failed_tasks:
                summary = f"Daily maintenance completed with {len(failed_tasks)} failures:\\n"
                for task in failed_tasks:
                    summary += (
                        f"- {task.task_type}: {task.results.get('error', 'Unknown error')}\\n"
                    )

                await workflow.execute_activity(
                    send_scheduled_notification,
                    "admin@company.com",
                    "Daily Maintenance Alert - Some Tasks Failed",
                    summary,
                    "email",
                    start_to_close_timeout=workflow.timedelta(minutes=2),
                )

            workflow.logger.info(
                f"Daily maintenance completed. {len(results)} tasks executed, {len(failed_tasks)} failed"
            )

            return results

        except Exception as e:
            workflow.logger.error(f"Daily maintenance workflow failed: {e}")

            # Send error notification
            await workflow.execute_activity(
                send_scheduled_notification,
                "admin@company.com",
                "Daily Maintenance Error",
                f"Daily maintenance workflow failed: {e!s}",
                "email",
                start_to_close_timeout=workflow.timedelta(minutes=2),
            )

            return results


@workflow.defn
class AdHocSchedulerWorkflow:
    """
    Ad-hoc scheduler for one-time or irregular scheduled tasks.
    Can be used for manual triggers or custom scheduling patterns.
    """

    @workflow.run
    async def run(self, task_type: str, task_params: dict) -> ScheduledTaskResult:
        """Execute an ad-hoc scheduled task"""

        workflow.logger.info(f"Starting ad-hoc task: {task_type}")

        if task_type == "competitor_scan":
            request = CompetitorScanRequest(**task_params)
            result = await workflow.execute_activity(
                schedule_competitor_scan,
                request,
                start_to_close_timeout=workflow.timedelta(minutes=15),
            )

            return ScheduledTaskResult(
                task_id=result.scan_id,
                task_type=task_type,
                execution_time=result.scan_date,
                success=result.success,
                results={
                    "competitors_scanned": result.competitors_scanned,
                    "results_found": result.results_found,
                    "scan_duration": result.scan_duration_seconds,
                },
            )

        elif task_type == "health_check":
            result = await workflow.execute_activity(
                health_check_external_services,
                start_to_close_timeout=workflow.timedelta(minutes=5),
            )
            return result

        elif task_type == "cleanup":
            data_type = task_params.get("data_type", "documents")
            retention_days = task_params.get("retention_days", 30)

            result = await workflow.execute_activity(
                cleanup_old_data,
                data_type,
                retention_days,
                start_to_close_timeout=workflow.timedelta(minutes=10),
            )
            return result

        else:
            # Unknown task type
            return ScheduledTaskResult(
                task_id=f"unknown-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                task_type=task_type,
                execution_time=datetime.now(),
                success=False,
                results={"error": f"Unknown task type: {task_type}"},
            )
