from dataclasses import dataclass

from temporalio import workflow

from activity.research_activities import (
    perform_searches,
    plan_searches,
    write_report,
)


@dataclass
class ResearchWorkflowResult:
    """Result from research workflow with markdown report"""

    short_summary: str
    markdown_report: str
    follow_up_questions: list[str]


@workflow.defn
class ResearchWorkflow:
    @workflow.run
    async def run(self, query: str) -> ResearchWorkflowResult:
        # Get the full report data using activities
        search_plan = await workflow.execute_activity(
            plan_searches,
            query,
            start_to_close_timeout=workflow.timedelta(minutes=5),
        )
        search_results = await workflow.execute_activity(
            perform_searches,
            search_plan,
            start_to_close_timeout=workflow.timedelta(minutes=10),
        )
        report_data = await workflow.execute_activity(
            write_report,
            args=(query, search_results),
            start_to_close_timeout=workflow.timedelta(minutes=5),
        )

        return ResearchWorkflowResult(
            short_summary=report_data.short_summary,
            markdown_report=report_data.markdown_report,
            follow_up_questions=report_data.follow_up_questions,
        )
