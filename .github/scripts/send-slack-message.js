/**
 * Sends a Slack-formatted message to Slack
 */

const { parseAssessments } = require('./format-message');
const { formatSlackMessage } = require('./format-slack-message');

async function sendSlackMessage(issueNumber, issueTitle, issueUrl, assessmentsJson, webhookUrl, core) {
  if (!webhookUrl) {
    core.warning('No Slack webhook URL provided, skipping notification');
    return;
  }

  const assessments = typeof assessmentsJson === 'string'
    ? parseAssessments(assessmentsJson, core)
    : assessmentsJson;

  const issue = {
    number: parseInt(issueNumber),
    title: issueTitle,
    html_url: issueUrl
  };

  const message = formatSlackMessage(issue, assessments);

  const payload = {
    text: message
  };

  try {
    const response = await fetch(webhookUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      throw new Error(`Slack API returned ${response.status}: ${response.statusText}`);
    }

    core.info('Slack notification sent successfully');
  } catch (err) {
    core.warning(`Slack notification failed: ${err.message}`);
    throw err;
  }
}

module.exports = { sendSlackMessage };

