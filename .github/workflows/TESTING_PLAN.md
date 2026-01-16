# Testing Plan for Issue Triage Workflow

## Overview
This document outlines the testing plan for the `.github/workflows/issue-opened.yml` workflow, which handles:
1. Duplicate issue detection using Gemini AI
2. Issue triage and labeling
3. AI assessment and processing
4. Slack notifications

## Bugs Fixed

### 1. Missing `repo_name` Output
- **Issue**: The "Verify Issue Still Open" step didn't set `repo_name` output, which is required by the AI Assessment step
- **Fix**: Added `core.setOutput('repo_name', context.repo.repo);` to the verify step

### 2. Missing Error Handling
- **Issue**: If the verify step failed, subsequent conditionals would fail
- **Fix**: Added `continue-on-error: true` to the verify step and improved conditional checks to verify step outcomes

### 3. Incomplete Conditional Logic
- **Issue**: Conditionals didn't check if previous steps succeeded before accessing their outputs
- **Fix**: Added `steps.verify-issue-open.outcome == 'success'` and `steps.get-issue.outcome == 'success'` checks to all dependent steps

### 4. Missing Assessment Output Check
- **Issue**: Process Assessments step could fail if AI assessment didn't produce output
- **Fix**: Added `steps.ai-assessment.outcome == 'success'` check to Process Assessments step

## Test Scenarios

### Test Category 1: Duplicate Detection

#### Test 1.1: Duplicate Issue Found
**Objective**: Verify that when a duplicate issue is detected, the workflow:
- Adds 'duplicate' label
- Adds a comment with the original issue number
- Closes the issue
- Skips all subsequent triage steps

**Steps**:
1. Create an issue with title "Bug: API server crashes"
2. Create a second issue with similar title "API server crashes when handling requests"
3. Trigger workflow on the second issue
4. Verify:
   - Issue #2 has 'duplicate' label
   - Issue #2 has a comment mentioning Issue #1
   - Issue #2 is closed
   - Workflow logs show triage steps were skipped

**Expected Result**: Issue closed as duplicate, no triage performed

---

#### Test 1.2: No Duplicate Found
**Objective**: Verify that when no duplicate is found, normal triage continues

**Steps**:
1. Create a unique issue with title "New feature: Add monitoring dashboard"
2. Trigger workflow
3. Verify:
   - Issue remains open
   - All triage steps execute
   - AI assessment is performed
   - Labels are applied
   - Slack notification sent (if configured)

**Expected Result**: Full triage workflow executes successfully

---

#### Test 1.3: Duplicate Check Fails (API Error)
**Objective**: Verify workflow continues even if duplicate check fails

**Steps**:
1. Temporarily break Gemini API key or settings
2. Create a new issue
3. Trigger workflow
4. Verify:
   - Duplicate check step fails gracefully
   - Verify step still executes
   - Triage continues normally

**Expected Result**: Workflow continues despite duplicate check failure

---

### Test Category 2: Issue State Verification

#### Test 2.1: Issue Already Closed
**Objective**: Verify workflow handles issues that are already closed

**Steps**:
1. Create and immediately close an issue
2. Edit the issue to trigger workflow
3. Verify:
   - Verify step detects issue is closed
   - All triage steps are skipped
   - Workflow completes without errors

**Expected Result**: Workflow skips triage for closed issues

---

#### Test 2.2: Issue Closed During Workflow Execution
**Objective**: Verify workflow handles race condition where issue is closed mid-execution

**Steps**:
1. Create an issue
2. Trigger workflow
3. Manually close the issue while workflow is running
4. Verify:
   - Verify step detects closed state
   - Subsequent steps are skipped
   - No errors occur

**Expected Result**: Workflow gracefully handles mid-execution closure

---

### Test Category 3: Normal Triage Flow

#### Test 3.1: Complete Triage Flow
**Objective**: Verify all triage steps execute correctly for a valid issue

**Steps**:
1. Create a well-formed bug report with:
   - Clear title
   - Description
   - Steps to reproduce
   - Environment details
2. Trigger workflow
3. Verify each step:
   - ✅ Duplicate check runs
   - ✅ Issue verification succeeds
   - ✅ Get Issue Details succeeds
   - ✅ AI Assessment produces output
   - ✅ kind/bug label is added
   - ✅ Process Assessments creates summary
   - ✅ Slack notification sent (if configured)

**Expected Result**: All steps execute successfully

---

#### Test 3.2: AI Assessment Failure
**Objective**: Verify workflow handles AI assessment failures gracefully

**Steps**:
1. Create an issue
2. Temporarily break AI assessment (invalid API key, etc.)
3. Trigger workflow
4. Verify:
   - AI Assessment step fails
   - Process Assessments step is skipped (due to conditional)
   - Other steps that don't depend on assessment still run
   - Workflow completes without crashing

**Expected Result**: Workflow continues despite AI assessment failure

---

### Test Category 4: Edge Cases

#### Test 4.1: Issue with Empty Body
**Objective**: Verify workflow handles issues with no body text

**Steps**:
1. Create an issue with only a title, no body
2. Trigger workflow
3. Verify:
   - No errors occur
   - Workflow handles empty body gracefully
   - AI assessment still runs (may produce different results)

**Expected Result**: Workflow handles empty body without errors

---

#### Test 4.2: Issue Edited (Not Just Opened)
**Objective**: Verify workflow works for both 'opened' and 'edited' trigger types

**Steps**:
1. Create an issue (triggers 'opened')
2. Edit the issue body (triggers 'edited')
3. Verify:
   - Workflow runs on both events
   - Duplicate check runs on edit (may find duplicates that didn't exist before)
   - Triage steps execute correctly

**Expected Result**: Workflow handles both trigger types

---

#### Test 4.3: Concurrent Workflow Runs
**Objective**: Verify concurrency control works correctly

**Steps**:
1. Create an issue
2. Quickly edit it multiple times to trigger concurrent runs
3. Verify:
   - Concurrency group prevents multiple runs
   - Only one workflow completes
   - No race conditions occur

**Expected Result**: Concurrency control prevents duplicate processing

---

### Test Category 5: Integration Tests

#### Test 5.1: End-to-End with Real Gemini API
**Objective**: Verify complete integration with Gemini API

**Prerequisites**:
- Valid `GEMINI_API_KEY` secret
- Valid `.gemini/settings.json` file
- GitHub MCP server configured

**Steps**:
1. Create a test issue
2. Run workflow in production environment
3. Monitor Gemini API calls
4. Verify:
   - Gemini successfully searches for duplicates
   - MCP server calls work correctly
   - Issue state changes are applied

**Expected Result**: Full integration works end-to-end

---

#### Test 5.2: Slack Notification Integration
**Objective**: Verify Slack notifications work correctly

**Prerequisites**:
- Valid `SLACK_WEBHOOK_URL` secret

**Steps**:
1. Create an issue
2. Trigger workflow
3. Verify:
   - Slack message is sent
   - Message contains correct issue details
   - Assessment output is included
   - Message formatting is correct

**Expected Result**: Slack notification sent successfully

---

## Manual Testing Checklist

### Pre-Testing Setup
- [ ] Verify all required secrets are configured:
  - [ ] `GITHUB_TOKEN` (auto-provided)
  - [ ] `GEMINI_API_KEY`
  - [ ] `SLACK_WEBHOOK_URL` (optional)
- [ ] Verify `.gemini/settings.json` exists and is valid
- [ ] Verify `.github/prompts/duplicate-check.prompt.txt` exists
- [ ] Verify `.github/prompts/bug-triage.prompt.yml` exists
- [ ] Verify all script files exist in `.github/scripts/`

### Testing Execution
- [ ] Test 1.1: Duplicate Issue Found
- [ ] Test 1.2: No Duplicate Found
- [ ] Test 1.3: Duplicate Check Fails
- [ ] Test 2.1: Issue Already Closed
- [ ] Test 2.2: Issue Closed During Execution
- [ ] Test 3.1: Complete Triage Flow
- [ ] Test 3.2: AI Assessment Failure
- [ ] Test 4.1: Issue with Empty Body
- [ ] Test 4.2: Issue Edited
- [ ] Test 4.3: Concurrent Workflow Runs
- [ ] Test 5.1: End-to-End with Real Gemini API
- [ ] Test 5.2: Slack Notification Integration

## Automated Testing Considerations

### Unit Tests (Future Enhancement)
- Mock GitHub API responses
- Test conditional logic
- Test output parsing
- Test error handling

### Integration Tests (Future Enhancement)
- Use GitHub Actions test framework
- Mock external APIs (Gemini, Slack)
- Test with test repository
- Validate workflow YAML syntax

## Monitoring and Validation

### Workflow Run Validation
After each test, verify:
1. **Workflow Status**: Check that workflow completes (success or expected failure)
2. **Step Outcomes**: Review each step's outcome in workflow logs
3. **Issue State**: Verify issue state matches expectations
4. **Labels**: Verify correct labels are applied
5. **Comments**: Verify comments are added correctly
6. **Logs**: Review logs for errors or warnings

### Key Metrics to Monitor
- Workflow execution time
- Step success/failure rates
- Duplicate detection accuracy
- False positive/negative rates for duplicates
- API call success rates (Gemini, GitHub, Slack)

## Rollback Plan

If issues are discovered:
1. Disable workflow by commenting out trigger or removing workflow file
2. Review logs to identify root cause
3. Fix bugs in development branch
4. Re-test using this plan
5. Re-enable workflow after validation

## Notes

- The linter warnings about Gemini action inputs are false positives (linter doesn't recognize the action)
- Workflow timeout is set to 10 minutes
- Concurrency is controlled per issue number
- All steps that depend on previous step outputs check for step success before accessing outputs
