/**
 * DOM Helper Utilities
 * Common functions for DOM manipulation and UI updates
 */

/**
 * Show loading indicator
 * @param {HTMLElement} element - Element to show loading state
 * @param {string} message - Loading message
 */
function showLoading(element, message = 'Loading...') {
  element.innerHTML = `
    <div class="loading-state" style="text-align: center; padding: 2rem;">
      <div class="spinner" style="border: 4px solid #f3f3f3; border-top: 4px solid #3498db; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto;"></div>
      <p style="margin-top: 1rem; color: #666;">${message}</p>
    </div>
  `;
}

/**
 * Show error message
 * @param {HTMLElement} element - Element to show error state
 * @param {string} message - Error message
 */
function showError(element, message) {
  element.innerHTML = `
    <div class="error-state" style="text-align: center; padding: 2rem; color: #e74c3c;">
      <h3>⚠️ Error</h3>
      <p>${message}</p>
    </div>
  `;
}

/**
 * Show success message
 * @param {HTMLElement} element - Element to show success state
 * @param {string} message - Success message
 */
function showSuccess(element, message) {
  element.innerHTML = `
    <div class="success-state" style="text-align: center; padding: 2rem; color: #27ae60;">
      <h3>✅ Success</h3>
      <p>${message}</p>
    </div>
  `;
}

/**
 * Create a card element
 * @param {Object} options - Card options
 * @returns {HTMLElement} Card element
 */
function createCard({ title, content, actions = [] }) {
  const card = document.createElement('div');
  card.className = 'card';
  card.style.cssText =
    'border: 1px solid #ddd; border-radius: 8px; padding: 1rem; margin: 0.5rem; background: white;';

  if (title) {
    const titleEl = document.createElement('h3');
    titleEl.textContent = title;
    titleEl.style.marginBottom = '0.5rem';
    card.appendChild(titleEl);
  }

  if (content) {
    const contentEl = document.createElement('div');
    contentEl.innerHTML = content;
    card.appendChild(contentEl);
  }

  if (actions.length > 0) {
    const actionsEl = document.createElement('div');
    actionsEl.className = 'card-actions';
    actionsEl.style.cssText = 'margin-top: 1rem; display: flex; gap: 0.5rem;';

    actions.forEach(action => {
      const btn = document.createElement('button');
      btn.textContent = action.label;
      btn.className = action.className || 'btn';
      btn.onclick = action.onClick;
      actionsEl.appendChild(btn);
    });

    card.appendChild(actionsEl);
  }

  return card;
}

/**
 * Format file size for display
 * @param {number} bytes - File size in bytes
 * @returns {string} Formatted file size
 */
function formatFileSize(bytes) {
  if (bytes === 0) {
    return '0 Bytes';
  }

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

/**
 * Format date for display
 * @param {string|Date} date - Date to format
 * @returns {string} Formatted date string
 */
function formatDate(date) {
  const d = new Date(date);
  return d.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
}

/**
 * Debounce function calls
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
function debounce(func, wait = 300) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Export functions
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    showLoading,
    showError,
    showSuccess,
    createCard,
    formatFileSize,
    formatDate,
    debounce
  };
}
