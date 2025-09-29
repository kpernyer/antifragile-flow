# Qwen-3B-Instruct Base Model

## Model Information

- **Model Name**: `Qwen/Qwen2.5-3B-Instruct`
- **Size**: 3 billion parameters
- **Type**: Instruction-tuned large language model
- **Framework**: Transformers-compatible
- **License**: Apache 2.0

## Specifications

```yaml
Architecture:
  Type: Causal Language Model
  Parameters: 3,085,938,688
  Layers: 28
  Hidden Size: 2048
  Attention Heads: 16
  Vocabulary Size: 151,936

Context:
  Max Sequence Length: 32,768 tokens
  Default Context: 8,192 tokens

Training:
  Base Model: Qwen2.5-3B
  Instruction Tuning: Yes
  Safety Alignment: Yes
```

## Usage in Training Service

This model serves as the base for LoRA fine-tuning in the organizational training system.

### LoRA Configuration

```python
LoraConfig(
    r=16,                    # Rank of adaptation
    lora_alpha=32,          # LoRA scaling parameter
    target_modules=[         # Attention layers to adapt
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj"
    ],
    lora_dropout=0.05,       # Dropout for regularization
    bias="none",            # No bias adaptation
    task_type=TaskType.CAUSAL_LM,
)
```

### Performance Characteristics

- **Training Speed**: Fast (suitable for development and testing)
- **Memory Requirements**: 8GB recommended
- **Inference Speed**: ~2-3 tokens/second on CPU, ~20-30 tokens/second on GPU
- **Quality**: Good instruction-following capabilities
- **Use Case**: Development, testing, and medium-complexity organizational tasks

## Loading Instructions

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

# Load base model
model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-3B-Instruct")
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-3B-Instruct")

# For training with LoRA
from peft import get_peft_model, LoraConfig, TaskType

lora_config = LoraConfig(...)
model = get_peft_model(model, lora_config)
```

## Integration with Service

Referenced in `service/model_training_service.py:140-145`:

```python
ModelType.QWEN_3B: {
    "model_name": "Qwen/Qwen2.5-3B-Instruct",
    "max_examples_per_doc": 30,
    "training_epochs": 2,
    "batch_size": 4,
}
```

## Organizational Training Results

When fine-tuned with organizational data:

- **Trainable Parameters**: 7,372,800 (0.24% of total)
- **Training Examples**: 8-30 per document
- **Training Time**: ~15-30 minutes
- **Adapter Size**: ~14MB (vs 6GB base model)

## Deployment Options

1. **Ollama Integration**: Can be deployed to Ollama for easy inference
2. **Direct Loading**: Load with transformers for custom inference
3. **API Serving**: Serve via FastAPI or similar frameworks
4. **Container Deployment**: Docker containers for scalable serving
