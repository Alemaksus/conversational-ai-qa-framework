"""JUnit XML report generation for test execution results."""

import xml.etree.ElementTree as ET
from pathlib import Path

from caqf.runner import ExecutionResult, ExecutionStatus


def generate_junit_report(
    results: list[ExecutionResult],
    output_path: str,
    suite_name: str = "Conversational AI QA Matrix",
) -> None:
    """Generate JUnit XML report from test execution results.
    
    Args:
        results: List of ExecutionResult objects
        output_path: Path where to write the JUnit XML file
        suite_name: Name of the test suite (default: "Conversational AI QA Matrix")
        
    Raises:
        OSError: If the file cannot be written
    """
    # Create testsuite element
    testsuite = ET.Element("testsuite")
    testsuite.set("name", suite_name)
    
    # Count statuses
    total_tests = len(results)
    failures = sum(1 for r in results if r.status == ExecutionStatus.FAIL)
    skipped = sum(1 for r in results if r.status == ExecutionStatus.BLOCKED)
    errors = 0  # We don't distinguish errors from failures
    
    testsuite.set("tests", str(total_tests))
    testsuite.set("failures", str(failures))
    testsuite.set("skipped", str(skipped))
    testsuite.set("errors", str(errors))
    
    # Add testcase elements
    for result in results:
        testcase = ET.SubElement(testsuite, "testcase")
        testcase.set("name", result.test_case_id)
        testcase.set("classname", suite_name)
        
        if result.status == ExecutionStatus.FAIL:
            # Add failure element
            failure = ET.SubElement(testcase, "failure")
            failure.set("message", result.details or "Test failed")
            
            # Build failure message from failed_reasons
            failure_parts = []
            if result.failed_reasons:
                failure_parts.extend(result.failed_reasons)
            if result.details:
                failure_parts.append(result.details)
            
            failure_text = "\n".join(failure_parts) if failure_parts else "Test failed"
            failure.text = failure_text
            
        elif result.status == ExecutionStatus.BLOCKED:
            # Add skipped element
            skipped_elem = ET.SubElement(testcase, "skipped")
            skipped_elem.set("message", result.details or "Test blocked")
            if result.details:
                skipped_elem.text = result.details
    
    # Create XML tree and write to file
    tree = ET.ElementTree(testsuite)
    
    # Create parent directories if needed
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Write XML with proper formatting
    # ET.indent is available in Python 3.9+
    try:
        ET.indent(tree, space="  ")
    except AttributeError:
        # Python < 3.9 doesn't have indent, but XML is still valid
        pass
    
    tree.write(
        output_path,
        encoding="utf-8",
        xml_declaration=True,
    )

