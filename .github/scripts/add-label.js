/**
 * Adds the kind/bug label to an issue
 */

module.exports = async function addLabel(github, context, core, issueNumber) {
  await github.rest.issues.addLabels({
    owner: context.repo.owner,
    repo: context.repo.repo,
    issue_number: issueNumber,
    labels: ['kind/bug'],
  });
  core.info(`Added kind/bug label to issue #${issueNumber} after AI assessment`);
};

