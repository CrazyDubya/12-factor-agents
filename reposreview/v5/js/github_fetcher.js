/**
 * GitHub Fetcher - Retrieve repository data from GitHub API
 * Handles README fetching, file structure, and metadata
 */

class GitHubFetcher {
  constructor(username = 'crazydubya') {
    this.username = username;
    this.baseURL = 'https://api.github.com';
    this.cache = new Map();
    this.cacheExpiry = 300000; // 5 minutes
  }

  /**
   * Get repository details from GitHub API
   */
  async getRepository(repoName) {
    const cacheKey = `repo_${repoName}`;
    const cached = this.getFromCache(cacheKey);
    if (cached) {
      return cached;
    }

    try {
      const response = await fetch(`${this.baseURL}/repos/${this.username}/${repoName}`);
      if (!response.ok) {
        throw new Error(`GitHub API error: ${response.status}`);
      }

      const data = await response.json();
      this.setCache(cacheKey, data);
      return data;
    } catch (error) {
      console.error('Failed to fetch repository:', error);
      return null;
    }
  }

  /**
   * Get existing README.md from repository
   */
  async getReadme(repoName) {
    const cacheKey = `readme_${repoName}`;
    const cached = this.getFromCache(cacheKey);
    if (cached) {
      return cached;
    }

    try {
      // Try multiple README variations
      const variations = ['README.md', 'readme.md', 'Readme.md', 'README.MD'];

      for (const filename of variations) {
        try {
          const response = await fetch(
            `${this.baseURL}/repos/${this.username}/${repoName}/contents/${filename}`
          );

          if (response.ok) {
            const data = await response.json();

            // Decode base64 content
            const content = atob(data.content);

            const result = {
              exists: true,
              content: content,
              filename: filename,
              size: data.size,
              sha: data.sha,
              url: data.html_url
            };

            this.setCache(cacheKey, result);
            return result;
          }
        } catch (_e) {
          // Try next variation
          continue;
        }
      }

      // No README found
      const result = { exists: false, content: null };
      this.setCache(cacheKey, result);
      return result;
    } catch (error) {
      console.error('Failed to fetch README:', error);
      return { exists: false, content: null, error: error.message };
    }
  }

  /**
   * Get repository file structure
   */
  async getFileStructure(repoName, path = '') {
    const cacheKey = `tree_${repoName}_${path}`;
    const cached = this.getFromCache(cacheKey);
    if (cached) {
      return cached;
    }

    try {
      const response = await fetch(
        `${this.baseURL}/repos/${this.username}/${repoName}/contents/${path}`
      );

      if (!response.ok) {
        throw new Error(`GitHub API error: ${response.status}`);
      }

      const data = await response.json();
      this.setCache(cacheKey, data);
      return data;
    } catch (error) {
      console.error('Failed to fetch file structure:', error);
      return [];
    }
  }

  /**
   * Get repository languages
   */
  async getLanguages(repoName) {
    const cacheKey = `languages_${repoName}`;
    const cached = this.getFromCache(cacheKey);
    if (cached) {
      return cached;
    }

    try {
      const response = await fetch(`${this.baseURL}/repos/${this.username}/${repoName}/languages`);

      if (!response.ok) {
        throw new Error(`GitHub API error: ${response.status}`);
      }

      const data = await response.json();
      this.setCache(cacheKey, data);
      return data;
    } catch (error) {
      console.error('Failed to fetch languages:', error);
      return {};
    }
  }

  /**
   * Get package.json or similar config files
   */
  async getPackageInfo(repoName) {
    const configFiles = [
      'package.json',
      'requirements.txt',
      'Cargo.toml',
      'pom.xml',
      'build.gradle',
      'go.mod',
      'composer.json',
      'Gemfile'
    ];

    const results = {};

    for (const filename of configFiles) {
      try {
        const response = await fetch(
          `${this.baseURL}/repos/${this.username}/${repoName}/contents/${filename}`
        );

        if (response.ok) {
          const data = await response.json();
          const content = atob(data.content);

          try {
            results[filename] = filename.endsWith('.json') ? JSON.parse(content) : content;
          } catch (_e) {
            results[filename] = content;
          }
        }
      } catch (_e) {
        // File doesn't exist, continue
        continue;
      }
    }

    return results;
  }

  /**
   * Build comprehensive repository context for AI analysis
   */
  async buildRepositoryContext(repoName) {
    try {
      const [repo, readme, languages, fileStructure, packageInfo] = await Promise.all([
        this.getRepository(repoName),
        this.getReadme(repoName),
        this.getLanguages(repoName),
        this.getFileStructure(repoName),
        this.getPackageInfo(repoName)
      ]);

      // Determine primary language
      const primaryLanguage =
        repo?.language ||
        Object.keys(languages).sort((a, b) => languages[b] - languages[a])[0] ||
        'Unknown';

      // Build file list
      const fileList = fileStructure
        .map(f => `${f.type === 'dir' ? '📁' : '📄'} ${f.name}`)
        .join('\n');

      // Extract dependencies from package info
      let dependencies = [];
      if (packageInfo['package.json']) {
        const pkg = packageInfo['package.json'];
        dependencies = [
          ...Object.keys(pkg.dependencies || {}),
          ...Object.keys(pkg.devDependencies || {})
        ];
      }

      return {
        name: repoName,
        full_name: repo?.full_name || `${this.username}/${repoName}`,
        description: repo?.description || 'No description',
        stars: repo?.stargazers_count || 0,
        forks: repo?.forks_count || 0,
        open_issues: repo?.open_issues_count || 0,
        size: repo?.size || 0,
        language: primaryLanguage,
        languages: languages,
        created_at: repo?.created_at,
        updated_at: repo?.updated_at,
        homepage: repo?.homepage,
        topics: repo?.topics || [],

        readme: readme,
        file_structure: fileList,
        package_info: packageInfo,
        dependencies: dependencies,

        // GitHub URLs
        html_url: repo?.html_url,
        clone_url: repo?.clone_url,

        // Additional metadata
        has_wiki: repo?.has_wiki,
        has_pages: repo?.has_pages,
        license: repo?.license?.name
      };
    } catch (error) {
      console.error('Failed to build repository context:', error);
      return null;
    }
  }

  /**
   * Cache management
   */
  getFromCache(key) {
    const cached = this.cache.get(key);
    if (!cached) {
      return null;
    }

    if (Date.now() - cached.timestamp > this.cacheExpiry) {
      this.cache.delete(key);
      return null;
    }

    return cached.data;
  }

  setCache(key, data) {
    this.cache.set(key, {
      data: data,
      timestamp: Date.now()
    });
  }

  clearCache() {
    this.cache.clear();
  }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = GitHubFetcher;
}
