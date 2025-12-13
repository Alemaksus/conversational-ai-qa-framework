"""Markdown report generation for test execution results."""

from datetime import datetime
from pathlib import Path
from typing import Union

from caqf.data.models import CaseModel
from caqf.runner import ExecutionResult, ExecutionStatus


def generate_markdown_report(
    results: list[Union[ExecutionResult, tuple[CaseModel, ExecutionResult]]],
    output_path: str,
    max_rows: int = 20,
) -> None:
    """Generate Markdown report from test execution results.
    
    Args:
        results: List of ExecutionResult objects or tuples of (case, result)
        output_path: Path where to write the Markdown file
        max_rows: Maximum number of test cases to include in the table
        
    Raises:
        OSError: If the file cannot be written
    """
    # Handle both ExecutionResult and (case, result) tuple formats
    processed_results = []
    cases_map = {}
    
    for item in results:
        if isinstance(item, tuple):
            case, result = item
            processed_results.append(result)
            cases_map[result.test_case_id] = case
        else:
            processed_results.append(item)
    
    # Count statuses
    total = len(processed_results)
    pass_count = sum(1 for r in processed_results if r.status == ExecutionStatus.PASS)
    fail_count = sum(1 for r in processed_results if r.status == ExecutionStatus.FAIL)
    blocked_count = sum(1 for r in processed_results if r.status == ExecutionStatus.BLOCKED)
    
    # Build report content
    lines = []
    
    # Title and timestamp
    lines.append("# Test Execution Report")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    
    # Summary section
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Total:** {total}")
    lines.append(f"- **PASS:** {pass_count}")
    lines.append(f"- **FAIL:** {fail_count}")
    lines.append(f"- **BLOCKED:** {blocked_count}")
    lines.append("")
    
    # Test cases table (first max_rows)
    if processed_results:
        lines.append("## Test Cases")
        lines.append("")
        lines.append("| ID | Status | Component | Notes |")
        lines.append("|----|--------|-----------|-------|")
        
        for result in processed_results[:max_rows]:
            test_id = result.test_case_id
            status = result.status.value
            
            # Get component from case if available
            component = ""
            if test_id in cases_map:
                component = cases_map[test_id].component
            
            # Build notes
            notes_parts = []
            if result.details:
                # Truncate details for table
                details_short = result.details[:50] + "..." if len(result.details) > 50 else result.details
                notes_parts.append(details_short)
            
            notes = " ".join(notes_parts) if notes_parts else "-"
            
            # Escape pipe characters in table cells
            test_id = test_id.replace("|", "\\|")
            status = status.replace("|", "\\|")
            component = component.replace("|", "\\|")
            notes = notes.replace("|", "\\|")
            
            lines.append(f"| {test_id} | {status} | {component} | {notes} |")
        
        if len(processed_results) > max_rows:
            lines.append("")
            lines.append(f"*Showing first {max_rows} of {total} test cases*")
        lines.append("")
    
    # Failures section
    failures = [r for r in processed_results if r.status == ExecutionStatus.FAIL]
    if failures:
        lines.append("## Failures")
        lines.append("")
        
        for result in failures:
            lines.append(f"### {result.test_case_id}")
            lines.append("")
            
            # Failed reasons
            if result.failed_reasons:
                lines.append("**Failed Reasons:**")
                lines.append("")
                for reason in result.failed_reasons:
                    lines.append(f"- {reason}")
                lines.append("")
            
            # Applied rules
            if result.applied_rules:
                lines.append("**Applied Rules:**")
                lines.append("")
                lines.append(", ".join(result.applied_rules))
                lines.append("")
            
            # Details
            if result.details:
                lines.append("**Details:**")
                lines.append("")
                lines.append(result.details)
                lines.append("")
            
            lines.append("---")
            lines.append("")
    
    # Write to file
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

