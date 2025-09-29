"""
Research activities for Temporal workflows
All OpenAI API calls should be in activities, not workflows
"""

import asyncio
from dataclasses import dataclass

from local_agent.core.clarifying_agent import Clarifications
from local_agent.core.pdf_generator_agent import (
    new_pdf_generator_agent,
)
from local_agent.core.planner_agent import (
    WebSearchPlan,
    new_planner_agent,
)
from local_agent.core.search_agent import new_search_agent
from local_agent.core.triage_agent import new_triage_agent
from local_agent.core.writer_agent import (
    ReportData,
    new_writer_agent,
)
import openai
from temporalio import activity

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


async def retry_with_backoff(func, *args, max_retries=3, **kwargs):
    """Retry function with exponential backoff and specific error handling"""
    last_exception = None

    for attempt in range(max_retries):
        try:
            return await func(*args, **kwargs)
        except openai.APIConnectionError as e:
            last_exception = e
            if attempt == max_retries - 1:
                activity.logger.error(f"Final attempt failed with connection error: {e}")
                # Return a safe fallback result
                break
            wait_time = 2**attempt
            activity.logger.warning(
                f"Connection error on attempt {attempt + 1}: {e}. Retrying in {wait_time}s..."
            )
            await asyncio.sleep(wait_time)
        except openai.RateLimitError as e:
            last_exception = e
            if attempt == max_retries - 1:
                activity.logger.error(f"Rate limit exceeded after {max_retries} attempts: {e}")
                break
            wait_time = 10 * (2**attempt)  # Longer wait for rate limits
            activity.logger.warning(
                f"Rate limit on attempt {attempt + 1}: {e}. Retrying in {wait_time}s..."
            )
            await asyncio.sleep(wait_time)
        except openai.APIError as e:
            last_exception = e
            activity.logger.error(f"OpenAI API error on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                break
            wait_time = 2**attempt
            await asyncio.sleep(wait_time)
        except Exception as e:
            last_exception = e
            activity.logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                break
            wait_time = 2**attempt
            await asyncio.sleep(wait_time)

    # If we get here, all retries failed
    activity.logger.error(f"All {max_retries} attempts failed. Last error: {last_exception}")
    raise last_exception


@activity.defn
async def check_clarifications_needed(query: str) -> ClarificationResult:
    """Check if clarifications are needed for the query"""
    try:
        run_config = RunConfig()
        triage_agent = new_triage_agent()

        async def run_triage():
            trace_id = gen_trace_id()
            with trace("Clarification check", trace_id=trace_id):
                input_items: list[TResponseInputItem] = [{"content": query, "role": "user"}]
                return await Runner.run(
                    triage_agent,
                    input_items,
                    run_config=run_config,
                )

        try:
            result = await retry_with_backoff(run_triage)

            # Check if clarifications were generated
            clarifications = _extract_clarifications(result)
            if clarifications and isinstance(clarifications, Clarifications):
                return ClarificationResult(
                    needs_clarifications=True, questions=clarifications.questions
                )
            else:
                # No clarifications needed, run direct research
                plan_result = await plan_searches(query)
                search_results = await perform_searches(plan_result)
                report = await write_report(query, search_results)
                return ClarificationResult(
                    needs_clarifications=False,
                    research_output=report.markdown_report,
                    report_data=report,
                )
        except Exception as e:
            activity.logger.error(f"Triage agent failed: {e}. Falling back to direct research.")
            # Fallback: skip clarifications and go straight to research
            try:
                plan_result = await plan_searches(query)
                search_results = await perform_searches(plan_result)
                report = await write_report(query, search_results)
                return ClarificationResult(
                    needs_clarifications=False,
                    research_output=report.markdown_report,
                    report_data=report,
                )
            except Exception as fallback_e:
                activity.logger.error(f"Fallback research also failed: {fallback_e}")
                # Final fallback: return a basic result
                return ClarificationResult(
                    needs_clarifications=False,
                    research_output=f"Research could not be completed due to technical issues. Query was: {query}",
                    report_data=None,
                )
    except Exception as e:
        activity.logger.error(f"Critical error in check_clarifications_needed: {e}")
        return ClarificationResult(
            needs_clarifications=False,
            research_output=f"Research could not be completed due to technical issues. Query was: {query}",
            report_data=None,
        )


@activity.defn
async def plan_searches(query: str) -> WebSearchPlan:
    """Plan web searches for the query"""
    try:
        run_config = RunConfig()
        planner_agent = new_planner_agent()

        async def run_planner():
            input_str: str = f"Query: {query}"
            result = await Runner.run(
                planner_agent,
                input_str,
                run_config=run_config,
            )
            return result.final_output_as(WebSearchPlan)

        return await retry_with_backoff(run_planner)
    except Exception as e:
        activity.logger.error(f"Search planning failed: {e}. Using fallback search plan.")
        # Fallback: create a simple search plan
        from local_agent.core.planner_agent import WebSearchItem

        return WebSearchPlan(
            searches=[
                WebSearchItem(query=query, reason="Direct search fallback due to planning failure")
            ]
        )


@activity.defn
async def perform_searches(search_plan: WebSearchPlan) -> list[str]:
    """Perform web searches based on the plan"""
    try:
        run_config = RunConfig()
        search_agent = new_search_agent()

        async def run_single_search(item):
            input_str: str = f"Search term: {item.query}\nReason for searching: {item.reason}"
            result = await Runner.run(
                search_agent,
                input_str,
                run_config=run_config,
            )
            return str(result.final_output) if result.final_output else None

        with custom_span("Search the web"):
            results = []
            for item in search_plan.searches:
                try:
                    result = await retry_with_backoff(run_single_search, item)
                    if result:
                        results.append(result)
                except Exception as e:
                    activity.logger.warning(f"Search failed for '{item.query}': {e}")
                    # Add a fallback search result
                    results.append(
                        f"Search for '{item.query}' failed, but this topic is relevant to the query."
                    )

            # Ensure we have at least one result
            if not results:
                results.append(
                    f"No search results were available. Please consider the query: {search_plan.searches[0].query if search_plan.searches else 'No search terms available'}"
                )

            return results
    except Exception as e:
        activity.logger.error(f"All searches failed: {e}")
        return [
            "Search functionality is currently unavailable. Please provide research based on general knowledge."
        ]


@activity.defn
async def write_report(query: str, search_results: list[str]) -> ReportData:
    """Write the final research report"""
    try:
        run_config = RunConfig()
        writer_agent = new_writer_agent()

        async def run_writer():
            input_str: str = f"Original query: {query}\nSummarized search results: {search_results}"

            # Generate markdown report
            markdown_result = await Runner.run(
                writer_agent,
                input_str,
                run_config=run_config,
            )

            return markdown_result.final_output_as(ReportData)

        return await retry_with_backoff(run_writer)
    except Exception as e:
        activity.logger.error(f"Report writing failed: {e}. Creating fallback report.")
        # Fallback: create a basic report
        fallback_content = f"""# Research Report

## Query
{query}

## Summary
Due to technical difficulties, a detailed research report could not be generated. However, based on the available search information, here is what we found:

## Available Information
"""
        for i, result in enumerate(search_results[:3], 1):
            fallback_content += f"\n{i}. {result}\n"

        fallback_content += """
## Conclusion
This research was limited due to technical issues. For more comprehensive results, please try again later or consider rephrasing your query.

## Follow-up Questions
- Would you like to try a more specific version of this query?
- Are there particular aspects of this topic you'd like to focus on?
"""

        return ReportData(
            short_summary=f"Limited research on: {query}",
            markdown_report=fallback_content,
            follow_up_questions=[
                "Would you like to try a more specific version of this query?",
                "Are there particular aspects of this topic you'd like to focus on?",
            ],
        )


@activity.defn
async def generate_pdf_report(report_data: ReportData) -> str | None:
    """Generate PDF from markdown report, return file path"""
    try:
        run_config = RunConfig()
        pdf_generator_agent = new_pdf_generator_agent()

        async def run_pdf_generator():
            pdf_result = await Runner.run(
                pdf_generator_agent,
                f"Convert this markdown report to PDF:\n\n{report_data.markdown_report}",
                run_config=run_config,
            )

            pdf_output = pdf_result.final_output_as(type(pdf_result.final_output))
            if pdf_output.success:
                return pdf_output.pdf_file_path
            return None

        return await retry_with_backoff(run_pdf_generator)
    except Exception as e:
        activity.logger.warning(f"PDF generation failed: {e}. Skipping PDF creation.")
        # PDF generation is optional, so we return None instead of failing
        return None


@activity.defn
async def complete_research_with_clarifications(
    original_query: str, questions: list[str], responses: dict[str, str]
) -> ReportData:
    """Complete research using clarification responses"""
    try:
        trace_id = gen_trace_id()
        with trace("Enhanced Research with clarifications", trace_id=trace_id):
            # Enrich the query with clarification responses
            enriched_query = _enrich_query(original_query, questions, responses)

            # Now run the full research pipeline with the enriched query
            search_plan = await plan_searches(enriched_query)
            search_results = await perform_searches(search_plan)
            report = await write_report(enriched_query, search_results)

            return report
    except Exception as e:
        activity.logger.error(f"Enhanced research with clarifications failed: {e}")
        # Fallback: try basic research without enhancement
        try:
            search_plan = await plan_searches(original_query)
            search_results = await perform_searches(search_plan)
            report = await write_report(original_query, search_results)
            return report
        except Exception as fallback_e:
            activity.logger.error(f"Fallback research also failed: {fallback_e}")
            # Final fallback: create a basic report with clarification info
            clarifications_text = "\n".join(
                [
                    f"Q: {q}\nA: {responses.get(f'question_{i}', 'No answer')}"
                    for i, q in enumerate(questions)
                ]
            )

            fallback_content = f"""# Research Report with Clarifications

## Original Query
{original_query}

## Clarifications Provided
{clarifications_text}

## Summary
Due to technical difficulties, detailed research could not be completed. However, your clarifications have been noted and would help provide more targeted research when the system is available.

## Next Steps
Please try your research again later, or consider breaking down your query into smaller, more specific questions.
"""

            return ReportData(
                short_summary=f"Research limited due to technical issues: {original_query}",
                markdown_report=fallback_content,
                follow_up_questions=["Would you like to try again with a simpler query?"],
            )


def _extract_clarifications(result) -> Clarifications | None:
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
    except Exception:
        return None


def _enrich_query(original_query: str, questions: list[str], responses: dict[str, str]) -> str:
    """Combine original query with clarification responses"""
    enriched = f"Original query: {original_query}\n\nAdditional context from clarifications:\n"
    for i, question in enumerate(questions):
        answer = responses.get(f"question_{i}", "No specific preference")
        enriched += f"- {question}: {answer}\n"
    return enriched
