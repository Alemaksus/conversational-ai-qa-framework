# Customer Support Chatbot Demo Runner
# This script demonstrates running the QA framework with the example test matrix

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Customer Support Chatbot QA Demo" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "test-case-matrix.xlsx")) {
    Write-Host "Error: test-case-matrix.xlsx not found in current directory" -ForegroundColor Red
    Write-Host "Please run this script from the examples/customer-support-chatbot/ directory" -ForegroundColor Yellow
    exit 1
}

# Check if framework is installed
try {
    python -m caqf --help | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Framework not installed"
    }
} catch {
    Write-Host "Error: Framework not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please run 'pip install -e .' from the project root" -ForegroundColor Yellow
    exit 1
}

Write-Host "Running test matrix with synthetic output (demo mode)..." -ForegroundColor Green
Write-Host ""

# Create reports directory
$reportsDir = "reports"
if (-not (Test-Path $reportsDir)) {
    New-Item -ItemType Directory -Path $reportsDir | Out-Null
}

# Run the framework
python -m caqf run `
    --matrix-path test-case-matrix.xlsx `
    --use-synthetic-actual `
    --junit-report "$reportsDir/junit.xml" `
    --md-report "$reportsDir/report.md"

$exitCode = $LASTEXITCODE

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
if ($exitCode -eq 0) {
    Write-Host "Demo completed successfully!" -ForegroundColor Green
} elseif ($exitCode -eq 2) {
    Write-Host "Demo completed with test failures (expected in demo mode)" -ForegroundColor Yellow
} else {
    Write-Host "Demo completed with errors" -ForegroundColor Red
}
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Reports generated:" -ForegroundColor Green
Write-Host "  - JUnit XML: $reportsDir/junit.xml" -ForegroundColor White
Write-Host "  - Markdown:  $reportsDir/report.md" -ForegroundColor White
Write-Host ""
Write-Host "To view the Markdown report:" -ForegroundColor Cyan
Write-Host "  Get-Content $reportsDir/report.md" -ForegroundColor Gray
Write-Host ""

exit $exitCode

