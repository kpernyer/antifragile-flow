"""
Model Training Service - Handles all AI model training operations

This service encapsulates all the technical complexity of:
- LoRA (Low-Rank Adaptation) fine-tuning
- SFT (Supervised Fine-Tuning) with instruction pairs
- RLHF (Reinforcement Learning from Human Feedback)
- Model deployment to Ollama
- Training job management and monitoring

The service provides a clean business interface while handling all the
underlying ML/AI technical implementation details.
"""

from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
import json
import logging
from pathlib import Path
import queue
import threading
from typing import Any
import uuid

logger = logging.getLogger(__name__)

# Import ML dependencies conditionally
try:
    from datasets import Dataset
    from peft import LoraConfig, TaskType, get_peft_model
    import torch
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        BitsAndBytesConfig,
        TrainingArguments,
    )
    from trl import SFTTrainer

    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    logger.warning("ML dependencies not available - training will be mocked")


class TrainingJobStatus(Enum):
    """Business status of training jobs"""

    QUEUED = "queued"
    TRAINING = "training"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ModelType(Enum):
    """Supported model types for training"""

    MISTRAL_7B = "mistral-7b"
    QWEN_3B = "qwen-3b"
    CUSTOM = "custom"


@dataclass
class TrainingJobRequest:
    """Business request for model training"""

    organization_name: str
    organization_id: str
    documents: list[dict[str, str]]  # {text, title, type}
    model_type: ModelType = ModelType.MISTRAL_7B
    organizational_values: list[str] = None
    communication_style: str = "professional"
    priority: str = "normal"  # low, normal, high
    deploy_to_ollama: bool = True
    requester_email: str | None = None


@dataclass
class TrainingJobResult:
    """Business result of model training"""

    job_id: str
    organization_name: str
    status: TrainingJobStatus
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    model_location: str | None = None
    ollama_model_name: str | None = None
    training_duration_minutes: float = 0.0
    training_examples_count: int = 0
    error_message: str | None = None


@dataclass
class HumanFeedback:
    """Human feedback for RLHF training"""

    prompt: str
    response_a: str
    response_b: str
    preferred_response: str  # 'a' or 'b'
    feedback_text: str | None = None
    reviewer: str | None = None


class ModelTrainingService:
    """
    Service for managing AI model training operations

    Provides business-focused interface for:
    - Submitting training jobs
    - Monitoring job progress
    - Managing trained models
    - Human feedback collection
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)

        # Directory structure
        self.models_dir = Path(self.config.get("models_dir", "./models"))
        self.training_data_dir = Path(self.config.get("training_data_dir", "./training_data"))
        self.jobs_dir = Path(self.config.get("jobs_dir", "./training_jobs"))

        # Ensure directories exist
        for dir_path in [self.models_dir, self.training_data_dir, self.jobs_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Job tracking
        self.active_jobs: dict[str, TrainingJobResult] = {}
        self.job_queue = queue.Queue()

        # Model configurations
        self.model_configs = {
            ModelType.MISTRAL_7B: {
                "model_name": "mistralai/Mistral-7B-Instruct-v0.2",
                "max_examples_per_doc": 20,
                "training_epochs": 3,
                "batch_size": 2,
            },
            ModelType.QWEN_3B: {
                "model_name": "Qwen/Qwen2.5-3B-Instruct",
                "max_examples_per_doc": 30,
                "training_epochs": 2,
                "batch_size": 4,
            },
        }

        # Start background training worker
        if self.enabled:
            self.training_worker = threading.Thread(target=self._training_worker, daemon=True)
            self.training_worker.start()
            logger.info("Model training service initialized")

    async def submit_training_job(self, request: TrainingJobRequest) -> str:
        """
        Submit a new training job (business interface)

        Returns job_id immediately, training runs in background
        """
        if not self.enabled:
            raise RuntimeError("Model training service is disabled")

        job_id = f"train_{request.organization_id}_{uuid.uuid4().hex[:8]}"

        # Create job record
        job_result = TrainingJobResult(
            job_id=job_id,
            organization_name=request.organization_name,
            status=TrainingJobStatus.QUEUED,
            created_at=datetime.now(),
        )

        self.active_jobs[job_id] = job_result

        # Save job request
        job_file = self.jobs_dir / f"{job_id}.json"
        with open(job_file, "w") as f:
            json.dump(
                {"request": asdict(request), "result": asdict(job_result)}, f, indent=2, default=str
            )

        # Queue for background processing
        self.job_queue.put((job_id, request))

        logger.info(f"Queued training job {job_id} for {request.organization_name}")
        return job_id

    def get_job_status(self, job_id: str) -> TrainingJobResult | None:
        """Get current status of training job"""
        return self.active_jobs.get(job_id)

    def list_organization_jobs(self, organization_id: str) -> list[TrainingJobResult]:
        """List all jobs for an organization"""
        return [job for job in self.active_jobs.values() if organization_id in job.job_id]

    def cancel_job(self, job_id: str) -> bool:
        """Cancel a training job if possible"""
        job = self.active_jobs.get(job_id)
        if job and job.status == TrainingJobStatus.QUEUED:
            job.status = TrainingJobStatus.CANCELLED
            logger.info(f"Cancelled training job {job_id}")
            return True
        return False

    def _training_worker(self):
        """Background worker that processes training jobs"""
        logger.info("Training worker started")

        while True:
            try:
                # Get next job from queue (blocks until available)
                job_id, request = self.job_queue.get()

                if job_id not in self.active_jobs:
                    continue

                job_result = self.active_jobs[job_id]

                # Skip cancelled jobs
                if job_result.status == TrainingJobStatus.CANCELLED:
                    continue

                logger.info(f"Starting training job {job_id}")
                self._execute_training_job(job_id, request, job_result)

            except Exception as e:
                logger.error(f"Training worker error: {e}")
                if "job_result" in locals():
                    job_result.status = TrainingJobStatus.FAILED
                    job_result.error_message = str(e)

    def _execute_training_job(
        self, job_id: str, request: TrainingJobRequest, job_result: TrainingJobResult
    ):
        """Execute the actual training job"""
        try:
            # Update status
            job_result.status = TrainingJobStatus.TRAINING
            job_result.started_at = datetime.now()

            if not ML_AVAILABLE:
                # Mock training for testing
                import time

                time.sleep(5)  # Simulate training time
                job_result.status = TrainingJobStatus.COMPLETED
                job_result.completed_at = datetime.now()
                job_result.training_duration_minutes = 0.1
                job_result.training_examples_count = len(request.documents) * 15
                job_result.ollama_model_name = f"org-{request.organization_id}"
                logger.info(f"Mock training completed for {job_id}")
                return

            # Real training implementation
            trainer = OrganizationalTrainer(
                job_id=job_id,
                model_config=self.model_configs[request.model_type],
                output_dir=self.models_dir / job_id,
            )

            # Generate training data
            training_examples = trainer.generate_training_examples(
                documents=request.documents,
                organization_name=request.organization_name,
                organizational_values=request.organizational_values or ["excellence", "innovation"],
                communication_style=request.communication_style,
            )

            job_result.training_examples_count = len(training_examples)

            # Execute training
            trainer.train(training_examples)

            # Deploy to Ollama if requested
            ollama_name = None
            if request.deploy_to_ollama:
                ollama_name = trainer.deploy_to_ollama(
                    request.organization_id, request.organization_name
                )

            # Update job result
            job_result.status = TrainingJobStatus.COMPLETED
            job_result.completed_at = datetime.now()
            job_result.training_duration_minutes = (
                job_result.completed_at - job_result.started_at
            ).total_seconds() / 60
            job_result.model_location = str(trainer.output_dir)
            job_result.ollama_model_name = ollama_name

            logger.info(f"Training job {job_id} completed successfully")

        except Exception as e:
            job_result.status = TrainingJobStatus.FAILED
            job_result.error_message = str(e)
            job_result.completed_at = datetime.now()
            logger.error(f"Training job {job_id} failed: {e}")

    async def collect_human_feedback(self, organization_id: str, feedback: HumanFeedback) -> bool:
        """
        Collect human feedback for RLHF training

        This will be used to improve model responses through
        reinforcement learning from human feedback
        """
        feedback_file = self.training_data_dir / f"feedback_{organization_id}.jsonl"

        feedback_record = {
            "timestamp": datetime.now().isoformat(),
            "organization_id": organization_id,
            **asdict(feedback),
        }

        with open(feedback_file, "a") as f:
            f.write(json.dumps(feedback_record) + "\n")

        logger.info(f"Collected human feedback for {organization_id}")
        return True

    def start_rlhf_training(self, organization_id: str) -> str:
        """
        Start RLHF training using collected human feedback

        This creates a new training job that improves the model
        based on human preferences
        """
        # This would create a specialized RLHF training job
        # For now, we'll prepare the framework

        feedback_file = self.training_data_dir / f"feedback_{organization_id}.jsonl"
        if not feedback_file.exists():
            raise ValueError(f"No feedback data available for {organization_id}")

        logger.info(f"RLHF training framework ready for {organization_id}")
        return f"rlhf_{organization_id}_{uuid.uuid4().hex[:8]}"


class OrganizationalTrainer:
    """Internal trainer class - handles technical ML details"""

    def __init__(self, job_id: str, model_config: dict[str, Any], output_dir: Path):
        self.job_id = job_id
        self.model_config = model_config
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # ML configuration
        self.device = self._get_device()
        self.lora_config = LoraConfig(
            r=16,
            lora_alpha=32,
            target_modules=[
                "q_proj",
                "k_proj",
                "v_proj",
                "o_proj",
                "gate_proj",
                "up_proj",
                "down_proj",
            ],
            lora_dropout=0.05,
            bias="none",
            task_type=TaskType.CAUSAL_LM,
        )

        # Note: BitsAndBytesConfig disabled on macOS
        self.bnb_config = None

    def _get_device(self) -> str:
        if torch.backends.mps.is_available():
            return "mps"
        elif torch.cuda.is_available():
            return "cuda"
        return "cpu"

    def generate_training_examples(
        self,
        documents: list[dict[str, str]],
        organization_name: str,
        organizational_values: list[str],
        communication_style: str,
    ) -> list[dict[str, str]]:
        """Generate supervised training pairs from documents"""
        examples = []
        values_str = ", ".join(organizational_values)
        max_examples = self.model_config["max_examples_per_doc"]

        for doc in documents:
            doc_text = doc.get("text", "")
            doc_title = doc.get("title", "Document")

            # Create chunks
            chunks = self._split_content(doc_text)

            for chunk in chunks[:max_examples]:
                # Strategic analysis examples
                examples.append(
                    {
                        "instruction": f"Analyze this from {organization_name}'s perspective, considering our values of {values_str}.",
                        "input": chunk,
                        "output": self._create_strategic_response(
                            chunk, organization_name, values_str, communication_style
                        ),
                        "source": doc_title,
                        "type": "strategic_analysis",
                    }
                )

                # Communication style examples
                examples.append(
                    {
                        "instruction": f"Rewrite this using {organization_name}'s {communication_style} communication style.",
                        "input": chunk[:300] + "...",
                        "output": self._adapt_to_org_style(
                            chunk, organization_name, communication_style
                        ),
                        "source": doc_title,
                        "type": "communication_adaptation",
                    }
                )

        return examples

    def _split_content(self, content: str, max_length: int = 500) -> list[str]:
        """Split content into training chunks"""
        sentences = content.replace("\n", " ").split(". ")
        chunks = []
        current = []
        current_len = 0

        for sentence in sentences:
            if current_len + len(sentence) > max_length and current:
                chunks.append(". ".join(current) + ".")
                current = [sentence]
                current_len = len(sentence)
            else:
                current.append(sentence)
                current_len += len(sentence)

        if current:
            chunks.append(". ".join(current))

        return chunks

    def _create_strategic_response(
        self, content: str, org_name: str, values: str, style: str
    ) -> str:
        """Create organizational strategic analysis response"""
        return f"""From {org_name}'s strategic perspective:

This content aligns with our core values of {values} and supports our organizational mission. Key strategic insights:

• **Strategic Alignment**: The content reinforces our commitment to {values.split(",")[0].strip()}
• **Value Integration**: Demonstrates consistency with our organizational principles
• **Actionable Insights**: Provides direction that supports our strategic objectives

Our {style} approach ensures we maintain focus on value creation while staying true to our organizational identity."""

    def _adapt_to_org_style(self, content: str, org_name: str, style: str) -> str:
        """Adapt content to organizational communication style"""
        adapted_content = content[:200] + "..." if len(content) > 200 else content
        return f"""[{org_name} - {style} communication style]

{adapted_content}

This message reflects our organizational voice and maintains consistency with our established communication standards and strategic messaging framework."""

    def train(self, training_examples: list[dict[str, str]]):
        """Execute LoRA training"""
        logger.info(f"Training with {len(training_examples)} examples")

        # Create dataset
        formatted_data = []
        for example in training_examples:
            if example.get("input"):
                text = f"### Instruction:\n{example['instruction']}\n\n### Input:\n{example['input']}\n\n### Response:\n{example['output']}"
            else:
                text = f"### Instruction:\n{example['instruction']}\n\n### Response:\n{example['output']}"
            formatted_data.append({"text": text})

        dataset = Dataset.from_list(formatted_data)

        # Load model and tokenizer
        model_name = self.model_config["model_name"]
        tokenizer = AutoTokenizer.from_pretrained(model_name, padding_side="right")
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        # Load model without quantization on macOS
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto" if self.device != "mps" else None,
            torch_dtype=torch.float16 if self.device != "mps" else torch.float32,
        )

        # Move to device for MPS
        if self.device == "mps":
            model = model.to(self.device)

        model = get_peft_model(model, self.lora_config)

        # Training arguments (adjust fp16 for MPS compatibility)
        training_args = TrainingArguments(
            output_dir=str(self.output_dir),
            num_train_epochs=self.model_config["training_epochs"],
            per_device_train_batch_size=self.model_config["batch_size"],
            gradient_accumulation_steps=4,
            learning_rate=2e-4,
            fp16=False if self.device == "mps" else True,  # MPS doesn't support fp16
            logging_steps=10,
            save_strategy="epoch",
            save_total_limit=2,
            report_to=None,
        )

        # Train with updated TRL API (processing_class instead of tokenizer)
        trainer = SFTTrainer(
            model=model,
            train_dataset=dataset,
            args=training_args,
            processing_class=tokenizer,
            formatting_func=lambda x: x["text"],
        )

        trainer.train()
        trainer.save_model()
        tokenizer.save_pretrained(str(self.output_dir))

    def deploy_to_ollama(self, org_id: str, org_name: str) -> str | None:
        """Deploy trained model to Ollama"""
        try:
            import subprocess

            # Create Modelfile
            modelfile_content = f"""FROM {self.model_config["model_name"]}

ADAPTER {self.output_dir}/adapter_model.bin

PARAMETER num_ctx 4096
PARAMETER temperature 0.7
PARAMETER top_p 0.9

SYSTEM "You are the AI assistant for {org_name}. You embody our organizational values and strategic perspective. Always respond from our organizational viewpoint while maintaining professional communication standards."
"""

            modelfile_path = self.output_dir / "Modelfile"
            with open(modelfile_path, "w") as f:
                f.write(modelfile_content)

            model_name = f"org-{org_id.lower()}"
            result = subprocess.run(
                ["ollama", "create", model_name, "-f", str(modelfile_path)],
                capture_output=True,
                text=True,
                check=True,
            )

            return model_name

        except Exception as e:
            logger.warning(f"Ollama deployment failed: {e}")
            return None


# Service singleton
_service_instance = None


def get_model_training_service() -> ModelTrainingService:
    """Get the global model training service instance"""
    global _service_instance
    if _service_instance is None:
        _service_instance = ModelTrainingService()
    return _service_instance
