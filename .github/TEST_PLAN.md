# AI Issue Triage Workflow - Test Plan

## Overview
This document outlines test scenarios for the AI Issue Triage workflow to ensure all functionality works correctly.

## Prerequisites
- Repository has labels: `triage/needs-triage`, `kind/bug`, `kind/feature`
- GitHub Actions are enabled
- Access to repository to create issues

## Test Scenarios

### Scenario 1: Bug Report with Complete Information ✅
**Goal:** Test AI triage for a well-formed bug report

**Steps:**
1. Create new issue with:
   - Title: `[TEST] Cluster fails to start on AWS with custom VPC`
   - Labels: `triage/needs-triage`, `kind/bug`
   - Body:
     ```markdown
     **Describe the bug**
     Cluster installation fails during bootstrap phase with timeout errors when using custom VPC configuration on AWS.
     
     **Version**
     OKD 4.20.0-0.okd-2024-10-15-123456
     IPI installation method on AWS
     
     **How reproducible**
     100% - happens every time with custom VPC
     
     **Log Bundle**
     https://example.com/logs/bootstrap-logs.tar.gz
     ```

**Expected Results:**
- ✅ Workflow triggers (check Actions tab)
- ✅ `ai-triage` job runs successfully
- ✅ AI assessment comment posted on issue
- ✅ Label `ai:bug-triage:ready for review` applied (or similar)
- ✅ `triage/needs-triage` label removed
- ✅ Workflow summary shows assessment
- ✅ `notify-slack` job runs (if webhook configured)

**Verification:**
- Check issue comments for AI assessment
- Check issue labels for triage result
- Check Actions workflow run for success

---

### Scenario 2: Bug Report Missing Information ⚠️
**Goal:** Test AI triage identifies missing details

**Steps:**
1. Create new issue with:
   - Title: `[TEST] Something is broken`
   - Labels: `triage/needs-triage`, `kind/bug`
   - Body:
     ```markdown
     It doesn't work. Help!
     ```

**Expected Results:**
- ✅ Workflow triggers
- ✅ `ai-triage` job runs
- ✅ AI assessment identifies missing information
- ✅ Label `ai:bug-triage:missing details` applied (or similar)
- ✅ Assessment suggests what information is needed

---

### Scenario 3: Feature Request with Complete Information ✅
**Goal:** Test AI triage for a well-formed feature request

**Steps:**
1. Create new issue with:
   - Title: `[TEST] Add support for custom certificate authorities`
   - Labels: `triage/needs-triage`, `kind/feature`
   - Body:
     ```markdown
     **Use Case**
     Organizations using internal CA certificates need to trust custom CAs when deploying OKD clusters.
     
     **Proposed Solution**
     Add a configuration option to import custom CA certificates during cluster installation.
     
     **Value Proposition**
     Enables OKD deployment in enterprise environments with internal certificate authorities.
     ```

**Expected Results:**
- ✅ Workflow triggers
- ✅ `ai-triage` job runs
- ✅ AI assessment comment posted
- ✅ Label `ai:enhancement-triage:ready for consideration` applied (or similar)
- ✅ Enhancement assessment is appropriate

---

### Scenario 4: Feature Request Needs Refinement ⚠️
**Goal:** Test AI identifies incomplete feature requests

**Steps:**
1. Create new issue with:
   - Title: `[TEST] Make it better`
   - Labels: `triage/needs-triage`, `kind/feature`
   - Body:
     ```markdown
     Would be nice to have more features.
     ```

**Expected Results:**
- ✅ Workflow triggers
- ✅ AI assessment identifies missing details
- ✅ Label `ai:enhancement-triage:needs refinement` applied (or similar)

---

### Scenario 5: Issue Without Triage Label ❌
**Goal:** Verify workflow doesn't trigger without required label

**Steps:**
1. Create new issue with:
   - Title: `[TEST] Regular issue without triage`
   - Labels: `kind/bug` (NO `triage/needs-triage`)
   - Body: Any content

**Expected Results:**
- ❌ Workflow does NOT trigger
- ❌ No AI assessment comment
- ✅ Issue remains unchanged

---

### Scenario 6: Issue with Only Triage Label ⚠️
**Goal:** Test behavior when triage label exists but no kind label

**Steps:**
1. Create new issue with:
   - Title: `[TEST] Issue with only triage label`
   - Labels: `triage/needs-triage` (NO `kind/bug` or `kind/feature`)
   - Body: Any content

**Expected Results:**
- ✅ Workflow triggers
- ⚠️ AI assessment may not match any prompt (no mapping for label)
- ✅ Workflow completes but may not apply specific triage label

---

### Scenario 7: Issue Reopened 🔄
**Goal:** Test workflow on reopened issues

**Steps:**
1. Create and close an issue with `triage/needs-triage` and `kind/bug` labels
2. Reopen the issue

**Expected Results:**
- ✅ Workflow triggers on reopen event
- ✅ AI triage runs again
- ✅ Assessment comment posted

---

### Scenario 8: Issue Edited ✏️
**Goal:** Test workflow on edited issues

**Steps:**
1. Create issue without `triage/needs-triage` label
2. Edit issue to add `triage/needs-triage` and `kind/bug` labels

**Expected Results:**
- ✅ Workflow triggers on edit event
- ✅ AI triage runs
- ✅ Assessment based on updated content

---

### Scenario 9: Label Added After Creation 🏷️
**Goal:** Test workflow when label is added via labeling event

**Steps:**
1. Create issue with `kind/bug` label (no triage label)
2. Add `triage/needs-triage` label to the issue

**Expected Results:**
- ✅ Workflow triggers on labeled event
- ✅ AI triage runs
- ✅ Assessment comment posted

---

### Scenario 10: Slack Notification slack
**Goal:** Test Slack integration (if webhook configured)

**Prerequisites:**
- `SLACK_WEBHOOK_URL` secret must be configured in repository

**Steps:**
1. Create issue that triggers successful triage (e.g., Scenario 1)
2. Check Slack channel

**Expected Results:**
- ✅ Slack message posted with:
  - Issue title and number
  - Author
  - Labels
  - Repository info
  - Link to issue
  - AI triage assessment
- ✅ No duplicate AI summary section (removed in cleanup)

---

## Edge Cases to Test

### Edge Case 1: Empty Issue Body
- Create issue with only title and required labels
- Verify workflow handles gracefully

### Edge Case 2: Very Long Issue Body
- Create issue with extremely long body (>5000 characters)
- Verify workflow handles within token limits

### Edge Case 3: Special Characters in Title/Body
- Include emojis, special chars, markdown
- Verify proper escaping in Slack notification

---

## Verification Checklist

For each successful test, verify:

- [ ] Workflow appears in Actions tab
- [ ] `ai-triage` job completes successfully (green checkmark)
- [ ] `notify-slack` job completes (may show warning if webhook not configured)
- [ ] Issue has AI assessment comment
- [ ] Appropriate triage label applied (`ai:bug-triage:*` or `ai:enhancement-triage:*`)
- [ ] `triage/needs-triage` label removed
- [ ] Workflow summary accessible in Actions run
- [ ] No errors in workflow logs
- [ ] Slack notification sent (if configured)

---

## Test Results Template

| Scenario | Date | Status | Notes |
|----------|------|--------|-------|
| 1. Bug Report Complete | | ⬜ Pass / ⬜ Fail | |
| 2. Bug Report Incomplete | | ⬜ Pass / ⬜ Fail | |
| 3. Feature Request Complete | | ⬜ Pass / ⬜ Fail | |
| 4. Feature Request Incomplete | | ⬜ Pass / ⬜ Fail | |
| 5. No Triage Label | | ⬜ Pass / ⬜ Fail | |
| 6. Only Triage Label | | ⬜ Pass / ⬜ Fail | |
| 7. Issue Reopened | | ⬜ Pass / ⬜ Fail | |
| 8. Issue Edited | | ⬜ Pass / ⬜ Fail | |
| 9. Label Added | | ⬜ Pass / ⬜ Fail | |
| 10. Slack Notification | | ⬜ Pass / ⬜ Fail | |

---

## Cleanup
After testing, close or delete all test issues with `[TEST]` in the title to keep the repository clean.

