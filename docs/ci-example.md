# CI/CD Integration Examples

This document shows how to integrate the Conversational AI QA Framework into your CI/CD pipeline. The framework generates JUnit XML reports that are compatible with most CI systems.

## Overview

The framework's CLI runner produces:
- **JUnit XML reports** for CI system integration (Jenkins, GitHub Actions, GitLab CI, etc.)
- **Markdown reports** for human-readable summaries
- **Exit codes** that indicate test status (0 = pass, 2 = failures, 1 = errors)

## GitHub Actions

### Basic Example

```yaml
name: QA Framework Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -e .
    
    - name: Run QA Framework Tests
      run: |
        python -m caqf run \
          --matrix-path examples/customer-support-chatbot/test-case-matrix.xlsx \
          --junit-report reports/junit.xml \
          --md-report reports/report.md
    
    - name: Publish Test Results
      uses: EnricoMi/publish-unit-test-result-action@v2
      if: always()
      with:
        files: reports/junit.xml
    
    - name: Upload Markdown Report
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: test-report
        path: reports/report.md
```

### With Matrix Testing

```yaml
name: QA Framework Tests

on:
  push:
    branches: [ main ]
  schedule:
    - cron: '0 2 * * *'  # Run daily at 2 AM

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        priority: [Critical, High, Medium]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -e .
    
    - name: Run QA Framework Tests (${{ matrix.priority }})
      run: |
        python -m caqf run \
          --matrix-path examples/customer-support-chatbot/test-case-matrix.xlsx \
          --priority "${{ matrix.priority }}" \
          --junit-report reports/junit-${{ matrix.priority }}.xml \
          --md-report reports/report-${{ matrix.priority }}.md
    
    - name: Publish Test Results
      uses: EnricoMi/publish-unit-test-result-action@v2
      if: always()
      with:
        files: reports/junit-${{ matrix.priority }}.xml
```

### With Slack Notifications

```yaml
    - name: Notify on Failure
      if: failure()
      uses: 8398a7/action-slack@v3
      with:
        status: ${{ job.status }}
        text: 'QA Framework tests failed. Check the test report for details.'
        webhook_url: ${{ secrets.SLACK_WEBHOOK_URL }}
```

## Jenkins

### Pipeline Script (Jenkinsfile)

```groovy
pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Setup') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install -e .
                '''
            }
        }
        
        stage('Run QA Tests') {
            steps {
                sh '''
                    . venv/bin/activate
                    python -m caqf run \
                        --matrix-path examples/customer-support-chatbot/test-case-matrix.xlsx \
                        --junit-report reports/junit.xml \
                        --md-report reports/report.md
                '''
            }
        }
        
        stage('Publish Test Results') {
            steps {
                junit 'reports/junit.xml'
                publishHTML([
                    reportDir: 'reports',
                    reportFiles: 'report.md',
                    reportName: 'QA Test Report'
                ])
            }
        }
    }
    
    post {
        always {
            archiveArtifacts artifacts: 'reports/**/*', fingerprint: true
        }
        failure {
            emailext (
                subject: "QA Framework Tests Failed - ${env.JOB_NAME}",
                body: "Test execution failed. See attached report.",
                attachmentsPattern: 'reports/report.md'
            )
        }
    }
}
```

### Freestyle Project Configuration

1. **Build Step**: Add "Execute shell" or "Execute Windows batch command":
   ```bash
   python -m caqf run \
       --matrix-path examples/customer-support-chatbot/test-case-matrix.xlsx \
       --junit-report reports/junit.xml \
       --md-report reports/report.md
   ```

2. **Post-build Actions**:
   - Add "Publish JUnit test result report"
   - Test report XMLs: `reports/junit.xml`
   - Add "Publish HTML reports" (optional, for Markdown)
   - HTML directory to archive: `reports`

## GitLab CI

```yaml
stages:
  - test

qa-tests:
  stage: test
  image: python:3.10
  before_script:
    - pip install --upgrade pip
    - pip install -r requirements.txt
    - pip install -e .
  script:
    - python -m caqf run
          --matrix-path examples/customer-support-chatbot/test-case-matrix.xlsx
          --junit-report reports/junit.xml
          --md-report reports/report.md
  artifacts:
    reports:
      junit: reports/junit.xml
    paths:
      - reports/
    expire_in: 1 week
  only:
    - main
    - develop
    - merge_requests
```

## Azure DevOps

```yaml
trigger:
  branches:
    include:
      - main
      - develop

pool:
  vmImage: 'ubuntu-latest'

steps:
- task: UsePythonVersion@0
  inputs:
    versionSpec: '3.10'

- script: |
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install -e .
  displayName: 'Install dependencies'

- script: |
    python -m caqf run
      --matrix-path examples/customer-support-chatbot/test-case-matrix.xlsx
      --junit-report reports/junit.xml
      --md-report reports/report.md
  displayName: 'Run QA Framework Tests'

- task: PublishTestResults@2
  inputs:
    testResultsFiles: 'reports/junit.xml'
    testRunTitle: 'QA Framework Test Results'

- task: PublishBuildArtifacts@1
  inputs:
    pathToPublish: 'reports'
    artifactName: 'test-reports'
```

## Best Practices

### 1. Exit Code Handling

The framework returns:
- `0`: All tests passed
- `2`: Some tests failed (expected in some scenarios)
- `1`: Runtime error (file missing, configuration error)

In CI, you may want to allow exit code 2 for non-blocking test runs:

```bash
python -m caqf run --matrix-path test-case-matrix.xlsx || [ $? -eq 2 ]
```

### 2. Parallel Execution

Run different priority levels in parallel:

```yaml
strategy:
  matrix:
    priority: [Critical, High, Medium]
```

### 3. Scheduled Runs

Set up nightly or weekly regression tests:

```yaml
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
```

### 4. Artifact Retention

Keep test reports for analysis:

```yaml
artifacts:
  expire_in: 30 days
```

### 5. Notifications

Configure notifications for test failures:
- Slack
- Email
- Microsoft Teams
- Custom webhooks

## Troubleshooting

### JUnit XML Not Found

- Ensure the `--junit-report` path is correct
- Check that parent directories exist (framework creates them automatically)
- Verify write permissions in the reports directory

### Tests Always Pass in CI

- Check if you're using `--use-synthetic-actual` (demo mode)
- Verify that "Actual Result" column is populated in Excel
- Review the generated Markdown report for details

### Exit Code Issues

- Exit code 2 (failures) is expected when tests fail
- Exit code 1 indicates a configuration or runtime error
- Check CI logs for detailed error messages

## Next Steps

- Customize test matrices for your specific use cases
- Integrate with your chatbot API to populate actual results automatically
- Set up dashboards using JUnit XML data
- Configure alerting for critical test failures


