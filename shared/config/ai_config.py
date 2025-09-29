"""
AI service configuration for OpenRouter and other AI providers.

Manages API keys, model selection, rate limiting, and cost control
for AI-powered activities in the system.
"""

from dataclasses import dataclass, field
import os


@dataclass
class ModelConfig:
    """Configuration for a specific AI model."""

    name: str
    provider: str  # "openrouter", "openai", "anthropic", etc.
    max_tokens: int = 4096
    temperature: float = 0.7
    cost_per_1k_tokens: float = 0.0
    context_window: int = 4096
    supports_function_calling: bool = False
    supports_vision: bool = False


@dataclass
class AIConfig:
    """
    Comprehensive AI service configuration.

    Manages multiple AI providers, model selection, rate limiting,
    and cost control across the system.
    """

    # Environment
    environment: str = "local"

    # Primary provider (OpenRouter recommended)
    primary_provider: str = "openrouter"
    openrouter_api_key: str | None = None
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    # Fallback providers
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    google_api_key: str | None = None

    # Model configurations
    default_model: str = "anthropic/claude-3-sonnet"
    available_models: dict[str, ModelConfig] = field(default_factory=dict)

    # Rate limiting and cost control
    max_requests_per_minute: int = 60
    max_tokens_per_request: int = 4096
    daily_cost_limit_usd: float = 100.0
    monthly_cost_limit_usd: float = 1000.0

    # Request configuration
    default_temperature: float = 0.7
    default_max_tokens: int = 1000
    default_timeout_seconds: int = 30
    max_retries: int = 3
    retry_delay_seconds: int = 1

    # Feature flags
    enable_function_calling: bool = True
    enable_vision: bool = False
    enable_cost_tracking: bool = True

    def __post_init__(self):
        """Initialize model configurations and load API keys."""
        self._load_api_keys()
        self._setup_default_models()

    def _load_api_keys(self) -> None:
        """Load API keys from environment variables."""
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY", self.openrouter_api_key)
        self.openai_api_key = os.getenv("OPENAI_API_KEY", self.openai_api_key)
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", self.anthropic_api_key)
        self.google_api_key = os.getenv("GOOGLE_API_KEY", self.google_api_key)

    def _setup_default_models(self) -> None:
        """Setup default model configurations."""
        self.available_models = {
            # Anthropic models (via OpenRouter)
            "anthropic/claude-3-sonnet": ModelConfig(
                name="anthropic/claude-3-sonnet",
                provider="openrouter",
                max_tokens=4096,
                temperature=0.7,
                cost_per_1k_tokens=0.003,
                context_window=200000,
                supports_function_calling=True,
                supports_vision=True,
            ),
            "anthropic/claude-3-haiku": ModelConfig(
                name="anthropic/claude-3-haiku",
                provider="openrouter",
                max_tokens=4096,
                temperature=0.7,
                cost_per_1k_tokens=0.00025,
                context_window=200000,
                supports_function_calling=True,
                supports_vision=True,
            ),
            # OpenAI models (via OpenRouter)
            "openai/gpt-4": ModelConfig(
                name="openai/gpt-4",
                provider="openrouter",
                max_tokens=4096,
                temperature=0.7,
                cost_per_1k_tokens=0.03,
                context_window=8192,
                supports_function_calling=True,
                supports_vision=False,
            ),
            "openai/gpt-3.5-turbo": ModelConfig(
                name="openai/gpt-3.5-turbo",
                provider="openrouter",
                max_tokens=4096,
                temperature=0.7,
                cost_per_1k_tokens=0.0015,
                context_window=16384,
                supports_function_calling=True,
                supports_vision=False,
            ),
            # Google models (via OpenRouter)
            "google/gemini-pro": ModelConfig(
                name="google/gemini-pro",
                provider="openrouter",
                max_tokens=2048,
                temperature=0.7,
                cost_per_1k_tokens=0.0005,
                context_window=30720,
                supports_function_calling=True,
                supports_vision=False,
            ),
            # Open source models (via OpenRouter)
            "meta-llama/llama-2-70b-chat": ModelConfig(
                name="meta-llama/llama-2-70b-chat",
                provider="openrouter",
                max_tokens=4096,
                temperature=0.7,
                cost_per_1k_tokens=0.0007,
                context_window=4096,
                supports_function_calling=False,
                supports_vision=False,
            ),
        }

    def get_model_config(self, model_name: str | None = None) -> ModelConfig:
        """Get configuration for the specified model."""
        model_name = model_name or self.default_model

        if model_name not in self.available_models:
            raise ValueError(f"Unknown model: {model_name}")

        return self.available_models[model_name]

    def get_api_key(self, provider: str) -> str | None:
        """Get API key for the specified provider."""
        if provider == "openrouter":
            return self.openrouter_api_key
        elif provider == "openai":
            return self.openai_api_key
        elif provider == "anthropic":
            return self.anthropic_api_key
        elif provider == "google":
            return self.google_api_key
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def get_models_by_capability(
        self,
        supports_function_calling: bool | None = None,
        supports_vision: bool | None = None,
        max_cost_per_1k_tokens: float | None = None,
    ) -> list[ModelConfig]:
        """Get models filtered by capabilities."""
        models = list(self.available_models.values())

        if supports_function_calling is not None:
            models = [m for m in models if m.supports_function_calling == supports_function_calling]

        if supports_vision is not None:
            models = [m for m in models if m.supports_vision == supports_vision]

        if max_cost_per_1k_tokens is not None:
            models = [m for m in models if m.cost_per_1k_tokens <= max_cost_per_1k_tokens]

        return sorted(models, key=lambda m: m.cost_per_1k_tokens)

    def get_best_model_for_task(
        self, task_type: str, max_cost_per_1k_tokens: float | None = None
    ) -> ModelConfig:
        """Get the best model for a specific task type."""
        task_requirements = {
            "document_analysis": {
                "supports_function_calling": False,
                "supports_vision": False,
                "prefer_accuracy": True,
            },
            "consensus_building": {
                "supports_function_calling": True,
                "supports_vision": False,
                "prefer_accuracy": True,
            },
            "research": {
                "supports_function_calling": True,
                "supports_vision": False,
                "prefer_capability": True,
            },
            "quick_summary": {
                "supports_function_calling": False,
                "supports_vision": False,
                "prefer_cost": True,
            },
        }

        requirements = task_requirements.get(task_type, {})

        # Get candidate models
        candidates = self.get_models_by_capability(
            supports_function_calling=requirements.get("supports_function_calling"),
            supports_vision=requirements.get("supports_vision"),
            max_cost_per_1k_tokens=max_cost_per_1k_tokens,
        )

        if not candidates:
            return self.get_model_config()  # Fallback to default

        # Select based on preference
        if requirements.get("prefer_cost"):
            return min(candidates, key=lambda m: m.cost_per_1k_tokens)
        elif requirements.get("prefer_accuracy"):
            # Prefer Claude models for accuracy
            claude_models = [m for m in candidates if "claude" in m.name.lower()]
            if claude_models:
                return max(
                    claude_models, key=lambda m: m.cost_per_1k_tokens
                )  # Higher cost usually means better model
        elif requirements.get("prefer_capability"):
            # Prefer models with larger context windows
            return max(candidates, key=lambda m: m.context_window)

        return candidates[0]

    def estimate_cost(self, model_name: str, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for a request."""
        model_config = self.get_model_config(model_name)
        total_tokens = input_tokens + output_tokens
        return (total_tokens / 1000) * model_config.cost_per_1k_tokens

    def validate(self) -> None:
        """Validate the AI configuration."""
        # Check that at least one API key is configured
        if not any(
            [
                self.openrouter_api_key,
                self.openai_api_key,
                self.anthropic_api_key,
                self.google_api_key,
            ]
        ):
            raise ValueError("At least one AI provider API key must be configured")

        # Validate primary provider has API key
        if self.primary_provider == "openrouter" and not self.openrouter_api_key:
            raise ValueError(
                "OpenRouter API key is required when using OpenRouter as primary provider"
            )

        # Validate rate limits
        if self.max_requests_per_minute <= 0:
            raise ValueError("max_requests_per_minute must be positive")

        if self.daily_cost_limit_usd < 0:
            raise ValueError("daily_cost_limit_usd must be non-negative")

        if self.monthly_cost_limit_usd < 0:
            raise ValueError("monthly_cost_limit_usd must be non-negative")

        # Validate default model exists
        if self.default_model not in self.available_models:
            raise ValueError(f"Default model '{self.default_model}' not found in available models")

        # Validate timeout and retry settings
        if self.default_timeout_seconds <= 0:
            raise ValueError("default_timeout_seconds must be positive")

        if self.max_retries < 0:
            raise ValueError("max_retries must be non-negative")

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization (excluding sensitive data)."""
        return {
            "environment": self.environment,
            "primary_provider": self.primary_provider,
            "default_model": self.default_model,
            "available_models": [model.name for model in self.available_models.values()],
            "rate_limits": {
                "max_requests_per_minute": self.max_requests_per_minute,
                "max_tokens_per_request": self.max_tokens_per_request,
                "daily_cost_limit_usd": self.daily_cost_limit_usd,
            },
            "features": {
                "function_calling": self.enable_function_calling,
                "vision": self.enable_vision,
                "cost_tracking": self.enable_cost_tracking,
            },
        }
