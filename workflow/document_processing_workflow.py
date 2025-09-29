"""
Document Processing Workflow - Business process for handling document uploads.

This workflow orchestrates the complete document processing pipeline:
1. Quick summary generation for immediate admin feedback
2. Full document analysis for business intelligence
3. Storage and indexing for future retrieval

This is a proper business workflow that coordinates multiple activities.
"""

from dataclasses import dataclass
from datetime import timedelta

from temporalio import workflow

from activity.document_activities import (
    DocumentSummaryResult,
    DocumentSummaryWorkflowResult,
    process_document_upload,  # Pure technical activity
)
from activity.organizational_learning_activities import (
    TrainingJobSubmission,
    submit_model_training_job,
    validate_training_readiness,
)
from agent_activity.ai_activities import (
    analyze_document_content,
    generate_document_summary,  # AI-powered activities
)


@dataclass
class DocumentProcessingRequest:
    """Request for document processing workflow"""

    file_paths: list[str]
    priority: str = "normal"  # low, normal, high
    admin_notification: bool = True
    deep_analysis: bool = True

    # Organizational learning options
    organization_name: str = ""
    organization_id: str = ""
    enable_model_training: bool = False
    model_preference: str = "balanced"  # fast, balanced, detailed
    organizational_values: list[str] = None
    communication_style: str = "professional"


@dataclass
class DocumentResult:
    """Result for a single document"""

    file_path: str
    quick_summary: DocumentSummaryWorkflowResult | None = None
    full_analysis: DocumentSummaryResult | None = None
    storage_info: dict | None = None
    success: bool = False
    error: str | None = None


@dataclass
class DocumentProcessingResult:
    """Result from document processing workflow"""

    request_id: str
    total_documents: int
    successful_documents: int
    failed_documents: int
    results: list[DocumentResult]
    admin_summaries: list[DocumentSummaryWorkflowResult]  # For immediate UI display
    business_analysis: list[DocumentSummaryResult]  # For business intelligence
    success: bool

    # Organizational learning results
    training_job_id: str = ""
    training_initiated: bool = False


@workflow.defn
class DocumentProcessingWorkflow:
    """
    Business workflow for document processing.

    Handles multiple documents with both quick summaries for admin UI
    and full analysis for business intelligence.

    Usage in OrganizationOnboardingWorkflow:
        doc_result = await workflow.execute_child_workflow(
            DocumentProcessingWorkflow.run,
            DocumentProcessingRequest(file_paths=documents)
        )
    """

    @workflow.run
    async def run(self, request: DocumentProcessingRequest) -> DocumentProcessingResult:
        """
        Execute document processing for multiple documents.

        Args:
            request: Document processing request with files and options

        Returns:
            Complete processing results with summaries and analysis
        """

        workflow.logger.info(
            f"Starting document processing for {len(request.file_paths)} documents"
        )

        request_id = f"doc-proc-{workflow.info().workflow_id}"
        results = []
        admin_summaries = []
        business_analysis = []
        successful_count = 0

        # Process each document
        for i, file_path in enumerate(request.file_paths):
            workflow.logger.info(
                f"Processing document {i + 1}/{len(request.file_paths)}: {file_path}"
            )

            doc_result = DocumentResult(file_path=file_path)

            try:
                # Step 1: Quick summary for admin UI (immediate feedback)
                if request.admin_notification:
                    quick_summary = await workflow.execute_activity(
                        generate_document_summary,
                        file_path,
                        start_to_close_timeout=timedelta(minutes=5),
                        retry_policy=workflow.RetryPolicy(
                            initial_interval=timedelta(seconds=5),
                            maximum_attempts=3,
                        ),
                    )
                    doc_result.quick_summary = quick_summary
                    admin_summaries.append(quick_summary)
                    workflow.logger.info(f"Quick summary completed for: {file_path}")

                # Step 2: Full analysis for business intelligence (if requested)
                if request.deep_analysis:
                    # Process document upload
                    document_info = await workflow.execute_activity(
                        process_document_upload,
                        file_path,
                        start_to_close_timeout=timedelta(minutes=5),
                        retry_policy=workflow.RetryPolicy(
                            initial_interval=timedelta(seconds=5),
                            maximum_attempts=3,
                        ),
                    )

                    # Analyze content
                    full_analysis = await workflow.execute_activity(
                        analyze_document_content,
                        document_info,
                        start_to_close_timeout=timedelta(minutes=10),
                        retry_policy=workflow.RetryPolicy(
                            initial_interval=timedelta(seconds=10),
                            maximum_attempts=2,
                        ),
                    )

                    doc_result.full_analysis = full_analysis
                    business_analysis.append(full_analysis)
                    workflow.logger.info(f"Full analysis completed for: {file_path}")

                # Mark as successful
                doc_result.success = True
                successful_count += 1

            except Exception as e:
                error_msg = f"Document processing failed for {file_path}: {e!s}"
                workflow.logger.error(error_msg)
                doc_result.error = error_msg
                doc_result.success = False

            results.append(doc_result)

        # Optionally initiate model training (non-blocking)
        training_job_id = ""
        training_initiated = False

        if request.enable_model_training and request.organization_name and successful_count > 0:
            try:
                # Convert processed documents for training
                training_documents = []
                for analysis in business_analysis:
                    training_documents.append(
                        {
                            "text": analysis.full_summary or analysis.short_summary,
                            "title": analysis.file_name,
                            "type": "organizational_document",
                        }
                    )

                # Validate training readiness
                validation = await workflow.execute_activity(
                    validate_training_readiness,
                    request.organization_name,
                    training_documents,
                    start_to_close_timeout=timedelta(minutes=1),
                )

                if validation["ready"]:
                    # Submit training job (returns immediately)
                    training_submission = TrainingJobSubmission(
                        organization_name=request.organization_name,
                        organization_id=request.organization_id,
                        processed_documents=training_documents,
                        model_preference=request.model_preference,
                        organizational_values=request.organizational_values,
                        communication_style=request.communication_style,
                        deploy_immediately=True,
                    )

                    training_job_id = await workflow.execute_activity(
                        submit_model_training_job,
                        training_submission,
                        start_to_close_timeout=timedelta(minutes=2),
                    )

                    training_initiated = True
                    workflow.logger.info(
                        f"Model training job {training_job_id} submitted for {request.organization_name}"
                    )
                else:
                    workflow.logger.info(
                        f"Skipping model training for {request.organization_name}: insufficient data"
                    )

            except Exception as e:
                workflow.logger.warning(f"Could not initiate model training: {e}")

        # Create final result
        final_result = DocumentProcessingResult(
            request_id=request_id,
            total_documents=len(request.file_paths),
            successful_documents=successful_count,
            failed_documents=len(request.file_paths) - successful_count,
            results=results,
            admin_summaries=admin_summaries,
            business_analysis=business_analysis,
            success=successful_count > 0,  # Success if at least one document processed
            training_job_id=training_job_id,
            training_initiated=training_initiated,
        )

        workflow.logger.info(
            f"Document processing completed: {successful_count}/{len(request.file_paths)} successful"
        )

        return final_result

    @workflow.query
    def get_processing_status(self) -> dict:
        """Query to get current processing status"""
        return {
            "status": "processing",
            "workflow_id": workflow.info().workflow_id,
            "stage": "document_processing",
        }
