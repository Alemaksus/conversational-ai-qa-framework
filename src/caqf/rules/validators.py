"""Pure validator functions for response validation."""

import re
from typing import Callable

from caqf.rules.types import Response


def not_empty_text(response: Response) -> tuple[bool, str]:
    """Validate that response text is not empty.
    
    Returns:
        (passed: bool, reason_if_failed: str)
    """
    if response.text.strip():
        return True, ""
    return False, "Response text is empty"


def contains_text(expected_substring: str, response: Response) -> tuple[bool, str]:
    """Validate that response text contains expected substring (case-insensitive).
    
    Args:
        expected_substring: The substring to search for
        response: The response to validate
        
    Returns:
        (passed: bool, reason_if_failed: str)
    """
    if expected_substring.lower() in response.text.lower():
        return True, ""
    return False, f"Response text does not contain '{expected_substring}'"


def regex_text(pattern: str, response: Response) -> tuple[bool, str]:
    """Validate that response text matches regex pattern (case-insensitive).
    
    Args:
        pattern: The regex pattern to match
        response: The response to validate
        
    Returns:
        (passed: bool, reason_if_failed: str)
    """
    try:
        if re.search(pattern, response.text, re.IGNORECASE):
            return True, ""
        return False, f"Response text does not match pattern '{pattern}'"
    except re.error as e:
        return False, f"Invalid regex pattern '{pattern}': {e}"


def max_latency_ms(max_ms: int, response: Response) -> tuple[bool, str]:
    """Validate that response latency is within maximum limit.
    
    Args:
        max_ms: Maximum allowed latency in milliseconds
        response: The response to validate
        
    Returns:
        (passed: bool, reason_if_failed: str)
    """
    if response.latency_ms is None:
        return False, "Response latency_ms is not provided"
    
    if response.latency_ms <= max_ms:
        return True, ""
    return False, f"Response latency {response.latency_ms}ms exceeds maximum {max_ms}ms"


def status_code_is(expected_code: int, response: Response) -> tuple[bool, str]:
    """Validate that response status code matches expected value.
    
    Args:
        expected_code: The expected status code
        response: The response to validate
        
    Returns:
        (passed: bool, reason_if_failed: str)
    """
    if response.status_code is None:
        return False, "Response status_code is not provided"
    
    if response.status_code == expected_code:
        return True, ""
    return False, f"Response status_code {response.status_code} does not match expected {expected_code}"

