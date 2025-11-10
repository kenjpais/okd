/**
 * Processes assessment output and formats messages for GitHub summary
 */

const { formatMessage, parseAssessments } = require('./format-message');

module.exports = async function processAssessments(assessmentOutput, context, core) {
  const assessments = parseAssessments(assessmentOutput, core);
  const message = formatMessage(context.payload.issue, assessments);
  core.summary.addRaw(message);
  await core.summary.write();
};

