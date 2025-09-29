from __future__ import annotations

import asyncio
from dataclasses import dataclass

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    # TODO: Restore progress updates
    from openai_agents.workflows.research_agents.clarifying_agent import Clarifications
    from openai_agents.workflows.research_agents.pdf_generator_agent import (
        new_pdf_generator_agent,
    )

    # from openai_agents.workflows.research_agents.instruction_agent import (
    #     new_instruction_agent,
    # )
    from openai_agents.workflows.research_agents.planner_agent import (
        WebSearchItem,
        WebSearchPlan,
        new_planner_agent,
    )
    from openai_agents.workflows.research_agents.search_agent import new_search_agent
    from openai_agents.workflows.research_agents.triage_agent import new_triage_agent
    from openai_agents.workflows.research_agents.writer_agent import (
        ReportData,
        new_writer_agent,
    )

    from agents import (
        RunConfig,
        Runner,
        TResponseInputItem,
        custom_span,
        gen_trace_id,
        trace,
    )


@dataclass
class ClarificationResult:
    """Result from initial clarification check"""

    needs_clarifications: bool
    questions: list[str] | None = None
    research_output: str | None = None
    report_data: ReportData | None = None


class InteractiveResearchManager:
    def __init__(self):
        self.run_config = RunConfig()
        self.search_agent = new_search_agent()
        self.planner_agent = new_planner_agent()
        self.writer_agent = new_writer_agent()
        self.triage_agent = new_triage_agent()
        self.pdf_generator_agent = new_pdf_generator_agent()

    async def run(self, query: str, use_clarifications: bool = False) -> str:
        """
        Run research with optional clarifying questions flow

        Args:
            query: The research query
            use_clarifications: If True, uses multi-agent flow with clarifying questions
        """
        if use_clarifications:
            # This method is for backwards compatibility, just use direct flow
            report = await self._run_direct(query)
            return report.markdown_report
        else:
            report = await self._run_direct(query)
            return report.markdown_report

    async def _run_direct(self, query: str) -> ReportData:
        """Original direct research flow"""
        trace_id = gen_trace_id()
        with trace("Research trace", trace_id=trace_id):
            search_plan = await self._plan_searches(query)
            search_results = await self._perform_searches(search_plan)
            report = await self._write_report(query, search_results)

        return report

    async def run_with_clarifications_start(self, query: str) -> ClarificationResult:
        """Start clarification flow and return whether clarifications are needed"""
        trace_id = gen_trace_id()
        with trace("Clarification check", trace_id=trace_id):
            # Start with triage agent to determine if clarifications are needed
            input_items: list[TResponseInputItem] = [{"content": query, "role": "user"}]
            result = await Runner.run(
                self.triage_agent,
                input_items,
                run_config=self.run_config,
            )

            # Check if clarifications were generated
            clarifications = self._extract_clarifications(result)
            if clarifications and isinstance(clarifications, Clarifications):
                return ClarificationResult(
                    needs_clarifications=True, questions=clarifications.questions
                )
            else:
                # No clarifications needed, continue with research
                # The triage agent routed to instruction agent, which should then
                # continue through planner -> search -> writer automatically
                # Let's run the direct research flow since no clarifications are needed
                search_plan = await self._plan_searches(query)
                search_results = await self._perform_searches(search_plan)
                report = await self._write_report(query, search_results)
                return ClarificationResult(
                    needs_clarifications=False,
                    research_output=report.markdown_report,
                    report_data=report,
                )

    async def run_with_clarifications_complete(
        self, original_query: str, questions: list[str], responses: dict[str, str]
    ) -> ReportData:
        """Complete research using clarification responses"""
        trace_id = gen_trace_id()
        with trace("Enhanced Research with clarifications", trace_id=trace_id):
            # Enrich the query with clarification responses
            enriched_query = self._enrich_query(original_query, questions, responses)

            # Now run the full research pipeline with the enriched query
            # This should go through planner → search → writer
            search_plan = await self._plan_searches(enriched_query)
            search_results = await self._perform_searches(search_plan)
            report = await self._write_report(enriched_query, search_results)

            return report

    def _extract_clarifications(self, result) -> Clarifications | None:
        """Extract clarifications from agent result if present"""
        try:
            # Check if the final output is Clarifications
            if hasattr(result, "final_output") and isinstance(result.final_output, Clarifications):
                return result.final_output

            # Look through result items for clarifications
            for item in result.new_items:
                if hasattr(item, "raw_item") and hasattr(item.raw_item, "content"):
                    content = item.raw_item.content
                    if isinstance(content, Clarifications):
                        return content
                # Also check if the item itself has output_type content
                if hasattr(item, "output") and isinstance(item.output, Clarifications):
                    return item.output

            # Try result.final_output_as() method if available
            try:
                clarifications = result.final_output_as(Clarifications)
                if clarifications:
                    return clarifications
            except Exception:
                pass

            return None
        except Exception as e:
            workflow.logger.info(f"Error extracting clarifications: {e}")
            return None

    def _enrich_query(
        self, original_query: str, questions: list[str], responses: dict[str, str]
    ) -> str:
        """Combine original query with clarification responses"""
        enriched = f"Original query: {original_query}\n\nAdditional context from clarifications:\n"
        for i, question in enumerate(questions):
            answer = responses.get(f"question_{i}", "No specific preference")
            enriched += f"- {question}: {answer}\n"
        return enriched

    async def _plan_searches(self, query: str) -> WebSearchPlan:
        input_str: str = f"Query: {query}"
        result = await Runner.run(
            self.planner_agent,
            input_str,
            run_config=self.run_config,
        )
        return result.final_output_as(WebSearchPlan)

    async def _perform_searches(self, search_plan: WebSearchPlan) -> list[str]:
        with custom_span("Search the web"):
            num_completed = 0
            tasks = [asyncio.create_task(self._search(item)) for item in search_plan.searches]
            results = []
            for task in workflow.as_completed(tasks):
                result = await task
                if result is not None:
                    results.append(result)
                num_completed += 1
            return results

    async def _search(self, item: WebSearchItem) -> str | None:
        input_str: str = f"Search term: {item.query}\nReason for searching: {item.reason}"
        try:
            result = await Runner.run(
                self.search_agent,
                input_str,
                run_config=self.run_config,
            )
            return str(result.final_output)
        except Exception:
            return None

    async def _write_report(self, query: str, search_results: list[str]) -> ReportData:
        input_str: str = f"Original query: {query}\nSummarized search results: {search_results}"

        # Generate markdown report
        markdown_result = await Runner.run(
            self.writer_agent,
            input_str,
            run_config=self.run_config,
        )

        report_data = markdown_result.final_output_as(ReportData)
        return report_data

    async def _generate_pdf_report(self, report_data: ReportData) -> str | None:
        """Generate PDF from markdown report, return file path"""
        try:
            pdf_result = await Runner.run(
                self.pdf_generator_agent,
                f"Convert this markdown report to PDF:\n\n{report_data.markdown_report}",
                run_config=self.run_config,
            )

            pdf_output = pdf_result.final_output_as(type(pdf_result.final_output))
            if pdf_output.success:
                return pdf_output.pdf_file_path
        except Exception:
            # If PDF generation fails, return None
            pass
        return None
