"""
Organization Onboarding Workflow - Main business process.

This is the primary business workflow that coordinates the complete
onboarding process for new organizations. It orchestrates multiple
sub-workflows to handle different aspects of onboarding.

Business Process:
1. Document Processing - Handle uploaded company documents
2. Interactive Research - Conduct guided research sessions
3. Competitor Monitoring - Set up ongoing competitive intelligence
4. Admin Notifications - Keep admins informed of progress
"""

from dataclasses import dataclass
from datetime import datetime, timedelta

from temporalio import workflow

from activity.scheduler_activities import (
    send_scheduled_notification,
)

# Model training now handled by DocumentProcessing workflow and service layer
from workflow.document_processing_workflow import (
    DocumentProcessingRequest,
    DocumentProcessingResult,
    DocumentProcessingWorkflow,
)

# TODO: Fix import after resolving openai_agents module issue
# from workflow.interactive_research_workflow import (
#     InteractiveResearchWorkflow,
#     InteractiveResearchResult,
# )
from workflow.scheduler_workflow import (
    CompetitorMonitoringWorkflow,
    WeeklyCompetitorReportRequest,
    WeeklyCompetitorReportResult,
)


@dataclass
class OnboardingRequest:
    """Request for organization onboarding"""

    organization_name: str
    documents: list[str]  # File paths to uploaded documents
    research_queries: list[str]  # Initial research questions
    competitors: list[str] = None  # Known competitors
    admin_emails: list[str] = None  # Admin notification recipients
    priority: str = "normal"  # low, normal, high

    # LoRA Model Training Options
    enable_model_training: bool = True  # Enable organizational model fine-tuning
    base_model: str = "mistralai/Mistral-7B-Instruct-v0.2"  # Base model for training
    # Alternative: "Qwen/Qwen2.5-3B-Instruct" for smaller/faster training
    organizational_values: list[str] = None  # Core organizational values
    communication_style: str = "professional and strategic"  # Communication preferences
    deploy_to_ollama: bool = True  # Deploy trained model to Ollama


@dataclass
class OnboardingProgress:
    """Progress tracking for onboarding process"""

    stage: str  # document_processing, model_training, research, competitor_setup, completed
    documents_processed: int = 0
    total_documents: int = 0
    model_training_completed: bool = False
    model_training_duration_minutes: float = 0.0
    ollama_model_name: str = None
    research_completed: bool = False
    competitor_monitoring_setup: bool = False
    admin_notifications_sent: int = 0


@dataclass
class OnboardingResult:
    """Result from complete organization onboarding"""

    organization_name: str
    onboarding_id: str
    start_time: datetime
    end_time: datetime
    success: bool

    # Sub-process results
    document_results: DocumentProcessingResult | None = None
    training_job_id: str = ""  # ID of background training job
    research_results: dict | None = None  # TODO: Change back to InteractiveResearchResult
    competitor_monitoring: WeeklyCompetitorReportResult | None = None

    # Summary information
    progress: OnboardingProgress = None
    admin_summary: str = ""
    next_steps: list[str] = None


@workflow.defn
class OrganizationOnboardingWorkflow:
    """
    Main business workflow for onboarding new organizations.

    This workflow coordinates multiple sub-processes:
    - Document processing for uploaded company materials
    - Interactive research for market intelligence
    - Competitor monitoring setup for ongoing surveillance
    - Admin notifications throughout the process

    Usage:
        result = await client.execute_workflow(
            OrganizationOnboardingWorkflow.run,
            OnboardingRequest(
                organization_name="Acme Corp",
                documents=["path/to/doc1.pdf", "path/to/doc2.pdf"],
                research_queries=["What is Acme Corp's market position?"],
                competitors=["Competitor A", "Competitor B"]
            ),
            id="onboarding-acme-corp",
            task_queue=shared.TASK_QUEUE_NAME,
        )
    """

    def __init__(self) -> None:
        self._progress = OnboardingProgress(stage="initializing")

    @workflow.run
    async def run(self, request: OnboardingRequest) -> OnboardingResult:
        """
        Execute complete organization onboarding process.

        Args:
            request: Onboarding request with org details and materials

        Returns:
            Complete onboarding result with all sub-process outcomes
        """

        start_time = datetime.now()
        onboarding_id = f"onboarding-{request.organization_name.lower().replace(' ', '-')}-{start_time.strftime('%Y%m%d-%H%M%S')}"

        workflow.logger.info(
            f"Starting onboarding for {request.organization_name} (ID: {onboarding_id})"
        )

        # Initialize progress tracking
        self._progress = OnboardingProgress(
            stage="document_processing", total_documents=len(request.documents)
        )

        try:
            # === PHASE 1: DOCUMENT PROCESSING ===
            workflow.logger.info("Phase 1: Document Processing")
            self._progress.stage = "document_processing"

            doc_processing_request = DocumentProcessingRequest(
                file_paths=request.documents,
                priority=request.priority,
                admin_notification=True,
                deep_analysis=True,
                # Organizational learning parameters
                organization_name=request.organization_name,
                organization_id=request.organization_name.lower().replace(" ", "-"),
                enable_model_training=request.enable_model_training,
                model_preference="balanced",  # Map from base_model if needed
                organizational_values=request.organizational_values,
                communication_style=request.communication_style,
            )

            # Execute document processing as child workflow
            document_results = await workflow.execute_child_workflow(
                DocumentProcessingWorkflow.run,
                doc_processing_request,
                id=f"{onboarding_id}-documents",
                task_timeout=timedelta(hours=1),
            )

            self._progress.documents_processed = document_results.successful_documents
            workflow.logger.info(
                f"Document processing completed: {document_results.successful_documents}/{document_results.total_documents} successful"
            )

            # Send admin notification about document processing
            if request.admin_emails and document_results.admin_summaries:
                await self._notify_admins(
                    request.admin_emails,
                    f"Document Processing Complete - {request.organization_name}",
                    self._create_document_summary(request.organization_name, document_results),
                )

            # === PHASE 2: ORGANIZATIONAL AI TRAINING STATUS ===
            workflow.logger.info("Phase 2: Checking Organizational AI Training")
            self._progress.stage = "ai_training_status"

            # Model training is handled by DocumentProcessing workflow (non-blocking)
            if document_results.training_initiated:
                self._progress.model_training_completed = False  # Training in progress
                self._progress.ollama_model_name = None  # Will be available later
                workflow.logger.info(
                    f"Organizational AI training initiated: {document_results.training_job_id}"
                )

                # Send notification about training initiation
                if request.admin_emails and document_results.training_job_id:
                    await self._notify_admins(
                        request.admin_emails,
                        f"Organizational AI Training Started - {request.organization_name}",
                        f"Your custom AI model training has been initiated (Job ID: {document_results.training_job_id}). "
                        f"This process will run in the background and you'll be notified when complete. "
                        f"The model will be available for testing once training finishes.",
                    )
            else:
                workflow.logger.info("No organizational AI training initiated")

            # === PHASE 3: INTERACTIVE RESEARCH ===
            workflow.logger.info("Phase 3: Interactive Research")
            self._progress.stage = "research"

            # TODO: Re-enable after fixing research workflow imports
            research_results = None
            if request.research_queries:
                workflow.logger.info("Research workflows temporarily disabled due to import issues")
                # Note: This would typically execute InteractiveResearchWorkflow
                # For now, we'll skip research and continue with onboarding
                research_results = {
                    "status": "skipped",
                    "reason": "Research workflows temporarily disabled",
                    "queries": request.research_queries,
                }
                self._progress.research_completed = False

            # === PHASE 4: COMPETITOR MONITORING SETUP ===
            workflow.logger.info("Phase 4: Competitor Monitoring Setup")
            self._progress.stage = "competitor_setup"

            competitor_monitoring = None
            if request.competitors:
                competitor_request = WeeklyCompetitorReportRequest(
                    competitors=request.competitors,
                    recipients=request.admin_emails or ["admin@company.com"],
                    scan_types=["news"],
                    notification_enabled=True,
                )

                try:
                    # Run initial competitor scan
                    competitor_monitoring = await workflow.execute_child_workflow(
                        CompetitorMonitoringWorkflow.run,
                        competitor_request,
                        id=f"{onboarding_id}-competitors",
                        task_timeout=timedelta(minutes=30),
                    )
                    self._progress.competitor_monitoring_setup = True
                    workflow.logger.info("Competitor monitoring setup completed")
                except Exception as e:
                    workflow.logger.warning(f"Competitor monitoring setup failed: {e}")

            # === PHASE 5: COMPLETION ===
            self._progress.stage = "completed"
            end_time = datetime.now()

            # Send final admin notification
            final_summary = self._create_final_summary(
                request, document_results, research_results, competitor_monitoring
            )

            if request.admin_emails:
                await self._notify_admins(
                    request.admin_emails,
                    f"Onboarding Complete - {request.organization_name}",
                    final_summary,
                )

            # Create final result
            result = OnboardingResult(
                organization_name=request.organization_name,
                onboarding_id=onboarding_id,
                start_time=start_time,
                end_time=end_time,
                success=True,
                document_results=document_results,
                training_job_id=document_results.training_job_id if document_results else "",
                research_results=research_results,
                competitor_monitoring=competitor_monitoring,
                progress=self._progress,
                admin_summary=final_summary,
                next_steps=self._generate_next_steps(document_results, research_results),
            )

            workflow.logger.info(
                f"Onboarding completed successfully for {request.organization_name}"
            )
            return result

        except Exception as e:
            workflow.logger.error(f"Onboarding failed for {request.organization_name}: {e}")

            # Send error notification
            if request.admin_emails:
                await self._notify_admins(
                    request.admin_emails,
                    f"Onboarding Failed - {request.organization_name}",
                    f"Onboarding process failed: {e!s}",
                )

            return OnboardingResult(
                organization_name=request.organization_name,
                onboarding_id=onboarding_id,
                start_time=start_time,
                end_time=datetime.now(),
                success=False,
                progress=self._progress,
                admin_summary=f"Onboarding failed: {e!s}",
            )

    async def _notify_admins(self, recipients: list[str], subject: str, message: str) -> None:
        """Send notification to admin users"""
        for recipient in recipients:
            try:
                await workflow.execute_activity(
                    send_scheduled_notification,
                    recipient,
                    subject,
                    message,
                    "email",
                    start_to_close_timeout=timedelta(minutes=2),
                )
                self._progress.admin_notifications_sent += 1
            except Exception as e:
                workflow.logger.warning(f"Failed to notify {recipient}: {e}")

    def _create_document_summary(self, org_name: str, doc_results: DocumentProcessingResult) -> str:
        """Create summary of document processing results"""
        summary = f"# Document Processing Summary - {org_name}\n\n"
        summary += f"**Processed:** {doc_results.successful_documents}/{doc_results.total_documents} documents\n\n"

        if doc_results.admin_summaries:
            summary += "## Key Documents:\n"
            for i, doc_summary in enumerate(doc_results.admin_summaries[:5], 1):  # Limit to 5
                summary += f"{i}. **{doc_summary.file_name}**\n"
                summary += f"   - {doc_summary.short_summary}\n"
                summary += f"   - Confidence: {doc_summary.confidence_score:.2f}\n\n"

        return summary

    # Model training summary now handled by service layer notifications

    def _create_final_summary(
        self, request: OnboardingRequest, doc_results, research_results, competitor_results
    ) -> str:
        """Create final onboarding summary"""
        summary = f"# Onboarding Complete - {request.organization_name}\n\n"

        summary += "## Process Summary\n"
        summary += (
            f"- **Documents:** {doc_results.successful_documents if doc_results else 0} processed\n"
        )
        summary += f"- **AI Model Training:** {'✅ Initiated' if doc_results and doc_results.training_initiated else '❌ Not Started'}\n"
        summary += f"- **Research:** {'✅ Completed' if research_results else '❌ Skipped'}\n"
        summary += f"- **Competitors:** {'✅ Monitoring setup' if competitor_results else '❌ Not configured'}\n\n"

        # Add model training info if initiated
        if doc_results and doc_results.training_initiated:
            summary += "## Organizational AI Training\n"
            summary += "- **Status:** Training in progress (background process)\n"
            summary += f"- **Job ID:** {doc_results.training_job_id}\n"
            summary += (
                "- **Progress:** Model will be available for testing once training completes\n"
            )
            summary += "\n"

        if doc_results and doc_results.admin_summaries:
            summary += "## Document Insights\n"
            for doc in doc_results.admin_summaries[:3]:  # Top 3 documents
                summary += f"- **{doc.file_name}:** {doc.short_summary}\n"

        return summary

    def _generate_next_steps(self, doc_results, research_results) -> list[str]:
        """Generate recommended next steps"""
        steps = []

        if doc_results and doc_results.successful_documents > 0:
            steps.append("Review document analysis results in admin dashboard")

        # AI training next steps
        if doc_results and doc_results.training_initiated:
            steps.append(
                f"Monitor organizational AI training progress (Job ID: {doc_results.training_job_id})"
            )
            steps.append("You'll be notified when your custom AI model is ready for testing")
            steps.append("Prepare feedback collection process for model improvement")
        elif request.enable_model_training:
            steps.append("Consider uploading additional organizational documents for AI training")

        if research_results:
            steps.append("Follow up on research findings and recommendations")
        else:
            steps.append("Schedule interactive research session")

        steps.append("Set up regular competitor monitoring alerts")
        steps.append("Schedule onboarding review meeting")

        return steps

    @workflow.query
    def get_progress(self) -> OnboardingProgress:
        """Query current onboarding progress"""
        return self._progress

    @workflow.query
    def get_status(self) -> dict:
        """Query detailed onboarding status"""
        return {
            "stage": self._progress.stage,
            "documents_processed": self._progress.documents_processed,
            "total_documents": self._progress.total_documents,
            "model_training_initiated": self._progress.model_training_completed,  # Reusing field for initiated status
            "training_job_id": getattr(self._progress, "training_job_id", ""),
            "ollama_model_name": self._progress.ollama_model_name,
            "research_completed": self._progress.research_completed,
            "competitor_monitoring_setup": self._progress.competitor_monitoring_setup,
            "admin_notifications_sent": self._progress.admin_notifications_sent,
            "workflow_id": workflow.info().workflow_id,
        }
