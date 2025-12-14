# Conversational AI QA Framework

A production-ready QA framework for testing conversational AI systems — chatbots and voice agents — with a focus on behavior validation, regression safety, and CI/CD integration.
This framework helps teams test conversational AI systems the same way they test traditional software:
with predictable test cases, regression safety, and CI-friendly reports.

## The Problem

Conversational AI systems fail differently from traditional software. Outputs are non-deterministic, bugs appear as behavioral regressions rather than crashes, and small changes in prompts or workflows can silently break user flows. Most monitoring focuses on uptime, not conversation quality.

This framework provides **QA structure for conversational AI** — enabling teams to define expected behaviors, validate responses systematically, and catch regressions before they reach production.

## Why This Framework Exists

Teams building chatbots and voice agents need predictable quality assurance, not experimental AI development. This framework addresses the gap between conversational AI capabilities and production-ready QA practices by providing:

- **Deterministic validation** at the QA layer (rules, expectations, execution)
- **Regression testing** for conversational flows
- **CI/CD integration** with standard reporting formats
- **Vendor-agnostic design** that works with any LLM or platform

---

## Key Features

- **Excel-driven test matrix**: Define test cases in Excel, maintainable by non-developers
- **Rules engine**: Validate responses using rule-based expectations (CONTAINS, NOT_EMPTY, LENGTH_MIN, etc.)
- **Test runner**: Execute test cases and generate execution results (PASS/FAIL/BLOCKED)
- **Pytest integration**: Run tests as part of your existing test suite
- **CLI runner**: Execute tests from command line, ideal for CI/CD pipelines
- **JUnit XML reports**: Standard format compatible with Jenkins, GitHub Actions, GitLab CI, and other CI systems
- **Markdown reports**: Human-readable test summaries with failure details
- **Demo mode**: Synthetic output generation for portfolio demonstrations and CI validation

---
## Real-world usage

This framework validates **real conversational AI outputs**.
In production environments, test cases are executed against **actual chatbot or voice agent responses**, provided via the Excel matrix or external pipelines.

A **demo mode** is included purely for:
- portfolio demonstrations
- CI validation
- framework testing without live integrations

Demo mode is optional and never required for real usage.

---
## Quickstart

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```

2. Activate the virtual environment:
   ```bash
   # On Windows (PowerShell)
   .venv\Scripts\Activate.ps1
   
   # On Windows (Command Prompt)
   .venv\Scripts\activate.bat
   
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install package (recommended):
   ```bash
   pip install -e .
   ```

5. Run tests:
   ```bash
   # Run unit tests only
   pytest -q -m unit
   
   # Run matrix tests (requires Actual Result in Excel)
   pytest -q -m matrix
   
   # Demo matrix run with synthetic actual output
   pytest -q -m matrix --use-synthetic-actual
   
   # Run all tests
   pytest -q
   ```

**Note:** Tests will work even without step 4 (package installation) thanks to `tests/conftest.py`, but installing the package is recommended for development.

---

## Execution Modes

The framework supports two execution modes, each suited for different use cases:

### Pytest-based Execution

Use pytest when:
- Running tests as part of a development workflow
- Integrating with existing pytest-based test suites
- Using pytest plugins and fixtures
- Running tests in IDEs with pytest support

```bash
# Run with filters
pytest -q -m matrix --priority "Critical,High" --component "Chatbot"

# Run in demo mode
pytest -q -m matrix --use-synthetic-actual
```

### CLI-based Execution

Use the CLI when:
- Running tests in CI/CD pipelines
- Generating reports for external systems
- Executing tests from scripts or automation
- Running tests without pytest infrastructure

```bash
# Basic execution
python -m caqf run --matrix-path path/to/matrix.xlsx

# With reports for CI
python -m caqf run --junit-report reports/junit.xml --md-report reports/report.md
```

**Note:** The CLI requires the package to be installed (`pip install -e .`). This reflects real-world usage in CI/CD and production-like environments.

---

## Demo Mode

The framework includes a **demo mode** (`--use-synthetic-actual`) that generates synthetic actual outputs when the "Actual Result" column in the Excel matrix is empty.

### When to Use Demo Mode

- **Portfolio demonstrations**: Show framework capabilities without requiring a live chatbot
- **CI validation**: Verify that test infrastructure works correctly
- **Documentation examples**: Provide runnable examples that don't depend on external systems
- **Framework development**: Test the framework itself without integration dependencies

### Production Usage

In production environments, **do not use demo mode**. Instead:

1. Populate the "Actual Result" column in your Excel matrix with real responses from your chatbot or voice system
2. Run the framework without `--use-synthetic-actual`
3. The framework will validate actual responses against expected rules

Demo mode is intended for demonstrations and validation only. Real projects should provide actual outputs from their conversational AI systems.

---

## Example Usage

The [customer support chatbot example](examples/customer-support-chatbot/) demonstrates a complete, real-world use case for an e-commerce platform's support chatbot.

**What you'll learn:**
- How to structure test cases in an Excel matrix for customer support scenarios
- How to define expected behaviors using rule-based validation
- How to run automated validation with the CLI
- How to generate reports for CI/CD integration
- How to handle different test scenarios (order status inquiries, return requests, account management, etc.)

**The example includes:**
- Ready-to-use test matrix (`test-case-matrix.xlsx`) with 12 test cases
- Step-by-step documentation explaining the business context
- PowerShell script (`run_demo.ps1`) for quick demonstration

For CI/CD integration examples, see [docs/ci-example.md](docs/ci-example.md).

---

## CLI Usage

The framework provides a CLI runner to execute test cases from the Excel matrix without pytest.

```bash
# Show help
python -m caqf --help

# Run tests with default matrix
python -m caqf run

# Run with custom matrix path
python -m caqf run --matrix-path path/to/matrix.xlsx

# Run with filters
python -m caqf run --priority "Critical,High" --component "Chatbot"

# Run in demo mode (generates synthetic actual output)
python -m caqf run --use-synthetic-actual

# Run with failure limits
python -m caqf run --max-failures 5 --show-failures 3

# Generate reports
python -m caqf run --junit-report reports/junit.xml --md-report reports/report.md
```

### CLI Options

- `--matrix-path`: Path to Excel test case matrix file (default: `templates/test-case-matrix.xlsx`)
- `--priority`: Filter by priority (comma-separated, e.g., `"Critical,High"`)
- `--status`: Filter by status (comma-separated, e.g., `"Ready"`)
- `--component`: Filter by component (comma-separated, e.g., `"Chatbot,Voice"`)
- `--use-synthetic-actual`: Generate synthetic actual output for demo when actual_result is missing
- `--max-failures`: Stop early after N failures (default: 10)
- `--show-failures`: Print top N failure details (default: 5)
- `--junit-report`: Path to write JUnit XML report (optional, for CI integration)
- `--md-report`: Path to write Markdown report (optional, for human-readable output)

### Exit Codes

- `0`: All tests passed (no failures)
- `2`: Some tests failed
- `1`: Runtime error (file missing, schema error, etc.)

## What problems this framework solves for teams

- Undetected conversational regressions after prompt or workflow changes
- Manual QA effort for chatbot testing that does not scale
- Lack of CI/CD visibility into conversational quality
- Non-technical stakeholders unable to maintain test cases
- No standard reporting for conversational AI behavior

This framework turns conversational behavior into **testable, reviewable, and automatable artifacts**.

---

## Who This Is For

This framework is designed for:

- **QA engineers** testing conversational AI systems
- **Engineering teams** building chatbots or voice agents who need regression testing
- **Companies** deploying conversational AI who want to ensure quality and catch regressions
- **Teams** using workflow automation platforms (e.g., n8n) with conversational interfaces

**Typical use cases:**
- Customer support chatbots
- Voice agents (IVR, AI call assistants)
- Workflow-driven conversational systems
- AI agents embedded into SaaS products

---

## What This Framework Is NOT

To avoid confusion, this project does **not**:

- Build or train AI models
- Implement voice or chatbot platforms
- Develop agent logic or workflows
- Replace ML engineering or data science
- Provide LLM orchestration or API management

This is a **QA and testing framework**, focused on validation and reliability. It tests conversational AI systems but does not implement them.

---

## Production Readiness

This framework is intentionally designed to be:

- **Testable**: comprehensive unit and integration test coverage
- **Deterministic**: Rules, expectations, and execution are predictable at the QA layer
- **CI/CD-friendly**: JUnit XML and Markdown reports, standard exit codes
- **Vendor-agnostic**: No dependency on specific LLMs or platforms

It can be adopted incrementally — from documentation-only QA to fully automated regression pipelines.

---

## Project Structure

```
conversational-ai-qa-framework/
├── src/
│   └── caqf/                      # Main package (Conversational AI QA Framework)
│       ├── __init__.py
│       ├── config.py              # Configuration loader
│       ├── data/                  # Data loading and models
│       │   ├── models.py          # CaseModel dataclass
│       │   └── matrix_loader.py  # Excel matrix loader
│       ├── rules/                 # Rules engine
│       │   ├── types.py           # Response and Rule types
│       │   ├── validators.py      # Rule validators
│       │   └── matchers.py        # Rule parsing and evaluation
│       ├── runner/                # Test execution layer
│       │   ├── execution_result.py
│       │   └── test_runner.py
│       ├── pytest_integration.py  # Pytest integration helpers
│       ├── cli.py                  # CLI implementation
│       ├── __main__.py             # CLI entry point (python -m caqf)
│       └── reporting/              # Report generation
│           ├── junit_report.py     # JUnit XML reports
│           └── markdown_report.py  # Markdown reports
├── tests/                          # Test suite
│   ├── __init__.py
│   ├── conftest.py                # Pytest configuration and hooks
│   ├── test_smoke.py              # Smoke tests
│   ├── test_matrix_loader.py     # Matrix loader tests
│   ├── test_rules_engine.py      # Rules engine tests
│   ├── test_test_runner.py       # Test runner tests
│   ├── test_e2e_from_excel.py    # End-to-end Excel matrix tests
│   ├── test_cli.py                # CLI tests
│   └── test_reporting.py          # Reporting tests
├── docs/                           # Documentation
│   ├── ci-example.md              # CI/CD integration examples
│   ├── test-strategy.md           # Testing strategy documentation
│   ├── test-scenarios.md          # Test scenario examples
│   ├── regression-checklist.md    # Regression testing checklist
│   └── monitoring-metrics.md      # Monitoring and metrics templates
├── examples/                       # Example use cases
│   └── customer-support-chatbot/   # Customer support chatbot example
│       ├── README.md               # Example documentation
│       ├── test-case-matrix.xlsx   # Example test matrix
│       └── run_demo.ps1            # Demo runner script
├── templates/                      # QA templates
│   ├── test-case-matrix.xlsx      # Excel test case matrix template
│   └── bug-report-template.md     # Bug report template
├── pytest.ini                     # Pytest configuration
├── pyproject.toml                 # Project configuration
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
└── README.md
```

---

## License

This project is licensed under the MIT License.

---

## Additional Resources

- [CI/CD Integration Examples](docs/ci-example.md) - GitHub Actions, Jenkins, GitLab CI examples
- [Test Strategy Documentation](docs/test-strategy.md) - Testing philosophy and approach
- [Test Scenarios](docs/test-scenarios.md) - Example test scenarios for conversational AI
- [Regression Checklist](docs/regression-checklist.md) - Pre-deployment validation checklist
- [Monitoring Metrics](docs/monitoring-metrics.md) - Quality metrics and monitoring templates

---

If you are looking for **QA support, test strategy, or validation for conversational AI systems or CI pipeline**, this framework reflects production-ready practices used in real projects.
