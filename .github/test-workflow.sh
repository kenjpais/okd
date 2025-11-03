#!/bin/bash

# AI Issue Triage Workflow Test Script
# This script helps create test issues for workflow testing
# Requires: GitHub CLI (gh) installed and authenticated

set -e

REPO="${GITHUB_REPOSITORY:-$(gh repo view --json nameWithOwner -q .nameWithOwner)}"
echo "Testing workflow for repository: $REPO"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}Error: GitHub CLI (gh) is not installed.${NC}"
    echo "Install it from: https://cli.github.com/"
    echo ""
    echo "Alternatively, you can create test issues manually using the test plan in TEST_PLAN.md"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${RED}Error: Not authenticated with GitHub CLI.${NC}"
    echo "Run: gh auth login"
    exit 1
fi

echo -e "${GREEN}GitHub CLI detected and authenticated${NC}"
echo ""

# Function to create a test issue
create_test_issue() {
    local title="$1"
    local body="$2"
    local labels="$3"
    local scenario="$4"
    
    echo -e "${YELLOW}Creating test issue: $scenario${NC}"
    echo "Title: $title"
    echo "Labels: $labels"
    echo ""
    
    local issue_url=$(gh issue create \
        --repo "$REPO" \
        --title "$title" \
        --body "$body" \
        --label "$labels" \
        --json url -q .url)
    
    echo -e "${GREEN}✓ Issue created: $issue_url${NC}"
    echo "Waiting 5 seconds for workflow to trigger..."
    sleep 5
    echo ""
}

# Scenario 1: Bug Report with Complete Information
create_test_issue \
    "[TEST] Scenario 1: Cluster fails to start on AWS with custom VPC" \
    "**Describe the bug**
Cluster installation fails during bootstrap phase with timeout errors when using custom VPC configuration on AWS.

**Version**
OKD 4.20.0-0.okd-2024-10-15-123456
IPI installation method on AWS

**How reproducible**
100% - happens every time with custom VPC

**Log Bundle**
https://example.com/logs/bootstrap-logs.tar.gz" \
    "triage/needs-triage,kind/bug" \
    "Scenario 1: Complete Bug Report"

# Scenario 2: Bug Report Missing Information
create_test_issue \
    "[TEST] Scenario 2: Something is broken" \
    "It doesn't work. Help!" \
    "triage/needs-triage,kind/bug" \
    "Scenario 2: Incomplete Bug Report"

# Scenario 3: Feature Request with Complete Information
create_test_issue \
    "[TEST] Scenario 3: Add support for custom certificate authorities" \
    "**Use Case**
Organizations using internal CA certificates need to trust custom CAs when deploying OKD clusters.

**Proposed Solution**
Add a configuration option to import custom CA certificates during cluster installation.

**Value Proposition**
Enables OKD deployment in enterprise environments with internal certificate authorities." \
    "triage/needs-triage,kind/feature" \
    "Scenario 3: Complete Feature Request"

# Scenario 4: Feature Request Needs Refinement
create_test_issue \
    "[TEST] Scenario 4: Make it better" \
    "Would be nice to have more features." \
    "triage/needs-triage,kind/feature" \
    "Scenario 4: Incomplete Feature Request"

# Scenario 5: Issue Without Triage Label (should NOT trigger)
create_test_issue \
    "[TEST] Scenario 5: Regular issue without triage" \
    "This issue should NOT trigger the workflow because it lacks the triage/needs-triage label." \
    "kind/bug" \
    "Scenario 5: No Triage Label (should not trigger)"

# Scenario 6: Issue with Only Triage Label
create_test_issue \
    "[TEST] Scenario 6: Issue with only triage label" \
    "This issue has triage label but no kind label. May not match any prompt mapping." \
    "triage/needs-triage" \
    "Scenario 6: Only Triage Label"

echo ""
echo -e "${GREEN}=== Test Issues Created ===${NC}"
echo ""
echo "Next steps:"
echo "1. Go to your repository: https://github.com/$REPO/issues"
echo "2. Check the Actions tab to see workflow runs"
echo "3. Review each test issue for AI assessment comments"
echo "4. Verify labels are applied correctly"
echo ""
echo "To view workflow runs:"
echo "  gh run list --repo $REPO --workflow='AI Issue Triage'"
echo ""
echo "To cleanup test issues later:"
echo "  gh issue list --repo $REPO --label 'TEST' --search '[TEST]' --json number -q '.[].number' | xargs -I {} gh issue close {} --repo $REPO"

