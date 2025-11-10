/**
 * Formats a simple message for both GitHub comments and Slack
 * Uses plain text format that works for both platforms
 */

function parseAssessments(assessmentOutput, core) {
  let assessments = [];
  try {
    assessments = JSON.parse(assessmentOutput || '[]');
  } catch (e) {
    if (core) {
      core.warning(`Failed to parse assessment output: ${e.message}`);
    }
  }
  return assessments;
}

function formatMessage(issue, assessments) {
  let message = `OKD Issue #${issue.number}: ${issue.title}\n`;
  message += `${issue.html_url}\n\n`;
  
  if (!assessments || assessments.length === 0) {
    message += 'No triage assessment available';
  } else {
    for (const assessment of assessments) {
      const label = assessment.assessmentLabel || 'N/A';
      const response = assessment.response || 'No response';
      
      message += `Label: ${label}\n`;
      message += `Assessment: ${response}\n`;
    }
  }
  
  return message.trim();
}

module.exports = { formatMessage, parseAssessments };

