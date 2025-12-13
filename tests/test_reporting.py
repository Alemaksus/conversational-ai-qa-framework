"""Tests for reporting functionality."""

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from caqf.data import CaseModel
from caqf.reporting import generate_junit_report, generate_markdown_report
from caqf.runner import ExecutionResult, ExecutionStatus


@pytest.fixture
def sample_results():
    """Create sample ExecutionResult objects for testing."""
    return [
        ExecutionResult(
            test_case_id="TC-001",
            status=ExecutionStatus.PASS,
            details="All rules passed",
            applied_rules=["CONTAINS", "NOT_EMPTY"],
        ),
        ExecutionResult(
            test_case_id="TC-002",
            status=ExecutionStatus.FAIL,
            details="Test failed",
            applied_rules=["CONTAINS", "NOT_EMPTY"],
            failed_reasons=["CONTAINS rule failed: expected 'hello' not found"],
        ),
        ExecutionResult(
            test_case_id="TC-003",
            status=ExecutionStatus.BLOCKED,
            details="No actual output provided",
        ),
    ]


@pytest.fixture
def sample_cases_with_results():
    """Create sample (case, result) tuples for testing."""
    cases = [
        CaseModel(
            test_case_id="TC-001",
            scenario_id="SC-001",
            component="Chatbot",
            test_description="Test 1",
            test_type="Functional",
            priority="High",
            prerequisites="",
            test_steps="Step 1",
            expected_result="Should contain hello",
        ),
        CaseModel(
            test_case_id="TC-002",
            scenario_id="SC-002",
            component="Voice",
            test_description="Test 2",
            test_type="Functional",
            priority="Critical",
            prerequisites="",
            test_steps="Step 2",
            expected_result="Should contain world",
        ),
    ]
    
    results = [
        ExecutionResult(
            test_case_id="TC-001",
            status=ExecutionStatus.PASS,
            details="All rules passed",
        ),
        ExecutionResult(
            test_case_id="TC-002",
            status=ExecutionStatus.FAIL,
            details="Test failed",
            failed_reasons=["CONTAINS rule failed"],
            applied_rules=["CONTAINS"],
        ),
    ]
    
    return list(zip(cases, results))


def test_junit_report_generation(sample_results, tmp_path):
    """Test JUnit XML report generation."""
    output_file = tmp_path / "junit.xml"
    
    generate_junit_report(sample_results, str(output_file))
    
    # Verify file exists
    assert output_file.exists()
    
    # Parse and validate XML
    tree = ET.parse(output_file)
    root = tree.getroot()
    
    # Check root element
    assert root.tag == "testsuite"
    assert root.get("name") == "Conversational AI QA Matrix"
    assert root.get("tests") == "3"
    assert root.get("failures") == "1"
    assert root.get("skipped") == "1"
    assert root.get("errors") == "0"
    
    # Check testcase elements
    testcases = root.findall("testcase")
    assert len(testcases) == 3
    
    # Check PASS testcase (no children)
    tc1 = [tc for tc in testcases if tc.get("name") == "TC-001"][0]
    assert len(list(tc1)) == 0  # No failure or skipped elements
    
    # Check FAIL testcase (has failure element)
    tc2 = [tc for tc in testcases if tc.get("name") == "TC-002"][0]
    failure = tc2.find("failure")
    assert failure is not None
    assert "CONTAINS rule failed" in failure.text
    
    # Check BLOCKED testcase (has skipped element)
    tc3 = [tc for tc in testcases if tc.get("name") == "TC-003"][0]
    skipped = tc3.find("skipped")
    assert skipped is not None
    assert skipped.get("message") == "No actual output provided"


def test_junit_report_custom_suite_name(sample_results, tmp_path):
    """Test JUnit XML report with custom suite name."""
    output_file = tmp_path / "junit.xml"
    
    generate_junit_report(sample_results, str(output_file), suite_name="Custom Suite")
    
    tree = ET.parse(output_file)
    root = tree.getroot()
    assert root.get("name") == "Custom Suite"


def test_junit_report_creates_directories(tmp_path, sample_results):
    """Test that JUnit report creates parent directories if needed."""
    output_file = tmp_path / "reports" / "subdir" / "junit.xml"
    
    generate_junit_report(sample_results, str(output_file))
    
    assert output_file.exists()
    assert output_file.parent.exists()


def test_markdown_report_generation(sample_cases_with_results, tmp_path):
    """Test Markdown report generation."""
    output_file = tmp_path / "report.md"
    
    generate_markdown_report(sample_cases_with_results, str(output_file))
    
    # Verify file exists
    assert output_file.exists()
    
    # Read and validate content
    content = output_file.read_text(encoding="utf-8")
    
    # Check title
    assert "# Test Execution Report" in content
    
    # Check summary
    assert "## Summary" in content
    assert "**Total:** 2" in content
    assert "**PASS:** 1" in content
    assert "**FAIL:** 1" in content
    
    # Check table
    assert "## Test Cases" in content
    assert "| ID | Status | Component | Notes |" in content
    assert "TC-001" in content
    assert "TC-002" in content
    assert "Chatbot" in content
    assert "Voice" in content
    
    # Check failures section
    assert "## Failures" in content
    assert "### TC-002" in content
    assert "**Failed Reasons:**" in content
    assert "- CONTAINS rule failed" in content
    assert "**Applied Rules:**" in content
    assert "CONTAINS" in content


def test_markdown_report_with_execution_results_only(tmp_path):
    """Test Markdown report with ExecutionResult objects only (no cases)."""
    results = [
        ExecutionResult(
            test_case_id="TC-001",
            status=ExecutionStatus.PASS,
            details="All rules passed",
        ),
        ExecutionResult(
            test_case_id="TC-002",
            status=ExecutionStatus.FAIL,
            details="Test failed",
            failed_reasons=["Rule failed"],
        ),
    ]
    
    output_file = tmp_path / "report.md"
    
    generate_markdown_report(results, str(output_file))
    
    # Verify file exists
    assert output_file.exists()
    
    content = output_file.read_text(encoding="utf-8")
    
    # Check summary
    assert "**Total:** 2" in content
    assert "**PASS:** 1" in content
    assert "**FAIL:** 1" in content
    
    # Check that component column exists (even if empty)
    assert "| ID | Status | Component | Notes |" in content


def test_markdown_report_max_rows(sample_cases_with_results, tmp_path):
    """Test Markdown report respects max_rows parameter."""
    # Create more results
    cases = []
    results = []
    for i in range(25):
        case = CaseModel(
            test_case_id=f"TC-{i+1:03d}",
            scenario_id="SC-001",
            component="Test",
            test_description="Test",
            test_type="Functional",
            priority="High",
            prerequisites="",
            test_steps="Step",
            expected_result="Result",
        )
        result = ExecutionResult(
            test_case_id=f"TC-{i+1:03d}",
            status=ExecutionStatus.PASS,
        )
        cases.append(case)
        results.append(result)
    
    test_data = list(zip(cases, results))
    output_file = tmp_path / "report.md"
    
    generate_markdown_report(test_data, str(output_file), max_rows=10)
    
    content = output_file.read_text(encoding="utf-8")
    
    # Should show first 10 rows
    assert "TC-001" in content
    assert "TC-010" in content
    # Should mention truncation
    assert "Showing first 10 of 25" in content


def test_markdown_report_creates_directories(tmp_path, sample_cases_with_results):
    """Test that Markdown report creates parent directories if needed."""
    output_file = tmp_path / "reports" / "subdir" / "report.md"
    
    generate_markdown_report(sample_cases_with_results, str(output_file))
    
    assert output_file.exists()
    assert output_file.parent.exists()


def test_markdown_report_no_failures(tmp_path):
    """Test Markdown report when there are no failures."""
    results = [
        ExecutionResult(
            test_case_id="TC-001",
            status=ExecutionStatus.PASS,
        ),
    ]
    
    output_file = tmp_path / "report.md"
    
    generate_markdown_report(results, str(output_file))
    
    content = output_file.read_text(encoding="utf-8")
    
    # Should not have failures section
    assert "## Failures" not in content

