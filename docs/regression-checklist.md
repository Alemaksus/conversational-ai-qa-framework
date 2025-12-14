# Regression Testing Checklist

## Overview

This checklist ensures that existing functionality continues to work after system changes (prompt updates, model changes, workflow modifications, etc.).

## Pre-Change Baseline

Before making any changes, establish a baseline:

- [ ] Document current behavior for critical flows
- [ ] Capture sample conversations for key scenarios
- [ ] Record current quality metrics
- [ ] Note any known issues or limitations

## Change Categories

### Prompt Changes
- [ ] Test all intents that use the modified prompt
- [ ] Verify response quality hasn't degraded
- [ ] Check for unintended behavior changes
- [ ] Validate tone and style consistency

### Model Updates
- [ ] Test intent recognition accuracy
- [ ] Verify response generation quality
- [ ] Check for new failure modes
- [ ] Validate performance (latency, cost)

### Workflow Changes
- [ ] Test all paths through modified workflow
- [ ] Verify integration points still work
- [ ] Check error handling paths
- [ ] Validate state management

### Integration Updates
- [ ] Test API contracts
- [ ] Verify data flow
- [ ] Check authentication/authorization
- [ ] Validate error propagation

## Critical Path Regression Tests

### User Authentication
- [ ] Login flow works
- [ ] Session management intact
- [ ] Authentication errors handled

### Core User Flows
- [ ] Primary use cases still functional
- [ ] Multi-turn conversations work
- [ ] Context preservation verified
- [ ] Response quality maintained

### Error Handling
- [ ] Error messages appropriate
- [ ] Fallback mechanisms work
- [ ] Recovery paths functional
- [ ] User experience not degraded

### Performance
- [ ] Response times acceptable
- [ ] No new latency issues
- [ ] Resource usage within limits
- [ ] No memory leaks introduced

## Quality Metrics Validation

After changes, verify metrics haven't regressed:

- [ ] Intent recognition accuracy
- [ ] Response appropriateness score
- [ ] User satisfaction metrics
- [ ] Error rate
- [ ] Average conversation length
- [ ] Task completion rate

## Scenario-Based Regression

Execute regression test suite:

- [ ] SCENARIO-001: Basic User Query
- [ ] SCENARIO-002: Multi-Turn Conversation
- [ ] SCENARIO-003: Unrecognized Intent
- [ ] SCENARIO-004: Missing Context
- [ ] SCENARIO-005: Order Placement Flow
- [ ] SCENARIO-006: Support Ticket Creation
- [ ] SCENARIO-007: Very Long User Input
- [ ] SCENARIO-008: Rapid Multiple Messages
- [ ] SCENARIO-009: ASR Error Recovery (if applicable)
- [ ] SCENARIO-010: Background Noise Handling (if applicable)

## Edge Case Validation

- [ ] Boundary conditions still handled
- [ ] Invalid inputs processed correctly
- [ ] Extreme values don't break system
- [ ] Concurrent requests handled

## Integration Points

- [ ] External APIs still accessible
- [ ] Database queries work correctly
- [ ] Message queue processing intact
- [ ] Logging and monitoring functional

## Post-Change Validation

After deployment:

- [ ] Smoke tests pass
- [ ] Monitoring shows no anomalies
- [ ] Error logs clean
- [ ] User feedback reviewed
- [ ] Quality metrics stable

## Rollback Criteria

If any of the following occur, consider rollback:

- [ ] Critical user flow broken
- [ ] Quality metrics drop significantly
- [ ] Error rate increases substantially
- [ ] Performance degradation
- [ ] User complaints spike

## Documentation Updates

- [ ] Update test scenarios if behavior changed intentionally
- [ ] Document any new known issues
- [ ] Update monitoring metrics if needed
- [ ] Revise regression checklist based on learnings

## Sign-Off

- [ ] All critical tests passed
- [ ] Quality metrics acceptable
- [ ] No blocking issues found
- [ ] Team sign-off obtained
- [ ] Ready for production deployment

## Notes

- Date of change: ___________
- Change description: ___________
- Tester: ___________
- Issues found: ___________
- Resolution: ___________


