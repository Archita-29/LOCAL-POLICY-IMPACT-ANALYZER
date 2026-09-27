"""Optional inference seam for the teammate's future trained model.

The API serves persisted results and never invents a fallback sentiment score.
Replace ``get_model_provider`` with the trained model adapter when it is ready.
"""

from typing import Any, Protocol


class ModelProvider(Protocol):
    def analyze(self, text: str) -> dict[str, Any]: ...


def get_model_provider() -> ModelProvider | None:
    """Return the configured inference provider, or None until one is wired in."""
    return None
