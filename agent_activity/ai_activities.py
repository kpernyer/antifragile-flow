"""
AI-powered document and research activities using OpenAI agents framework.
These activities handle all AI operations that require OpenAI API calls.
"""

from datetime import datetime
from pathlib import Path

from temporalio import activity

# Import data classes from main activity module
from activity.document_activities import (
    DocumentInfo,
    DocumentSummaryResult,
    DocumentSummaryWorkflowResult,
    SimpleResearchResult,
)
from agent_activity.core.writer_agent import (
    ReportData,
    new_writer_agent,
)
from agents import (
    RunConfig,
    Runner,
    gen_trace_id,
    trace,
)


@activity.defn
async def analyze_document_content(document_info: DocumentInfo) -> DocumentSummaryResult:
    """Analyze document content and generate summary with key takeaways"""

    activity.logger.info(f"Analyzing document: {document_info.file_name}")

    try:
        # Initialize the research agent with proper tracing
        run_config = RunConfig(trace_id=gen_trace_id())

        # Create an agent to analyze the document
        research_agent = new_writer_agent()

        # Create prompt for document analysis
        analysis_prompt = f"""
        Please analyze the following document and provide a comprehensive summary:

        Document: {document_info.file_name}
        Type: {document_info.file_type}
        Content:
        {document_info.extracted_text}

        Please provide:
        1. A short summary (2-3 sentences)
        2. Key takeaways (3-5 bullet points)
        3. Main topics covered
        4. A detailed markdown report
        """

        with trace("document_analysis_agent", run_config.trace_id):
            result = await Runner.run(research_agent, analysis_prompt, run_config)

            if result.is_success:
                report_data: ReportData = result.data

                # Extract structured information from the response
                summary_result = DocumentSummaryResult(
                    document_info=document_info,
                    short_summary=report_data.executive_summary or "Summary not available",
                    key_takeaways=report_data.key_findings or [],
                    main_topics=report_data.research_scope or [],
                    markdown_report=report_data.full_report or "",
                    confidence_score=0.8,  # Default confidence
                )

                activity.logger.info(f"Document analysis completed for: {document_info.file_name}")
                return summary_result
            else:
                error_msg = f"Document analysis failed: {result.error}"
                activity.logger.error(error_msg)
                raise Exception(error_msg)

    except Exception as e:
        activity.logger.error(f"Document analysis failed for {document_info.file_name}: {e!s}")
        raise


@activity.defn
async def generate_document_summary(file_path: str) -> DocumentSummaryWorkflowResult:
    """
    Quick document summary for immediate admin UI display.
    Combines document processing + summary generation for fast user feedback.
    """

    activity.logger.info(f"Generating quick summary for: {file_path}")

    try:
        # First process the document upload
        from activity.document_activities import process_document_upload

        document_info = await process_document_upload(file_path)

        # Then analyze with AI
        analysis_result = await analyze_document_content(document_info)

        # Convert to workflow result format for UI
        workflow_result = DocumentSummaryWorkflowResult(
            document_name=document_info.file_name,
            document_type=document_info.file_type,
            summary_text=analysis_result.short_summary,
            key_points=analysis_result.key_takeaways,
            topics=analysis_result.main_topics,
            processing_time=datetime.now().isoformat(),
            success=True,
        )

        activity.logger.info(f"Quick summary completed for: {file_path}")
        return workflow_result

    except Exception as e:
        error_msg = f"Quick summary generation failed for {file_path}: {e!s}"
        activity.logger.error(error_msg)

        # Return error result for UI
        return DocumentSummaryWorkflowResult(
            document_name=Path(file_path).name,
            document_type="unknown",
            summary_text=f"Error: {error_msg}",
            key_points=[],
            topics=[],
            processing_time=datetime.now().isoformat(),
            success=False,
            error_message=error_msg,
        )


@activity.defn
async def perform_simple_research(query: str, context: str | None = None) -> SimpleResearchResult:
    """
    Perform simple research using OpenAI agents with prompt templates.
    Fallback to basic OpenAI API if prompt system fails.
    """

    activity.logger.info(f"Performing research: {query}")

    try:
        # Initialize the research agent
        run_config = RunConfig(trace_id=gen_trace_id())

        research_agent = new_writer_agent()

        # Create research prompt
        context_text = f"\nContext: {context}" if context else ""
        research_prompt = f"""
        Please research the following query and provide a comprehensive response:

        Query: {query}{context_text}

        Please provide:
        1. Direct answer to the query
        2. Key findings and insights
        3. Sources or reasoning behind your conclusions
        4. Any relevant background information
        """

        with trace("simple_research_agent", run_config.trace_id):
            result = await Runner.run(research_agent, research_prompt, run_config)

            if result.is_success:
                report_data: ReportData = result.data

                research_result = SimpleResearchResult(
                    query=query,
                    context=context,
                    findings=report_data.full_report or "No findings available",
                    key_insights=report_data.key_findings or [],
                    sources=["OpenAI GPT Analysis"],  # Agent-based source
                    confidence_score=0.8,
                    research_timestamp=datetime.now().isoformat(),
                    success=True,
                )

                activity.logger.info(f"Research completed for query: {query}")
                return research_result
            else:
                error_msg = f"Research failed: {result.error}"
                activity.logger.error(error_msg)
                raise Exception(error_msg)

    except Exception as e:
        activity.logger.error(f"Research failed for query '{query}': {e!s}")

        # Return error result
        return SimpleResearchResult(
            query=query,
            context=context,
            findings=f"Research failed: {e!s}",
            key_insights=[],
            sources=[],
            confidence_score=0.0,
            research_timestamp=datetime.now().isoformat(),
            success=False,
            error_message=str(e),
        )
