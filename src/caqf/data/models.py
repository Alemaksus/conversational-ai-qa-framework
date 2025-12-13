"""Data models for test cases."""

from dataclasses import dataclass


@dataclass
class TestCase:
    """Represents a test case from the Excel matrix."""

    test_case_id: str
    scenario_id: str
    component: str
    test_description: str
    test_type: str
    priority: str
    prerequisites: str
    test_steps: str
    expected_result: str
    actual_result: str | None = None
    status: str | None = None
    notes: str | None = None

