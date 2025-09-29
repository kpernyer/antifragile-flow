# Ollama Local LLM Setup Guide

A comprehensive reference for setting up and using local LLMs with Ollama for development and coding tasks.

## Quick Start

### Prerequisites
- [Ollama installed](https://ollama.ai/download)
- Sufficient RAM/VRAM for your chosen model
- Terminal access

### Installation

#### macOS
```bash
# Download and install Ollama for macOS
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve
```

**Note:** If the universal installer fails on macOS, use Homebrew instead:
```bash
# Install via Homebrew (recommended for macOS)
brew install ollama

# Start Ollama service
ollama serve
```

#### Linux
```bash
# Download and install Ollama for Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve
```

#### Alternative Installation Methods

**macOS (using Homebrew - Recommended):**
```bash
# Install via Homebrew (primary method for macOS)
brew install ollama

# Start Ollama service
ollama serve
```

**Linux (using package managers):**

**Ubuntu/Debian:**
```bash
# Add Ollama repository
curl -fsSL https://ollama.ai/install.sh | sh

# Or install via snap
sudo snap install ollama
```

**Fedora/RHEL/CentOS:**
```bash
# Install via package manager
curl -fsSL https://ollama.ai/install.sh | sh
```

**Arch Linux:**
```bash
# Install via AUR
yay -S ollama-bin

# Or install via pacman (if available)
sudo pacman -S ollama
```

## Model Configurations

### 1. GPT-OSS-20B (Instruct) - Balanced Performance

**Best for:** General coding, Q&A, text processing
**Memory:** ~12GB RAM/VRAM recommended
**Speed:** Moderate

#### Modelfile: `gpt-oss-20b`
```dockerfile
FROM openai/gpt-oss-20b-instruct:Q4_K_M

PARAMETER num_ctx 8192
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER repeat_penalty 1.1

SYSTEM """
You are a helpful, concise assistant for English text tasks (summaries, drafting, Q&A, light coding).
Prioritize accuracy and short, clear answers unless asked for more detail.
"""
```

#### Setup Commands
```bash
# Create the model
ollama create gpt-oss-20b -f ./gpt-oss-20b

# Run the model
ollama run gpt-oss-20b
```

---

### 2. Gemma 7B (Instruct) - Fast & Efficient

**Best for:** Quick demos, writing, summarization
**Memory:** ~6GB RAM/VRAM
**Speed:** Fast (great for M-series Macs)

#### Modelfile: `gemma-7b`
```dockerfile
FROM gemma:7b-instruct-q4_K_M

PARAMETER num_ctx 8192
PARAMETER temperature 0.6
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER repeat_penalty 1.1

SYSTEM """
You are a fast, efficient English writing and summarization assistant.
Keep responses brief and friendly. Prefer bullet points for lists.
"""
```

#### Setup Commands
```bash
# Create the model
ollama create gemma-7b -f ./gemma-7b

# Run the model
ollama run gemma-7b
```

---

### 3. Mistral 7B (Instruct) - Reasoning & Coding

**Best for:** Reasoning tasks, coding, step-by-step explanations
**Memory:** ~6GB RAM/VRAM
**Speed:** Fast

#### Modelfile: `mistral-7b`
```dockerfile
FROM mistral:7b-instruct-q4_K_M

PARAMETER num_ctx 8192
PARAMETER temperature 0.6
PARAMETER top_p 0.9
PARAMETER top_k 50
PARAMETER repeat_penalty 1.15

SYSTEM """
You are an English-first assistant optimized for reasoning, Q&A, and light coding.
Explain briefly, cite assumptions, and show steps only when requested.
"""
```

#### Setup Commands
```bash
# Create the model
ollama create mistral-7b -f ./mistral-7b

# Run the model
ollama run mistral-7b
```

## Performance Optimization

### Quantization Levels
Choose based on your hardware:

| Quantization | Memory Usage | Quality | Use Case |
|--------------|--------------|---------|----------|
| `q3_K_M` | Low | Basic | Limited RAM/VRAM |
| `q4_K_M` | Medium | Good | **Recommended default** |
| `q5_K_M` | High | Better | More memory available |
| `q6_K` | Very High | Best | High-end hardware |

### Context Window Tuning
```bash
# For long documents, increase context
PARAMETER num_ctx 16384  # Default: 8192

# Check memory before increasing
ollama ps  # Shows memory usage
```

### Temperature Settings
```bash
# For coding (more deterministic)
PARAMETER temperature 0.3

# For creative tasks
PARAMETER temperature 0.8

# Default (balanced)
PARAMETER temperature 0.6-0.7
```

## Development Workflow

### Running Multiple Models
```bash
# Terminal 1
ollama run gpt-oss-20b

# Terminal 2
ollama run gemma-7b

# Terminal 3
ollama run mistral-7b
```

### Model Management
```bash
# List installed models
ollama list

# Remove a model
ollama rm model-name

# Pull latest version
ollama pull model-name

# Check model info
ollama show model-name
```

### API Integration
```bash
# Start Ollama with API
ollama serve

# API endpoint
curl http://localhost:11434/api/generate -d '{
  "model": "gpt-oss-20b",
  "prompt": "Write a Python function to sort a list"
}'
```

## Hardware Recommendations

### Mac (Apple Silicon)
- **M1/M2 with 8GB RAM:** Use `q3_K_M` quantization
- **M1/M2 with 16GB+ RAM:** Use `q4_K_M` quantization
- **M1/M2 Pro/Max:** Use `q5_K_M` for better quality

### Windows/Linux
- **8GB RAM:** Stick to 7B models with `q3_K_M`
- **16GB RAM:** Can run 20B models with `q4_K_M`
- **32GB+ RAM:** Use `q5_K_M` or `q6_K` for best quality

### GPU Acceleration
```bash
# Check if CUDA is available
nvidia-smi

# Ollama will automatically use GPU if available
# For AMD GPUs, use ROCm (Linux only)
```

## Troubleshooting

### Common Issues

**Out of Memory**
```bash
# Reduce quantization
# Change from q4_K_M to q3_K_M

# Or reduce context window
PARAMETER num_ctx 4096
```

**Slow Performance**
```bash
# Check if GPU is being used
ollama ps

# Ensure sufficient RAM is available
# Close other memory-intensive applications
```

**Model Not Found**
```bash
# Pull the base model first
ollama pull openai/gpt-oss-20b-instruct:Q4_K_M

# Then create your custom model
ollama create gpt-oss-20b -f ./gpt-oss-20b
```

**Version Mismatch Warning**
```bash
# If you see: "Warning: client version is X.X.X"
# This means your client and server versions don't match

# Check current versions
ollama --version  # Client version
ollama ps         # Server version info

# Update Ollama to latest version
# macOS (Homebrew):
brew upgrade ollama

# Linux:
curl -fsSL https://ollama.ai/install.sh | sh

# Restart Ollama service
ollama serve
```

**Stopping Ollama Service**
```bash
# Method 1: Using ollama command (recommended)
ollama stop

# Method 2: Kill process on port 11434
lsof -ti:11434 | xargs kill -9

# Method 3: Find and kill Ollama process
pkill -f ollama

# Method 4: Kill by process ID (if you know the PID)
kill -9 <PID>

# Verify Ollama is stopped
lsof -i:11434  # Should show no processes
```

## Integration Examples

### Python Integration
```python
import requests
import json

def query_ollama(prompt, model="gpt-oss-20b"):
    response = requests.post('http://localhost:11434/api/generate',
                           json={'model': model, 'prompt': prompt})
    return response.json()['response']

# Usage
code_suggestion = query_ollama("Write a function to validate email addresses")
```

### Node.js Integration
```javascript
const axios = require('axios');

async function queryOllama(prompt, model = 'gpt-oss-20b') {
  const response = await axios.post('http://localhost:11434/api/generate', {
    model,
    prompt
  });
  return response.data.response;
}
```

## Best Practices

1. **Start Small:** Begin with 7B models for faster iteration
2. **Test Prompts:** Use the same prompt across models to compare
3. **Monitor Resources:** Keep an eye on memory usage during development
4. **Version Control:** Save your Modelfiles in your project
5. **Documentation:** Keep notes on which model works best for your use case

## Quick Reference Commands

```bash
# Essential commands
ollama serve                    # Start Ollama service
ollama list                     # List installed models
ollama run model-name           # Run a model interactively
ollama ps                       # Show running models
ollama rm model-name            # Remove a model
ollama pull model-name          # Download a model
ollama create name -f file      # Create custom model
```

---

*Last updated: $(date)*
*For more information, visit [Ollama Documentation](https://github.com/ollama/ollama)*
