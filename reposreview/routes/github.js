/**
 * GitHub API Routes
 * Handles all GitHub CLI operations: repos, issues, pull requests
 */

const express = require('express');
const { exec } = require('child_process');
const { promisify } = require('util');
const execAsync = promisify(exec);

const router = express.Router();

/**
 * Execute GitHub CLI command with error handling
 * @param {string} command - GitHub CLI command to execute
 * @returns {Promise<Object>} Parsed JSON result or error
 */
async function executeGitHubCommand(command) {
  try {
    const { stdout, stderr } = await execAsync(command);
    if (stderr && !stderr.includes('WARNING')) {
      throw new Error(stderr);
    }
    return JSON.parse(stdout || '{}');
  } catch (error) {
    throw new Error(`GitHub CLI error: ${error.message}`);
  }
}

// Repository Operations
router.get('/repos', async (_req, res) => {
  try {
    const repos = await executeGitHubCommand(
      'gh repo list --json name,description,url,stargazerCount,updatedAt,primaryLanguage --limit 100'
    );
    res.json({ success: true, data: repos });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

router.get('/repo/:owner/:name', async (req, res) => {
  try {
    const { owner, name } = req.params;
    const repo = await executeGitHubCommand(
      `gh repo view ${owner}/${name} --json name,description,url,stargazerCount,forkCount,openIssues,primaryLanguage,createdAt,updatedAt`
    );
    res.json({ success: true, data: repo });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

router.post('/repo/create', async (req, res) => {
  try {
    const { name, description, visibility = 'public' } = req.body;
    const visibilityFlag = visibility === 'private' ? '--private' : '--public';
    await execAsync(`gh repo create ${name} ${visibilityFlag} --description "${description}"`);
    res.json({ success: true, message: 'Repository created successfully' });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

router.post('/repo/clone', async (req, res) => {
  try {
    const { repo, destination } = req.body;
    const destFlag = destination ? destination : '.';
    await execAsync(`gh repo clone ${repo} ${destFlag}`);
    res.json({ success: true, message: 'Repository cloned successfully' });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Issue Operations
router.get('/issue/list', async (req, res) => {
  try {
    const { repo, state = 'open' } = req.query;
    const repoFlag = repo ? `-R ${repo}` : '';
    const issues = await executeGitHubCommand(
      `gh issue list ${repoFlag} --state ${state} --json number,title,state,createdAt,author`
    );
    res.json({ success: true, data: issues });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

router.get('/issue/view/:number', async (req, res) => {
  try {
    const { number } = req.params;
    const { repo } = req.query;
    const repoFlag = repo ? `-R ${repo}` : '';
    const issue = await executeGitHubCommand(
      `gh issue view ${number} ${repoFlag} --json number,title,body,state,author,createdAt,comments`
    );
    res.json({ success: true, data: issue });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

router.post('/issue/create', async (req, res) => {
  try {
    const { repo, title, body } = req.body;
    const repoFlag = repo ? `-R ${repo}` : '';
    await execAsync(`gh issue create ${repoFlag} --title "${title}" --body "${body}"`);
    res.json({ success: true, message: 'Issue created successfully' });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

router.post('/issue/close', async (req, res) => {
  try {
    const { repo, number } = req.body;
    const repoFlag = repo ? `-R ${repo}` : '';
    await execAsync(`gh issue close ${number} ${repoFlag}`);
    res.json({ success: true, message: 'Issue closed successfully' });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

router.post('/issue/comment', async (req, res) => {
  try {
    const { repo, number, comment } = req.body;
    const repoFlag = repo ? `-R ${repo}` : '';
    await execAsync(`gh issue comment ${number} ${repoFlag} --body "${comment}"`);
    res.json({ success: true, message: 'Comment added successfully' });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Pull Request Operations
router.get('/pr/list', async (req, res) => {
  try {
    const { repo, state = 'open' } = req.query;
    const repoFlag = repo ? `-R ${repo}` : '';
    const prs = await executeGitHubCommand(
      `gh pr list ${repoFlag} --state ${state} --json number,title,state,createdAt,author,headRefName`
    );
    res.json({ success: true, data: prs });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

router.post('/pr/create', async (req, res) => {
  try {
    const { repo, title, body, base = 'main', head } = req.body;
    const repoFlag = repo ? `-R ${repo}` : '';
    await execAsync(
      `gh pr create ${repoFlag} --title "${title}" --body "${body}" --base ${base} --head ${head}`
    );
    res.json({ success: true, message: 'Pull request created successfully' });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

router.post('/pr/merge', async (req, res) => {
  try {
    const { repo, number, method = 'merge' } = req.body;
    const repoFlag = repo ? `-R ${repo}` : '';
    const methodFlag = `--${method}`;
    await execAsync(`gh pr merge ${number} ${repoFlag} ${methodFlag}`);
    res.json({ success: true, message: 'Pull request merged successfully' });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

router.get('/pr/checks/:number', async (req, res) => {
  try {
    const { number } = req.params;
    const { repo } = req.query;
    const repoFlag = repo ? `-R ${repo}` : '';
    const checks = await executeGitHubCommand(
      `gh pr checks ${number} ${repoFlag} --json name,state,conclusion`
    );
    res.json({ success: true, data: checks });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

module.exports = router;
