"""End-to-end tests loaded from Excel test case matrix."""

import pytest

from caqf.data import CaseModel
from caqf.pytest_integration import (
    build_test_id,
    generate_synthetic_actual_output,
    load_cases_for_pytest,
)
from caqf.runner import TestRunner


def pytest_generate_tests(metafunc):
    """Generate test cases dynamically from Excel matrix.
    
    This hook is called by pytest to parametrize tests based on
    test cases loaded from the Excel matrix file.
    """
    if "test_case" in metafunc.fixturenames:
        # Get matrix path from command-line option
        matrix_path = metafunc.config.getoption("--matrix-path")
        
        # Load test cases
        try:
            cases = load_cases_for_pytest(matrix_path)
        except FileNotFoundError:
            pytest.skip(f"Matrix file not found: {matrix_path}")
            return
        except Exception as e:
            pytest.skip(f"Failed to load matrix: {e}")
            return
        
        # Apply filters from command-line options
        # Import here to avoid circular dependency
        from tests.conftest import filter_test_cases
        
        priority = metafunc.config.getoption("--priority")
        status = metafunc.config.getoption("--status")
        component = metafunc.config.getoption("--component")
        
        filtered_cases = filter_test_cases(cases, priority, status, component)
        
        if not filtered_cases:
            pytest.skip("No test cases match the filter criteria")
            return
        
        # Store collection info for summary (using config cache)
        total_loaded = len(cases)
        total_filtered = len(filtered_cases)
        use_synthetic = metafunc.config.getoption("--use-synthetic-actual")
        
        missing_actual = sum(1 for c in filtered_cases if not c.actual_result)
        has_actual = total_filtered - missing_actual
        
        # Store in config for later use in pytest_report_collectionfinish
        if not hasattr(metafunc.config, "_matrix_collection_info"):
            metafunc.config._matrix_collection_info = {}
        metafunc.config._matrix_collection_info = {
            "total_loaded": total_loaded,
            "total_filtered": total_filtered,
            "has_actual": has_actual,
            "missing_actual": missing_actual,
            "use_synthetic": use_synthetic,
        }
        
        # Parametrize with test cases
        # Use build_test_id for readable test names
        ids = [build_test_id(case) for case in filtered_cases]
        metafunc.parametrize("test_case", filtered_cases, ids=ids)


@pytest.mark.matrix
def test_case_execution(test_case, pytestconfig):
    """Execute a test case from the Excel matrix.
    
    This test is parametrized dynamically by pytest_generate_tests
    based on test cases loaded from the Excel matrix.
    
    Args:
        test_case: CaseModel instance loaded from Excel matrix
        pytestconfig: Pytest config object (injected by pytest)
    """
    # Use actual_result from matrix as actual_output, or generate synthetic if enabled
    use_synthetic = pytestconfig.getoption("--use-synthetic-actual")
    
    if test_case.actual_result:
        actual_output = test_case.actual_result
    elif use_synthetic:
        # DEMO mode: generate synthetic output
        actual_output = generate_synthetic_actual_output(test_case)
    else:
        actual_output = None
    
    # Run the test case through the test runner
    runner = TestRunner()
    result = runner.run_test(test_case, actual_output)
    
    # Handle different execution statuses
    if result.status.value == "BLOCKED":
        pytest.skip(
            f"No Actual Result provided in matrix for {test_case.test_case_id}. "
            f"Component: {test_case.component}, Scenario: {test_case.scenario_id}"
        )
    
    elif result.status.value == "FAIL":
        # Build readable failure message
        failure_parts = [
            f"Test Case: {test_case.test_case_id}",
            f"Scenario: {test_case.scenario_id}",
            f"Component: {test_case.component}",
            f"Expected Result: {test_case.expected_result}",
            f"Actual Output: {actual_output if actual_output else '(None)'}",
        ]
        
        if result.failed_reasons:
            failure_parts.append(f"Failed Rules: {', '.join(result.failed_reasons)}")
        
        if result.details:
            failure_parts.append(f"Details: {result.details}")
        
        failure_message = " | ".join(failure_parts)
        pytest.fail(failure_message)
    
    elif result.status.value == "PASS":
        # Test passed - no assertion needed, just verify status
        assert result.status.value == "PASS"
    
    else:
        # Unexpected status
        pytest.fail(f"Unexpected execution status: {result.status.value}")

