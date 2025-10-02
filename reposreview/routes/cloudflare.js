/**
 * Cloudflare API Routes
 * Handles Cloudflare Pages and Container deployments via Wrangler CLI
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
 * Detect deployment type based on repository structure
 * @param {string} directory - Repository directory
 * @returns {Promise<string>} 'container' or 'pages'
 */
async function detectDeploymentType(directory) {
  if (await hasDockerfile(directory)) {
    return 'container';
  }
  return 'pages';
}

// Cloudflare Pages Operations
router.get('/projects', async (_req, res) => {
  try {
    const { stdout } = await execAsync('wrangler pages project list --format json');
    const projects = JSON.parse(stdout || '[]');
    res.json({ success: true, data: projects });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

router.post('/project/create', async (req, res) => {
  try {
    const { name, production_branch = 'main' } = req.body;
    await execAsync(
      `wrangler pages project create ${name} --production-branch ${production_branch}`
    );
    res.json({ success: true, message: 'Cloudflare Pages project created successfully' });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

router.post('/deploy', async (req, res) => {
  try {
    const { directory, project_name, branch = 'main' } = req.body;
    const cmd = `wrangler pages deploy ${directory} --project-name ${project_name} --branch ${branch}`;
    const { stdout } = await execAsync(cmd);
    const urlMatch = stdout.match(/https:\/\/[^\s]+/);
    const deploymentUrl = urlMatch ? urlMatch[0] : null;

    res.json({
      success: true,
      message: 'Deployed to Cloudflare Pages successfully',
      url: deploymentUrl
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Cloudflare Container Operations (NEW 2025)
router.get('/container/list', async (_req, res) => {
  try {
    const { stdout } = await execAsync('wrangler deployments list --format json');
    const containers = JSON.parse(stdout || '[]');
    res.json({ success: true, data: containers });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

router.post('/container/deploy', async (req, res) => {
  try {
    const { directory, name, dockerfile = 'Dockerfile' } = req.body;
    const dockerfilePath = path.join(directory, dockerfile);

    // Verify Dockerfile exists
    await fs.access(dockerfilePath);

    // Build and deploy container
    const cmd = `wrangler deploy --dockerfile ${dockerfilePath} --name ${name}`;
    const { stdout } = await execAsync(cmd, { cwd: directory });

    const urlMatch = stdout.match(/https:\/\/[^\s]+/);
    const deploymentUrl = urlMatch ? urlMatch[0] : null;

    res.json({
      success: true,
      message: 'Container deployed to Cloudflare successfully',
      url: deploymentUrl
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Smart Deploy - Auto-detect deployment type
router.post('/deploy/auto', async (req, res) => {
  try {
    const { directory, name } = req.body;
    const deploymentType = await detectDeploymentType(directory);

    if (deploymentType === 'container') {
      // Deploy as container
      const cmd = `wrangler deploy --dockerfile ${path.join(directory, 'Dockerfile')} --name ${name}`;
      const { stdout } = await execAsync(cmd, { cwd: directory });
      const urlMatch = stdout.match(/https:\/\/[^\s]+/);

      res.json({
        success: true,
        type: 'container',
        message: 'Deployed as Cloudflare Container',
        url: urlMatch ? urlMatch[0] : null
      });
    } else {
      // Deploy as static site
      const cmd = `wrangler pages deploy ${directory} --project-name ${name}`;
      const { stdout } = await execAsync(cmd);
      const urlMatch = stdout.match(/https:\/\/[^\s]+/);

      res.json({
        success: true,
        type: 'pages',
        message: 'Deployed to Cloudflare Pages',
        url: urlMatch ? urlMatch[0] : null
      });
    }
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

module.exports = router;
