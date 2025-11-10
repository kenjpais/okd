/**
 * Adds the kind/bug label to an issue
 */

async function addLabel(github, context, core, issueNumber) {
  try {
    await github.rest.issues.addLabels({
      owner: context.repo.owner,
      repo: context.repo.repo,
      issue_number: issueNumber,
      labels: ['kind/bug'],
    });
    core.info(`Added kind/bug label to issue #${issueNumber} after AI assessment`);
  } catch (error) {
    // Label might already exist, which is fine
    if (error.status === 422) {
      core.info(`Label kind/bug already exists on issue #${issueNumber}`);
    } else {
      core.warning(`Failed to add label to issue #${issueNumber}: ${error.message}`);
      throw error;
    }
  }
}

module.exports = { addLabel };

