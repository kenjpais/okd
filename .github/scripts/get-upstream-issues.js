/**
 * Fetches newly created issues from upstream repository
 */

/**
 * Gets issues created in the last 24 hours from upstream repository
 */
async function getUpstreamIssues(github, core, upstreamOwner, upstreamRepo) {
  try {
    // Calculate the timestamp for 24 hours ago
    const oneDayAgo = new Date();
    oneDayAgo.setDate(oneDayAgo.getDate() - 1);
    const since = oneDayAgo.toISOString();

    core.info(`Fetching issues from ${upstreamOwner}/${upstreamRepo} created since ${since}`);

    // Fetch issues created in the last 24 hours
    const { data: allIssues } = await github.rest.issues.listForRepo({
      owner: upstreamOwner,
      repo: upstreamRepo,
      state: 'open',
      sort: 'created',
      direction: 'desc',
      since: since,
      per_page: 100,
    });

    // Filter out pull requests
    const issues = allIssues.filter(issue => !issue.pull_request);

    if (issues.length === 0) {
      core.info('No new issues found in upstream repository');
      core.setOutput('issue_numbers', '[]');
    } else {
      const issueNumbers = issues.map(issue => issue.number);
      core.setOutput('issue_numbers', JSON.stringify(issueNumbers));
      core.info(`Found ${issueNumbers.length} new issue(s) from upstream: ${issueNumbers.join(', ')}`);
    }
  } catch (error) {
    core.error(`Error fetching upstream issues: ${error.message}`);
    core.setOutput('issue_numbers', '[]');
    throw error;
  }
}

module.exports = { getUpstreamIssues };
