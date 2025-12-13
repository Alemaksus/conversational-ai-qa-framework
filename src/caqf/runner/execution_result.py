"""Execution result models for test runs."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ExecutionStatus(Enum):
    """Status of a test case execution."""

    PASS = "PASS"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"


@dataclass
class ExecutionResult:
    """Result of executing a test case.

    Represents the outcome of running a test case through the execution layer,
    including status, details, which rules were applied, and failure reasons.
    """

    test_case_id: str
    status: ExecutionStatus
    details: Optional[str] = None
    applied_rules: Optional[list[str]] = None
    failed_reasons: Optional[list[str]] = None

