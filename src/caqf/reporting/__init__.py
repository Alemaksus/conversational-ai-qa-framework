"""Reporting module for generating test execution reports."""

from caqf.reporting.junit_report import generate_junit_report
from caqf.reporting.markdown_report import generate_markdown_report

__all__ = ["generate_junit_report", "generate_markdown_report"]

