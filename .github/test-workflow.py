#!/usr/bin/env python3

"""
Issue Triage Workflow Test Script

This script helps create test issues for workflow testing.
Requires: GitHub CLI (gh) installed and authenticated.
"""

import subprocess
import sys
import time
import re
import json
from typing import List, Optional, Tuple
import unittest

# Colors for terminal output
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
NC = "\033[0m"

# Constants
WORKFLOW_WAIT_SECONDS = 10

# Compiled regex patterns for performance
_ISSUE_NUMBER_PATTERN = re.compile(r"/issues/(\d+)")
_ISSUE_NUMBER_IN_TITLE_PATTERN = re.compile(
    r"#\s*(\d+)\b"
)  # For "AI Triage for Issue #123"
_GITHUB_URL_PATTERN = re.compile(r"https://github\.com/[^\s]+")
_REPO_PATTERN = re.compile(r"github\.com[:/]([^/]+/[^/]+?)(?:\.git)?$")


# Utility functions
def extract_repo_from_git_url(git_url: str) -> Optional[str]:
    """Extract owner/repo from git URL."""
    if not git_url:
        return None
    match = _REPO_PATTERN.search(git_url.strip())
    return match.group(1) if match else None


def extract_issue_number_from_url(url: str) -> Optional[str]:
    """Extract issue number from GitHub issue URL."""
    match = _ISSUE_NUMBER_PATTERN.search(url)
    return match.group(1) if match else None


def extract_url_from_output(output: str) -> Optional[str]:
    """Extract GitHub URL from command output."""
    match = _GITHUB_URL_PATTERN.search(output)
    return match.group(0) if match else None


def print_colored(message: str, color: str = NC) -> None:
    """Print colored message to terminal."""
    print(f"{color}{message}{NC}")


# GitHub CLI functions
def run_command(cmd: List[str]) -> Tuple[int, str, str]:
    """Run a shell command and return exit code, stdout, stderr."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return result.returncode, result.stdout, result.stderr
    except FileNotFoundError as e:
        return 1, "", str(e)


def check_gh_cli() -> bool:
    """Check if GitHub CLI is installed."""
    exit_code, _, _ = run_command(["gh", "--version"])
    return exit_code == 0


def check_gh_auth() -> bool:
    """Check if GitHub CLI is authenticated."""
    exit_code, _, _ = run_command(["gh", "auth", "status"])
    return exit_code == 0


def get_repository() -> Optional[str]:
    """Get repository name from git remote or gh CLI."""
    # Try git remote
    exit_code, stdout, _ = run_command(["git", "remote", "get-url", "origin"])
    if exit_code == 0 and stdout:
        repo = extract_repo_from_git_url(stdout)
        if repo:
            return repo

    # Try gh CLI
    exit_code, stdout, _ = run_command(
        ["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"]
    )
    if exit_code == 0 and stdout:
        return stdout.strip()

    return None


def get_issue_labels(repo: str, issue_number: str) -> List[str]:
    """Get current labels for an issue."""
    issue = get_issue(repo, issue_number)
    if not issue:
        return []
    return [label.get("name") for label in issue.get("labels", [])]


def create_test_issue(
    repo: str, title: str, body: str, labels: List[str], scenario: str
) -> Optional[str]:
    """Create a test issue and return the issue URL."""
    print_colored(f"Creating test issue: {scenario}", YELLOW)
    print(f"Title: {title}")
    print(f"Labels: {', '.join(labels)}\n")

    # Build command
    cmd = ["gh", "issue", "create", "--repo", repo, "--title", title, "--body", body]
    for label in labels:
        cmd.extend(["--label", label])

    # Create issue
    exit_code, stdout, stderr = run_command(cmd)
    if exit_code != 0:
        print_colored(f"✗ Failed to create issue: {stderr}", RED)
        return None

    # Extract URL and issue number (gh CLI outputs URL to stdout, fallback to stderr)
    issue_url = extract_url_from_output(stdout)
    if not issue_url:
        issue_url = extract_url_from_output(stderr)
    if not issue_url:
        print_colored("✗ Failed to extract issue URL", RED)
        return None

    issue_number = extract_issue_number_from_url(issue_url)
    print_colored(f"✓ Issue created: {issue_url}", GREEN)

    # Verify parameters (non-blocking, just for logging)
    if issue_number:
        print_colored("Verifying issue parameters...", YELLOW)
        if not verify_issue(repo, issue_number, title, body, labels):
            print_colored("⚠ Issue verification failed, but continuing", YELLOW)
        print()

    print(f"Waiting {WORKFLOW_WAIT_SECONDS} seconds for workflow to trigger...")
    time.sleep(WORKFLOW_WAIT_SECONDS)
    print()
    return issue_url


def get_issue(repo: str, issue_number: str):
    exit_code, stdout, stderr = run_command(
        [
            "gh",
            "issue",
            "view",
            issue_number,
            "--repo",
            repo,
            "--json",
            "title,body,labels",
        ]
    )

    if exit_code != 0:
        print_colored(f"✗ Failed to get issue #{issue_number}: {stderr}", RED)
        return {}

    try:
        # gh CLI outputs JSON to stdout, errors to stderr
        return json.loads(stdout) if stdout else {}
    except json.JSONDecodeError as e:
        print_colored(f"✗ Failed to parse issue #{issue_number}: {e}", RED)
        return {}


def get_issue_comments(repo: str, issue_number: str) -> List[dict]:
    """Get all comments for an issue."""
    exit_code, stdout, stderr = run_command(
        [
            "gh",
            "api",
            f"repos/{repo}/issues/{issue_number}/comments",
            "--jq",
            ".[] | {body: .body}",
        ]
    )

    if exit_code != 0:
        print_colored(
            f"⚠ Warning: Failed to fetch comments for issue #{issue_number}: {stderr}",
            YELLOW,
        )
        return []

    try:
        # gh CLI with --jq outputs one JSON object per line
        comments = []
        if stdout.strip():
            for line in stdout.strip().split("\n"):
                if line.strip():
                    try:
                        comment_data = json.loads(line)
                        # Extract just the body for our validation
                        comments.append({"body": comment_data.get("body", "")})
                    except json.JSONDecodeError:
                        # Skip malformed lines
                        continue
        return comments
    except json.JSONDecodeError as e:
        print_colored(
            f"⚠ Warning: Failed to parse comments for issue #{issue_number}: {e}",
            YELLOW,
        )
        return []


def get_workflow_runs(repo: str, workflow_name: str = "Triage New Issue") -> List[dict]:
    exit_code, stdout, stderr = run_command(
        [
            "gh",
            "run",
            "list",
            "--repo",
            repo,
            "--workflow",
            workflow_name,
            "--event",
            "issues",
            "--json",
            "databaseId,displayTitle,status,conclusion,createdAt,updatedAt",
            "--limit",
            "20",
        ]
    )
    if exit_code != 0:
        print_colored(f"⚠ Warning: Failed to query workflow runs: {stderr}", YELLOW)
        return []

    try:
        # gh CLI outputs JSON to stdout, errors to stderr
        return json.loads(stdout) if stdout else []
    except json.JSONDecodeError as e:
        print_colored(f"✗ Failed to parse workflow runs: {e}", RED)
        return []


class TestWorkflow(unittest.TestCase):
    """Test the issue triage workflow."""

    repo = None  # Class variable to store repository name

    @classmethod
    def setUpClass(cls):
        # Check prerequisites
        if not check_gh_cli():
            print_colored("Error: GitHub CLI (gh) is not installed.", RED)
            print("Install it from: https://cli.github.com/")
            sys.exit(1)

        print_colored("GitHub CLI detected\n", GREEN)

        if not check_gh_auth():
            print_colored("Error: Not authenticated with GitHub CLI.", RED)
            print("Run: gh auth login")
            sys.exit(1)

        print_colored("GitHub CLI authenticated\n", GREEN)

        repo = get_repository()
        if not repo:
            print_colored("Error: Could not determine repository.", RED)
            print("Please run from a git repository or ensure gh CLI is configured.")
            sys.exit(1)

        cls.repo = repo  # Store repo as class variable
        print_colored(f"Repository: {cls.repo}\n", GREEN)

    def test_workflow(self):
        """Test the issue triage workflow."""
        repo = type(self).repo  # Access class variable directly
        test_scenarios = get_test_scenarios()
        created_issues = []
        scenario_metadata = {}  # Map issue_number -> scenario metadata
        
        for test in test_scenarios:
            issue_url = create_test_issue(
                repo=repo,
                title=test["title"],
                body=test["body"],
                labels=test["labels"],
                scenario=test["scenario"],
            )
            if issue_url:
                created_issues.append(issue_url)
                issue_number = extract_issue_number_from_url(issue_url)
                if issue_number:
                    # Store scenario metadata for validation
                    scenario_metadata[issue_number] = {
                        "is_positive": test.get("is_positive", False),
                        "expected_assessment": test.get("expected_assessment"),
                        "expected_labels": test.get("expected_labels", test["labels"]),
                        "scenario": test["scenario"],
                    }

        # Summary
        print_colored("\n=== Test Issues Created ===\n", GREEN)
        print(
            f"Created {len(created_issues)} out of {len(test_scenarios)} test issues\n"
        )

        self.validate_test_issues(repo, created_issues, scenario_metadata)

        print("Next steps:")
        print(f"1. Go to: https://github.com/{repo}/issues")
        print("2. Check the Actions tab to see workflow runs")
        print("3. Review each test issue for AI assessment comments\n")
        print("To view workflow runs:")
        print(f"  gh run list --repo {repo} --workflow='Triage New Issue'\n")

    def validate_test_issues(
        self, repo: str, created_issues: List[str], scenario_metadata: dict
    ) -> None:
        """Validate workflow completion for all created issues."""
        # Extract issue numbers
        issue_numbers = []
        for issue in created_issues:
            issue_number = extract_issue_number_from_url(issue)
            if issue_number:
                issue_numbers.append(issue_number)

        # Validate each issue with retry logic
        for issue_number in issue_numbers:
            metadata = scenario_metadata.get(issue_number, {})
            self._validate_issue_with_retry(repo, issue_number, metadata)

    def _validate_issue_with_retry(
        self, repo: str, issue_number: str, metadata: dict
    ) -> None:
        """Validate a single issue with exponential backoff retries."""
        max_retries = 3
        base_wait_seconds = 10
        scenario = metadata.get("scenario", "Unknown")

        for attempt in range(max_retries + 1):
            # Fetch current workflow runs
            runs = get_workflow_runs(repo)

            # Build lookup map for this issue
            # Find the most recent run for this issue (runs are already sorted by most recent first)
            run = None
            for workflow_run in runs:
                title = workflow_run.get("displayTitle", "")
                match = _ISSUE_NUMBER_IN_TITLE_PATTERN.search(title)
                if match:
                    issue_num = match.group(1)
                    # Use exact string match to avoid partial matches (e.g., #1 matching #11)
                    if issue_num == issue_number:
                        run = workflow_run
                        break  # Take the first (most recent) match

            if not run:
                if attempt < max_retries:
                    wait_time = base_wait_seconds * (2 ** attempt)
                    print_colored(
                        f"⚠ No workflow run found for issue #{issue_number} ({scenario}), waiting {wait_time}s before retry {attempt + 1}/{max_retries}...",
                        YELLOW,
                    )
                    time.sleep(wait_time)
                    continue
                else:
                    print_colored(
                        f"⚠ No workflow run found for issue #{issue_number} ({scenario})", YELLOW
                    )
                    self.fail(f"Issue {issue_number} ({scenario}): No workflow run found")
                    return

            # Extract status
            status = run.get("status", "unknown")
            conclusion = run.get("conclusion", "unknown")
            run_id = run.get("databaseId")
            created = run.get("createdAt", "")
            updated = run.get("updatedAt", "")

            # Validate required fields
            if not run_id:
                self.fail(f"Issue {issue_number} ({scenario}): No run_id found")
                return
            if not created:
                self.fail(f"Issue {issue_number} ({scenario}): No createdAt timestamp")
                return
            if not updated:
                self.fail(f"Issue {issue_number} ({scenario}): No updatedAt timestamp")
                return

            # If status is in_progress and we haven't exhausted retries, wait and retry
            if status == "in_progress" and attempt < max_retries:
                wait_time = base_wait_seconds * (2 ** attempt)
                print_colored(
                    f"Issue #{issue_number} ({scenario}) → Status: {status}, Conclusion: {conclusion}",
                    YELLOW,
                )
                print_colored(
                    f"⏳ Workflow still in progress, waiting {wait_time}s before retry {attempt + 1}/{max_retries}...",
                    YELLOW,
                )
                time.sleep(wait_time)
                continue

            # Status is either completed or we've exhausted retries
            print_colored(
                f"Issue #{issue_number} ({scenario}) → Status: {status}, Conclusion: {conclusion}",
                (
                    GREEN
                    if conclusion == "success"
                    else YELLOW if status == "completed" else RED
                ),
            )

            # Validate status and conclusion
            if status == "in_progress":
                self.fail(
                    f"Issue {issue_number} ({scenario}) did not complete after {max_retries} retries with exponential backoff"
                )
                return

            self.assertEqual(
                status,
                "completed",
                f"Issue {issue_number} ({scenario}) did not complete",
            )
            self.assertEqual(
                conclusion,
                "success",
                f"Issue {issue_number} ({scenario}) did not complete successfully",
            )
            print_colored(f"✓ Issue {issue_number} ({scenario}) workflow validated", GREEN)

            # Validate labels if expected
            expected_labels = metadata.get("expected_labels")
            if expected_labels:
                self._validate_issue_labels(repo, issue_number, expected_labels, scenario)

            # Validate AI assessment comment if this scenario should have one
            if metadata.get("is_positive") or metadata.get("expected_assessment"):
                expected_assessment = metadata.get("expected_assessment")
                self._validate_ai_assessment_comment(repo, issue_number, expected_assessment, scenario)

            return

    def _validate_issue_labels(
        self, repo: str, issue_number: str, expected_labels: List[str], scenario: str
    ) -> None:
        """Validate that issue has the expected labels after workflow runs."""
        time.sleep(2)  # Allow labels to propagate
        
        actual_labels = get_issue_labels(repo, issue_number)
        expected_labels_set = set(expected_labels)
        actual_labels_set = set(actual_labels)
        
        # Check if kind/bug label is preserved (should be if it was in original labels)
        if "kind/bug" in expected_labels_set:
            if "kind/bug" not in actual_labels_set:
                self.fail(
                    f"Issue {issue_number} ({scenario}): Expected 'kind/bug' label to be preserved, but it's missing. "
                    f"Actual labels: {sorted(actual_labels)}"
                )
            else:
                print_colored(
                    f"✓ Issue {issue_number} ({scenario}): 'kind/bug' label preserved",
                    GREEN,
                )
        
        # Check AI assessment labels (e.g., ai:bug-triage:critical-coreapi)
        # We're lenient: require ai:bug-triage prefix and component match, but severity can differ
        ai_labels = [label for label in expected_labels_set if label.startswith("ai:")]
        if ai_labels:
            for expected_ai_label in ai_labels:
                # Extract component from expected label (format: ai:bug-triage:severity-component)
                # e.g., "ai:bug-triage:critical-installation" -> "installation"
                if not expected_ai_label.startswith("ai:bug-triage:"):
                    # If it doesn't match expected format, do exact match
                    if expected_ai_label not in actual_labels_set:
                        self.fail(
                            f"Issue {issue_number} ({scenario}): Expected AI label '{expected_ai_label}' not found. "
                            f"Actual labels: {sorted(actual_labels)}"
                        )
                    else:
                        print_colored(
                            f"✓ Issue {issue_number} ({scenario}): AI label '{expected_ai_label}' correctly assigned",
                            GREEN,
                        )
                    continue
                
                # Extract component from expected label
                # Format: ai:bug-triage:severity-component
                parts = expected_ai_label.replace("ai:bug-triage:", "").split("-", 1)
                if len(parts) < 2:
                    # Fallback to exact match if format is unexpected
                    if expected_ai_label not in actual_labels_set:
                        self.fail(
                            f"Issue {issue_number} ({scenario}): Expected AI label '{expected_ai_label}' not found. "
                            f"Actual labels: {sorted(actual_labels)}"
                        )
                    continue
                
                expected_component = parts[1]  # e.g., "installation", "coreapi", "networking"
                
                # Check if any actual label has ai:bug-triage prefix and contains the component
                found_match = False
                matching_label = None
                for actual_label in actual_labels:
                    if actual_label.startswith("ai:bug-triage:"):
                        # Extract component from actual label
                        actual_parts = actual_label.replace("ai:bug-triage:", "").split("-", 1)
                        if len(actual_parts) >= 2 and actual_parts[1] == expected_component:
                            found_match = True
                            matching_label = actual_label
                            break
                
                if not found_match:
                    self.fail(
                        f"Issue {issue_number} ({scenario}): Expected AI label with component '{expected_component}' not found. "
                        f"Expected format: ai:bug-triage:*{expected_component}. "
                        f"Actual labels: {sorted(actual_labels)}"
                    )
                else:
                    print_colored(
                        f"✓ Issue {issue_number} ({scenario}): AI label '{matching_label}' found (component '{expected_component}' matches)",
                        GREEN,
                    )

    def _validate_ai_assessment_comment(
        self, repo: str, issue_number: str, expected_assessment: Optional[str] = None, scenario: str = "Unknown"
    ) -> None:
        """Validate that AI assessment comment is present with expected severity-component format."""
        # Add a small delay to allow comments to propagate through GitHub API
        time.sleep(2)
        
        # Retry fetching comments with exponential backoff
        max_comment_retries = 3
        base_wait_seconds = 3
        
        for attempt in range(max_comment_retries + 1):
            comments = get_issue_comments(repo, issue_number)
            
            # Debug: Log what comments we found
            if comments:
                print_colored(
                    f"  Found {len(comments)} comment(s) for issue #{issue_number} ({scenario})",
                    YELLOW,
                )
                # Show first 150 chars of each comment for debugging
                for i, comment in enumerate(comments):
                    body_preview = comment.get("body", "")[:150].replace("\n", " ")
                    print_colored(
                        f"  Comment {i+1}: {body_preview}...",
                        YELLOW,
                    )
            
            # Search for the AI assessment text in comments
            assessment_found = False
            found_assessment = None
            for comment in comments:
                body = comment.get("body", "")
                if "AI Assessment:" in body:
                    # Extract the severity-component format (e.g., "critical-CoreAPI" or "high-Networking")
                    match = re.search(r"AI Assessment:\s*([^\n\s]+)", body, re.IGNORECASE)
                    if match:
                        found_assessment = match.group(1).strip()
                        # AI assessment comment found - validate format (severity-component)
                        if re.match(r"^(critical|high|medium|low)-(coreapi|networking|installation|storage|webconsole|documentation)$", found_assessment, re.IGNORECASE):
                            assessment_found = True
                            print_colored(
                                f"✓ Issue {issue_number} ({scenario}): Found AI Assessment comment with '{found_assessment}'",
                                GREEN,
                            )
                            return
            
            # If not found and we have retries left, wait and retry
            if not assessment_found and attempt < max_comment_retries:
                wait_time = base_wait_seconds * (2 ** attempt)
                print_colored(
                    f"⏳ AI Assessment comment not found yet for issue #{issue_number} ({scenario}), waiting {wait_time}s before retry {attempt + 1}/{max_comment_retries}...",
                    YELLOW,
                )
                time.sleep(wait_time)
                continue
            
            # If we've exhausted retries, fail the test with detailed error
            if not assessment_found:
                if not comments:
                    self.fail(
                        f"Issue {issue_number} ({scenario}): No comments found (expected AI Assessment comment after {max_comment_retries + 1} attempts)"
                    )
                else:
                    # Check what assessment was actually provided
                    actual_assessments = []
                    for comment in comments:
                        body = comment.get("body", "")
                        if "AI Assessment:" in body:
                            match = re.search(r"AI Assessment:\s*([^\n\s]+)", body, re.IGNORECASE)
                            if match:
                                actual_assessments.append(match.group(1).strip())
                    
                    if actual_assessments:
                        self.fail(
                            f"Issue {issue_number} ({scenario}): AI Assessment comment found but format is invalid. "
                            f"Expected format: severity-component (e.g., critical-CoreAPI). "
                            f"Found: {', '.join(actual_assessments)}"
                        )
                    else:
                        self.fail(
                            f"Issue {issue_number} ({scenario}): AI Assessment comment not found in issue comments after {max_comment_retries + 1} attempts"
                        )
                return


def verify_issue(
    repo: str,
    issue_number: str,
    expected_title: str,
    expected_body: str,
    expected_labels: List[str],
) -> bool:
    """Verify that the created issue has the expected parameters."""

    try:
        issue = get_issue(repo, issue_number)
        if not issue:
            return False

        issues_found = []

        # Verify title
        if issue.get("title") != expected_title:
            print_colored("⚠ Warning: Title mismatch", YELLOW)
            print(f"  Expected: {expected_title}")
            print(f"  Actual: {issue.get('title')}")
            issues_found.append("title")

        # Verify body (normalize whitespace)
        if issue.get("body", "").rstrip() != expected_body.rstrip():
            print_colored("⚠ Warning: Body mismatch", YELLOW)
            issues_found.append("body")

        # Verify labels
        actual_labels = {label.get("name") for label in issue.get("labels", [])}
        expected_labels_set = set(expected_labels)

        if actual_labels != expected_labels_set:
            print_colored("⚠ Warning: Labels mismatch", YELLOW)
            print(f"  Expected: {sorted(expected_labels)}")
            print(f"  Actual: {sorted(actual_labels)}")
            missing = expected_labels_set - actual_labels
            extra = actual_labels - expected_labels_set
            if missing:
                print(f"  Missing: {sorted(missing)}")
            if extra:
                print(f"  Extra: {sorted(extra)}")
            issues_found.append("labels")

        if issues_found:
            print_colored(f"⚠ Verification issues: {', '.join(issues_found)}", YELLOW)
            return False

        print_colored("✓ All parameters verified", GREEN)
        return True

    except json.JSONDecodeError:
        print_colored("⚠ Warning: Failed to parse verification response", YELLOW)
        return False


def get_test_scenarios() -> List[dict]:
    """Return list of test scenarios with realistic Kubernetes/OpenShift contexts."""
    tests = [
        {
            "title": "[TEST] Scenario 1: Complete Cluster API Failure",
            "body": """**Describe the bug**
All control plane nodes became unresponsive, causing complete cluster outage. API server stops responding to all requests.

**Version**
OKD 4.15.0-0.okd-2024-03-15-123456

**Steps to Reproduce**
1. Deploy OKD 4.15 cluster on bare metal with 3 control plane nodes
2. After 48 hours of uptime, API server stops responding
3. Verify: oc get nodes returns timeout errors
4. Check API server logs show etcd connection failures

**Expected behavior**
Cluster should remain available and API server should respond to all requests

**Actual behavior**
All API requests fail with connection timeout. Cluster is completely inaccessible. etcd quorum may be lost.

**Environment**
- Platform: Bare metal
- OKD version: 4.15.0-0.okd-2024-03-15-123456
- Number of control plane nodes: 3
- Network: OVN-Kubernetes
- etcd: 3 member cluster

**Logs/Error Messages**
```
E0315 14:30:00.123456 apiserver.go:1234] Unable to connect to etcd: dial tcp 10.0.1.5:2379: connect: connection refused
E0315 14:30:05.123456 cache.go:567] Failed to list *v1.Node: the server is currently unable to handle the request
```""",
            "labels": ["kind/bug"],
            "scenario": "Scenario 1: Complete Cluster API Failure - Ready for Review",
            "is_positive": True,
            "expected_assessment": "Ready for Review",
            "expected_labels": ["kind/bug", "ai:bug-triage:critical-coreapi"],
        },
        {
            "title": "[TEST] Scenario 2: OpenShift IPI Installation",
            "body": """**Describe the bug**
Cluster installation fails during bootstrap phase when using custom VPC configuration on AWS.

**Version**
OKD 4.16.0-0.okd-2024-06-10-234567
IPI installation method on AWS

**How reproducible**
100% - happens every time with custom VPC

**Expected behavior**
Installation should complete successfully

**Actual behavior**
Bootstrap times out after 30 minutes""",
            "labels": ["kind/bug"],
            "scenario": "Scenario 2: OpenShift IPI Installation Missing Details",
            "is_positive": True,
            "expected_assessment": "Missing Details",
            "expected_labels": ["kind/bug", "ai:bug-triage:high-installation"],
        },
        {
            "title": "[TEST] Scenario 3: Networking CNI Issue",
            "body": """**Describe the bug**
Pods can't reach each other across nodes. But sometimes they can reach each other. The error messages say it's a network policy issue but the logs show DNS problems. I tried restarting the network pods and that fixed it once, but then it broke again the next day. Maybe it's related to the firewall rules? Or could it be a CNI plugin bug?""",
            "labels": ["kind/bug"],
            "scenario": "Scenario 3: Networking CNI Issue Needs Clarification",
            "is_positive": True,
            "expected_assessment": "Needs Clarification",
            "expected_labels": ["kind/bug", "ai:bug-triage:medium-networking"],
        },
        {
            "title": "[TEST] Scenario 4: Storage PV Mounting Issue",
            "body": """**Describe the bug**
Persistent volumes fail to mount on worker nodes after upgrading cluster from OKD 4.15 to 4.16.

**Version**
OKD 4.16.0-0.okd-2024-06-10-234567

**Steps to Reproduce**
1. Upgrade cluster from OKD 4.15 to 4.16 using standard upgrade procedure
2. Create PVC with storage class 'gp3-csi' on AWS
3. Deploy pod with volumeMount referencing the PVC
4. Observe pod status: oc get pods -w

**Expected behavior**
PV should mount successfully and pod should start normally

**Actual behavior**
Pod remains in Pending state indefinitely. Events show: "Unable to attach or mount volumes: timed out waiting for the condition"

**Environment**
- Platform: AWS
- OKD version: 4.16.0-0.okd-2024-06-10-234567
- Storage class: gp3-csi
- CSI driver: ebs-csi-driver-operator
- Previous version: 4.15.0-0.okd-2024-03-15-123456

**Logs/Error Messages**
```
E0610 08:15:00.123456 mount_linux.go:175] Mount failed: exit status 32
Mounting command: systemd-run
Mounting arguments: --description=Kubernetes transient mount for /var/lib/kubelet/pods/...
E0610 08:15:05.123456 attacher.go:123] Failed to attach volume: volume not found
```""",
            "labels": ["kind/bug"],
            "scenario": "Scenario 4: Storage PV Mounting Issue - Ready for Review",
            "is_positive": True,
            "expected_assessment": "Ready for Review",
            "expected_labels": ["kind/bug", "ai:bug-triage:high-storage"],
        },
        {
            "title": "[TEST] Scenario 5: Incomplete Bug Report",
            "body": "My cluster doesn't work. Help!",
            "labels": ["kind/bug"],
            "scenario": "Scenario 5: Incomplete Bug Report - Missing Details",
            "is_positive": True,
            "expected_assessment": "Missing Details",
            "expected_labels": ["kind/bug", "ai:bug-triage:medium-coreapi"],
        },
        {
            "title": "[TEST] Scenario 6: Ingress Controller CrashLoop",
            "body": """**Describe the bug**
Ingress controller pods enter CrashLoopBackOff state after cluster upgrade, causing all routes to be inaccessible.

**Version**
OKD 4.17.0-0.okd-2024-09-01-345678

**Steps to Reproduce**
1. Upgrade OKD cluster from 4.16 to 4.17
2. Wait for ingress controller pods to restart
3. Check pod status: oc get pods -n openshift-ingress
4. Observe CrashLoopBackOff state

**Expected behavior**
Ingress controller pods should run normally and routes should be accessible

**Actual behavior**
All ingress controller pods crash repeatedly. Routes return 503 Service Unavailable. External traffic cannot reach applications.

**Environment**
- Platform: AWS
- OKD version: 4.17.0-0.okd-2024-09-01-345678
- Ingress controller: haproxy-router
- Number of replicas: 2

**Logs/Error Messages**
```
E0901 12:00:00.123456 router.go:456] Failed to initialize router: failed to load certificates: x509: certificate has expired or is not yet valid
F0901 12:00:01.123456 router.go:234] Router initialization failed, exiting
```""",
            "labels": ["kind/bug"],
            "scenario": "Scenario 6: Ingress Controller CrashLoop - Ready for Review",
            "is_positive": True,
            "expected_assessment": "Ready for Review",
            "expected_labels": ["kind/bug", "ai:bug-triage:high-networking"],
        },
        {
            "title": "[TEST] Scenario 7: WebConsole UI Issue",
            "body": """**Describe the bug**
Button text in WebConsole is misaligned on mobile viewport, causing poor user experience.

**Version**
OKD 4.17.0-0.okd-2024-09-01-345678

**Steps to Reproduce**
1. Open WebConsole on mobile device (or resize browser to mobile width)
2. Navigate to Projects page
3. Observe "Create Project" button text alignment

**Expected behavior**
Button text should be centered and properly aligned

**Actual behavior**
Text is shifted to the right by approximately 5 pixels, making it difficult to read

**Environment**
- Platform: Any
- Browser: Chrome Mobile 120, Safari Mobile 17
- OKD version: 4.17.0-0.okd-2024-09-01-345678
- Screen size: 375x667 (iPhone SE)""",
            "labels": ["kind/bug"],
            "scenario": "Scenario 7: WebConsole UI Issue - Ready for Review",
            "is_positive": True,
            "expected_assessment": "Ready for Review",
            "expected_labels": ["kind/bug", "ai:bug-triage:low-webconsole"],
        },
    ]
    return tests

def main() -> None:
    """Main function to run tests."""
    # Run unittest test suite
    unittest.main(verbosity=2)


if __name__ == "__main__":
    main()
