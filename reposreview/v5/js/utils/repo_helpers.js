/**
 * Repository Helper Utilities
 * Functions for repository data processing and analysis
 */

/**
 * Calculate repository statistics
 * @param {Array} repos - Array of repository objects
 * @returns {Object} Statistics object
 */
function calculateStats(repos) {
  const stats = {
    total: repos.length,
    byLanguage: {},
    byYear: {},
    totalStars: 0,
    totalForks: 0,
    avgStars: 0,
    avgForks: 0
  };

  repos.forEach(repo => {
    // Language stats
    const lang = repo.language || repo.primaryLanguage || 'Unknown';
    stats.byLanguage[lang] = (stats.byLanguage[lang] || 0) + 1;

    // Year stats
    const year = new Date(repo.created_at || repo.createdAt).getFullYear();
    stats.byYear[year] = (stats.byYear[year] || 0) + 1;

    // Star and fork stats
    stats.totalStars += repo.stargazers_count || repo.stars || 0;
    stats.totalForks += repo.forks_count || repo.forks || 0;
  });

  stats.avgStars = Math.round(stats.totalStars / stats.total);
  stats.avgForks = Math.round(stats.totalForks / stats.total);

  return stats;
}

/**
 * Filter repositories by criteria
 * @param {Array} repos - Array of repository objects
 * @param {Object} filters - Filter criteria
 * @returns {Array} Filtered repositories
 */
function filterRepos(repos, filters = {}) {
  return repos.filter(repo => {
    // Language filter
    if (filters.language && filters.language !== 'all') {
      const repoLang = repo.language || repo.primaryLanguage || 'Unknown';
      if (repoLang !== filters.language) {
        return false;
      }
    }

    // Search filter
    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      const nameMatch = (repo.name || '').toLowerCase().includes(searchLower);
      const descMatch = (repo.description || '').toLowerCase().includes(searchLower);
      if (!nameMatch && !descMatch) {
        return false;
      }
    }

    // Year filter
    if (filters.year) {
      const repoYear = new Date(repo.created_at || repo.createdAt).getFullYear();
      if (repoYear !== parseInt(filters.year)) {
        return false;
      }
    }

    // Stars filter
    if (filters.minStars) {
      const stars = repo.stargazers_count || repo.stars || 0;
      if (stars < parseInt(filters.minStars)) {
        return false;
      }
    }

    return true;
  });
}

/**
 * Sort repositories by criteria
 * @param {Array} repos - Array of repository objects
 * @param {string} sortBy - Sort criteria
 * @param {string} order - Sort order (asc/desc)
 * @returns {Array} Sorted repositories
 */
function sortRepos(repos, sortBy = 'updated', order = 'desc') {
  const sorted = [...repos].sort((a, b) => {
    let aVal, bVal;

    switch (sortBy) {
      case 'name':
        aVal = (a.name || '').toLowerCase();
        bVal = (b.name || '').toLowerCase();
        break;
      case 'stars':
        aVal = a.stargazers_count || a.stars || 0;
        bVal = b.stargazers_count || b.stars || 0;
        break;
      case 'forks':
        aVal = a.forks_count || a.forks || 0;
        bVal = b.forks_count || b.forks || 0;
        break;
      case 'updated':
        aVal = new Date(a.updated_at || a.updatedAt || 0);
        bVal = new Date(b.updated_at || b.updatedAt || 0);
        break;
      case 'created':
        aVal = new Date(a.created_at || a.createdAt || 0);
        bVal = new Date(b.created_at || b.createdAt || 0);
        break;
      default:
        return 0;
    }

    if (aVal < bVal) {
      return order === 'asc' ? -1 : 1;
    }
    if (aVal > bVal) {
      return order === 'asc' ? 1 : -1;
    }
    return 0;
  });

  return sorted;
}

/**
 * Get top repositories by criteria
 * @param {Array} repos - Array of repository objects
 * @param {string} criteria - Criteria to rank by
 * @param {number} limit - Number of top repos to return
 * @returns {Array} Top repositories
 */
function getTopRepos(repos, criteria = 'stars', limit = 10) {
  return sortRepos(repos, criteria, 'desc').slice(0, limit);
}

/**
 * Extract unique languages from repositories
 * @param {Array} repos - Array of repository objects
 * @returns {Array} Array of unique languages
 */
function getUniqueLanguages(repos) {
  const languages = new Set();
  repos.forEach(repo => {
    const lang = repo.language || repo.primaryLanguage;
    if (lang) {
      languages.add(lang);
    }
  });
  return Array.from(languages).sort();
}

/**
 * Group repositories by language
 * @param {Array} repos - Array of repository objects
 * @returns {Object} Repositories grouped by language
 */
function groupByLanguage(repos) {
  const grouped = {};
  repos.forEach(repo => {
    const lang = repo.language || repo.primaryLanguage || 'Unknown';
    if (!grouped[lang]) {
      grouped[lang] = [];
    }
    grouped[lang].push(repo);
  });
  return grouped;
}

// Export functions
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    calculateStats,
    filterRepos,
    sortRepos,
    getTopRepos,
    getUniqueLanguages,
    groupByLanguage
  };
}
