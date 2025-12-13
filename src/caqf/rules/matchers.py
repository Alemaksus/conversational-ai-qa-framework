"""Parsing and evaluation of expected result rules."""

import re
from typing import Callable

from caqf.rules.types import Response, Rule
from caqf.rules.validators import (
    contains_text,
    max_latency_ms,
    not_empty_text,
    regex_text,
    status_code_is,
)


def parse_expected_result_to_rules(expected_result: str) -> list[Rule]:
    """Parse expected result text into a list of validation rules.
    
    Supports two modes:
    1. Plain English mode: If no rule prefixes are found, creates default rules:
       - NOT_EMPTY
       - CONTAINS: <expected_result>
    
    2. Rule-based mode: If any line starts with a supported prefix, parses each line as a rule.
       Supported prefixes:
       - NOT_EMPTY
       - CONTAINS: <text>
       - REGEX: <pattern>
       - MAX_LATENCY_MS: <int>
       - STATUS_CODE: <int>
    
    Args:
        expected_result: The expected result text from the test case matrix
        
    Returns:
        List of Rule objects
    """
    if not expected_result:
        return [Rule(name="NOT_EMPTY", params={})]
    
    lines = [line.strip() for line in expected_result.split("\n")]
    lines = [line for line in lines if line]  # Remove empty lines
    
    if not lines:
        return [Rule(name="NOT_EMPTY", params={})]
    
    # Check if any line starts with a rule prefix
    rule_prefixes = ["NOT_EMPTY", "CONTAINS:", "REGEX:", "MAX_LATENCY_MS:", "STATUS_CODE:"]
    has_rule_prefix = any(line.startswith(prefix) for line in lines for prefix in rule_prefixes)
    
    if not has_rule_prefix:
        # Plain English mode: default rules
        return [
            Rule(name="NOT_EMPTY", params={}),
            Rule(name="CONTAINS", params={"text": expected_result.strip()}),
        ]
    
    # Rule-based mode: parse each line
    rules = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        if line == "NOT_EMPTY":
            rules.append(Rule(name="NOT_EMPTY", params={}))
        
        elif line.startswith("CONTAINS:"):
            text = line[len("CONTAINS:"):].strip()
            if text:
                rules.append(Rule(name="CONTAINS", params={"text": text}))
        
        elif line.startswith("REGEX:"):
            pattern = line[len("REGEX:"):].strip()
            if pattern:
                rules.append(Rule(name="REGEX", params={"pattern": pattern}))
        
        elif line.startswith("MAX_LATENCY_MS:"):
            value_str = line[len("MAX_LATENCY_MS:"):].strip()
            try:
                max_ms = int(value_str)
                rules.append(Rule(name="MAX_LATENCY_MS", params={"max_ms": max_ms}))
            except ValueError:
                # Skip invalid rule
                pass
        
        elif line.startswith("STATUS_CODE:"):
            value_str = line[len("STATUS_CODE:"):].strip()
            try:
                code = int(value_str)
                rules.append(Rule(name="STATUS_CODE", params={"code": code}))
            except ValueError:
                # Skip invalid rule
                pass
    
    return rules if rules else [Rule(name="NOT_EMPTY", params={})]


def _apply_rule(rule: Rule, response: Response) -> tuple[bool, str]:
    """Apply a single rule to a response.
    
    Args:
        rule: The rule to apply
        response: The response to validate
        
    Returns:
        (passed: bool, reason_if_failed: str)
    """
    if rule.name == "NOT_EMPTY":
        return not_empty_text(response)
    
    elif rule.name == "CONTAINS":
        text = rule.params.get("text", "")
        return contains_text(text, response)
    
    elif rule.name == "REGEX":
        pattern = rule.params.get("pattern", "")
        return regex_text(pattern, response)
    
    elif rule.name == "MAX_LATENCY_MS":
        max_ms = rule.params.get("max_ms", 0)
        return max_latency_ms(max_ms, response)
    
    elif rule.name == "STATUS_CODE":
        code = rule.params.get("code", 0)
        return status_code_is(code, response)
    
    else:
        return False, f"Unknown rule: {rule.name}"


def evaluate_rules(rules: list[Rule], response: Response) -> tuple[bool, list[str]]:
    """Evaluate a list of rules against a response.
    
    Args:
        rules: List of rules to evaluate
        response: The response to validate
        
    Returns:
        Tuple of (passed: bool, list_of_failure_reasons: list[str])
        If passed is True, failure_reasons will be an empty list.
    """
    failure_reasons = []
    
    for rule in rules:
        passed, reason = _apply_rule(rule, response)
        if not passed:
            failure_reasons.append(f"{rule.name}: {reason}")
    
    return len(failure_reasons) == 0, failure_reasons

