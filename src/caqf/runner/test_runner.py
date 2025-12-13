"""Test runner for executing test cases against actual outputs."""

from typing import Union

from caqf.data.models import CaseModel
from caqf.rules import Response, evaluate_rules, parse_expected_result_to_rules
from caqf.runner.execution_result import ExecutionResult, ExecutionStatus


class TestRunner:
    """Executes test cases by validating actual outputs against expected rules.

    The runner operates on pure logic: it takes a test case and actual output,
    applies the rules engine, and returns an execution result. It does not
    know or care how the actual output was produced (API call, LLM, mock, etc.).

    This separation allows the framework to be used with any execution method
    while maintaining consistent validation logic.
    """

    def run_test(
        self, test_case: CaseModel, actual_output: Union[str, dict, None]
    ) -> ExecutionResult:
        """Run a test case against an actual output.

        Args:
            test_case: The test case to execute (contains expected_result rules)
            actual_output: The actual output to validate. Can be:
                - str: Plain text response
                - dict: Response with optional fields (text, latency_ms, status_code, meta)
                - None: Indicates blocked test (no output available)

        Returns:
            ExecutionResult with status (PASS/FAIL/BLOCKED) and details

        QA Intent:
            This method implements the core test execution logic:
            1. If no actual output → BLOCKED (test cannot run)
            2. Parse expected_result into validation rules
            3. Convert actual_output to Response format
            4. Evaluate all rules against the response
            5. Return PASS if all rules pass, FAIL if any rule fails
        """
        # Handle blocked case: no actual output
        if actual_output is None:
            return ExecutionResult(
                test_case_id=test_case.test_case_id,
                status=ExecutionStatus.BLOCKED,
                details="No actual output provided",
            )

        # Handle empty string output
        if isinstance(actual_output, str) and not actual_output.strip():
            return ExecutionResult(
                test_case_id=test_case.test_case_id,
                status=ExecutionStatus.BLOCKED,
                details="Actual output is empty",
            )

        # Handle empty dict output
        if isinstance(actual_output, dict):
            text = actual_output.get("text", "")
            if not text or (isinstance(text, str) and not text.strip()):
                return ExecutionResult(
                    test_case_id=test_case.test_case_id,
                    status=ExecutionStatus.BLOCKED,
                    details="Actual output text is empty",
                )

        # Convert actual_output to Response format
        response = self._convert_to_response(actual_output)

        # Parse expected_result into rules
        rules = parse_expected_result_to_rules(test_case.expected_result)

        # Evaluate rules
        passed, failure_reasons = evaluate_rules(rules, response)

        # Collect rule names that were applied (evaluated)
        applied_rules = [rule.name for rule in rules]

        # Determine status and details
        if passed:
            return ExecutionResult(
                test_case_id=test_case.test_case_id,
                status=ExecutionStatus.PASS,
                details="All rules passed",
                applied_rules=applied_rules,
                failed_reasons=None,
            )
        else:
            details = "; ".join(failure_reasons)
            return ExecutionResult(
                test_case_id=test_case.test_case_id,
                status=ExecutionStatus.FAIL,
                details=details,
                applied_rules=applied_rules,
                failed_reasons=failure_reasons,
            )

    def _convert_to_response(self, actual_output: Union[str, dict]) -> Response:
        """Convert actual_output to Response format.

        Args:
            actual_output: Either a string or dict with response data

        Returns:
            Response object ready for rule evaluation
        """
        if isinstance(actual_output, str):
            return Response(text=actual_output)

        # Handle dict format
        if isinstance(actual_output, dict):
            text = actual_output.get("text", "")
            if not isinstance(text, str):
                text = str(text) if text is not None else ""

            return Response(
                text=text,
                latency_ms=actual_output.get("latency_ms"),
                status_code=actual_output.get("status_code"),
                meta=actual_output.get("meta"),
            )

        # Fallback: convert to string
        return Response(text=str(actual_output))

