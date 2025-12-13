"""Pytest integration layer for loading and executing test cases from Excel matrix."""

from pathlib import Path

from caqf.data import CaseModel, load_test_cases
from caqf.rules import parse_expected_result_to_rules


def load_cases_for_pytest(path: str) -> list[CaseModel]:
    """Load test cases from Excel matrix file for pytest execution.
    
    Args:
        path: Path to the Excel file containing test cases
        
    Returns:
        List of CaseModel objects loaded from the Excel file
        
    Raises:
        FileNotFoundError: If the Excel file does not exist
        MatrixSchemaError: If required columns are missing
    """
    return load_test_cases(path)


def build_test_id(case: CaseModel) -> str:
    """Build a stable, filesystem-friendly test ID from a test case.
    
    Format: "TC-001__SC-001__ComponentName"
    - Uses double underscore as separator for clarity
    - Removes spaces and special characters from component name
    - Ensures deterministic, readable test IDs
    
    Args:
        case: The test case to build an ID for
        
    Returns:
        Stable test ID string suitable for pytest and filesystem use
    """
    # Clean component name: replace spaces with underscores, remove special chars
    component_clean = case.component.replace(" ", "_")
    # Remove any remaining special characters that might cause issues
    component_clean = "".join(c for c in component_clean if c.isalnum() or c == "_")
    
    # Build ID: test_case_id__scenario_id__component
    test_id = f"{case.test_case_id}__{case.scenario_id}__{component_clean}"
    
    return test_id


def generate_synthetic_actual_output(case: CaseModel) -> str:
    """Generate a simple synthetic actual_output for demo purposes.
    
    This is a DEMO mode feature that creates deterministic synthetic output
    likely to satisfy the expected_result rules. It's minimal and intended
    only for portfolio/demo purposes, not real testing.
    
    Strategy:
    - If expected_result contains rule prefixes, extract text from CONTAINS rules
    - Otherwise, use the expected_result text itself
    - Always ensure output is non-empty to satisfy NOT_EMPTY rule
    
    Args:
        case: The test case to generate synthetic output for
        
    Returns:
        Synthetic actual_output string
    """
    expected = case.expected_result
    
    # Parse rules to understand what's expected
    rules = parse_expected_result_to_rules(expected)
    
    # Look for CONTAINS rules to extract expected text
    contains_texts = []
    for rule in rules:
        if rule.name == "CONTAINS":
            text = rule.params.get("text", "")
            if text:
                contains_texts.append(text)
    
    # If we found CONTAINS text, use it
    if contains_texts:
        # Use the first CONTAINS text, or combine them
        synthetic = contains_texts[0]
        if len(contains_texts) > 1:
            synthetic = " ".join(contains_texts[:2])  # Limit to first 2
    else:
        # No CONTAINS rules found, use expected_result as-is (plain English mode)
        # But limit length to avoid overly long synthetic output
        synthetic = expected[:200] if len(expected) > 200 else expected
        if not synthetic.strip():
            synthetic = "Response generated for demo purposes"
    
    # Ensure it's not empty (satisfies NOT_EMPTY rule)
    if not synthetic.strip():
        synthetic = "Demo response"
    
    return synthetic

