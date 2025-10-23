# Slack Integration Setup for OKD AI Triage

**Repository:** https://github.com/kenjpais/okd  
**Status:** ✅ **Workflow Ready - Awaiting Slack Configuration**

---

## ✅ What's Working

The AI triage workflow has been successfully updated to send **both AI triage assessments AND issue summaries** to Slack!

### Current Functionality

1. **AI Triage Job**
   - ✅ Analyzes issues with AI
   - ✅ Posts assessment comments
   - ✅ Applies appropriate labels
   - ✅ Outputs triage results for Slack

2. **Slack Notification Job**
   - ✅ Generates AI summary of the issue
   - ✅ Receives triage assessment from ai-triage job
   - ✅ Formats rich Slack message with blocks
   - ✅ Ready to send when webhook is configured

---

## 📋 What Gets Sent to Slack

When fully configured, Slack notifications will include:

### Message Structure

```
🚨 New OKD Issue #[number]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Title: [Issue title]
👤 Author: [username]
🏷️ Labels: [comma-separated labels]
📁 Repository: kenjpais/okd

🔗 View Issue on GitHub

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🤖 AI Triage Assessment:
ai:bug-triage:ready for review
[Full triage assessment with quality analysis]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 AI Summary:
[Brief summary of the issue]
[Key technical points for OKD/Kubernetes]
[Suggested priority level]
```

---

## 🔧 How to Enable Slack Notifications

### Step 1: Create a Slack Incoming Webhook

1. Go to your Slack workspace
2. Navigate to: **Apps** → **Incoming Webhooks**
3. Click **Add to Slack**
4. Choose the channel where notifications should appear
5. Click **Add Incoming WebHooks integration**
6. Copy the **Webhook URL** (looks like: `https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXX`)

### Step 2: Add Webhook to GitHub Repository

1. Go to your repository: https://github.com/kenjpais/okd
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Set:
   - **Name:** `SLACK_WEBHOOK_URL`
   - **Value:** [paste your webhook URL]
5. Click **Add secret**

### Step 3: Test the Integration

Create a new issue with the required labels:

```bash
gh issue create \
  --title "Test Slack notification" \
  --label "triage/needs-triage,kind/bug" \
  --body "Testing Slack integration with AI triage"
```

Within ~30-40 seconds, you should receive a Slack notification!

---

## 🧪 Test Results (Without Slack)

**Test Issue #2:** [Pod crashes on startup](https://github.com/kenjpais/okd/issues/2)

✅ **Workflow Status:** Both jobs completed successfully
- `ai-triage` job: SUCCESS (20s)
- `notify-slack` job: SUCCESS (37s)

✅ **AI Triage:** Posted assessment comment
✅ **Label Applied:** `ai:bug-triage:ready for review`
✅ **Triage Output:** Successfully passed to Slack job
✅ **AI Summary:** Generated successfully

**Log Message:**
```
ℹ️ Slack webhook not configured. Set SLACK_WEBHOOK_URL secret to enable notifications.
```

The workflow **gracefully handles** missing webhook configuration and completes successfully.

---

## 📊 Workflow Details

### Jobs Overview

1. **ai-triage**
   - Runs when: Issue has `triage/needs-triage` label
   - Actions:
     - Checks out repository
     - Runs AI assessment
     - Posts comment
     - Applies labels
     - Outputs triage result

2. **notify-slack**
   - Runs when: Any issue event (always runs after ai-triage)
   - Actions:
     - Generates AI summary
     - Formats labels
     - Creates rich Slack message
     - Sends to Slack webhook (if configured)

### Data Flow

```
Issue Created/Labeled
       ↓
ai-triage Job
  - AI Analysis
  - Label Application
  - Output: triage_result
       ↓
notify-slack Job
  - Receives: triage_result
  - Generates: AI summary
  - Combines: triage + summary
  - Sends → Slack
```

---

## 📝 Slack Message Format

The workflow uses **Slack Block Kit** for rich formatting:

### Blocks Structure

1. **Header Block**
   - Shows issue number

2. **Fields Section**
   - Title, Author, Labels, Repository

3. **Link Section**
   - Direct link to GitHub issue

4. **Triage Assessment Section**
   - AI triage label
   - Full assessment text

5. **Summary Section**
   - AI-generated summary
   - Technical points
   - Priority suggestion

---

## 🔄 How It Works with Your Current Setup

### Current Behavior (No Webhook)

1. Issue is created with `triage/needs-triage`
2. AI triage runs → posts comment + applies label ✅
3. Slack job runs → generates summary ✅
4. Slack job checks for webhook → not found
5. Logs message: "Slack webhook not configured"
6. Workflow completes successfully ✅

### Behavior After Adding Webhook

1. Issue is created with `triage/needs-triage`
2. AI triage runs → posts comment + applies label ✅
3. Slack job runs → generates summary ✅
4. Slack job checks for webhook → found! ✅
5. Sends rich notification to Slack ✅
6. Logs: "Slack notification sent for issue #X" ✅
7. Workflow completes successfully ✅

---

## 🎯 Benefits

### For Issue Reporters
- Immediate AI feedback on issue quality
- Clear guidance on missing information
- Faster response from maintainers

### For Maintainers
- **Real-time Slack notifications** for all new issues
- **AI triage assessment** in every notification
- **Issue summary** for quick context
- **Priority suggestions** for planning
- **Rich formatting** for easy reading
- **Direct links** to issues

---

## 🔍 Verification

You can verify the setup is working by:

1. **Check workflow file:**
   ```bash
   cat .github/workflows/issue-triage.yml
   ```

2. **Check recent workflow runs:**
   ```bash
   gh run list --workflow=issue-triage.yml --limit 5
   ```

3. **View specific run:**
   ```bash
   gh run view [run-id] --log
   ```

4. **Check issue labels:**
   ```bash
   gh issue view 2 --json labels
   ```

---

## 📚 Related Documentation

- **Setup Guide:** OKD_AI_TRIAGE_SETUP.md
- **GitHub Action:** [AI Assessment Comment Labeler](https://github.com/marketplace/actions/ai-assessment-comment-labeler)
- **Slack Incoming Webhooks:** https://api.slack.com/messaging/webhooks

---

## ✅ Next Steps

1. **Add SLACK_WEBHOOK_URL secret** to repository (see instructions above)
2. **Create a test issue** to verify Slack notifications
3. **Customize Slack channel** if needed (update webhook)
4. **Monitor notifications** and adjust as needed

---

**Status:** Ready for Slack integration - just add the webhook secret!  
**Last Updated:** October 23, 2025
