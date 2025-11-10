/**
 * Issue-related utilities: getting issue details
 */

/**
 * Gets issue details and sets outputs
 */
async function getIssueDetails(github, context, core, issueNumber, owner, repo) {
  const { data: issue } = await github.rest.issues.get({
    owner: owner,
    repo: repo,
    issue_number: issueNumber,
  });
  
  core.setOutput('issue_number', issue.number);
  core.setOutput('issue_title', issue.title);
  core.setOutput('issue_body', issue.body || '');
  core.setOutput('issue_url', issue.html_url);
  core.setOutput('repo_name', repo);
}

module.exports = { getIssueDetails };

