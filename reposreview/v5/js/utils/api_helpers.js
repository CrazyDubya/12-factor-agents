/**
 * API Helper Utilities
 * Common functions for making API calls to the backend server
 */

const API_BASE_URL = 'http://localhost:3000';

/**
 * Make a GET request to the API
 * @param {string} endpoint - API endpoint path
 * @param {Object} params - Query parameters
 * @returns {Promise<Object>} API response data
 */
async function apiGet(endpoint, params = {}) {
  const url = new URL(`${API_BASE_URL}${endpoint}`);
  Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));

  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`API Error: ${response.status} ${response.statusText}`);
  }

  return await response.json();
}

/**
 * Make a POST request to the API
 * @param {string} endpoint - API endpoint path
 * @param {Object} data - Request body data
 * @returns {Promise<Object>} API response data
 */
async function apiPost(endpoint, data = {}) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.status} ${response.statusText}`);
  }

  return await response.json();
}

/**
 * Check if API server is healthy
 * @returns {Promise<boolean>} True if server is healthy
 */
async function checkAPIHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.ok;
  } catch (_error) {
    return false;
  }
}

/**
 * Format error message for display
 * @param {Error} error - Error object
 * @returns {string} Formatted error message
 */
function formatError(error) {
  if (error.response?.data?.error) {
    return error.response.data.error;
  }
  if (error.message) {
    return error.message;
  }
  return 'An unknown error occurred';
}

// Export functions
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { apiGet, apiPost, checkAPIHealth, formatError };
}
