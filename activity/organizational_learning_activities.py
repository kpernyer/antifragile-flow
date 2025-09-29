"""
Organizational Learning Activities

These activities handle business-level operations for organizational AI training.
They focus on business concepts and delegate technical implementation to services.

Key principles:
- Activities know about business concepts (training jobs, models, organizations)
- Activities do NOT know about technical details (LoRA, transformers, PyTorch)
- All technical complexity is handled by service layer
- Activities return quickly and don't block workflows
"""

from dataclasses import dataclass
import logging

from temporalio import activity

from service.model_training_service import (
    HumanFeedback,
    ModelType,
    TrainingJobRequest,
    TrainingJobStatus,
    get_model_training_service,
)

logger = logging.getLogger(__name__)


@dataclass
class TrainingJobSubmission:
    """Business request to start model training"""

    organization_name: str
    organization_id: str
    processed_documents: list[dict[str, str]]  # From document processing
    model_preference: str = "balanced"  # fast, balanced, detailed
    organizational_values: list[str] = None
    communication_style: str = "professional"
    deploy_immediately: bool = True
    requester_email: str | None = None



@activity.defn
async def submit_model_training_job(request: TrainingJobSubmission) -> str:
    """
    Submit organizational model training job

    Business operation: Start training a custom AI model for the organization
    Returns immediately with job_id, training continues in background
    """
    activity.logger.info(f"Submitting model training for {request.organization_name}")

    # Map business preferences to technical model types
    model_type_mapping = {
        "fast": ModelType.QWEN_3B,
        "balanced": ModelType.MISTRAL_7B,
        "detailed": ModelType.MISTRAL_7B,
    }

    model_type = model_type_mapping.get(request.model_preference, ModelType.MISTRAL_7B)

    # Create service request
    training_request = TrainingJobRequest(
        organization_name=request.organization_name,
        organization_id=request.organization_id,
        documents=request.processed_documents,
        model_type=model_type,
        organizational_values=request.organizational_values,
        communication_style=request.communication_style,
        deploy_to_ollama=request.deploy_immediately,
        requester_email=request.requester_email,
    )

    # Submit to service (non-blocking)
    service = get_model_training_service()
    job_id = await service.submit_training_job(training_request)

    activity.logger.info(f"Training job {job_id} submitted for {request.organization_name}")
    return job_id


@activity.defn
async def check_training_job_status(job_id: str) -> TrainingJobStatus:
    """
    Check status of training job

    Business operation: Get current status of organizational model training
    """
    activity.logger.info(f"Checking status of training job {job_id}")

    service = get_model_training_service()
    job_result = service.get_job_status(job_id)

    if not job_result:
        return TrainingJobStatus(
            job_id=job_id,
            organization_name="Unknown",
            status="not_found",
            progress_message="Training job not found",
        )

    # Map technical status to business status
    status_messages = {
        "queued": "Training job is queued and will start soon",
        "training": "AI model is being trained with organizational documents",
        "completed": "Organizational AI model is ready for use",
        "failed": "Training encountered an issue and could not complete",
        "cancelled": "Training job was cancelled",
    }

    return TrainingJobStatus(
        job_id=job_id,
        organization_name=job_result.organization_name,
        status=job_result.status.value,
        progress_message=status_messages.get(job_result.status.value, "Status unknown"),
        model_available=job_result.status.value == "completed",
        ollama_model_name=job_result.ollama_model_name,
    )


@activity.defn
async def get_organization_training_history(organization_id: str) -> list[TrainingJobStatus]:
    """
    Get training history for organization

    Business operation: Review all model training attempts for organization
    """
    activity.logger.info(f"Getting training history for {organization_id}")

    service = get_model_training_service()
    jobs = service.list_organization_jobs(organization_id)

    return [
        TrainingJobStatus(
            job_id=job.job_id,
            organization_name=job.organization_name,
            status=job.status.value,
            progress_message=f"Training {job.status.value}",
            model_available=job.status.value == "completed",
            ollama_model_name=job.ollama_model_name,
        )
        for job in jobs
    ]


@activity.defn
async def cancel_training_job(job_id: str) -> bool:
    """
    Cancel training job if possible

    Business operation: Stop model training (if not yet started)
    """
    activity.logger.info(f"Attempting to cancel training job {job_id}")

    service = get_model_training_service()
    cancelled = service.cancel_job(job_id)

    if cancelled:
        activity.logger.info(f"Successfully cancelled training job {job_id}")
    else:
        activity.logger.info(f"Could not cancel training job {job_id} - may have already started")

    return cancelled


@activity.defn
async def collect_model_feedback(
    organization_id: str,
    prompt: str,
    model_response_a: str,
    model_response_b: str,
    preferred_response: str,
    feedback_notes: str = "",
    reviewer_email: str = "",
) -> bool:
    """
    Collect human feedback for model improvement

    Business operation: Gather feedback to improve organizational AI responses
    """
    activity.logger.info(f"Collecting model feedback for {organization_id}")

    feedback = HumanFeedback(
        prompt=prompt,
        response_a=model_response_a,
        response_b=model_response_b,
        preferred_response=preferred_response,
        feedback_text=feedback_notes,
        reviewer=reviewer_email,
    )

    service = get_model_training_service()
    success = await service.collect_human_feedback(organization_id, feedback)

    if success:
        activity.logger.info(f"Feedback collected for {organization_id}")
    else:
        activity.logger.warning(f"Failed to collect feedback for {organization_id}")

    return success


@activity.defn
async def start_model_improvement(organization_id: str) -> str:
    """
    Start model improvement using collected feedback

    Business operation: Improve organizational AI based on human feedback (RLHF)
    """
    activity.logger.info(f"Starting model improvement for {organization_id}")

    service = get_model_training_service()
    improvement_job_id = service.start_rlhf_training(organization_id)

    activity.logger.info(
        f"Model improvement job {improvement_job_id} started for {organization_id}"
    )
    return improvement_job_id


@activity.defn
async def validate_training_readiness(
    organization_name: str, processed_documents: list[dict[str, str]]
) -> dict[str, bool]:
    """
    Validate if organization is ready for model training

    Business operation: Check if we have sufficient data for training
    """
    activity.logger.info(f"Validating training readiness for {organization_name}")

    # Business validation rules
    min_documents = 2
    min_total_content = 1000  # characters
    min_document_size = 200  # characters per document

    has_enough_documents = len(processed_documents) >= min_documents

    total_content = sum(len(doc.get("text", "")) for doc in processed_documents)
    has_enough_content = total_content >= min_total_content

    documents_adequate_size = all(
        len(doc.get("text", "")) >= min_document_size for doc in processed_documents
    )

    ready = has_enough_documents and has_enough_content and documents_adequate_size

    validation_result = {
        "ready": ready,
        "has_enough_documents": has_enough_documents,
        "has_enough_content": has_enough_content,
        "documents_adequate_size": documents_adequate_size,
        "document_count": len(processed_documents),
        "total_content_chars": total_content,
    }

    activity.logger.info(
        f"Training readiness for {organization_name}: {'Ready' if ready else 'Not ready'}"
    )

    return validation_result
