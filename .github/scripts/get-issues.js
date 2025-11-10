/**
 * Issue-related utilities: getting issues to triage and issue details
 */

/**
 * Gets issues to triage, filtering for kind/bug label
 */
async function getIssuesToTriage(github, context, core) {
  let issues;
  
  if (context.eventName === 'issues' && context.payload.issue) {
    // Only process if issue has kind/bug label (required for AI assessment)
    if (context.payload.issue.labels?.some(l => l.name === 'kind/bug')) {
      issues = [context.payload.issue];
    } else {
      issues = [];
      core.info('Issue does not have kind/bug label, skipping triage');
    }
  } else {
    // For workflow_dispatch, get recent issues and filter for kind/bug label
    const { data: allIssues } = await github.rest.issues.listForRepo({
      owner: context.repo.owner,
      repo: context.repo.repo,
      state: 'open',
      sort: 'created',
      direction: 'desc',
      per_page: 2,
    });
    
    // Filter out pull requests and filter for kind/bug label
    issues = allIssues
      .filter(issue => !issue.pull_request)
      .filter(issue => issue.labels?.some(l => l.name === 'kind/bug'));
  }
  
  if (issues.length === 0) {
    core.info('No issues with kind/bug label found to triage');
    core.setOutput('issue_numbers', '[]');
  } else {
    const issueNumbers = issues.map(issue => issue.number);
    core.setOutput('issue_numbers', JSON.stringify(issueNumbers));
    core.info(`Processing ${issueNumbers.length} issue(s) with kind/bug label: ${issueNumbers.join(', ')}`);
  }
}

/**
 * Gets issue details and sets outputs
 */
async function getIssueDetails(github, context, core, issueNumber) {
  const { data: issue } = await github.rest.issues.get({
    owner: context.repo.owner,
    repo: context.repo.repo,
    issue_number: issueNumber,
  });
  
  core.setOutput('issue_number', issue.number);
  core.setOutput('issue_title', issue.title);
  core.setOutput('issue_body', issue.body || '');
  core.setOutput('issue_url', issue.html_url);
  
  // Extract repo name for ai-assessment action
  const repoName = context.payload.repository?.name || context.repo.repo;
  core.setOutput('repo_name', repoName);
}

module.exports = { getIssuesToTriage, getIssueDetails };

