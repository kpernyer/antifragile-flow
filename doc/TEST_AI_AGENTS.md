# 🧪 AI Agent Testing Guide

This guide shows you how to test the AI agents in the clean architecture system.

## 🎯 **Quick Start - Testing Methods**

### **Method 1: Import Testing** ⚡ (Always works)
```bash
# Test that everything imports correctly (no API key needed)
uv run python -c "
from agent_activity.ai_activities import (
    analyze_document_content,
    generate_document_summary,
    perform_simple_research
)
from agent_activity.core.writer_agent import new_writer_agent
print('✅ All AI agent imports successful')
"
```

### **Method 2: Technical Layer Testing** 🔧 (No API key needed)
```bash
# Test pure technical activities (file processing, no AI)
uv run python -c "
import asyncio
from activity.document_activities import process_document_upload
from pathlib import Path

async def test():
    test_file = Path('test.txt')
    test_file.write_text('Sample document content for testing.')
    try:
        result = await process_document_upload(str(test_file))
        print(f'✅ Technical processing: {result.file_name}')
        print(f'   Extracted: {len(result.extracted_text)} chars')
    finally:
        test_file.unlink()

asyncio.run(test())
"
```

### **Method 3: Full AI Testing** 🤖 (Requires OpenAI API key)
```bash
# Test complete AI functionality (needs valid OpenAI API key)
export OPENAI_API_KEY="your-api-key-here"
uv run python test_ai_agents.py
```

### **Method 4: Temporal Workflow Testing** 🔄 (Complete integration)
```bash
# Terminal 1: Start worker
uv run python worker/onboarding_worker.py

# Terminal 2: Run workflow test
uv run python test/test_document_processing_starter.py
```

## 🔧 **Prerequisites**

### **For Technical Testing (Methods 1 & 2)**
- ✅ Python environment set up
- ✅ Dependencies installed (`uv sync`)

### **For AI Testing (Method 3)**
- ✅ Valid OpenAI API key
- ✅ Internet connection
- ✅ Set environment variable: `export OPENAI_API_KEY="sk-..."`

### **For Workflow Testing (Method 4)**
- ✅ Temporal server running: `make temporal`
- ✅ Valid OpenAI API key
- ✅ Worker process running

## 📋 **Test Scenarios**

### **Scenario 1: Document Analysis**
```python
# Test document upload + AI analysis
from activity.document_activities import process_document_upload
from agent_activity.ai_activities import analyze_document_content

# Create test document
test_content = '''
BUSINESS REPORT Q3 2024
Revenue: $2.5M (up 15%)
Key achievements:
- 150 new customers
- 2 product launches
- Team grew by 8 people
'''

# Test the pipeline
document_info = await process_document_upload("report.txt")
analysis = await analyze_document_content(document_info)
```

### **Scenario 2: Research Query**
```python
# Test research functionality
from agent_activity.ai_activities import perform_simple_research

result = await perform_simple_research(
    "What are the benefits of workflow orchestration?",
    "Software development context"
)
print(f"Research findings: {result.findings}")
```

### **Scenario 3: Quick Summary**
```python
# Test combined document processing + analysis
from agent_activity.ai_activities import generate_document_summary

summary = await generate_document_summary("business_plan.txt")
print(f"Summary: {summary.summary_text}")
```

## 🎯 **Architecture Testing Points**

### **✅ Clean Separation Validation**
```bash
# Verify technical activities have no AI dependencies
grep -r "openai\|OpenAI" activity/document_activities.py
# Should only find imports in agent_activity/

# Verify AI activities use proper imports
grep -r "from activity" agent_activity/ai_activities.py
# Should only import dataclasses, not AI functions
```

### **✅ Import Structure Validation**
```python
# Technical activities should import successfully
from activity.document_activities import process_document_upload

# AI activities should import successfully
from agent_activity.ai_activities import analyze_document_content

# Should NOT work (proves separation)
# from activity.document_activities import analyze_document_content  # ❌
```

## 🚀 **Sample Test Output**

### **Successful Technical Test**
```
✅ Technical processing works: test_document.txt
   Extracted 123 characters
🎯 Technical layer is working!
```

### **Successful AI Test**
```
✅ Document processed: business_report.txt
   Size: 1,247 bytes
   Text length: 1,247 chars

✅ Analysis completed with confidence: 0.8
   Summary: Quarterly business report showing 15% revenue growth
   Key takeaways: 3 items
   Main topics: ['Revenue Growth', 'Customer Acquisition', 'Team Expansion']

✅ Quick summary completed: business_report.txt
   Success: True
   Summary: Strong Q3 performance with significant growth metrics
```

## 🔧 **Troubleshooting**

### **Import Errors**
```bash
# If imports fail, check Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
uv run python -c "import sys; print('\\n'.join(sys.path))"
```

### **OpenAI API Errors**
```bash
# Check API key is set
echo $OPENAI_API_KEY

# Test API key validity
uv run python -c "
import openai
openai.api_key = os.environ.get('OPENAI_API_KEY')
print('API key configured')
"
```

### **Temporal Connection Errors**
```bash
# Check Temporal server is running
curl http://localhost:8233/api/v1/namespaces

# Or start Temporal server
make temporal
```

## 📊 **Test Coverage Areas**

### **✅ Unit Tests**
- Individual activity functions
- Data structure validation
- Error handling

### **✅ Integration Tests**
- Activity → Activity chains
- Workflow orchestration
- Error propagation

### **✅ System Tests**
- End-to-end workflows
- Temporal integration
- External API integration

### **✅ Architecture Tests**
- Import separation
- Dependency isolation
- Clean boundaries

## 🎯 **Best Testing Practices**

1. **Start Simple**: Test imports and technical layers first
2. **Layer by Layer**: Test each architectural layer independently
3. **Mock External APIs**: Use mocks for unit tests, real APIs for integration
4. **Error Scenarios**: Test failure cases and error handling
5. **Performance**: Monitor AI API latency and costs
6. **Security**: Never commit API keys to repository

## 🔗 **Related Files**

- `test_ai_agents.py` - Comprehensive AI agent testing script
- `test/test_document_processing_starter.py` - Temporal workflow testing
- `activity/README.md` - Technical activities documentation
- `agent_activity/README.md` - AI activities documentation
