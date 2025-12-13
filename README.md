# Conversational AI QA Framework

A **QA-first framework** for testing conversational systems — **chatbots and voice agents** — with a strong focus on **behavior validation, regression safety, monitoring, and workflow reliability**.

This project is designed for teams building conversational AI on top of workflow automation (e.g. n8n) who need **predictable quality**, not experimental AI development.

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

## Example Usage

See the [customer support chatbot example](examples/customer-support-chatbot/) for a complete, real-world use case demonstrating how to:

- Define test cases in an Excel matrix
- Run automated validation with the CLI
- Generate reports for CI/CD integration
- Handle different test scenarios (order status, returns, account management, etc.)

The example includes:
- Ready-to-use test matrix (`test-case-matrix.xlsx`)
- Step-by-step documentation
- PowerShell script for quick demo (`run_demo.ps1`)

For CI/CD integration examples, see [docs/ci-example.md](docs/ci-example.md).

---

## CLI Usage

The framework provides a CLI runner to execute test cases from the Excel matrix without pytest.

**Note:** The CLI requires the package to be installed (step 4 in Quickstart: `pip install -e .`). Without installation, `python -m caqf` will fail with "No module named caqf".

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
│   └── test_e2e_from_excel.py    # End-to-end Excel matrix tests
├── docs/                           # Documentation
│   └── ci-example.md              # CI/CD integration examples
├── examples/                       # Example use cases
│   └── customer-support-chatbot/   # Customer support chatbot example
│       ├── README.md               # Example documentation
│       ├── test-case-matrix.xlsx   # Example test matrix
│       └── run_demo.ps1            # Demo runner script
├── templates/                      # QA templates
│   └── test-case-matrix.xlsx      # Excel test case matrix template
├── pytest.ini                     # Pytest configuration
├── pyproject.toml                 # Project configuration
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
└── README.md
```

---

## Who this is for

This framework is useful if you are:

- A **startup or SaaS team** running chatbots or voice agents in production  
- A **product or engineering team** experiencing regressions after prompt, model, or workflow changes  
- A company that needs **QA structure for conversational AI**, but does not want to build ML infrastructure  
- A team preparing for **scale, audits, or long-term maintenance**

Typical use cases:
- Customer support chatbots  
- Voice agents (IVR, AI call assistants)  
- Workflow-driven conversational systems  
- AI agents embedded into SaaS products  

---

## What problem this framework solves

Conversational AI systems fail differently from traditional software:

- Outputs are **non-deterministic**
- Bugs often appear as **behavioral regressions**, not crashes
- Small changes in prompts or workflows can silently break user flows
- Monitoring usually focuses on uptime, not conversation quality

This framework addresses those gaps by providing **QA structure**, not AI implementation.

---

## What is included

This repository focuses on **QA artifacts and patterns**, not on building AI agents.

Included concepts and materials:

- **QA strategy for conversational systems**
- **Scenario-based test design** for chatbots and voice agents
- **Regression models** for conversational behavior
- **Failure mode analysis** (ASR, NLU, logic, latency, fallback paths)
- **Monitoring and metrics templates** for conversational quality
- **Documentation-first approach** suitable for distributed teams

The framework is intentionally **vendor-agnostic** and can be adapted to:
- Chatbots
- Voice platforms
- Workflow engines
- API-driven conversational systems

---

## What this framework is NOT

To avoid confusion, this project does **not**:

- Build or train AI models  
- Implement voice or chatbot platforms  
- Develop agent logic or workflows  
- Replace ML engineering or data science  

This is a **QA and testing framework**, focused on validation and reliability.

---

## How teams typically use it

Teams usually apply this framework to:

1. Define **expected conversational behavior**
2. Design **test scenarios** for critical user flows
3. Detect **regressions after changes**
4. Track conversational quality with **clear metrics**
5. Transfer QA ownership to non-specialists via documentation

It works well as:
- A starting point for **AI QA processes**
- A reference for **conversational testing strategy**
- A foundation for **automation or monitoring expansion**

---

## Why QA-first for conversational AI

Conversational systems behave more like **products** than algorithms.

Treating them as testable systems — with scenarios, regression, and monitoring — leads to:
- Fewer production incidents
- Faster iteration cycles
- Better user experience
- Lower long-term maintenance cost

---

## About this project

This repository is a **reference QA framework**, created to demonstrate:
- How conversational AI can be tested systematically
- How QA practices adapt to chatbots and voice agents
- How to reduce risk without overengineering AI solutions

---

If you are looking for **QA support, test strategy, or validation for conversational AI systems**, this framework reflects the approach I use in real projects.
