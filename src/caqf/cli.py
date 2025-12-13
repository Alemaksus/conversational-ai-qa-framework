"""CLI implementation for running test cases from Excel matrix."""

import argparse
import sys
from typing import Optional

from caqf.data import load_test_cases
from caqf.pytest_integration import (
    filter_test_cases,
    generate_synthetic_actual_output,
)
from caqf.reporting import generate_junit_report, generate_markdown_report
from caqf.runner import ExecutionStatus, TestRunner


def _truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max_length, adding ellipsis if truncated."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def run_tests(
    matrix_path: str,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    component: Optional[str] = None,
    use_synthetic_actual: bool = False,
    max_failures: int = 10,
    show_failures: int = 5,
    junit_report: Optional[str] = None,
    md_report: Optional[str] = None,
) -> int:
    """Run test cases from Excel matrix and return exit code.
    
    Args:
        matrix_path: Path to Excel matrix file
        priority: Comma-separated list of priorities to filter
        status: Comma-separated list of statuses to filter
        component: Comma-separated list of components to filter
        use_synthetic_actual: Whether to generate synthetic actual output
        max_failures: Stop early after N failures
        show_failures: Print top N failure details
        
    Returns:
        Exit code: 0 if no failures, 2 if failures, 1 for errors
    """
    try:
        # Load test cases
        cases = load_test_cases(matrix_path)
        total_loaded = len(cases)
        
        # Apply filters
        filtered_cases = filter_test_cases(cases, priority, status, component)
        total_filtered = len(filtered_cases)
        
        if total_filtered == 0:
            print(f"Loaded: {total_loaded}")
            print(f"Filtered: {total_filtered}")
            print("No test cases match the filter criteria.")
            return 0
        
        # Run tests
        runner = TestRunner()
        results = []
        failure_count = 0
        
        for case in filtered_cases:
            # Determine actual output
            actual_output = case.actual_result if case.actual_result else None
            
            if actual_output is None and use_synthetic_actual:
                actual_output = generate_synthetic_actual_output(case)
            
            # Run test
            result = runner.run_test(case, actual_output)
            results.append((case, result))
            
            # Count failures for early stopping
            if result.status == ExecutionStatus.FAIL:
                failure_count += 1
                if failure_count >= max_failures:
                    print(f"\nStopping early after {max_failures} failures (--max-failures={max_failures})")
                    break
        
        # Count statuses
        pass_count = sum(1 for _, r in results if r.status == ExecutionStatus.PASS)
        fail_count = sum(1 for _, r in results if r.status == ExecutionStatus.FAIL)
        blocked_count = sum(1 for _, r in results if r.status == ExecutionStatus.BLOCKED)
        
        # Print summary
        print(f"\nLoaded: {total_loaded}")
        print(f"Filtered: {total_filtered}")
        print(f"PASS: {pass_count}")
        print(f"FAIL: {fail_count}")
        print(f"BLOCKED: {blocked_count}")
        
        # Print failure details
        if fail_count > 0:
            print(f"\nTop {min(show_failures, fail_count)} failure(s):")
            failures = [(c, r) for c, r in results if r.status == ExecutionStatus.FAIL]
            for idx, (case, result) in enumerate(failures[:show_failures], 1):
                print(f"\n{idx}. Test Case: {case.test_case_id}")
                print(f"   Scenario: {case.scenario_id}")
                print(f"   Component: {case.component}")
                print(f"   Expected: {_truncate_text(case.expected_result, 80)}")
                if result.failed_reasons:
                    print(f"   Failed Reasons: {', '.join(result.failed_reasons)}")
        
        # Generate reports
        if junit_report:
            try:
                # Extract just ExecutionResult objects for JUnit
                result_objects = [r for _, r in results]
                generate_junit_report(result_objects, junit_report)
                print(f"\nJUnit XML report written to: {junit_report}")
            except Exception as e:
                print(f"Warning: Failed to generate JUnit report: {e}", file=sys.stderr)
        
        if md_report:
            try:
                # Pass tuples for Markdown (needs case info for component)
                generate_markdown_report(results, md_report)
                print(f"Markdown report written to: {md_report}")
            except Exception as e:
                print(f"Warning: Failed to generate Markdown report: {e}", file=sys.stderr)
        
        # Return exit code
        if fail_count > 0:
            return 2
        return 0
        
    except FileNotFoundError as e:
        print(f"Error: File not found: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser for CLI."""
    parser = argparse.ArgumentParser(
        prog="caqf",
        description="Conversational AI QA Framework - Run test cases from Excel matrix",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # 'run' subcommand
    run_parser = subparsers.add_parser(
        "run",
        help="Run test cases from Excel matrix",
    )
    
    run_parser.add_argument(
        "--matrix-path",
        type=str,
        default="templates/test-case-matrix.xlsx",
        help="Path to Excel test case matrix file (default: templates/test-case-matrix.xlsx)",
    )
    
    run_parser.add_argument(
        "--priority",
        type=str,
        default=None,
        help="Filter by priority (comma-separated, e.g., 'Critical,High')",
    )
    
    run_parser.add_argument(
        "--status",
        type=str,
        default=None,
        help="Filter by status (comma-separated, e.g., 'Ready')",
    )
    
    run_parser.add_argument(
        "--component",
        type=str,
        default=None,
        help="Filter by component (comma-separated, e.g., 'Chatbot,Voice')",
    )
    
    run_parser.add_argument(
        "--use-synthetic-actual",
        action="store_true",
        default=False,
        help="Generate synthetic actual output for demo when actual_result is missing (DEMO mode)",
    )
    
    run_parser.add_argument(
        "--max-failures",
        type=int,
        default=10,
        help="Stop early after N failures (default: 10)",
    )
    
    run_parser.add_argument(
        "--show-failures",
        type=int,
        default=5,
        help="Print top N failure details (default: 5)",
    )
    
    run_parser.add_argument(
        "--junit-report",
        type=str,
        default=None,
        help="Path to write JUnit XML report (optional)",
    )
    
    run_parser.add_argument(
        "--md-report",
        type=str,
        default=None,
        help="Path to write Markdown report (optional)",
    )
    
    return parser


def main(args: Optional[list[str]] = None) -> int:
    """Main entry point for CLI.
    
    Args:
        args: Command-line arguments (defaults to sys.argv[1:])
        
    Returns:
        Exit code: 0 if no failures, 2 if failures, 1 for errors
    """
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    
    if parsed_args.command == "run":
        return run_tests(
            matrix_path=parsed_args.matrix_path,
            priority=parsed_args.priority,
            status=parsed_args.status,
            component=parsed_args.component,
            use_synthetic_actual=parsed_args.use_synthetic_actual,
            max_failures=parsed_args.max_failures,
            show_failures=parsed_args.show_failures,
            junit_report=parsed_args.junit_report,
            md_report=parsed_args.md_report,
        )
    else:
        # No command provided, show help
        parser.print_help()
        return 0

