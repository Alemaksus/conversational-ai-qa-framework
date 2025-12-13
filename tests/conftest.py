"""Pytest configuration to ensure src/ is in sys.path for tests.

This allows tests to run without requiring 'pip install -e .' first,
making the repository portfolio-friendly for 'git clone → pytest' workflow.
"""

import sys
from pathlib import Path

# Locate project root (parent of tests/ directory)
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src"

# Add src/ to sys.path if not already present
# This ensures imports like 'from caqf.data import ...' work
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Import after sys.path is set up
import pytest

from caqf.data import CaseModel


def pytest_addoption(parser):
    """Add custom command-line options for pytest."""
    parser.addoption(
        "--matrix-path",
        action="store",
        default="templates/test-case-matrix.xlsx",
        help="Path to Excel test case matrix file",
    )
    parser.addoption(
        "--priority",
        action="store",
        default=None,
        help="Filter by priority (comma-separated, e.g., 'High,Critical')",
    )
    parser.addoption(
        "--status",
        action="store",
        default=None,
        help="Filter by status (comma-separated, e.g., 'Ready')",
    )
    parser.addoption(
        "--component",
        action="store",
        default=None,
        help="Filter by component (comma-separated, e.g., 'Chatbot,Voice')",
    )
    parser.addoption(
        "--use-synthetic-actual",
        action="store_true",
        default=False,
        help="Generate synthetic actual_output for demo when actual_result is missing (DEMO mode)",
    )


def filter_test_cases(
    cases: list[CaseModel],
    priority: str | None = None,
    status: str | None = None,
    component: str | None = None,
) -> list[CaseModel]:
    """Filter test cases based on provided criteria.
    
    Args:
        cases: List of test cases to filter
        priority: Comma-separated list of priorities to include (e.g., "High,Critical")
        status: Comma-separated list of statuses to include (e.g., "Ready")
        component: Comma-separated list of components to include (e.g., "Chatbot,Voice")
        
    Returns:
        Filtered list of test cases matching the criteria
    """
    filtered = cases
    
    if priority:
        priority_list = [p.strip() for p in priority.split(",")]
        filtered = [c for c in filtered if c.priority in priority_list]
    
    if status:
        status_list = [s.strip() for s in status.split(",")]
        filtered = [c for c in filtered if c.status in status_list]
    
    if component:
        component_list = [c.strip() for c in component.split(",")]
        filtered = [c for c in filtered if c.component in component_list]
    
    return filtered


def pytest_collection_modifyitems(config, items):
    """Automatically add markers to tests based on file location."""
    for item in items:
        # Mark tests in test_e2e_from_excel.py as matrix
        if "test_e2e_from_excel" in str(item.fspath):
            item.add_marker(pytest.mark.matrix)
        # Mark all other tests as unit
        else:
            item.add_marker(pytest.mark.unit)


def pytest_report_collectionfinish(config, start_path, items):
    """Print summary after test collection for matrix tests."""
    # Count matrix tests
    matrix_tests = [item for item in items if "test_e2e_from_excel" in str(item.fspath)]
    
    if matrix_tests and hasattr(config, "_matrix_collection_info"):
        info = config._matrix_collection_info
        total_loaded = info.get("total_loaded", 0)
        total_filtered = info.get("total_filtered", len(matrix_tests))
        has_actual = info.get("has_actual", 0)
        missing_actual = info.get("missing_actual", 0)
        use_synthetic = info.get("use_synthetic", False)
        
        print(f"\n[Matrix Tests] Loaded: {total_loaded}, Filtered: {total_filtered}, "
              f"With actual_result: {has_actual}, Missing actual_result: {missing_actual}")
        if use_synthetic and missing_actual > 0:
            print(f"[DEMO Mode] Will generate synthetic output for {missing_actual} test(s)")
        elif missing_actual > 0:
            print(f"[Note] {missing_actual} test(s) will be skipped (use --use-synthetic-actual for demo)")

