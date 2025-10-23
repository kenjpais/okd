# AI Issue Triage Setup for OKD Fork

**Repository:** https://github.com/kenjpais/okd  
**Original Project:** [OKD - The Community Distribution of Kubernetes](https://github.com/okd-project/okd)  
**Setup Date:** October 23, 2025  
**Status:** ✅ **Active and Working**

---

## Overview

This fork of the OKD repository has been enhanced with an AI-powered issue triage workflow that automatically assesses issue quality and applies appropriate labels to help maintainers prioritize and manage issues effectively.

## What Was Added

### 1. AI Triage Workflow (`.github/workflows/issue-triage.yml`)
- Automatically triggers when issues are labeled with `triage/needs-triage`
- Uses GitHub's AI Assessment Comment Labeler action (v1.0.1)
- Powered by OpenAI GPT-4o-mini via GitHub Models API
- Posts detailed AI assessment as a comment on the issue
- Automatically applies labels based on assessment results

### 2. Prompt Files (`.github/prompts/`)

#### **`bug-triage.prompt.yml`**
Specialized for OKD bug reports, assesses:
- Problem description clarity
- Reproduction steps
- Environment information (cluster version, platform)
- Log output quality

Possible assessments:
- `ai:bug-triage:ready for review` - Complete and actionable
- `ai:bug-triage:missing details` - Needs more information
- `ai:bug-triage:needs clarification` - Confusing or contradictory

#### **`enhancement-triage.prompt.yml`**
Specialized for OKD feature requests, assesses:
- Use case clarity for OKD users/operators
- Proposed solution
- Value proposition to the OKD community
- Scope appropriateness

Possible assessments:
- `ai:enhancement-triage:ready for consideration` - Well-defined
- `ai:enhancement-triage:needs refinement` - Good idea, needs details
- `ai:enhancement-triage:requires discussion` - Needs community input

### 3. Labels

Created the following labels:
- `triage/needs-triage` (orange) - Trigger label for AI assessment
- `kind/bug` (red) - Bug report identifier
- `kind/feature` (blue) - Feature request identifier

AI-generated labels are automatically applied after assessment.

---

## How It Works

1. **Issue Creation**: User creates an issue with labels `triage/needs-triage` and either `kind/bug` or `kind/feature`

2. **Workflow Triggers**: The AI triage workflow automatically starts

3. **AI Analysis**: 
   - Appropriate prompt file is selected based on issue type
   - AI analyzes the issue content against quality criteria
   - Assessment is generated with specific feedback

4. **Results Posted**:
   - AI posts detailed assessment as a comment
   - Appropriate label is applied (e.g., `ai:bug-triage:ready for review`)
   - Original `triage/needs-triage` label is removed
   - Workflow summary is generated

---

## Testing Results

**Test Issue:** [#1 - Installation fails on AWS with custom VPC](https://github.com/kenjpais/okd/issues/1)

✅ **Result:** SUCCESS

**AI Assessment:**
```
### AI Assessment: Ready for Review

1. **Problem Description**: The bug report clearly outlines the failure during 
   the installation of OKD 4.20 on AWS, mentioning the expected behavior and 
   the actual issue of timeouts.

2. **Reproduction Steps**: Specific steps are provided to easily reproduce the 
   issue, making it actionable for developers.

3. **Environment Information**: The report includes details such as the OKD 
   version, the AWS platform, and that a custom VPC was used, which is crucial 
   for understanding the context of the bug.

4. **Log Output**: Relevant log messages are included to illustrate the nature 
   of the errors encountered, aiding diagnosis.

Overall Recommendation: Proceed with reviewing the bug report and investigate 
the timeout issue related to the bootstrap phase in the described environment.
```

**Labels Applied:** `ai:bug-triage:ready for review`

**Workflow Runs:** 3/3 completed successfully in ~20-23 seconds each

---

## Usage Guide

### For Issue Reporters

When creating a new issue:

1. **For Bug Reports:**
   - Use labels: `triage/needs-triage` and `kind/bug`
   - Include: problem description, reproduction steps, environment info, logs
   - AI will assess completeness and provide feedback

2. **For Feature Requests:**
   - Use labels: `triage/needs-triage` and `kind/feature`
   - Include: use case, proposed solution, value proposition
   - AI will evaluate clarity and scope

### For Maintainers

The AI assessment helps you:
- **Quickly identify** high-quality, actionable issues
- **Spot** issues that need more information
- **Prioritize** based on AI-suggested labels
- **Request specific information** based on AI feedback

You can:
- Re-trigger assessment by adding `triage/needs-triage` label again
- Override AI assessment if needed
- Use AI labels for filtering and prioritization

---

## Integration with OKD

The prompts are specifically tailored for OKD context:
- References Kubernetes and OpenShift
- Understands OKD-specific terminology
- Considers cluster deployment scenarios
- Recognizes OKD version formats
- Aware of common OKD platforms (AWS, bare metal, etc.)

---

## Benefits

1. **Faster Triage**: Instant AI assessment vs manual review
2. **Consistency**: Same criteria applied to all issues
3. **Better Quality**: Encourages complete issue reports
4. **Time Savings**: Maintainers focus on actionable issues
5. **Improved Communication**: Clear feedback on what's missing

---

## Workflow Configuration

**Model:** OpenAI GPT-4o-mini (via GitHub Models API)  
**Max Tokens:** 300  
**Permissions Required:**
- `issues: write` - Post comments and apply labels
- `models: read` - Access GitHub Models API
- `contents: read` - Read prompt files

---

## Performance Metrics

Based on testing:
- **Average Runtime:** ~20-23 seconds per assessment
- **Success Rate:** 100% (3/3 workflows completed)
- **AI Response Time:** ~2-3 seconds
- **Assessment Accuracy:** Context-aware and detailed

---

## Future Enhancements

Potential improvements:
1. Add more issue types (documentation, security, etc.)
2. Integrate with project boards
3. Add severity/priority assessment
4. Track metrics on issue quality over time
5. Add webhook notifications for high-priority issues

---

## Links

- **Forked Repository:** https://github.com/kenjpais/okd
- **Original OKD Project:** https://github.com/okd-project/okd
- **Test Issue #1:** https://github.com/kenjpais/okd/issues/1
- **AI Assessment Action:** https://github.com/marketplace/actions/ai-assessment-comment-labeler

---

## Maintenance

The workflow is self-contained and requires minimal maintenance:
- Prompt files can be updated to adjust assessment criteria
- Labels are automatically managed by the workflow
- GitHub Models API is maintained by GitHub

---

**Setup Completed By:** AI Assistant (Cursor)  
**Based On:** Successful implementation in release-page-summarizer repository  
**Documentation Date:** October 23, 2025
