"""
Prompt and template management system for LLM interactions.

Provides centralized, type-safe, and versioned prompt management
with Jinja2 templating support and role-based organization.
"""

from .loader import PromptLoader
from .registry import PromptRegistry
from .schemas.base import (
    PromptDefinition,
    PromptMetadata,
    PromptTemplate,
    PromptVariable,
    RenderContext,
)
from .templates import TemplateEngine

# Global instances
_loader = PromptLoader()
_registry = PromptRegistry()
_template_engine = TemplateEngine()


# Convenience functions
def load_prompt(prompt_id: str, **kwargs) -> str:
    """Load and render a prompt by ID with provided variables."""
    return _registry.get_rendered_prompt(prompt_id, **kwargs)


def get_prompt_template(prompt_id: str) -> PromptTemplate:
    """Get a prompt template by ID."""
    return _registry.get_template(prompt_id)


def reload_prompts() -> None:
    """Reload all prompts from definitions."""
    _registry.reload()


__all__ = [
    "PromptDefinition",
    "PromptLoader",
    "PromptMetadata",
    "PromptRegistry",
    "PromptTemplate",
    "PromptVariable",
    "RenderContext",
    "TemplateEngine",
    "get_prompt_template",
    "load_prompt",
    "reload_prompts",
]
