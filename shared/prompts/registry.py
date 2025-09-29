"""
Prompt registry for caching and managing prompt templates.

Provides centralized access to prompts with caching, usage tracking,
and template rendering capabilities.
"""

from datetime import datetime
import logging
from typing import Any

from .loader import PromptLoader
from .schemas.base import PromptTemplate, RenderContext, TemplateRenderError
from .templates import TemplateEngine

logger = logging.getLogger(__name__)


class PromptRegistry:
    """Central registry for prompt templates with caching and rendering."""

    def __init__(self, prompts_dir: str | None = None):
        """Initialize the prompt registry.

        Args:
            prompts_dir: Directory containing prompt definitions.
        """
        self.loader = PromptLoader(prompts_dir)
        self.template_engine = TemplateEngine()
        self._templates: dict[str, PromptTemplate] = {}
        self._cache_timestamp: datetime | None = None
        self._loaded = False

    def load_all_prompts(self) -> None:
        """Load all prompts from definitions into the registry."""
        logger.info("Loading all prompts into registry...")
        self._templates.clear()

        for definition in self.loader.load_all_prompts():
            for prompt_template in definition.prompts:
                prompt_id = prompt_template.metadata.id

                if prompt_id in self._templates:
                    logger.warning(
                        f"Duplicate prompt ID found: {prompt_id}. Overwriting previous definition."
                    )

                self._templates[prompt_id] = prompt_template
                logger.debug(f"Loaded prompt: {prompt_id}")

        self._cache_timestamp = datetime.now()
        self._loaded = True
        logger.info(f"Loaded {len(self._templates)} prompts into registry")

    def _load_specific_prompt(self, prompt_id: str) -> None:
        """Load a specific prompt by searching for its ID in YAML files.

        Args:
            prompt_id: The prompt ID to search for and load.
        """
        logger.debug(f"Searching for specific prompt: {prompt_id}")

        # Use targeted loading to avoid validation errors from other prompts
        prompt_template = self.loader.find_prompt_by_id(prompt_id)
        if prompt_template:
            self._templates[prompt_id] = prompt_template
            logger.debug(f"Loaded specific prompt: {prompt_id}")
        else:
            logger.debug(f"Specific prompt not found: {prompt_id}")

    def get_template(self, prompt_id: str) -> PromptTemplate:
        """Get a prompt template by ID.

        Args:
            prompt_id: The unique prompt identifier.

        Returns:
            The prompt template.

        Raises:
            KeyError: If prompt ID is not found.
        """
        # Try to load specific prompt first if not already loaded
        if prompt_id not in self._templates:
            self._load_specific_prompt(prompt_id)

        # If still not found after specific loading, try loading all
        if prompt_id not in self._templates and not self._loaded:
            self.load_all_prompts()

        if prompt_id not in self._templates:
            available_ids = list(self._templates.keys())
            raise KeyError(
                f"Prompt '{prompt_id}' not found. "
                f"Available prompts: {', '.join(available_ids[:10])}{'...' if len(available_ids) > 10 else ''}"
            )

        template = self._templates[prompt_id]

        # Update usage tracking
        template.metadata.usage_count += 1
        template.metadata.last_used = datetime.now()

        return template

    def get_rendered_prompt(
        self, prompt_id: str, context: RenderContext | None = None, **variables
    ) -> str:
        """Get a rendered prompt string.

        Args:
            prompt_id: The unique prompt identifier.
            context: Rendering context. If None, creates from variables.
            **variables: Template variables to render.

        Returns:
            Rendered prompt string.

        Raises:
            KeyError: If prompt ID is not found.
            TemplateRenderError: If rendering fails.
        """
        template = self.get_template(prompt_id)

        if context is None:
            context = RenderContext(variables=variables)
        else:
            # Merge provided variables with context variables
            context.variables.update(variables)

        # Validate required variables
        self._validate_required_variables(template, context.variables)

        # Render the main template
        rendered_content = self.template_engine.render_template(template.template, context)

        # If there's a system prompt, render it separately
        if template.system_prompt:
            system_content = self.template_engine.render_template(template.system_prompt, context)
            # For system prompts, we might want to format differently
            return f"SYSTEM: {system_content}\n\nUSER: {rendered_content}"

        return rendered_content

    def get_system_and_user_prompts(
        self, prompt_id: str, context: RenderContext | None = None, **variables
    ) -> tuple[str | None, str]:
        """Get system and user prompts separately.

        Args:
            prompt_id: The unique prompt identifier.
            context: Rendering context.
            **variables: Template variables.

        Returns:
            Tuple of (system_prompt, user_prompt). System prompt may be None.
        """
        template = self.get_template(prompt_id)

        if context is None:
            context = RenderContext(variables=variables)
        else:
            context.variables.update(variables)

        self._validate_required_variables(template, context.variables)

        user_prompt = self.template_engine.render_template(template.template, context)

        system_prompt = None
        if template.system_prompt:
            system_prompt = self.template_engine.render_template(template.system_prompt, context)

        return system_prompt, user_prompt

    def list_prompts(
        self, category: str | None = None, tags: list[str] | None = None
    ) -> list[PromptTemplate]:
        """List available prompts with optional filtering.

        Args:
            category: Filter by category.
            tags: Filter by tags (prompts must have all specified tags).

        Returns:
            List of matching prompt templates.
        """
        if not self._loaded:
            self.load_all_prompts()

        prompts = list(self._templates.values())

        if category:
            prompts = [p for p in prompts if p.metadata.category == category]

        if tags:
            prompts = [p for p in prompts if all(tag in p.metadata.tags for tag in tags)]

        return sorted(prompts, key=lambda p: p.metadata.name)

    def search_prompts(self, query: str) -> list[PromptTemplate]:
        """Search prompts by name, description, or tags.

        Args:
            query: Search query string.

        Returns:
            List of matching prompt templates.
        """
        if not self._loaded:
            self.load_all_prompts()

        query_lower = query.lower()
        matches = []

        for template in self._templates.values():
            # Search in name, description, and tags
            searchable_text = " ".join(
                [
                    template.metadata.name,
                    template.metadata.description,
                    " ".join(template.metadata.tags),
                ]
            ).lower()

            if query_lower in searchable_text:
                matches.append(template)

        return sorted(matches, key=lambda p: p.metadata.name)

    def get_usage_stats(self) -> dict[str, Any]:
        """Get usage statistics for all prompts.

        Returns:
            Dictionary with usage statistics.
        """
        if not self._loaded:
            self.load_all_prompts()

        total_prompts = len(self._templates)
        total_usage = sum(t.metadata.usage_count for t in self._templates.values())
        used_prompts = sum(1 for t in self._templates.values() if t.metadata.usage_count > 0)

        most_used = max(
            self._templates.values(), key=lambda t: t.metadata.usage_count, default=None
        )

        return {
            "total_prompts": total_prompts,
            "total_usage": total_usage,
            "used_prompts": used_prompts,
            "unused_prompts": total_prompts - used_prompts,
            "most_used_prompt": most_used.metadata.id if most_used else None,
            "most_used_count": most_used.metadata.usage_count if most_used else 0,
            "cache_timestamp": self._cache_timestamp,
        }

    def reload(self) -> None:
        """Reload all prompts from definitions."""
        logger.info("Reloading prompts from definitions...")
        self.load_all_prompts()

    def validate_all_templates(self) -> dict[str, list[str]]:
        """Validate all loaded templates.

        Returns:
            Dictionary mapping prompt IDs to lists of validation errors.
        """
        if not self._loaded:
            self.load_all_prompts()

        results = {}

        for prompt_id, template in self._templates.items():
            errors = []

            # Validate template syntax
            if not self.template_engine.validate_template(template.template):
                errors.append("Invalid template syntax")

            if template.system_prompt and not self.template_engine.validate_template(
                template.system_prompt
            ):
                errors.append("Invalid system prompt syntax")

            # Check for unused variables
            template_vars = self.template_engine.get_template_variables(template.template)
            if template.system_prompt:
                template_vars.update(
                    self.template_engine.get_template_variables(template.system_prompt)
                )

            defined_vars = {var.name for var in template.variables}
            unused_vars = defined_vars - template_vars

            if unused_vars:
                errors.append(f"Unused variables: {', '.join(unused_vars)}")

            results[prompt_id] = errors

        return results

    def _validate_required_variables(
        self, template: PromptTemplate, variables: dict[str, Any]
    ) -> None:
        """Validate that all required variables are provided.

        Args:
            template: The prompt template.
            variables: Provided variables.

        Raises:
            TemplateRenderError: If required variables are missing.
        """
        required_vars = {var.name for var in template.variables if var.required}
        provided_vars = set(variables.keys())
        missing_vars = required_vars - provided_vars

        if missing_vars:
            raise TemplateRenderError(
                f"Missing required variables for prompt '{template.metadata.id}': {', '.join(missing_vars)}"
            )
