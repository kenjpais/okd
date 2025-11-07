# AI Assessment Workflow Logic Documentation

## Workflow Overview

### How the AI Assessment Labeler Works

1. **Trigger**: Workflow runs when `kind/bug` label is applied to an issue
2. **AI Assessment Step**: `github/ai-assessment-comment-labeler@v1.0.1` action:
   - Reads `bug-triage.prompt.yml` from `./.github/prompts`
   - Sends issue body to AI model (`openai/gpt-4o`)
   - AI analyzes issue for completeness and returns assessment
3. **Label Assignment**: Action automatically creates labels based on assessment response:
   - Format: `ai:{prompt-stem}:{priority}-{component}` (lowercased)
   - Example: `ai:bug-triage:critical-coreapi`
   - Example: `ai:bug-triage:high-networking`
   - Example: `ai:bug-triage:medium-installation`
   - Example: `ai:bug-triage:low-webconsole`
   - Priority: critical, high, medium, low
   - Component: coreapi, networking, installation, storage, webconsole, documentation
4. **Label Preservation**: `kind/bug` label is preserved after AI assessment

### Expected AI Response Format

The prompt expects responses like:
```
AI Assessment: high-Networking Ready for Review
```

Or:
```
AI Assessment: critical-CoreAPI Missing Details
```

The action extracts the assessment status (Ready for Review, Missing Details, Needs Clarification) and creates the corresponding label.

## Test Scenarios

### Updated Test Cases (7 scenarios)

1. **Complete Cluster API Failure** - Ready for Review
   - Complete bug report with all required information
   - Expected label: `ai:bug-triage:critical-coreapi`

2. **OpenShift IPI Installation** - Missing Details
   - Missing reproduction steps and logs
   - Expected label: `ai:bug-triage:high-installation`

3. **Networking CNI Issue** - Needs Clarification
   - Contradictory and confusing description
   - Expected label: `ai:bug-triage:medium-networking`

4. **Storage PV Mounting Issue** - Ready for Review
   - Complete storage issue with full details
   - Expected label: `ai:bug-triage:high-storage`

5. **Incomplete Bug Report** - Missing Details
   - Minimal information provided
   - Expected label: `ai:bug-triage:medium-coreapi`

6. **Ingress Controller CrashLoop** - Ready for Review
   - Complete ingress controller issue
   - Expected label: `ai:bug-triage:high-networking`

7. **WebConsole UI Issue** - Ready for Review
   - Complete UI bug report
   - Expected label: `ai:bug-triage:low-webconsole`

## Test Execution

```bash
python3 .github/test-workflow.py
```

Each test follows **Given-When-Then** structure:
- **Given**: Issue with `kind/bug` label and realistic Kubernetes/OpenShift bug content
- **When**: Workflow runs and AI assessment completes
- **Then**: Correct AI assessment label is assigned (and only that label from the assessment)

