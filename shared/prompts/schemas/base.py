"""
Base schemas for prompt definitions and metadata.

Provides Pydantic models for type-safe prompt management
and validation of prompt definitions.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class PromptRole(str, Enum):
    """Roles for different types of prompts."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"


class PromptCategory(str, Enum):
    """Categories for organizing prompts."""

    AGENT = "agent"
    WORKFLOW = "workflow"
    PERSONA = "persona"
    COMMON = "common"
    ERROR_HANDLING = "error_handling"
    FORMATTING = "formatting"


class ModelProvider(str, Enum):
    """Supported AI model providers."""

    OPENROUTER = "openrouter"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"


class PromptVariable(BaseModel):
    """Definition of a prompt template variable."""

    name: str = Field(description="Variable name")
    type: str = Field(description="Variable type (string, int, bool, list, dict)")
    description: str = Field(description="Variable description")
    required: bool = Field(default=True, description="Whether variable is required")
    default: Any = Field(default=None, description="Default value if not required")
    examples: list[str] = Field(default_factory=list, description="Example values")


class PromptMetadata(BaseModel):
    """Metadata for prompt definitions."""

    id: str = Field(description="Unique prompt identifier")
    name: str = Field(description="Human-readable prompt name")
    description: str = Field(description="Prompt description and purpose")
    category: PromptCategory = Field(description="Prompt category")
    version: str = Field(default="1.0.0", description="Semantic version")
    author: str = Field(default="antifragile-flow", description="Prompt author")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    tags: list[str] = Field(default_factory=list, description="Searchable tags")

    # Model preferences
    preferred_models: list[str] = Field(default_factory=list, description="Preferred model names")
    min_context_length: int = Field(default=1000, description="Minimum context length required")
    max_tokens: int = Field(default=1000, description="Recommended max tokens for response")
    temperature: float = Field(default=0.7, description="Recommended temperature")

    # Usage tracking
    usage_count: int = Field(default=0, description="Number of times used")
    last_used: datetime | None = Field(default=None, description="Last usage timestamp")


class PromptTemplate(BaseModel):
    """Complete prompt template definition."""

    metadata: PromptMetadata = Field(description="Prompt metadata")
    role: PromptRole = Field(description="Message role")
    template: str = Field(description="Jinja2 template string")
    variables: list[PromptVariable] = Field(default_factory=list, description="Template variables")
    examples: list[dict[str, Any]] = Field(default_factory=list, description="Usage examples")

    # Advanced features
    system_prompt: str | None = Field(default=None, description="Optional system prompt")
    follow_up_prompts: list[str] = Field(default_factory=list, description="Related prompt IDs")
    conditional_logic: dict[str, Any] = Field(
        default_factory=dict, description="Conditional rendering rules"
    )


class RenderContext(BaseModel):
    """Context for rendering prompt templates."""

    variables: dict[str, Any] = Field(default_factory=dict, description="Template variables")
    user_id: str | None = Field(default=None, description="User identifier")
    session_id: str | None = Field(default=None, description="Session identifier")
    conversation_history: list[dict[str, str]] = Field(
        default_factory=list, description="Previous messages"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional context metadata"
    )


class PromptDefinition(BaseModel):
    """Root prompt definition from YAML files."""

    version: str = Field(description="Definition format version")
    prompts: list[PromptTemplate] = Field(description="List of prompt templates")

    class Config:
        extra = "forbid"  # Don't allow undefined fields


class PromptValidationError(Exception):
    """Raised when prompt validation fails."""

    pass


class TemplateRenderError(Exception):
    """Raised when template rendering fails."""

    pass
