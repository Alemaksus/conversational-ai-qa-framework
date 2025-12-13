"""Type definitions for the rules engine."""

from dataclasses import dataclass
from typing import Callable


@dataclass
class Response:
    """Represents a conversational response for validation."""

    text: str
    latency_ms: int | None = None
    status_code: int | None = None
    meta: dict | None = None


@dataclass
class Rule:
    """Represents a validation rule."""

    name: str
    params: dict

    def apply(self, response: Response) -> tuple[bool, str]:
        """Apply the rule to a response.
        
        Returns:
            Tuple of (passed: bool, reason_if_failed: str)
        """
        # This will be implemented by validators
        raise NotImplementedError("Rule.apply() must be implemented by validators")

