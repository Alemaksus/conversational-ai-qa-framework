"""Tests for the test runner execution layer."""

import pytest

from caqf.data.models import CaseModel
from caqf.runner import ExecutionResult, ExecutionStatus, TestRunner


def test_runner_pass_case():
    """Test PASS case when expected rule is satisfied."""
    runner = TestRunner()

    test_case = CaseModel(
        test_case_id="TC-001",
        scenario_id="SCENARIO-001",
        component="Component1",
        test_description="Test description",
        test_type="Functional",
        priority="High",
        prerequisites="None",
        test_steps="Step 1",
        expected_result="CONTAINS: confirmation",
    )

    actual_output = "Your order confirmation is ready"

    result = runner.run_test(test_case, actual_output)

    assert isinstance(result, ExecutionResult)
    assert result.test_case_id == "TC-001"
    assert result.status == ExecutionStatus.PASS
    assert result.details == "All rules passed"
    assert result.applied_rules is not None
    assert "CONTAINS" in result.applied_rules
    assert result.failed_reasons is None


def test_runner_fail_case():
    """Test FAIL case when rule is not satisfied."""
    runner = TestRunner()

    test_case = CaseModel(
        test_case_id="TC-002",
        scenario_id="SCENARIO-001",
        component="Component1",
        test_description="Test description",
        test_type="Functional",
        priority="High",
        prerequisites="None",
        test_steps="Step 1",
        expected_result="CONTAINS: confirmation",
    )

    actual_output = "Your order is pending"

    result = runner.run_test(test_case, actual_output)

    assert isinstance(result, ExecutionResult)
    assert result.test_case_id == "TC-002"
    assert result.status == ExecutionStatus.FAIL
    assert result.details is not None
    assert "does not contain" in result.details
    assert result.applied_rules is not None
    assert "CONTAINS" in result.applied_rules
    assert result.failed_reasons is not None
    assert len(result.failed_reasons) > 0
    assert any("does not contain" in reason for reason in result.failed_reasons)


def test_runner_blocked_case_none():
    """Test BLOCKED case when actual_output is None."""
    runner = TestRunner()

    test_case = CaseModel(
        test_case_id="TC-003",
        scenario_id="SCENARIO-001",
        component="Component1",
        test_description="Test description",
        test_type="Functional",
        priority="High",
        prerequisites="None",
        test_steps="Step 1",
        expected_result="CONTAINS: confirmation",
    )

    actual_output = None

    result = runner.run_test(test_case, actual_output)

    assert isinstance(result, ExecutionResult)
    assert result.test_case_id == "TC-003"
    assert result.status == ExecutionStatus.BLOCKED
    assert result.details == "No actual output provided"
    assert result.applied_rules is None
    assert result.failed_reasons is None


def test_runner_blocked_case_empty_string():
    """Test BLOCKED case when actual_output is empty string."""
    runner = TestRunner()

    test_case = CaseModel(
        test_case_id="TC-004",
        scenario_id="SCENARIO-001",
        component="Component1",
        test_description="Test description",
        test_type="Functional",
        priority="High",
        prerequisites="None",
        test_steps="Step 1",
        expected_result="CONTAINS: confirmation",
    )

    actual_output = ""

    result = runner.run_test(test_case, actual_output)

    assert isinstance(result, ExecutionResult)
    assert result.test_case_id == "TC-004"
    assert result.status == ExecutionStatus.BLOCKED
    assert result.details == "Actual output is empty"
    assert result.applied_rules is None
    assert result.failed_reasons is None


def test_runner_blocked_case_whitespace_only():
    """Test BLOCKED case when actual_output is whitespace only."""
    runner = TestRunner()

    test_case = CaseModel(
        test_case_id="TC-005",
        scenario_id="SCENARIO-001",
        component="Component1",
        test_description="Test description",
        test_type="Functional",
        priority="High",
        prerequisites="None",
        test_steps="Step 1",
        expected_result="CONTAINS: confirmation",
    )

    actual_output = "   "

    result = runner.run_test(test_case, actual_output)

    assert isinstance(result, ExecutionResult)
    assert result.test_case_id == "TC-005"
    assert result.status == ExecutionStatus.BLOCKED
    assert result.details == "Actual output is empty"
    assert result.applied_rules is None
    assert result.failed_reasons is None


def test_runner_with_dict_output():
    """Test runner with dict format actual_output."""
    runner = TestRunner()

    test_case = CaseModel(
        test_case_id="TC-006",
        scenario_id="SCENARIO-001",
        component="Component1",
        test_description="Test description",
        test_type="Functional",
        priority="High",
        prerequisites="None",
        test_steps="Step 1",
        expected_result="CONTAINS: success",
    )

    actual_output = {"text": "Operation completed successfully", "latency_ms": 200}

    result = runner.run_test(test_case, actual_output)

    assert isinstance(result, ExecutionResult)
    assert result.test_case_id == "TC-006"
    assert result.status == ExecutionStatus.PASS
    assert result.details == "All rules passed"


def test_runner_with_dict_output_empty_text():
    """Test BLOCKED case when dict output has empty text."""
    runner = TestRunner()

    test_case = CaseModel(
        test_case_id="TC-007",
        scenario_id="SCENARIO-001",
        component="Component1",
        test_description="Test description",
        test_type="Functional",
        priority="High",
        prerequisites="None",
        test_steps="Step 1",
        expected_result="CONTAINS: confirmation",
    )

    actual_output = {"text": "", "latency_ms": 200}

    result = runner.run_test(test_case, actual_output)

    assert isinstance(result, ExecutionResult)
    assert result.test_case_id == "TC-007"
    assert result.status == ExecutionStatus.BLOCKED
    assert result.details == "Actual output text is empty"


def test_runner_multiple_rules_all_pass():
    """Test runner with multiple rules that all pass."""
    runner = TestRunner()

    test_case = CaseModel(
        test_case_id="TC-008",
        scenario_id="SCENARIO-001",
        component="Component1",
        test_description="Test description",
        test_type="Functional",
        priority="High",
        prerequisites="None",
        test_steps="Step 1",
        expected_result="""NOT_EMPTY
CONTAINS: order
REGEX: \\d{4}""",
    )

    actual_output = "Your order 1234 has been processed"

    result = runner.run_test(test_case, actual_output)

    assert isinstance(result, ExecutionResult)
    assert result.test_case_id == "TC-008"
    assert result.status == ExecutionStatus.PASS
    assert result.details == "All rules passed"
    assert result.applied_rules is not None
    assert "NOT_EMPTY" in result.applied_rules
    assert "CONTAINS" in result.applied_rules
    assert "REGEX" in result.applied_rules
    assert result.failed_reasons is None


def test_runner_multiple_rules_some_fail():
    """Test runner with multiple rules where some fail."""
    runner = TestRunner()

    test_case = CaseModel(
        test_case_id="TC-009",
        scenario_id="SCENARIO-001",
        component="Component1",
        test_description="Test description",
        test_type="Functional",
        priority="High",
        prerequisites="None",
        test_steps="Step 1",
        expected_result="""NOT_EMPTY
CONTAINS: confirmation
REGEX: \\d{4}""",
    )

    actual_output = "Your order is pending"

    result = runner.run_test(test_case, actual_output)

    assert isinstance(result, ExecutionResult)
    assert result.test_case_id == "TC-009"
    assert result.status == ExecutionStatus.FAIL
    assert result.details is not None
    # Should have failure reasons for both CONTAINS and REGEX
    assert "does not contain" in result.details or "does not match pattern" in result.details
    assert result.applied_rules is not None
    assert len(result.applied_rules) == 3
    assert result.failed_reasons is not None
    assert len(result.failed_reasons) >= 2  # At least CONTAINS and REGEX should fail


def test_runner_plain_english_expected_result():
    """Test runner with plain English expected_result (default rules)."""
    runner = TestRunner()

    test_case = CaseModel(
        test_case_id="TC-010",
        scenario_id="SCENARIO-001",
        component="Component1",
        test_description="Test description",
        test_type="Functional",
        priority="High",
        prerequisites="None",
        test_steps="Step 1",
        expected_result="User should receive a confirmation message",
    )

    actual_output = "User should receive a confirmation message"

    result = runner.run_test(test_case, actual_output)

    assert isinstance(result, ExecutionResult)
    assert result.test_case_id == "TC-010"
    assert result.status == ExecutionStatus.PASS
    assert result.applied_rules is not None
    assert "NOT_EMPTY" in result.applied_rules
    assert "CONTAINS" in result.applied_rules
    assert result.failed_reasons is None

