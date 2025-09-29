# Model Directory

This directory contains base models and organization-specific trained models for the Antifragile Flow system.

## Directory Structure

```
models/
├── base/                           # Base model references
│   ├── qwen-3b-instruct/          # Qwen-3B development model
│   │   └── MODEL_INFO.md          # Model specifications and usage
│   └── mistral-7b-instruct/       # Mistral-7B production model
│       └── MODEL_INFO.md          # Model specifications and usage
├── trained/                       # Organization-specific trained models
│   └── techcorp-demo/             # Example TechCorp trained model
│       ├── adapter_model.safetensors   # LoRA adapter weights
│       ├── adapter_config.json         # LoRA configuration
│       ├── tokenizer.json             # Tokenizer files
│       └── TRAINING_INFO.md           # Training details and usage
└── README.md                      # This file
```

## Base Models

### Qwen-3B-Instruct
- **Purpose**: Development and testing
- **Size**: 3B parameters (~6GB)
- **Speed**: Fast training and inference
- **Use Case**: Rapid prototyping, development iterations

### Mistral-7B-Instruct
- **Purpose**: Production deployments
- **Size**: 7B parameters (~14GB)
- **Quality**: Superior reasoning and analysis
- **Use Case**: Customer-facing applications, strategic analysis

## Trained Models

### TechCorp Demo
- **Base Model**: Qwen-3B-Instruct
- **Training Method**: LoRA fine-tuning
- **Organizational Focus**: Innovation, integrity, sustainability
- **Use Case**: Demonstration of organizational AI customization

## Model Usage Patterns

### Development Workflow
```python
# 1. Load base model for training
base_model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-3B-Instruct")

# 2. Apply LoRA for organizational training
lora_config = LoraConfig(r=16, lora_alpha=32, ...)
model = get_peft_model(base_model, lora_config)

# 3. Train with organizational data
trainer = SFTTrainer(model=model, train_dataset=org_dataset, ...)
trainer.train()

# 4. Save trained adapter
model.save_pretrained("models/trained/org-name")
```

### Production Inference
```python
# Load trained organizational model
base_model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-3B-Instruct")
model = PeftModel.from_pretrained(base_model, "models/trained/techcorp-demo")
tokenizer = AutoTokenizer.from_pretrained("models/trained/techcorp-demo")

# Generate organization-specific responses
response = model.generate(...)
```

## Integration with Services

### Model Training Service
The training service automatically manages models in this directory:

```python
# service/model_training_service.py
self.models_dir = Path("./models/trained")      # Trained models
self.base_models_path = Path("./models/base")   # Base model references
```

### Local LLM Service
The local LLM service loads models from this structure:

```python
# service/local_llm_service.py
def load_organizational_model(self, org_id: str):
    model_path = f"models/trained/org-{org_id}"
    base_path = "models/base/qwen-3b-instruct"
    # Load and serve organizational model
```

## Storage Strategy

### What IS Stored (Small & Custom) ✅

**LoRA Adapter Weights** - 28MB per organization
```bash
models/trained/techcorp-demo/adapter_model.safetensors  # 28MB - Custom organizational knowledge
```
- **Why stored**: Contains unique organizational training (TechCorp values, style, knowledge)
- **Size**: Only 0.24% of full model weights (7.4M trainable parameters)
- **Version Control**: Perfect size for git (organizational IP preserved)

**Tokenizer & Configuration** - 15MB per organization
```bash
models/trained/techcorp-demo/tokenizer.json     # 11MB - Custom tokenizer
models/trained/techcorp-demo/vocab.json         # 2.8MB - Vocabulary
models/trained/techcorp-demo/adapter_config.json # <1MB - LoRA configuration
```
- **Why stored**: Required for model inference and may contain org-specific tokens
- **Essential**: Cannot use trained model without these files

### What is NOT Stored (Large & Standard) ❌

**Base Model Weights** - 6GB-14GB each
```python
# Referenced but NOT stored in repository
"Qwen/Qwen2.5-3B-Instruct"        # ~6GB base model
"mistralai/Mistral-7B-Instruct-v0.2" # ~14GB base model
```

**Why NOT stored:**
- **Size**: Too large for version control (6GB-14GB each)
- **Standard**: Available from Hugging Face Hub
- **Unchanging**: Same base model for all organizations
- **Runtime Download**: Downloaded and cached when needed

### Size Comparison

| Component | Size | Stored? | Purpose |
|-----------|------|---------|---------|
| **LoRA Adapter** | 28MB | ✅ YES | Custom organizational knowledge |
| **Tokenizer Files** | 15MB | ✅ YES | Required for inference |
| **Config Files** | <1MB | ✅ YES | Model configuration |
| **Base Model Weights** | 6GB+ | ❌ NO | Standard, downloadable |
| **Total per Organization** | 43MB | ✅ YES | Git-friendly size |
| **Runtime Requirements** | 6GB+ | ❌ CACHED | Downloaded once, reused |

### LoRA Efficiency Example

**Traditional Fine-tuning**:
- Store entire 6GB model per organization
- 10 organizations = 60GB storage
- Expensive, slow, hard to manage

**LoRA Approach**:
- Store 6GB base model once (cached from Hugging Face)
- Store 28MB adapter per organization
- 10 organizations = 6GB + (28MB × 10) = 6.3GB total
- **🎯 95% storage savings!**

### Runtime Loading Process

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

# 1. Download/load base model (6GB) - cached locally after first download
base_model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen2.5-3B-Instruct"  # Downloads from Hugging Face Hub
)

# 2. Load custom LoRA adapter (28MB) - from our repository
model = PeftModel.from_pretrained(
    base_model,
    "models/trained/techcorp-demo"  # Our stored organizational weights
)

# 3. Load custom tokenizer (15MB) - from our repository
tokenizer = AutoTokenizer.from_pretrained(
    "models/trained/techcorp-demo"  # Our stored tokenizer config
)

# Result: 6GB base model + 28MB organizational customization
# = Complete TechCorp-specific AI model ready for inference
```

### Storage Considerations

#### Development
- **Local Storage**: 43MB per trained organizational model
- **Size Management**: Base models cached in `~/.cache/huggingface/`
- **Version Control**: Only custom adapters and configs tracked in git
- **Backup**: Easy to backup organizational IP (small adapter files)

#### Production
- **Container Strategy**: Download base models during container build/startup
- **Persistent Volumes**: Store organizational adapters in persistent storage
- **Model Registry**: Version and manage organizational model adapters
- **Scaling**: Each organization's custom knowledge fits in 43MB

#### Benefits of This Approach
- ✅ **Version Control Friendly**: Track organizational knowledge without huge files
- ✅ **Cost Effective**: Share base models across organizations
- ✅ **Fast Deployment**: Quick to copy/deploy 43MB adapters
- ✅ **Organizational Privacy**: Each org's knowledge isolated in small adapters
- ✅ **Easy Backup**: Critical organizational AI assets are small files
- ✅ **Scalable**: Add unlimited organizations with minimal storage overhead

## Performance Optimization

### Memory Management
```python
# Load models on-demand
models_cache = {}

def get_model(org_id: str):
    if org_id not in models_cache:
        models_cache[org_id] = load_model(org_id)
    return models_cache[org_id]

# Unload unused models
def cleanup_unused_models():
    # Implementation for memory management
    pass
```

### Inference Optimization
- **Quantization**: Reduce model size for faster inference
- **Batching**: Process multiple requests efficiently
- **Caching**: Cache frequent organizational queries

## Security and Privacy

### Model Access Control
- Organizational models are isolated
- Access control per organization
- Audit logging for model usage

### Data Protection
- Training data remains within organizational boundaries
- No cross-organization data leakage
- Secure model storage and transmission

## Deployment Strategies

### Container-Based
```dockerfile
# Copy models to container
COPY models/ /app/models/

# Expose model serving endpoints
EXPOSE 8091
```

### Volume-Based
```yaml
# docker-compose.yml
volumes:
  - ./models:/app/models:ro  # Read-only model access
```

### Registry-Based
- Central model registry for enterprise deployment
- Version management and rollback capabilities
- Automated model deployment pipelines

This directory structure supports the complete lifecycle of organizational AI model development, training, and deployment within the Antifragile Flow system.
