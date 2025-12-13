"""Tests for the rules engine."""

import pytest

from caqf.rules import Response, Rule, evaluate_rules, parse_expected_result_to_rules


def test_plain_english_expected_result_creates_default_rules():
    """Test that plain English expected result creates default NOT_EMPTY + CONTAINS rules."""
    expected_result = "User should receive a confirmation message"
    rules = parse_expected_result_to_rules(expected_result)
    
    assert len(rules) == 2
    assert rules[0].name == "NOT_EMPTY"
    assert rules[1].name == "CONTAINS"
    assert rules[1].params["text"] == expected_result


def test_rule_mode_parses_multiple_rules():
    """Test that rule-based mode parses multiple rules correctly."""
    expected_result = """NOT_EMPTY
CONTAINS: confirmation
REGEX: \\d{4}
MAX_LATENCY_MS: 500
STATUS_CODE: 200"""
    
    rules = parse_expected_result_to_rules(expected_result)
    
    assert len(rules) == 5
    assert rules[0].name == "NOT_EMPTY"
    assert rules[1].name == "CONTAINS"
    assert rules[1].params["text"] == "confirmation"
    assert rules[2].name == "REGEX"
    assert rules[2].params["pattern"] == "\\d{4}"
    assert rules[3].name == "MAX_LATENCY_MS"
    assert rules[3].params["max_ms"] == 500
    assert rules[4].name == "STATUS_CODE"
    assert rules[4].params["code"] == 200


def test_contains_pass_and_fail():
    """Test CONTAINS rule pass and fail scenarios."""
    from caqf.rules.validators import contains_text
    
    # Pass case
    response = Response(text="Your order has been confirmed")
    passed, reason = contains_text("confirmed", response)
    assert passed
    assert reason == ""
    
    # Fail case
    response = Response(text="Your order is pending")
    passed, reason = contains_text("confirmed", response)
    assert not passed
    assert "does not contain" in reason


def test_regex_pass_and_fail():
    """Test REGEX rule pass and fail scenarios."""
    from caqf.rules.validators import regex_text
    
    # Pass case
    response = Response(text="Order ID: 1234")
    passed, reason = regex_text(r"\d{4}", response)
    assert passed
    assert reason == ""
    
    # Fail case
    response = Response(text="Order ID: ABC")
    passed, reason = regex_text(r"\d{4}", response)
    assert not passed
    assert "does not match pattern" in reason
    
    # Invalid regex
    response = Response(text="Some text")
    passed, reason = regex_text(r"[invalid", response)
    assert not passed
    assert "Invalid regex pattern" in reason


def test_max_latency_behavior():
    """Test MAX_LATENCY_MS rule behavior."""
    from caqf.rules.validators import max_latency_ms
    
    # Pass case
    response = Response(text="OK", latency_ms=300)
    passed, reason = max_latency_ms(500, response)
    assert passed
    assert reason == ""
    
    # Fail case - exceeds limit
    response = Response(text="OK", latency_ms=600)
    passed, reason = max_latency_ms(500, response)
    assert not passed
    assert "exceeds maximum" in reason
    
    # Fail case - latency not provided
    response = Response(text="OK", latency_ms=None)
    passed, reason = max_latency_ms(500, response)
    assert not passed
    assert "not provided" in reason


def test_status_code_behavior():
    """Test STATUS_CODE rule behavior."""
    from caqf.rules.validators import status_code_is
    
    # Pass case
    response = Response(text="OK", status_code=200)
    passed, reason = status_code_is(200, response)
    assert passed
    assert reason == ""
    
    # Fail case - wrong code
    response = Response(text="Error", status_code=404)
    passed, reason = status_code_is(200, response)
    assert not passed
    assert "does not match expected" in reason
    
    # Fail case - status_code not provided
    response = Response(text="OK", status_code=None)
    passed, reason = status_code_is(200, response)
    assert not passed
    assert "not provided" in reason


def test_evaluate_rules_collects_reasons():
    """Test that evaluate_rules collects all failure reasons."""
    rules = [
        Rule(name="NOT_EMPTY", params={}),
        Rule(name="CONTAINS", params={"text": "confirmation"}),
        Rule(name="MAX_LATENCY_MS", params={"max_ms": 100}),
    ]
    
    # All pass
    response = Response(text="Your order confirmation is ready", latency_ms=50)
    passed, reasons = evaluate_rules(rules, response)
    assert passed
    assert reasons == []
    
    # Some fail
    response = Response(text="Order pending", latency_ms=200)
    passed, reasons = evaluate_rules(rules, response)
    assert not passed
    assert len(reasons) == 2
    assert any("does not contain" in r for r in reasons)
    assert any("exceeds maximum" in r for r in reasons)


def test_empty_expected_result_creates_not_empty_rule():
    """Test that empty expected result creates only NOT_EMPTY rule."""
    rules = parse_expected_result_to_rules("")
    assert len(rules) == 1
    assert rules[0].name == "NOT_EMPTY"


def test_rule_mode_with_empty_lines():
    """Test that rule mode ignores empty lines."""
    expected_result = """NOT_EMPTY

CONTAINS: test

STATUS_CODE: 200"""
    
    rules = parse_expected_result_to_rules(expected_result)
    assert len(rules) == 3
    assert rules[0].name == "NOT_EMPTY"
    assert rules[1].name == "CONTAINS"
    assert rules[2].name == "STATUS_CODE"


def test_invalid_numeric_rules_are_skipped():
    """Test that invalid numeric values in rules are skipped."""
    expected_result = """NOT_EMPTY
MAX_LATENCY_MS: invalid
STATUS_CODE: not_a_number
CONTAINS: valid"""
    
    rules = parse_expected_result_to_rules(expected_result)
    # Should have NOT_EMPTY, CONTAINS (invalid numeric rules skipped)
    assert len(rules) == 2
    assert rules[0].name == "NOT_EMPTY"
    assert rules[1].name == "CONTAINS"


def test_not_empty_validator():
    """Test NOT_EMPTY validator."""
    from caqf.rules.validators import not_empty_text
    
    # Pass case
    response = Response(text="Some text")
    passed, reason = not_empty_text(response)
    assert passed
    assert reason == ""
    
    # Fail case - empty
    response = Response(text="")
    passed, reason = not_empty_text(response)
    assert not passed
    assert "empty" in reason
    
    # Fail case - whitespace only
    response = Response(text="   ")
    passed, reason = not_empty_text(response)
    assert not passed
    assert "empty" in reason

