# RAG vs Fine-tuning: A Comprehensive Guide

A deep dive into when to use Retrieval-Augmented Generation (RAG), fine-tuning, or both for enterprise AI applications.

## 🎯 Overview

Modern AI applications often face a critical architectural decision: **RAG vs Fine-tuning vs Hybrid approaches**. This guide explains the trade-offs, implementation strategies, and when to use each approach.

## 📊 What is a "Row of Data" in Fine-tuning?

Fine-tuning requires **structured training examples**, not raw documents. Each "row" represents an input/output pair that teaches the model specific behaviors.

### Training Data Formats

**Instruction Tuning (Mistral/Gemma/Llama):**
```json
{
  "instruction": "Summarize the following strategic memo in 3 bullet points.",
  "input": "Memo text here...",
  "output": "- Point one\n- Point two\n- Point three"
}
```

**Plain Q&A (Domain-specific answers):**
```json
{
  "prompt": "What are the main growth risks for industrial access solutions?",
  "completion": "The risks include shrinking margins, commoditization of hardware, and reliance on outdated wireless standards."
}
```

**Key Insight:** 1,000 rows = 1,000 teaching examples, not 1,000 documents.

## 🔧 Fine-tuning vs RAG: Core Differences

### 1. **Fine-tuning (LoRA, Unsloth, etc.)**

**What it does:**
- Adjusts the base model's weights to remember patterns, style, or answers
- Internalizes knowledge into the model's parameters
- Teaches specific response formats and behaviors

**Benefits:**
- ✅ **Style & tone baked in**: Model speaks in your corporate voice without prompts
- ✅ **Runtime efficiency**: No need to constantly feed context
- ✅ **Great for repetitive tasks**: Consistent formatting and structure
- ✅ **Lower latency**: Direct generation without retrieval overhead

**Drawbacks:**
- ❌ **Less flexible for updates**: Adding new documents requires retraining
- ❌ **Risk of overfitting**: Can become brittle with limited training data
- ❌ **Hallucination risk**: May "parrot" training data or generate incorrect information
- ❌ **Higher computational cost**: Requires significant GPU resources for training

### 2. **RAG (Retrieval-Augmented Generation)**

**What it does:**
- Stores documents in a vector database
- Retrieves relevant chunks at query time
- Appends context to prompts for generation
- Model remains unchanged

**Benefits:**
- ✅ **Dynamic updates**: Add/remove documents instantly
- ✅ **Scalable with limited data**: Works with 5-10 documents
- ✅ **Traceability**: Show which passages were used
- ✅ **Factual accuracy**: Grounded in actual source material
- ✅ **No training required**: Works immediately with new documents

**Drawbacks:**
- ❌ **No style learning**: Model won't adopt your tone without careful prompting
- ❌ **Context window bound**: Limited by model's context length (8k-128k tokens)
- ❌ **Slightly slower**: Each query requires retrieval + larger prompts
- ❌ **Retrieval dependency**: Quality depends on embedding and search quality

## ⚖️ When to Use Each Approach

### **Choose Fine-tuning When:**
- You want the model to speak in your organization's strategic voice
- You'll reuse the same patterns repeatedly (summaries, risk analysis, frameworks)
- Your data is more about style/behavior than raw facts
- You have stable, well-curated training examples
- Performance and latency are critical

### **Choose RAG When:**
- You want the model to stay up-to-date with living documents
- Your data contains facts, numbers, or content that changes frequently
- You need explainability ("this answer came from Doc A, section 3")
- You have limited training data but extensive document collections
- You need to handle diverse, unstructured information

### **Choose Hybrid (Fine-tune + RAG) When:**
- You want both polished style AND factual accuracy
- You have both stable patterns AND dynamic content
- You're building production demos that need both quality and traceability
- You can afford the complexity of managing both systems

## 🚀 Implementation Strategies

### **Fine-tuning Pipeline (Unsloth + LoRA)**

#### 1. Data Preparation
```python
# Convert strategic documents to training examples
import json
import pathlib
from pypdf import PdfReader

def create_training_data():
    train_rows = []

    for pdf_file in pathlib.Path("docs/").glob("*.pdf"):
        text = extract_text_from_pdf(pdf_file)

        # Create instruction examples
        train_rows.extend([
            {
                "instruction": "Summarize this strategy memo in 3 bullets.",
                "input": text[:4000],
                "output": "- Strategic point one\n- Strategic point two\n- Strategic point three"
            },
            {
                "instruction": "List the top 5 risks mentioned and why they matter.",
                "input": text[:4000],
                "output": "1) Risk one because...\n2) Risk two because..."
            }
        ])

    # Save to JSONL format
    with open("data/train.jsonl", "w") as f:
        for row in train_rows:
            f.write(json.dumps(row) + "\n")
```

#### 2. Training Script (Unsloth)
```python
from datasets import load_dataset
from unsloth import FastLanguageModel
from transformers import TrainingArguments
from trl import SFTTrainer

# Load dataset
dataset = load_dataset("json", data_files="data/train.jsonl", split="train")

# Format for instruction tuning
def format_row(ex):
    return f"""### Instruction:
{ex['instruction']}

### Input:
{ex.get('input','')}

### Response:
{ex['output']}"""

dataset = dataset.map(lambda ex: {"text": format_row(ex)})

# Load and prepare model
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="mistral-7b-instruct",
    load_in_4bit=True,
)
model = FastLanguageModel.get_peft_model(
    model,
    lora_r=16, lora_alpha=32, lora_dropout=0.05,
    target_modules="all-linear"
)

# Train
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=4096,
    args=TrainingArguments(
        output_dir="out-ft",
        per_device_train_batch_size=2,
        gradient_accumulation_steps=8,
        learning_rate=1e-4,
        num_train_epochs=2,
        fp16=True
    ),
)
trainer.train()
```

#### 3. Ollama Integration
```dockerfile
# Modelfile for fine-tuned model
FROM your-org/mistral-7b-ft:Q4_K_M
PARAMETER num_ctx 8192
PARAMETER temperature 0.7
SYSTEM "You speak in the company's strategic voice. Be concise and structured."
```

### **RAG Pipeline (Local Stack)**

#### 1. Stack Components
```bash
# Embeddings: bge-small-en (fast) or gte-large (better)
# Vector DB: Chroma (simple local)
# Orchestrator: Custom (as in Living Twin)
# Generator: Local Mistral-7B or GPT-oss-20B
```

#### 2. RAG Server Implementation
```python
from fastapi import FastAPI
from llama_index.core import VectorStoreIndex, ServiceContext
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
import requests

app = FastAPI()
client = chromadb.PersistentClient(path="rag_db")
collection = client.get_or_create_collection("strategy")

# Setup embeddings and index
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
vs = ChromaVectorStore(chroma_collection=collection)
index = VectorStoreIndex.from_vector_store(vs, embed_model=embed_model)

def ollama_chat(prompt: str) -> str:
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "mistral-7b", "prompt": prompt, "stream": False}
    )
    return response.json()["response"]

@app.get("/ask")
def ask(q: str):
    retriever = index.as_retriever(similarity_top_k=4)
    context_nodes = retriever.retrieve(q)
    context = "\n\n".join(n.get_content() for n in context_nodes)

    prompt = f"""Answer using ONLY the context below. If unknown, say so.

Context:
{context}

Question: {q}

Answer:"""

    return {"answer": ollama_chat(prompt), "sources": [n.metadata for n in context_nodes]}
```

### **Hybrid Pipeline (Best of Both Worlds)**

#### 1. Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Query    │───►│   RAG Retrieval │───►│   Fine-tuned    │
│                 │    │   (Facts)       │    │   Generator     │
└─────────────────┘    └─────────────────┘    │   (Style)       │
                                             └─────────────────┘
```

#### 2. Implementation
```python
def hybrid_query(query: str):
    # 1. Retrieve relevant context
    retriever = index.as_retriever(similarity_top_k=4)
    context_nodes = retriever.retrieve(query)
    context = "\n\n".join(n.get_content() for n in context_nodes)

    # 2. Generate with fine-tuned model + context
    prompt = f"""You are the company's strategic assistant. Use the provided CONTEXT facts verbatim.

Question: {query}

Context:
{context}

Assistant: Produce a 5-bullet executive summary, a risks/mitigations table, and a "Why it matters" paragraph."""

    # Use fine-tuned model for generation
    return ollama_chat(prompt, model="mistral-7b-ft")
```

## 📈 Performance Comparison

### **Latency Benchmarks**
| Approach | Model | Latency | Quality | Cost |
|----------|-------|---------|---------|------|
| **Fine-tuned** | Mistral-7B Q4 | ~40-80 tok/s | High | Training cost |
| **RAG** | Mistral-7B Q4 | ~30-60 tok/s | Variable | Low |
| **Hybrid** | Mistral-7B Q4 | ~25-50 tok/s | Highest | Training + runtime |

### **Resource Requirements**
| Component | VRAM | RAM | Storage |
|-----------|------|-----|---------|
| **Fine-tuning** | 8-24GB | 16-32GB | 10-50GB |
| **RAG (Chroma)** | 2-4GB | 8-16GB | 1-10GB |
| **Hybrid** | 8-24GB | 16-32GB | 10-50GB |

## 🎯 Use Case Recommendations

### **Strategic Analysis (Fine-tuned)**
```bash
# Best for: Executive summaries, risk assessments, strategy frameworks
# Why: Consistent formatting, corporate voice, repetitive patterns
```

### **Document Q&A (RAG)**
```bash
# Best for: Policy questions, technical documentation, dynamic content
# Why: Factual accuracy, traceability, up-to-date information
```

### **Executive Demos (Hybrid)**
```bash
# Best for: Board presentations, investor demos, client showcases
# Why: Professional polish + factual grounding
```

## 🔧 Evaluation Framework

### **Metrics to Track**
```python
# 1. Accuracy Metrics
- Exact match rate
- ROUGE scores
- BLEU scores
- Human preference scores

# 2. Performance Metrics
- Response latency
- Throughput (queries/second)
- Resource utilization

# 3. Business Metrics
- User satisfaction
- Task completion rate
- Cost per query
```

### **Evaluation Script**
```python
import ragas
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_relevancy

# Create evaluation dataset
eval_dataset = create_eval_dataset()

# Evaluate RAG system
results = evaluate(
    eval_dataset,
    metrics=[faithfulness, answer_relevancy, context_relevancy]
)
```

## 🚀 Production Deployment

### **Fine-tuned Model Deployment**
```bash
# 1. Export to GGUF format
python -m llama_cpp.convert_hf_to_gguf /path/to/model --outfile model.gguf

# 2. Quantize for production
./llama.cpp/quantize model.gguf model-q4_k_m.gguf q4_k_m

# 3. Deploy with Ollama
ollama create my-model -f Modelfile
ollama run my-model
```

### **RAG System Deployment**
```bash
# 1. Vector database setup
docker run -p 8000:8000 chromadb/chroma

# 2. Embedding service
docker run -p 8080:8080 sentence-transformers/all-MiniLM-L6-v2

# 3. API service
uvicorn rag_server:app --host 0.0.0.0 --port 8000
```

### **Hybrid System Deployment**
```bash
# 1. Load fine-tuned model
ollama run mistral-7b-ft

# 2. Start RAG service
uvicorn hybrid_server:app --reload

# 3. Configure load balancer
# Route queries to appropriate system based on type
```

## 💡 Best Practices

### **Data Quality**
- **Fine-tuning**: Quality > quantity. 1,000 excellent examples > 10,000 mediocre ones
- **RAG**: Focus on chunking strategy and embedding quality
- **Hybrid**: Ensure training data aligns with retrieval patterns

### **Model Selection**
- **Fine-tuning**: Start with smaller models (Mistral-7B) for faster iteration
- **RAG**: Choose embeddings based on domain (BGE for general, domain-specific for specialized)
- **Hybrid**: Use same base model for both fine-tuning and generation

### **Cost Optimization**
- **Fine-tuning**: Use LoRA/QLoRA to reduce training costs
- **RAG**: Cache frequently accessed embeddings
- **Hybrid**: Implement smart routing to minimize unnecessary processing

## 🔮 Future Trends

### **Emerging Technologies**
- **Mixture of Experts (MoE)**: More efficient fine-tuning
- **Retrieval-Augmented Fine-tuning (RAFT)**: Combining both approaches during training
- **Multi-modal RAG**: Handling images, audio, and video alongside text

### **Industry Adoption**
- **Enterprise**: Moving toward hybrid approaches for maximum flexibility
- **Startups**: Starting with RAG, adding fine-tuning as they scale
- **Research**: Exploring new architectures that combine both paradigms

---

## 📚 Additional Resources

- **Fine-tuning Tools**: [Unsloth](https://github.com/unslothai/unsloth), [LoRA](https://github.com/microsoft/LoRA)
- **RAG Frameworks**: [LlamaIndex](https://github.com/run-llama/llama_index), [LangChain](https://github.com/langchain-ai/langchain)
- **Evaluation**: [RAGAS](https://github.com/explodinggradients/ragas), [TruLens](https://github.com/truera/trulens)

---

*This guide provides a foundation for choosing and implementing the right AI approach for your specific use case. The key is understanding your requirements and starting with the simplest approach that meets your needs.*
