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

