/**
 * Processes assessment output and formats messages for GitHub summary
 */

const { formatMessage, parseAssessments } = require('./format-message');

async function processAssessments(assessmentOutput, issueNumber, issueTitle, issueUrl, core) {
  const assessments = parseAssessments(assessmentOutput, core);
  
  const issue = {
    number: parseInt(issueNumber),
    title: issueTitle,
    html_url: issueUrl
  };
  
  const message = formatMessage(issue, assessments);
  core.summary.addRaw(message);
  await core.summary.write();
}

module.exports = { processAssessments };

