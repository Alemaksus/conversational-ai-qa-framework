# Customer Support Chatbot Example

This example demonstrates how to use the Conversational AI QA Framework to test a customer support chatbot for an e-commerce platform.

## Business Context

**Scenario**: An e-commerce company has deployed a customer support chatbot to handle common customer inquiries, reducing support ticket volume and improving response times.

**Challenge**: After each deployment (prompt updates, workflow changes, model upgrades), the team needs confidence that critical customer interactions still work correctly. Manual testing is time-consuming and doesn't scale.

**Solution**: Use the QA framework to define expected behaviors in an Excel matrix, run automated validation, and catch regressions before they reach production.

## Test Coverage

This example includes test cases for:

- **Order Status Inquiries**: Customers checking order delivery status
- **Return Requests**: Processing return and refund requests
- **Product Information**: Answering questions about products, availability, and specifications
- **Account Management**: Password resets, profile updates, subscription changes
- **Error Handling**: Unrecognized intents, missing context, system errors
- **Compliance**: GDPR-related requests, data privacy inquiries

## Test Matrix Structure

The `test-case-matrix.xlsx` file contains:

- **12 test cases** covering critical customer support scenarios
- **Priority levels**: Critical, High, Medium
- **Components**: Chatbot, NLU, Workflow, API integrations
- **Expected results**: Defined using rule-based validation (CONTAINS, NOT_EMPTY, etc.)

## Running the Example

### Prerequisites

1. Python 3.10+ installed
2. Framework installed: `pip install -e .` (from project root)
3. Excel file: `test-case-matrix.xlsx` in this directory

### Quick Start

**Windows (PowerShell):**
```powershell
.\run_demo.ps1
```

**Manual Run:**
```bash
# Run with synthetic output (demo mode)
python -m caqf run --matrix-path test-case-matrix.xlsx --use-synthetic-actual

# Run with actual results (requires Actual Result column in Excel)
python -m caqf run --matrix-path test-case-matrix.xlsx

# Run with filters (only Critical priority tests)
python -m caqf run --matrix-path test-case-matrix.xlsx --priority "Critical" --use-synthetic-actual

# Generate reports
python -m caqf run --matrix-path test-case-matrix.xlsx --use-synthetic-actual --junit-report reports/junit.xml --md-report reports/report.md
```

## Interpreting Results

### PASS
- All validation rules passed
- Response meets expected criteria
- Ready for production

### FAIL
- One or more validation rules failed
- Review `failed_reasons` in the output
- Check the actual response against expected rules
- Fix the issue before deployment

### BLOCKED
- No actual output available (Actual Result column empty)
- Use `--use-synthetic-actual` for demo purposes
- In production, populate Actual Result from your chatbot API

## Integration with Your Chatbot

To use this framework with your actual chatbot:

1. **Populate Actual Results**: After each test run, capture the chatbot's actual responses and add them to the "Actual Result" column in Excel.

2. **Define Expected Rules**: Use the framework's rule syntax in the "Expected Result" column:
   - `CONTAINS: order number` - Response must contain "order number"
   - `NOT_EMPTY` - Response must not be empty
   - `LENGTH_MIN: 10` - Response must be at least 10 characters
   - Combine rules: `CONTAINS: confirmation AND NOT_EMPTY`

3. **Run in CI/CD**: See `../../docs/ci-example.md` for GitHub Actions and Jenkins integration examples.

## Customization

### Adding New Test Cases

1. Open `test-case-matrix.xlsx`
2. Add a new row with:
   - Test Case ID (unique identifier)
   - Scenario ID (grouping identifier)
   - Component (Chatbot, NLU, Workflow, etc.)
   - Test Description
   - Expected Result (using rule syntax)
3. Run the framework to validate

### Modifying Expected Results

Update the "Expected Result" column to reflect changes in your chatbot's behavior. The framework will validate against these rules.

## Next Steps

- Review the generated reports (`reports/junit.xml` and `reports/report.md`)
- Integrate into your CI/CD pipeline (see `../../docs/ci-example.md`)
- Expand test coverage for additional scenarios
- Set up monitoring dashboards using the JUnit XML output

## Support

For framework documentation, see the main [README.md](../../README.md).

For CI/CD integration examples, see [docs/ci-example.md](../../docs/ci-example.md).

