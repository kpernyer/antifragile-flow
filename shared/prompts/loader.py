"""
Prompt loader for reading and validating YAML prompt definitions.

Handles loading prompt definitions from YAML files with validation
and error handling.
"""

from collections.abc import Generator
import logging
from pathlib import Path

from pydantic import ValidationError
import yaml

from .schemas.base import PromptDefinition, PromptTemplate, PromptValidationError

logger = logging.getLogger(__name__)


class PromptLoader:
    """Loads and validates prompt definitions from YAML files."""

    def __init__(self, prompts_dir: Path | None = None):
        """Initialize the prompt loader.

        Args:
            prompts_dir: Directory containing prompt definitions.
                        Defaults to shared/prompts/definitions/
        """
        if prompts_dir is None:
            # Default to definitions directory relative to this file
            current_dir = Path(__file__).parent
            prompts_dir = current_dir / "definitions"

        self.prompts_dir = Path(prompts_dir)
        if not self.prompts_dir.exists():
            logger.warning(f"Prompts directory does not exist: {self.prompts_dir}")

    def load_all_prompts(self) -> Generator[PromptDefinition, None, None]:
        """Load all prompt definitions from YAML files.

        Yields:
            PromptDefinition objects from all YAML files found.

        Raises:
            PromptValidationError: If validation fails for any prompt.
        """
        if not self.prompts_dir.exists():
            logger.warning(f"Prompts directory not found: {self.prompts_dir}")
            return

        yaml_files = list(self.prompts_dir.rglob("*.yaml")) + list(self.prompts_dir.rglob("*.yml"))

        if not yaml_files:
            logger.warning(f"No YAML files found in {self.prompts_dir}")
            return

        for yaml_file in yaml_files:
            try:
                definition = self.load_prompt_file(yaml_file)
                if definition:
                    yield definition
            except Exception as e:
                logger.error(f"Failed to load prompt file {yaml_file}: {e}")
                continue

    def load_prompt_file(self, file_path: Path) -> PromptDefinition | None:
        """Load a single prompt definition file.

        Args:
            file_path: Path to the YAML file.

        Returns:
            PromptDefinition object or None if loading fails.

        Raises:
            PromptValidationError: If validation fails.
        """
        try:
            logger.debug(f"Loading prompt file: {file_path}")

            with file_path.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if not data:
                logger.warning(f"Empty prompt file: {file_path}")
                return None

            # Validate against schema
            definition = PromptDefinition(**data)

            # Additional validation
            self._validate_prompt_definition(definition, file_path)

            logger.debug(f"Successfully loaded {len(definition.prompts)} prompts from {file_path}")
            return definition

        except yaml.YAMLError as e:
            raise PromptValidationError(f"YAML parsing error in {file_path}: {e}") from e
        except ValidationError as e:
            raise PromptValidationError(f"Validation error in {file_path}: {e}") from e
        except Exception as e:
            raise PromptValidationError(f"Unexpected error loading {file_path}: {e}") from e

    def _validate_prompt_definition(self, definition: PromptDefinition, file_path: Path) -> None:
        """Additional validation for prompt definitions.

        Args:
            definition: The prompt definition to validate.
            file_path: Path to the source file for error reporting.

        Raises:
            PromptValidationError: If validation fails.
        """
        # Check for duplicate prompt IDs within the file
        prompt_ids = [prompt.metadata.id for prompt in definition.prompts]
        duplicates = {pid for pid in prompt_ids if prompt_ids.count(pid) > 1}

        if duplicates:
            raise PromptValidationError(
                f"Duplicate prompt IDs in {file_path}: {', '.join(duplicates)}"
            )

        # Validate template variables
        for prompt in definition.prompts:
            self._validate_prompt_template(prompt, file_path)

    def _validate_prompt_template(self, prompt_template, file_path: Path) -> None:
        """Validate individual prompt template.

        Args:
            prompt_template: The prompt template to validate.
            file_path: Path to the source file for error reporting.

        Raises:
            PromptValidationError: If validation fails.
        """
        # Check that template uses only defined variables
        import re

        template = prompt_template.template
        if prompt_template.system_prompt:
            template += " " + prompt_template.system_prompt

        # Find all template variables (Jinja2 format)
        template_vars = set(re.findall(r"\{\{\s*(\w+)(?:\.[^}]*)?\s*\}\}", template))
        defined_vars = {var.name for var in prompt_template.variables}

        # Allow some built-in variables
        allowed_builtins = {"now", "today", "user_id", "session_id"}
        template_vars -= allowed_builtins

        undefined_vars = template_vars - defined_vars
        if undefined_vars:
            logger.warning(
                f"Undefined variables in prompt {prompt_template.metadata.id} "
                f"from {file_path}: {', '.join(undefined_vars)}"
            )

        # Check variable types
        for var in prompt_template.variables:
            if var.type not in ["string", "int", "float", "bool", "list", "dict", "any"]:
                logger.warning(
                    f"Unknown variable type '{var.type}' for variable '{var.name}' "
                    f"in prompt {prompt_template.metadata.id} from {file_path}"
                )

    def get_prompt_files(self) -> list[Path]:
        """Get list of all YAML files in the prompts directory.

        Returns:
            List of Path objects for YAML files.
        """
        if not self.prompts_dir.exists():
            return []

        return list(self.prompts_dir.rglob("*.yaml")) + list(self.prompts_dir.rglob("*.yml"))

    def validate_all_prompts(self) -> dict[str, list[str]]:
        """Validate all prompt files and return validation results.

        Returns:
            Dictionary mapping file paths to lists of validation errors.
            Empty list means no errors.
        """
        results = {}

        for yaml_file in self.get_prompt_files():
            errors = []
            try:
                self.load_prompt_file(yaml_file)
            except PromptValidationError as e:
                errors.append(str(e))
            except Exception as e:
                errors.append(f"Unexpected error: {e}")

            results[str(yaml_file)] = errors

        return results

    def find_prompt_by_id(self, prompt_id: str) -> PromptTemplate | None:
        """Find a specific prompt by ID without validating all prompts.

        Args:
            prompt_id: The prompt ID to search for.

        Returns:
            The prompt template if found, None otherwise.
        """
        if not self.prompts_dir.exists():
            return None

        for yaml_file in self.get_prompt_files():
            try:
                logger.debug(f"Searching for '{prompt_id}' in: {yaml_file}")

                with yaml_file.open("r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)

                if not data or "prompts" not in data:
                    continue

                # Only validate the structure we need, skip variable validation
                definition = PromptDefinition.model_validate(data)

                # Search through prompts in this file
                for prompt_template in definition.prompts:
                    if prompt_template.metadata.id == prompt_id:
                        logger.debug(f"Found prompt '{prompt_id}' in file: {yaml_file}")
                        return prompt_template

            except Exception as e:
                # Skip files with errors when doing targeted search
                logger.debug(f"Skipping file {yaml_file} during search: {e}")
                continue

        logger.debug(f"Prompt '{prompt_id}' not found in any file")
        return None
