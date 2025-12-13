"""Tests for CLI runner."""

import subprocess
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

from caqf.cli import create_parser, main, run_tests


def test_cli_help():
    """Test that --help works for main CLI."""
    # Test by calling parser directly since package may not be installed
    parser = create_parser()
    help_output = parser.format_help()
    assert "Conversational AI QA Framework" in help_output
    assert "run" in help_output


def test_cli_run_help():
    """Test that --help works for run subcommand."""
    parser = create_parser()
    # Get the run subparser directly
    run_parser = parser._subparsers._group_actions[0].choices["run"]
    help_output = run_parser.format_help()
    assert "--matrix-path" in help_output
    assert "--priority" in help_output
    assert "--use-synthetic-actual" in help_output


def test_cli_run_demo_mode():
    """Test CLI run with --use-synthetic-actual (demo mode)."""
    matrix_path = "templates/test-case-matrix.xlsx"
    
    # Check if matrix file exists
    matrix_file = Path(__file__).parent.parent / matrix_path
    if not matrix_file.exists():
        pytest.skip(f"Matrix file not found: {matrix_path}")
    
    # Run CLI with demo mode
    exit_code = run_tests(
        matrix_path=matrix_path,
        use_synthetic_actual=True,
        max_failures=10,
        show_failures=5,
    )
    
    # Should exit with 0 (no failures in demo mode with synthetic output)
    assert exit_code == 0


def test_cli_run_with_nonexistent_file():
    """Test CLI run with non-existent matrix file."""
    exit_code = run_tests(
        matrix_path="nonexistent-file.xlsx",
        use_synthetic_actual=False,
    )
    # Should exit with 1 (error)
    assert exit_code == 1


def test_cli_run_with_filters():
    """Test CLI run with filters applied."""
    matrix_path = "templates/test-case-matrix.xlsx"
    
    # Check if matrix file exists
    matrix_file = Path(__file__).parent.parent / matrix_path
    if not matrix_file.exists():
        pytest.skip(f"Matrix file not found: {matrix_path}")
    
    # Run CLI with filters
    exit_code = run_tests(
        matrix_path=matrix_path,
        priority="Critical",
        use_synthetic_actual=True,
        max_failures=10,
        show_failures=5,
    )
    
    # Should complete successfully (exit code 0 or 2 depending on results)
    assert exit_code in (0, 2)


def test_cli_run_no_command_shows_help():
    """Test that running without command shows help."""
    # Call main() directly with no args (simulates python -m caqf)
    exit_code = main([])
    # Should exit with 0 (help shown)
    assert exit_code == 0


def test_cli_run_max_failures():
    """Test CLI run with max-failures limit."""
    matrix_path = "templates/test-case-matrix.xlsx"
    
    # Check if matrix file exists
    matrix_file = Path(__file__).parent.parent / matrix_path
    if not matrix_file.exists():
        pytest.skip(f"Matrix file not found: {matrix_path}")
    
    # Run CLI with very low max_failures
    exit_code = run_tests(
        matrix_path=matrix_path,
        use_synthetic_actual=True,
        max_failures=1,
        show_failures=1,
    )
    
    # Should complete (exit code 0 or 2)
    assert exit_code in (0, 2)

