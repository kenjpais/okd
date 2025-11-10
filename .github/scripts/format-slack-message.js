/**
 * Formats messages specifically for Slack
 * Converts GitHub markdown formatting to Slack's format
 */

/**
 * Converts markdown text to Slack-compatible formatting
 */
function convertMarkdownToSlack(text) {
  if (!text) return '';

  let converted = text;

  // Convert markdown headers (### Header) to bold text
  converted = converted.replace(/^###\s+(.+)$/gm, '*$1*');
  converted = converted.replace(/^##\s+(.+)$/gm, '*$1*');
  converted = converted.replace(/^#\s+(.+)$/gm, '*$1*');

  // Convert markdown bold (**text** or __text__) to Slack bold (*text*)
  converted = converted.replace(/\*\*(.+?)\*\*/g, '*$1*');
  converted = converted.replace(/__(.+?)__/g, '*$1*');

  // Convert markdown links [text](url) to Slack links <url|text>
  converted = converted.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<$2|$1>');

  // Convert markdown code blocks ``` to plain text (Slack handles these differently)
  converted = converted.replace(/```[\s\S]*?```/g, (match) => {
    return match.replace(/```/g, '');
  });

  // Convert inline code `text` to Slack inline code (same format)
  // No change needed, Slack uses the same format

  return converted;
}

/**
 * Formats a message specifically for Slack
 */
function formatSlackMessage(issue, assessments) {
  let message = `*OKD Issue #${issue.number}*: ${issue.title}\n`;
  message += `<${issue.html_url}|View Issue>\n\n`;

  if (!assessments || assessments.length === 0) {
    message += '_No triage assessment available_';
  } else {
    for (const assessment of assessments) {
      const label = assessment.assessmentLabel || 'N/A';
      const response = assessment.response || 'No response';

      // Convert markdown in the response to Slack format
      const slackFormattedResponse = convertMarkdownToSlack(response);

      message += `*Label:* ${label}\n`;
      message += `*Assessment:*\n${slackFormattedResponse}\n`;
    }
  }

  return message.trim();
}

module.exports = { formatSlackMessage, convertMarkdownToSlack };
