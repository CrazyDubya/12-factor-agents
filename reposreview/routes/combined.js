/**
 * Combined Operations Routes
 * Handles operations that combine GitHub CLI and Cloudflare Wrangler
 */

const express = require('express');
const { exec } = require('child_process');
const { promisify } = require('util');
const fs = require('fs').promises;
const path = require('path');
const execAsync = promisify(exec);

const router = express.Router();

/**
 * Check if directory contains a Dockerfile
 * @param {string} directory - Directory path to check
 * @returns {Promise<boolean>} True if Dockerfile exists
 */
async function hasDockerfile(directory) {
  try {
    await fs.access(path.join(directory, 'Dockerfile'));
    return true;
  } catch (_error) {
    return false;
  }
}

/**
 * Clone from GitHub and deploy to Cloudflare
 */
router.post('/clone-and-deploy', async (req, res) => {
  try {
    const { repo, project_name, deploy_type = 'auto' } = req.body;
    const tempDir = `/tmp/clone-${Date.now()}`;

    // Step 1: Clone repository
    await execAsync(`gh repo clone ${repo} ${tempDir}`);

    // Step 2: Detect deployment type
    let deploymentType = deploy_type;
    if (deploy_type === 'auto') {
      deploymentType = (await hasDockerfile(tempDir)) ? 'container' : 'pages';
    }

    // Step 3: Deploy based on type
    let deploymentUrl = null;
    let deploymentMessage = '';

    if (deploymentType === 'container') {
      const cmd = `wrangler deploy --dockerfile ${path.join(tempDir, 'Dockerfile')} --name ${project_name}`;
      const { stdout } = await execAsync(cmd, { cwd: tempDir });
      const urlMatch = stdout.match(/https:\/\/[^\s]+/);
      deploymentUrl = urlMatch ? urlMatch[0] : null;
      deploymentMessage = 'Cloned and deployed as Cloudflare Container';
    } else {
      const cmd = `wrangler pages deploy ${tempDir} --project-name ${project_name}`;
      const { stdout } = await execAsync(cmd);
      const urlMatch = stdout.match(/https:\/\/[^\s]+/);
      deploymentUrl = urlMatch ? urlMatch[0] : null;
      deploymentMessage = 'Cloned and deployed to Cloudflare Pages';
    }

    // Step 4: Cleanup temporary directory
    await execAsync(`rm -rf ${tempDir}`);

    res.json({
      success: true,
      message: deploymentMessage,
      type: deploymentType,
      url: deploymentUrl
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

module.exports = router;
