# Prompt and Template Management System

A comprehensive system for managing AI prompts and templates with type safety, validation, and centralized management.

## 🚀 Features

- **Centralized Management**: All prompts in YAML files with structured organization
- **Type Safety**: Pydantic schemas for validation and type checking
- **Jinja2 Templating**: Dynamic prompt generation with custom filters and functions
- **Role-Based Organization**: Separate prompts for agents, workflows, personas, and common use cases
- **Version Control**: Semantic versioning for prompt evolution
- **Usage Tracking**: Monitor prompt usage and performance
- **Validation**: Comprehensive validation of prompt definitions and templates
- **CLI Tools**: Command-line interface for managing prompts
- **Caching**: Performance optimization with intelligent caching

## 📁 Directory Structure

```
shared/prompts/
├── __init__.py                 # Public API
├── loader.py                   # YAML file loading and validation
├── registry.py                 # Prompt caching and management
├── templates.py                # Jinja2 template engine
├── cli.py                      # Command-line tools
├── schemas/                    # Pydantic schemas
│   ├── __init__.py
│   ├── base.py
│   ├── agent_prompts.py
│   └── workflow_prompts.py
├── definitions/                # YAML prompt definitions
│   ├── agents/                 # Agent-specific prompts
│   │   ├── document_processor.yaml
│   │   ├── knowledge_builder.yaml
│   │   └── consensus_builder.yaml
│   ├── workflows/              # Workflow prompts
│   │   ├── onboarding.yaml
│   │   └── consensus_building.yaml
│   ├── personas/               # Persona-based prompts
│   │   ├── ceo.yaml
│   │   ├── vp_engineering.yaml
│   │   └── vp_sales.yaml
│   └── common/                 # Shared prompts
│       ├── system_messages.yaml
│       └── error_handling.yaml
└── examples/                   # Usage examples
    ├── __init__.py
    └── integration_example.py
```

## 🔧 Quick Start

### 1. Basic Usage

```python
from shared.prompts import load_prompt

# Simple prompt loading
prompt = load_prompt(
    "document_processor.analyze_document",
    document_type="contract",
    document_title="Software License Agreement",
    document_content="This agreement..."
)
```

### 2. Advanced Usage with Context

```python
from shared.prompts import PromptRegistry, RenderContext

registry = PromptRegistry()

# Create rendering context
context = RenderContext(
    variables={
        "decision_topic": "Budget allocation",
        "participants": [{"name": "John", "role": "VP Sales"}]
    },
    user_id="user123",
    session_id="session456",
    conversation_history=[
        {"role": "user", "content": "Previous message"}
    ]
)

# Get system and user prompts separately
system_prompt, user_prompt = registry.get_system_and_user_prompts(
    "consensus_builder.facilitate_decision",
    context
)
```

### 3. Agent Integration

```python
class DocumentProcessorAgent:
    def __init__(self):
        self.prompt_registry = PromptRegistry()

    async def analyze_document(self, document_type: str, content: str) -> str:
        return load_prompt(
            "document_processor.analyze_document",
            document_type=document_type,
            document_content=content,
            document_title="Uploaded Document"
        )
```

## 📝 YAML Prompt Definition Format

```yaml
version: "1.0"
prompts:
  - metadata:
      id: "agent.action_name"              # Unique identifier
      name: "Human Readable Name"          # Display name
      description: "What this prompt does" # Purpose description
      category: "agent"                    # Category (agent/workflow/persona/common)
      version: "1.0.0"                     # Semantic version
      tags: ["tag1", "tag2"]              # Searchable tags
      preferred_models: ["claude-3-sonnet"] # Recommended models
      min_context_length: 4000             # Minimum context needed
      max_tokens: 1500                     # Recommended max response
      temperature: 0.7                     # Recommended temperature

    role: "user"                          # Message role (system/user/assistant)

    system_prompt: |                      # Optional system prompt
      You are an expert in...

    template: |                           # Jinja2 template
      Please analyze: {{ document_title }}

      {% if specific_focus %}
      Focus on: {{ specific_focus }}
      {% endif %}

      {{ document_content | truncate_words(1500) }}

    variables:                            # Template variables
      - name: document_title
        type: string
        description: "Title of the document"
        required: true
        examples: ["Contract", "Report"]

      - name: specific_focus
        type: string
        description: "Analysis focus area"
        required: false
        default: "general_analysis"

    examples:                            # Usage examples
      - variables:
          document_title: "License Agreement"
          specific_focus: "legal_terms"
```

## 🛠️ CLI Usage

The system includes a comprehensive CLI for managing prompts:

```bash
# Validate all prompt definitions
python -m shared.prompts.cli validate

# List available prompts
python -m shared.prompts.cli list
python -m shared.prompts.cli list --category agent --tags "document,analysis"

# Show prompt details
python -m shared.prompts.cli show document_processor.analyze_document

# Test prompt rendering
python -m shared.prompts.cli test document_processor.analyze_document \
  --variables "document_type=contract" \
  --variables "document_title=Test Contract"

# Test with variables file
python -m shared.prompts.cli test consensus_builder.facilitate_decision \
  --variables-file test_variables.json \
  --system-user-split

# Show usage statistics
python -m shared.prompts.cli stats --details

# Create example prompt file
python -m shared.prompts.cli create-example example.yaml
```

## 🎯 Custom Jinja2 Filters and Functions

The template engine includes custom filters for common prompt patterns:

### Filters

```jinja2
{{ text | truncate_words(50) }}              # Truncate to 50 words
{{ persona_name | format_persona }}          # Format persona names
{{ amount | format_currency("USD") }}        # Format currency
{{ items | format_list("and") }}            # Format lists with conjunction
{{ text | indent_text(4) }}                 # Indent text by 4 spaces
```

### Functions

```jinja2
{{ format_timestamp(now, "%Y-%m-%d") }}      # Format timestamps
{{ get_conversation_summary(history, 200) }} # Summarize conversation
{{ conditional_section(condition, content) }} # Conditional content
{{ format_decision_context(context) }}       # Format decision context
```

## 🔍 Integration Patterns

### 1. Temporal Activity Integration

```python
from temporalio import activity
from shared.prompts import load_prompt

@activity.defn
async def analyze_document_activity(request: DocumentRequest) -> DocumentAnalysis:
    """Temporal activity that uses prompts."""

    # Load prompt for document analysis
    prompt = load_prompt(
        "document_processor.analyze_document",
        document_type=request.document_type,
        document_title=request.title,
        document_content=request.content
    )

    # Send to AI service
    response = await ai_service.generate(prompt)

    return DocumentAnalysis(content=response)
```

### 2. Workflow Integration

```python
from temporalio import workflow
from shared.prompts import load_prompt

@workflow.defn
class ConsensusWorkflow:

    @workflow.run
    async def run(self, request: ConsensusRequest) -> ConsensusResult:
        # Initialize consensus process
        init_prompt = load_prompt(
            "workflow.consensus.initiate_process",
            process_title=request.title,
            decision_topic=request.topic,
            participants=request.participants
        )

        # Continue with workflow...
```

### 3. Persona-Based Responses

```python
class PersonaManager:
    def get_ceo_response(self, situation: str, context: dict) -> str:
        return load_prompt(
            "persona.ceo.strategic_thinking",
            decision_type="strategic",
            situation_description=situation,
            **context
        )
```

## 📊 Monitoring and Analytics

The system tracks prompt usage and provides analytics:

```python
from shared.prompts import PromptRegistry

registry = PromptRegistry()

# Get usage statistics
stats = registry.get_usage_stats()
print(f"Total prompts: {stats['total_prompts']}")
print(f"Most used: {stats['most_used_prompt']}")

# List prompts by category
agent_prompts = registry.list_prompts(category="agent")
workflow_prompts = registry.list_prompts(category="workflow")

# Search prompts
search_results = registry.search_prompts("document analysis")
```

## 🧪 Testing and Validation

### Validation Features

- **YAML Syntax**: Validates YAML structure and syntax
- **Schema Validation**: Ensures all required fields are present
- **Template Syntax**: Validates Jinja2 template syntax
- **Variable References**: Checks template variables are defined
- **Duplicate IDs**: Prevents duplicate prompt identifiers

### Testing Prompts

```python
# Test prompt rendering
from shared.prompts.examples import validate_all_prompts

validation_results = validate_all_prompts()
for prompt_id, errors in validation_results.items():
    if errors:
        print(f"Validation errors in {prompt_id}: {errors}")
```

## 🚀 Best Practices

### 1. Prompt Organization

- **Use descriptive IDs**: `agent.action_name` or `workflow.step_name`
- **Consistent categorization**: Organize by function (agent/workflow/persona/common)
- **Semantic versioning**: Update versions when making changes
- **Comprehensive metadata**: Include descriptions, tags, and model preferences

### 2. Template Design

- **Clear variable names**: Use descriptive variable names
- **Required vs optional**: Clearly mark required variables
- **Default values**: Provide sensible defaults for optional variables
- **Examples**: Include usage examples for complex prompts

### 3. Integration

- **Error handling**: Always handle template rendering errors
- **Fallback prompts**: Provide simple fallbacks for critical functions
- **Context management**: Use RenderContext for complex scenarios
- **Caching**: Leverage the registry's caching for performance

### 4. Maintenance

- **Regular validation**: Run validation checks in CI/CD
- **Usage monitoring**: Track prompt usage to identify popular/unused prompts
- **Version management**: Keep old versions for backward compatibility
- **Documentation**: Maintain clear descriptions and examples

## 🔄 Migration and Deployment

### Adding New Prompts

1. Create YAML file in appropriate category directory
2. Define metadata, template, and variables
3. Validate with CLI: `python -m shared.prompts.cli validate`
4. Test rendering: `python -m shared.prompts.cli test your.prompt.id`
5. Deploy and monitor usage

### Updating Existing Prompts

1. Update version number in metadata
2. Modify template while maintaining backward compatibility
3. Test with existing variable sets
4. Update documentation and examples
5. Deploy gradually with feature flags

## 📚 API Reference

### Core Functions

- `load_prompt(prompt_id, **variables)` - Load and render a prompt
- `get_prompt_template(prompt_id)` - Get template object
- `reload_prompts()` - Reload all prompts from files

### Classes

- `PromptRegistry` - Main prompt management class
- `PromptLoader` - YAML file loading and validation
- `TemplateEngine` - Jinja2 template rendering
- `RenderContext` - Context for template rendering

### Schemas

- `PromptDefinition` - Root prompt definition schema
- `PromptTemplate` - Individual template schema
- `PromptMetadata` - Metadata schema
- `PromptVariable` - Variable definition schema

This system provides a robust foundation for managing AI prompts across your entire application, ensuring consistency, maintainability, and type safety.
