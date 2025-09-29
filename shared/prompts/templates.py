"""
Template rendering engine for prompt templates.

Handles Jinja2 template rendering with custom filters and functions
for prompt generation.
"""

from datetime import datetime
import logging
from typing import Any

from jinja2 import Environment, Template, TemplateError, select_autoescape

from .schemas.base import RenderContext, TemplateRenderError

logger = logging.getLogger(__name__)


class TemplateEngine:
    """Template rendering engine with custom filters and functions."""

    def __init__(self):
        """Initialize the template engine with custom environment."""
        self.env = Environment(
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Register custom filters and functions
        self._register_custom_filters()
        self._register_custom_functions()

    def render_template(
        self, template_string: str, context: RenderContext, **additional_vars
    ) -> str:
        """Render a template string with the provided context.

        Args:
            template_string: The Jinja2 template string.
            context: Rendering context with variables.
            **additional_vars: Additional variables to include.

        Returns:
            Rendered template string.

        Raises:
            TemplateRenderError: If rendering fails.
        """
        try:
            template = self.env.from_string(template_string)

            # Combine all variables
            render_vars = {
                **context.variables,
                **additional_vars,
                "user_id": context.user_id,
                "session_id": context.session_id,
                "conversation_history": context.conversation_history,
                "metadata": context.metadata,
                "now": datetime.now(),
                "today": datetime.now().date(),
            }

            return template.render(**render_vars).strip()

        except TemplateError as e:
            raise TemplateRenderError(f"Template rendering failed: {e}") from e
        except Exception as e:
            raise TemplateRenderError(f"Unexpected error during rendering: {e}") from e

    def validate_template(self, template_string: str) -> bool:
        """Validate that a template string is syntactically correct.

        Args:
            template_string: The template string to validate.

        Returns:
            True if valid, False otherwise.
        """
        try:
            self.env.from_string(template_string)
            return True
        except TemplateError:
            return False
        except Exception:
            return False

    def get_template_variables(self, template_string: str) -> set[str]:
        """Extract variable names used in a template.

        Args:
            template_string: The template string to analyze.

        Returns:
            Set of variable names found in the template.
        """
        try:
            template = self.env.from_string(template_string)
            return template.environment.meta.find_undeclared_variables(
                template.environment.parse(template_string)
            )
        except Exception:
            return set()

    def _register_custom_filters(self) -> None:
        """Register custom Jinja2 filters."""

        def truncate_words(text: str, count: int = 50, suffix: str = "...") -> str:
            """Truncate text to specified word count."""
            if not isinstance(text, str):
                return str(text)

            words = text.split()
            if len(words) <= count:
                return text

            return " ".join(words[:count]) + suffix

        def format_persona(persona_name: str) -> str:
            """Format persona name for display."""
            return persona_name.replace("_", " ").title()

        def format_currency(amount: float, currency: str = "USD") -> str:
            """Format currency amounts."""
            return f"{currency} {amount:,.2f}"

        def format_list(items: list[Any], conjunction: str = "and") -> str:
            """Format a list of items with proper conjunction."""
            if not items:
                return ""
            if len(items) == 1:
                return str(items[0])
            if len(items) == 2:
                return f"{items[0]} {conjunction} {items[1]}"

            return f"{', '.join(str(item) for item in items[:-1])}, {conjunction} {items[-1]}"

        def indent_text(text: str, spaces: int = 2) -> str:
            """Indent all lines of text."""
            if not text:
                return text
            indent = " " * spaces
            return "\n".join(indent + line for line in text.split("\n"))

        def format_decision_context_filter(
            context: dict[str, Any],
            include_background: bool = True,
            include_constraints: bool = True,
        ) -> str:
            """Format decision-making context as a filter."""
            sections = []

            if include_background and "background" in context:
                sections.append(f"Background: {context['background']}")

            if "objective" in context:
                sections.append(f"Objective: {context['objective']}")

            if include_constraints and "constraints" in context:
                constraints = context["constraints"]
                if isinstance(constraints, list):
                    constraints_text = "; ".join(constraints)
                else:
                    constraints_text = str(constraints)
                sections.append(f"Constraints: {constraints_text}")

            if "deadline" in context:
                sections.append(f"Deadline: {context['deadline']}")

            return "\n".join(sections) if sections else "No context provided."

        # Register all filters
        self.env.filters["truncate_words"] = truncate_words
        self.env.filters["format_persona"] = format_persona
        self.env.filters["format_currency"] = format_currency
        self.env.filters["format_list"] = format_list
        self.env.filters["indent_text"] = indent_text
        self.env.filters["format_decision_context"] = format_decision_context_filter

    def _register_custom_functions(self) -> None:
        """Register custom Jinja2 global functions."""

        def format_timestamp(
            timestamp: datetime | None = None, format_str: str = "%Y-%m-%d %H:%M:%S"
        ) -> str:
            """Format timestamp with specified format."""
            if timestamp is None:
                timestamp = datetime.now()
            return timestamp.strftime(format_str)

        def get_conversation_summary(history: list[dict[str, str]], max_length: int = 200) -> str:
            """Generate a summary of conversation history."""
            if not history:
                return "No previous conversation."

            # Simple summary logic - in production, this might use an LLM
            total_messages = len(history)
            if total_messages == 1:
                return f"Previous message: {history[0].get('content', '')[:max_length]}..."

            return f"Conversation with {total_messages} messages. Latest: {history[-1].get('content', '')[:max_length]}..."

        def conditional_section(condition: Any, content: str) -> str:
            """Include content only if condition is truthy."""
            return content if condition else ""

        def format_decision_context(
            context: dict[str, Any],
            include_background: bool = True,
            include_constraints: bool = True,
        ) -> str:
            """Format decision-making context."""
            sections = []

            if include_background and "background" in context:
                sections.append(f"Background: {context['background']}")

            if "objective" in context:
                sections.append(f"Objective: {context['objective']}")

            if include_constraints and "constraints" in context:
                constraints = context["constraints"]
                if isinstance(constraints, list):
                    constraints_text = "; ".join(constraints)
                else:
                    constraints_text = str(constraints)
                sections.append(f"Constraints: {constraints_text}")

            if "deadline" in context:
                sections.append(f"Deadline: {context['deadline']}")

            return "\n".join(sections) if sections else "No context provided."

        # Register all global functions
        self.env.globals["format_timestamp"] = format_timestamp
        self.env.globals["get_conversation_summary"] = get_conversation_summary
        self.env.globals["conditional_section"] = conditional_section
        self.env.globals["format_decision_context"] = format_decision_context

    def create_template(self, template_string: str) -> Template:
        """Create a reusable template object.

        Args:
            template_string: The template string.

        Returns:
            Compiled Jinja2 template.

        Raises:
            TemplateRenderError: If template compilation fails.
        """
        try:
            return self.env.from_string(template_string)
        except TemplateError as e:
            raise TemplateRenderError(f"Template compilation failed: {e}") from e
