"""
Model Training Activities for LoRA Fine-tuning

These activities handle local model fine-tuning using LoRA (Low-Rank Adaptation)
for organizational DNA models. Supports multiple base models including:
- Mistral-7B-Instruct-v0.2
- Qwen-3B variants
- Other compatible models

The activities convert uploaded documents into training data and fine-tune
local models that capture organizational communication patterns and values.
"""

from dataclasses import dataclass
from datetime import datetime
import json
import logging
from pathlib import Path
import subprocess
from typing import Any

from temporalio import activity

# Import fine-tuning dependencies conditionally
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

    FINE_TUNING_AVAILABLE = True
except ImportError:
    FINE_TUNING_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class TrainingExample:
    """Training example for fine-tuning"""

    instruction: str
    input: str
    output: str
    source_document: str


@dataclass
class ModelTrainingRequest:
    """Request for LoRA model training"""

    organization_name: str
    organization_id: str
    documents: list[dict[str, str]]  # List of {text, title, type} documents
    base_model: str = "mistralai/Mistral-7B-Instruct-v0.2"  # Default to Mistral-7B
    # Alternative: "Qwen/Qwen2.5-3B-Instruct" for smaller model
    training_examples: int = 50  # Number of training examples to generate per document
    epochs: int = 3
    learning_rate: float = 2e-4
    batch_size: int = 2
    deploy_to_ollama: bool = True
    organizational_values: list[str] = None
    communication_style: str = "professional and strategic"


@dataclass
class ModelTrainingResult:
    """Result from LoRA model training"""

    success: bool
    organization_name: str
    training_job_id: str
    model_path: str
    ollama_model_name: str | None = None
    training_examples_generated: int = 0
    training_duration_minutes: float = 0.0
    error_message: str | None = None
    model_metadata: dict[str, Any] | None = None


class OrganizationalLoRATrainer:
    """LoRA trainer for organizational models"""

    def __init__(self, base_model: str, training_job_id: str, output_dir: str):
        self.base_model = base_model
        self.training_job_id = training_job_id
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Detect best available device
        if torch.backends.mps.is_available():
            self.device = "mps"
        elif torch.cuda.is_available():
            self.device = "cuda"
        else:
            self.device = "cpu"

        logger.info(f"Using device: {self.device}")

        # LoRA configuration optimized for organizational training
        self.lora_config = LoraConfig(
            r=16,  # Rank - balance between performance and efficiency
            lora_alpha=32,  # Scaling parameter
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

        # Quantization for memory efficiency
        self.bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
        )

    def generate_training_examples(
        self,
        documents: list[dict[str, str]],
        organization_name: str,
        organizational_values: list[str],
        communication_style: str,
        examples_per_doc: int = 50,
    ) -> list[TrainingExample]:
        """Generate training examples from organizational documents"""
        examples = []
        values_str = (
            ", ".join(organizational_values)
            if organizational_values
            else "excellence, innovation, integrity"
        )

        for doc in documents:
            doc_text = doc.get("text", "")
            doc_title = doc.get("title", "Document")

            # Split document into chunks
            chunks = self._split_text(doc_text, max_length=800)

            for _i, chunk in enumerate(chunks[:examples_per_doc]):
                # 1. Strategic Analysis Examples
                examples.append(
                    TrainingExample(
                        instruction=f"Analyze this content from {organization_name}'s strategic perspective and provide insights aligned with our organizational values.",
                        input=f"Content to analyze: {chunk}",
                        output=self._generate_strategic_analysis(
                            chunk, organization_name, values_str, communication_style
                        ),
                        source_document=doc_title,
                    )
                )

                # 2. Value Alignment Examples
                examples.append(
                    TrainingExample(
                        instruction=f"How does this content align with {organization_name}'s core values and strategic priorities?",
                        input=f"Content: {chunk[:300]}...",
                        output=self._generate_value_alignment(chunk, organization_name, values_str),
                        source_document=doc_title,
                    )
                )

                # 3. Communication Style Examples
                examples.append(
                    TrainingExample(
                        instruction=f"Rewrite this content using {organization_name}'s preferred communication style and organizational voice.",
                        input=f"Original content: {chunk[:400]}...",
                        output=self._adapt_communication_style(
                            chunk, organization_name, communication_style
                        ),
                        source_document=doc_title,
                    )
                )

                # 4. Q&A Examples based on document content
                if len(chunk) > 200:
                    question = self._generate_question_from_content(chunk)
                    examples.append(
                        TrainingExample(
                            instruction=question,
                            input="",
                            output=self._generate_organizational_answer(
                                chunk, organization_name, question, values_str
                            ),
                            source_document=doc_title,
                        )
                    )

        logger.info(f"Generated {len(examples)} training examples from {len(documents)} documents")
        return examples

    def _split_text(self, text: str, max_length: int = 800) -> list[str]:
        """Split text into manageable chunks"""
        sentences = text.split(". ")
        chunks = []
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            sentence_length = len(sentence)
            if current_length + sentence_length > max_length and current_chunk:
                chunks.append(". ".join(current_chunk) + ".")
                current_chunk = [sentence]
                current_length = sentence_length
            else:
                current_chunk.append(sentence)
                current_length += sentence_length + 2  # +2 for '. '

        if current_chunk:
            chunks.append(". ".join(current_chunk))

        return chunks

    def _generate_strategic_analysis(
        self, _content: str, org_name: str, values: str, _style: str
    ) -> str:
        """Generate strategic analysis response"""
        return f"""From {org_name}'s strategic perspective, this content presents several key opportunities and considerations:

**Strategic Alignment:** This aligns well with our core values of {values} and supports our organizational mission. The content suggests potential for leveraging our existing capabilities while maintaining focus on strategic priorities.

**Key Insights:**
- Demonstrates alignment with our organizational principles
- Presents opportunities for value creation consistent with our strategic direction
- Supports our commitment to {values.split(",")[0].strip()} and operational excellence

**Organizational Implications:** This content reinforces our strategic positioning and provides actionable insights that can inform decision-making across our key business areas while maintaining consistency with our established values and communication style."""

    def _generate_value_alignment(self, _content: str, org_name: str, values: str) -> str:
        """Generate value alignment explanation"""
        return f"""This content strongly aligns with {org_name}'s core organizational values:

**Primary Alignments:**
- **{values.split(",")[0].strip().title()}:** The content demonstrates our commitment to this foundational value
- **{values.split(",")[1].strip().title() if "," in values else "Innovation"}:** Reflects our strategic approach to continuous improvement
- **{values.split(",")[2].strip().title() if values.count(",") >= 2 else "Integrity"}:** Maintains consistency with our ethical standards

**Strategic Value:** This alignment ensures that our organizational actions remain consistent with our stated principles while supporting our long-term strategic objectives. It reinforces our cultural identity and strengthens our market positioning through authentic value-driven decision making."""

    def _adapt_communication_style(self, content: str, org_name: str, style: str) -> str:
        """Adapt content to organizational communication style"""
        adapted = f"[{org_name} Communication Style: {style}]\n\n"

        # Extract key points and adapt them
        key_points = content.split(". ")[:3]  # Take first 3 sentences

        adapted += "**Key Message:** " + ". ".join(key_points) + "\n\n"
        adapted += f"**{org_name} Perspective:** This content has been adapted to reflect our organizational voice and communication standards. "
        adapted += f"We maintain our commitment to {style} communication while ensuring consistency with our strategic messaging and brand identity."

        return adapted

    def _generate_question_from_content(self, content: str) -> str:
        """Generate relevant question from content"""
        if "strategy" in content.lower():
            return "What are the strategic implications of this information for our organization?"
        elif "market" in content.lower():
            return "How does this market information affect our strategic positioning?"
        elif "customer" in content.lower():
            return "What does this tell us about our customer relationships and value proposition?"
        elif "innovation" in content.lower():
            return "How can we leverage this innovation opportunity within our organizational framework?"
        else:
            return "How should our organization interpret and respond to this information?"

    def _generate_organizational_answer(
        self, content: str, org_name: str, _question: str, values: str
    ) -> str:
        """Generate organizational-specific answer"""
        return f"""Based on {org_name}'s strategic framework and commitment to {values}, here's our organizational perspective:

**Analysis:** {content[:200]}...

**Our Response:** As an organization committed to {values.split(",")[0].strip()}, we interpret this information through the lens of our strategic priorities and values-based decision making. This content supports our understanding of the market landscape and reinforces our positioning strategy.

**Next Steps:** We should evaluate this information against our strategic roadmap and consider how it informs our operational planning and stakeholder engagement strategies."""

    def prepare_training_data(self, examples: list[TrainingExample]) -> Dataset:
        """Convert training examples to HuggingFace Dataset"""
        # Convert to instruction-tuning format
        formatted_data = []
        for example in examples:
            if example.input:
                text = f"### Instruction:\n{example.instruction}\n\n### Input:\n{example.input}\n\n### Response:\n{example.output}"
            else:
                text = f"### Instruction:\n{example.instruction}\n\n### Response:\n{example.output}"

            formatted_data.append({"text": text})

        # Create dataset
        dataset = Dataset.from_list(formatted_data)
        logger.info(f"Prepared dataset with {len(dataset)} examples")
        return dataset

    def initialize_model_and_tokenizer(self):
        """Initialize model and tokenizer with LoRA"""
        logger.info(f"Loading base model: {self.base_model}")

        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            self.base_model,
            trust_remote_code=True,
            padding_side="right",
            add_eos_token=True,
        )

        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        # Load model with quantization
        model = AutoModelForCausalLM.from_pretrained(
            self.base_model,
            quantization_config=self.bnb_config,
            device_map="auto",
            trust_remote_code=True,
            torch_dtype=torch.float16,
        )

        # Apply LoRA
        model = get_peft_model(model, self.lora_config)
        model.print_trainable_parameters()

        return model, tokenizer

    def train(
        self,
        training_data: Dataset,
        model,
        tokenizer,
        epochs: int = 3,
        batch_size: int = 2,
        learning_rate: float = 2e-4,
    ):
        """Execute LoRA training"""
        logger.info(f"Starting LoRA training with {len(training_data)} examples")

        training_args = TrainingArguments(
            output_dir=str(self.output_dir),
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            gradient_accumulation_steps=4,
            warmup_steps=50,
            learning_rate=learning_rate,
            fp16=True,
            logging_steps=10,
            save_strategy="epoch",
            evaluation_strategy="no",
            save_total_limit=2,
            load_best_model_at_end=False,
            report_to=None,  # Disable wandb/tensorboard
            remove_unused_columns=False,
        )

        trainer = SFTTrainer(
            model=model,
            train_dataset=training_data,
            tokenizer=tokenizer,
            args=training_args,
            dataset_text_field="text",
            max_seq_length=2048,
        )

        # Train
        trainer.train()

        # Save model and tokenizer
        trainer.save_model()
        tokenizer.save_pretrained(str(self.output_dir))

        logger.info(f"Training completed. Model saved to {self.output_dir}")

    def create_ollama_modelfile(self, organization_name: str) -> str:
        """Create Ollama Modelfile for deployment"""
        modelfile_content = f'''FROM {self.base_model}

# Load LoRA adapter
ADAPTER {self.output_dir}/adapter_model.bin

# Optimized parameters for organizational AI
PARAMETER num_ctx 4096
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER repeat_penalty 1.1

# Organizational system prompt
SYSTEM """You are the AI assistant for {organization_name}. You embody our organizational values, strategic vision, and communication style.

Core Responsibilities:
1. Provide insights aligned with our organizational identity and values
2. Communicate using our established tone and style
3. Consider our strategic context in all recommendations
4. Maintain consistency with our documented principles

Always respond from {organization_name}'s perspective, reflecting our unique organizational culture and strategic priorities."""
'''

        modelfile_path = self.output_dir / "Modelfile"
        with modelfile_path.open("w") as f:
            f.write(modelfile_content)

        return str(modelfile_path)

    def deploy_to_ollama(self, organization_id: str, organization_name: str) -> str | None:
        """Deploy trained model to Ollama"""
        logger.info(f"Deploying model to Ollama for {organization_name}")

        # Create Modelfile
        modelfile_path = self.create_ollama_modelfile(organization_name)

        # Generate model name
        model_name = f"org-{organization_id.lower().replace(' ', '-')}"

        try:
            # Create model in Ollama
            subprocess.run(
                ["ollama", "create", model_name, "-f", modelfile_path],
                capture_output=True,
                text=True,
                check=True,
            )

            logger.info(f"Successfully deployed model '{model_name}' to Ollama")
            return model_name

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to deploy to Ollama: {e}")
            logger.error(f"Error output: {e.stderr}")
            return None
        except FileNotFoundError:
            logger.error("Ollama not found. Please install Ollama first.")
            return None


@activity.defn
async def train_organizational_model(request: ModelTrainingRequest) -> ModelTrainingResult:
    """
    Activity to train organizational LoRA model from documents

    This activity:
    1. Generates training examples from uploaded documents
    2. Fine-tunes a local model using LoRA for memory efficiency
    3. Optionally deploys to Ollama for easy inference
    4. Supports both Mistral-7B and Qwen-3B base models
    """
    activity.logger.info(f"Starting model training for {request.organization_name}")
    start_time = datetime.now()

    if not FINE_TUNING_AVAILABLE:
        return ModelTrainingResult(
            success=False,
            organization_name=request.organization_name,
            training_job_id="",
            model_path="",
            error_message="Fine-tuning dependencies not available. Please install torch, transformers, peft, and trl.",
        )

    # Generate unique training job ID
    training_job_id = f"train-{request.organization_id}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    # Create output directory
    output_dir = Path(f"experiments/fine-tuning/models/{training_job_id}")
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Initialize trainer
        trainer = OrganizationalLoRATrainer(
            base_model=request.base_model,
            training_job_id=training_job_id,
            output_dir=str(output_dir),
        )

        # Generate training examples from documents
        activity.logger.info("Generating training examples from documents")
        training_examples = trainer.generate_training_examples(
            documents=request.documents,
            organization_name=request.organization_name,
            organizational_values=request.organizational_values
            or ["excellence", "innovation", "integrity"],
            communication_style=request.communication_style,
            examples_per_doc=request.training_examples,
        )

        if not training_examples:
            raise ValueError("No training examples generated from documents")

        # Save training examples as JSONL
        training_data_path = output_dir / "training_data.jsonl"
        with training_data_path.open("w") as f:
            for example in training_examples:
                data = {
                    "instruction": example.instruction,
                    "input": example.input,
                    "output": example.output,
                    "source_document": example.source_document,
                }
                f.write(json.dumps(data) + "\n")

        # Prepare training dataset
        training_data = trainer.prepare_training_data(training_examples)

        # Initialize model and tokenizer
        activity.logger.info(f"Initializing {request.base_model} with LoRA")
        model, tokenizer = trainer.initialize_model_and_tokenizer()

        # Train the model
        activity.logger.info("Starting LoRA fine-tuning")
        trainer.train(
            training_data=training_data,
            model=model,
            tokenizer=tokenizer,
            epochs=request.epochs,
            batch_size=request.batch_size,
            learning_rate=request.learning_rate,
        )

        # Deploy to Ollama if requested
        ollama_model_name = None
        if request.deploy_to_ollama:
            activity.logger.info("Deploying to Ollama")
            ollama_model_name = trainer.deploy_to_ollama(
                request.organization_id, request.organization_name
            )

        # Calculate training duration
        end_time = datetime.now()
        duration_minutes = (end_time - start_time).total_seconds() / 60

        # Save training metadata
        metadata = {
            "training_job_id": training_job_id,
            "organization_name": request.organization_name,
            "organization_id": request.organization_id,
            "base_model": request.base_model,
            "training_examples": len(training_examples),
            "documents_processed": len(request.documents),
            "training_duration_minutes": duration_minutes,
            "ollama_model_name": ollama_model_name,
            "training_config": {
                "epochs": request.epochs,
                "batch_size": request.batch_size,
                "learning_rate": request.learning_rate,
            },
            "completed_at": end_time.isoformat(),
        }

        metadata_path = output_dir / "training_metadata.json"
        with metadata_path.open("w") as f:
            json.dump(metadata, f, indent=2)

        activity.logger.info(
            f"Model training completed successfully for {request.organization_name}"
        )

        return ModelTrainingResult(
            success=True,
            organization_name=request.organization_name,
            training_job_id=training_job_id,
            model_path=str(output_dir),
            ollama_model_name=ollama_model_name,
            training_examples_generated=len(training_examples),
            training_duration_minutes=duration_minutes,
            model_metadata=metadata,
        )

    except Exception as e:
        activity.logger.error(f"Model training failed for {request.organization_name}: {e}")

        return ModelTrainingResult(
            success=False,
            organization_name=request.organization_name,
            training_job_id=training_job_id,
            model_path=str(output_dir) if "output_dir" in locals() else "",
            error_message=str(e),
            training_duration_minutes=(datetime.now() - start_time).total_seconds() / 60,
        )


@activity.defn
async def test_qwen_model(
    organization_name: str, test_prompt: str = "What are our organizational values?"
) -> dict[str, Any]:
    """
    Activity to test Qwen-3B model specifically

    Tests the smaller Qwen model for comparison with Mistral-7B
    """
    activity.logger.info(f"Testing Qwen-3B model for {organization_name}")

    if not FINE_TUNING_AVAILABLE:
        return {"success": False, "error": "Fine-tuning dependencies not available"}

    try:
        # Quick test with Qwen-3B base model
        from transformers import AutoModelForCausalLM, AutoTokenizer

        model_name = "Qwen/Qwen2.5-3B-Instruct"

        # Load tokenizer and model
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(
            model_name, torch_dtype=torch.float16, device_map="auto"
        )

        # Test generation
        inputs = tokenizer(test_prompt, return_tensors="pt")
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=150,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
            )

        response = tokenizer.decode(outputs[0], skip_special_tokens=True)

        return {
            "success": True,
            "model_name": model_name,
            "test_prompt": test_prompt,
            "response": response,
            "model_size_gb": "~6GB (3B parameters)",
        }

    except Exception as e:
        activity.logger.error(f"Qwen model test failed: {e}")
        return {"success": False, "error": str(e)}
