# Issue Mirroring and AI Triage Setup

This document explains how to set up automated issue mirroring from the original repository (`okd-project/okd`) to your fork (`kenjpais/okd`) and run AI triage on the mirrored issues.

## Overview

The system consists of two main workflows:

1. **Mirror Issues Workflow** (`mirror-issues.yml`): Periodically fetches new issues from the original repository and creates mirrored issues in your fork.
2. **Issue Triage Workflow** (`issue-triage.yml`): Automatically runs AI assessment on issues with the `kind/bug` label and posts results to Slack.

## Prerequisites

1. A fork of the original repository (`okd-project/okd`) at `kenjpais/okd`
2. A GitHub Personal Access Token (PAT) with the following scopes:
   - `repo` (full control of private repositories)
   - `workflow` (update GitHub Action workflows)

## Setup Instructions

### Step 1: Create a Personal Access Token (PAT)

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a descriptive name (e.g., "OKD Issue Mirroring")
4. Select the following scopes:
   - `repo` (Full control of private repositories)
   - `workflow` (Update GitHub Action workflows)
5. Click "Generate token"
6. **Copy the token immediately** (you won't be able to see it again)

### Step 2: Add PAT as Repository Secret

1. Go to your fork repository: `https://github.com/kenjpais/okd`
2. Navigate to Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name: `PAT_TOKEN`
5. Value: Paste your Personal Access Token
6. Click "Add secret"

### Step 3: Configure Slack Webhook (Optional but Recommended)

1. Create a Slack webhook URL in your Slack workspace
2. Go to your fork repository: `https://github.com/kenjpais/okd`
3. Navigate to Settings → Secrets and variables → Actions
4. Click "New repository secret"
5. Name: `SLACK_WEBHOOK_URL`
6. Value: Paste your Slack webhook URL
7. Click "Add secret"

### Step 4: Verify Workflow Files

Ensure the following files exist in your repository:

- `.github/workflows/mirror-issues.yml` - Issue mirroring workflow
- `.github/workflows/issue-triage.yml` - AI triage workflow
- `.github/mirrored-issues.json` - Tracking file for processed issues
- `.github/prompts/bug-triage.prompt.yml` - AI prompt configuration

### Step 5: Enable GitHub Actions

1. Go to your fork repository: `https://github.com/kenjpais/okd`
2. Navigate to Settings → Actions → General
3. Under "Workflow permissions", select "Read and write permissions"
4. Check "Allow GitHub Actions to create and approve pull requests"
5. Click "Save"

### Step 6: Test the Workflow

1. Manually trigger the mirror workflow:
   - Go to Actions tab in your repository
   - Select "Mirror Issues from Original Repo"
   - Click "Run workflow"
   - Select your branch and click "Run workflow"

2. Verify that:
   - Issues are being mirrored from `okd-project/okd`
   - Mirrored issues have the `kind/bug` label
   - The AI triage workflow runs automatically
   - Slack notifications are sent (if configured)

## How It Works

### Issue Mirroring Process

1. **Scheduled Execution**: The workflow runs every 5 minutes (configurable via cron)
2. **Fetch Issues**: Retrieves all open issues from `okd-project/okd`
3. **Check Tracking**: Compares against `.github/mirrored-issues.json` to avoid duplicates
4. **Create Mirrored Issues**: For each new issue:
   - Creates a new issue in your fork with title: `[ORIGINAL #<number>] <original title>`
   - Includes original issue details and a link back to the original
   - Automatically adds `kind/bug` label to trigger AI triage
5. **Update Tracking**: Records processed issue numbers in the tracking file

### AI Triage Process

1. **Trigger**: When an issue is created or labeled with `kind/bug`
2. **AI Assessment**: Uses GitHub's AI assessment action to analyze the issue
3. **Label Assignment**: Automatically creates labels like:
   - `ai:bug-triage:critical-networking`
   - `ai:bug-triage:high-coreapi`
   - Format: `ai:bug-triage:{priority}-{component}`
4. **Comment**: Posts an explanation comment on the issue
5. **Slack Notification**: Sends assessment results to Slack (if configured)

## Configuration

### Adjust Mirror Schedule

Edit `.github/workflows/mirror-issues.yml` and modify the cron schedule:

```yaml
schedule:
  - cron: '*/5 * * * *'  # Every 5 minutes
  # Other examples:
  # - cron: '0 * * * *'   # Every hour
  # - cron: '0 */6 * * *' # Every 6 hours
```

### Change Repository Names

If you need to mirror from a different repository, update the environment variables in `.github/workflows/mirror-issues.yml`:

```yaml
env:
  ORIGINAL_OWNER: okd-project
  ORIGINAL_REPO: okd
  FORK_OWNER: kenjpais
  FORK_REPO: okd
```

### Modify AI Triage Behavior

Edit `.github/prompts/bug-triage.prompt.yml` to change how issues are assessed.

## Troubleshooting

### Issues Not Being Mirrored

1. Check the Actions tab for workflow run logs
2. Verify `PAT_TOKEN` secret is set correctly
3. Ensure the PAT has `repo` scope
4. Check that the original repository is accessible (public repos don't need special permissions)

### AI Triage Not Running

1. Verify the mirrored issue has the `kind/bug` label
2. Check the Actions tab for the triage workflow logs
3. Ensure the workflow file has correct permissions

### Slack Notifications Not Working

1. Verify `SLACK_WEBHOOK_URL` secret is set
2. Test the webhook URL manually
3. Check workflow logs for Slack-related errors

### Rate Limiting

If you encounter rate limiting:
- The workflow includes a 1-second delay between issue creations
- GitHub API rate limits: 5,000 requests/hour for authenticated requests
- If needed, increase the delay or reduce the schedule frequency

## Monitoring

- **Workflow Runs**: Check the Actions tab to see workflow execution history
- **Tracking File**: View `.github/mirrored-issues.json` to see which issues have been processed
- **Slack Channel**: Monitor Slack for AI assessment notifications

## Security Notes

- Never commit your PAT token to the repository
- Use repository secrets for all sensitive values
- Regularly rotate your PAT token
- Review workflow logs for any unexpected behavior

## Support

For issues or questions:
1. Check the workflow logs in the Actions tab
2. Review this documentation
3. Check GitHub Actions documentation: https://docs.github.com/en/actions

