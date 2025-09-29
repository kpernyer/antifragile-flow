# Mistral-7B-Instruct Base Model

## Model Information

- **Model Name**: `mistralai/Mistral-7B-Instruct-v0.2`
- **Size**: 7 billion parameters
- **Type**: Instruction-tuned large language model
- **Framework**: Transformers-compatible
- **License**: Apache 2.0

## Specifications

```yaml
Architecture:
  Type: Causal Language Model
  Parameters: ~7,241,732,096
  Layers: 32
  Hidden Size: 4096
  Attention Heads: 32
  Vocabulary Size: 32,000

Context:
  Max Sequence Length: 32,768 tokens
  Default Context: 8,192 tokens
  Sliding Window: 4,096 tokens

Training:
  Base Model: Mistral-7B
  Instruction Tuning: Yes
  Safety Alignment: Yes
  Training Data: High-quality instruction datasets
```

## Usage in Training Service

This model serves as the production-quality base for LoRA fine-tuning in the organizational training system.

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

- **Training Speed**: Moderate (production-quality training)
- **Memory Requirements**: 16GB recommended (32GB for optimal performance)
- **Inference Speed**: ~1-2 tokens/second on CPU, ~15-25 tokens/second on GPU
- **Quality**: Excellent instruction-following and reasoning capabilities
- **Use Case**: Production deployments requiring high-quality responses

## Loading Instructions

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

# Load base model
model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-Instruct-v0.2")
tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.2")

# For training with LoRA
from peft import get_peft_model, LoraConfig, TaskType

lora_config = LoraConfig(...)
model = get_peft_model(model, lora_config)
```

## Integration with Service

Referenced in `service/model_training_service.py:134-139`:

```python
ModelType.MISTRAL_7B: {
    "model_name": "mistralai/Mistral-7B-Instruct-v0.2",
    "max_examples_per_doc": 20,
    "training_epochs": 3,
    "batch_size": 2,
}
```

## Organizational Training Results

When fine-tuned with organizational data:

- **Trainable Parameters**: ~14,745,600 (0.20% of total)
- **Training Examples**: 15-25 per document
- **Training Time**: ~45-90 minutes
- **Adapter Size**: ~28MB (vs 14GB base model)

## Advanced Features

### Sliding Window Attention
- Processes longer sequences efficiently
- Better context understanding for complex documents
- Ideal for strategic analysis and detailed document processing

### Production Capabilities
- Superior reasoning and analysis
- Better organizational context understanding
- More consistent strategic recommendations
- Enhanced communication style adaptation

## Deployment Options

1. **Ollama Integration**: Premium model option for organizational assistants
2. **Dedicated Inference Servers**: High-throughput serving infrastructure
3. **Cloud Deployment**: Scalable cloud-based serving
4. **Edge Deployment**: Local deployment for maximum privacy

## Comparison with Qwen-3B

| Aspect | Qwen-3B | Mistral-7B |
|--------|---------|------------|
| **Speed** | Faster | Moderate |
| **Quality** | Good | Excellent |
| **Memory** | 8GB | 16GB |
| **Use Case** | Development/Testing | Production |
| **Training Time** | 15-30 min | 45-90 min |
| **Reasoning** | Basic-Intermediate | Advanced |

## Recommended Usage

- **Development Phase**: Start with Qwen-3B for rapid iteration
- **Production Phase**: Deploy Mistral-7B for customer-facing applications
- **Hybrid Approach**: Qwen-3B for internal tools, Mistral-7B for strategic analysis
