"""Factory function for initializing LLM models."""

from typing import Optional, Any
from langchain.chat_models import init_chat_model


# Model name mappings - friendly names to provider-specific formats
MODEL_REGISTRY = {
    # OpenAI models
    "gpt-4o-mini": "openai:gpt-4o-mini",
    "gpt-4o": "openai:gpt-4o",
    "gpt-4": "openai:gpt-4",
    "gpt-3.5": "openai:gpt-3.5-turbo",

    # Anthropic models
    "claude-sonnet": "anthropic:claude-sonnet-4-5-20250929",
    "claude-opus": "anthropic:claude-3-opus-20240229",
    "claude-haiku": "anthropic:claude-haiku-4-5-20251001",

    # Aliases for convenience
    "default": "openai:gpt-4o-mini",
    "fast": "openai:gpt-4o-mini",
    "smart": "anthropic:claude-sonnet-4-5-20250929",
    "reliable":"anthropic:claude-haiku-4-5-20251001",
}


def get_model(
    name: str = "default",
    **kwargs: Any
) -> Any:
    """
    Factory function to initialize LLM models by name.

    Args:
        name: Model name or alias. Can be:
            - A friendly name from MODEL_REGISTRY (e.g., "gpt-4o-mini", "claude-sonnet")
            - A direct provider:model format (e.g., "openai:gpt-4", "anthropic:claude-3-opus")
        temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative). Default: 0.0
        **kwargs: Additional parameters passed to init_chat_model

    Returns:
        Initialized chat model instance

    Raises:
        ValueError: If model name is not recognized
        ImportError: If required API key is missing in environment

    Examples:
        >>> # Using friendly names
        >>> model = get_model("gpt-4o-mini")
        >>> model = get_model("claude-sonnet")

        >>> # Using provider:model format
        >>> model = get_model("openai:gpt-4o")

        >>> # Using aliases
        >>> model = get_model("fast")  # Uses gpt-4o-mini
        >>> model = get_model("smart")  # Uses claude-sonnet
    """
    temperature: float = 0.0
    # Look up model name in registry, or use as-is if not found
    model_string = MODEL_REGISTRY.get(name, name)

    # If still no colon (not in provider:model format), it's an unknown name
    if ":" not in model_string:
        available = ", ".join(sorted(MODEL_REGISTRY.keys()))
        raise ValueError(
            f"Unknown model name: '{name}'. "
            f"Available models: {available}. "
            f"Or use provider:model format (e.g., 'openai:gpt-4')"
        )

    try:
        # Use LangChain's init_chat_model for consistent initialization
        return init_chat_model(
            model=model_string,
            temperature=temperature,
            **kwargs
        )
    except Exception as e:
        # Provide helpful error message for missing API keys
        provider = model_string.split(":")[0]
        key_name = f"{provider.upper()}_API_KEY"

        error_msg = (
            f"Failed to initialize model '{model_string}'. "
            f"Ensure {key_name} is set in your .env file. "
            f"Original error: {str(e)}"
        )
        raise ImportError(error_msg) from e


def list_available_models() -> dict:
    """
    Get all available model names and their mappings.

    Returns:
        Dictionary mapping friendly names to provider:model strings
    """
    return MODEL_REGISTRY.copy()


def add_model(name: str, provider_model: str) -> None:
    """
    Dynamically add a new model to the registry.

    Args:
        name: Friendly name for the model
        provider_model: Provider:model string (e.g., "openai:gpt-4")

    Raises:
        ValueError: If provider_model is not in provider:model format
    """
    if ":" not in provider_model:
        raise ValueError(
            f"provider_model must be in 'provider:model' format, got: {provider_model}"
        )
    MODEL_REGISTRY[name] = provider_model
