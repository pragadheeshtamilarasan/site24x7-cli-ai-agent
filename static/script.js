/**
 * Site24x7 CLI AI Agent - Frontend JavaScript
 * Handles dynamic interactions and API calls
 */

// Global variables
let actionInProgress = false;
let refreshInterval = null;

/**
 * Initialize the application
 */
document.addEventListener('DOMContentLoaded', function() {
    initializeComponents();
    setupEventListeners();
    
    // Auto-refresh functionality
    startAutoRefresh();
});

/**
 * Initialize components
 */
function initializeComponents() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Handle form submissions
    document.addEventListener('submit', function(e) {
        const form = e.target;
        if (form.classList.contains('needs-validation')) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        }
    });
    
    // Handle AJAX errors globally
    window.addEventListener('unhandledrejection', function(event) {
        console.error('Unhandled promise rejection:', event.reason);
        showNotification('An unexpected error occurred', 'error');
    });
}

/**
 * Start auto-refresh functionality
 */
function startAutoRefresh() {
    // Clear existing interval
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
    
    // Set up new interval (every 30 seconds)
    refreshInterval = setInterval(() => {
        if (!actionInProgress) {
            refreshStatus();
        }
    }, 30000);
}

/**
 * Stop auto-refresh
 */
function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
    }
}

/**
 * Refresh system status
 */
async function refreshStatus() {
    try {
        const response = await fetch('/api/v1/status');
        const data = await response.json();
        
        if (response.ok) {
            updateStatusDisplay(data);
            updateLastUpdateTime();
        } else {
            console.error('Status refresh failed:', data);
        }
    } catch (error) {
        console.error('Status refresh error:', error);
    }
}

/**
 * Update status display
 */
function updateStatusDisplay(status) {
    // Update overall health
    const healthElement = document.querySelector('[data-status="health"]');
    if (healthElement) {
        const badgeClass = getStatusBadgeClass(status.overall_health);
        healthElement.className = `badge ${badgeClass}`;
        healthElement.innerHTML = `<i class="fas fa-${getStatusIcon(status.overall_health)} me-1"></i>${status.overall_health.charAt(0).toUpperCase() + status.overall_health.slice(1)}`;
    }
    
    // Update scheduler status
    const schedulerElement = document.querySelector('[data-status="scheduler"]');
    if (schedulerElement) {
        const badgeClass = status.scheduler_status === 'running' ? 'bg-success' : 'bg-danger';
        schedulerElement.className = `badge ${badgeClass}`;
        schedulerElement.innerHTML = `<i class="fas fa-${status.scheduler_status === 'running' ? 'play' : 'stop'} me-1"></i>${status.scheduler_status.charAt(0).toUpperCase() + status.scheduler_status.slice(1)}`;
    }
    
    // Update endpoints count
    const endpointsElement = document.querySelector('[data-status="endpoints"]');
    if (endpointsElement) {
        endpointsElement.textContent = status.api_documentation.endpoints_count || 0;
    }
}

/**
 * Get status badge class
 */
function getStatusBadgeClass(status) {
    switch (status) {
        case 'healthy': return 'bg-success';
        case 'degraded': return 'bg-warning';
        case 'error': return 'bg-danger';
        default: return 'bg-secondary';
    }
}

/**
 * Get status icon
 */
function getStatusIcon(status) {
    switch (status) {
        case 'healthy': return 'check-circle';
        case 'degraded': return 'exclamation-triangle';
        case 'error': return 'times-circle';
        default: return 'question-circle';
    }
}

/**
 * Update last update time
 */
function updateLastUpdateTime() {
    const lastUpdateElement = document.getElementById('last-update');
    if (lastUpdateElement) {
        const now = new Date();
        lastUpdateElement.textContent = now.toISOString().slice(0, 19) + 'Z';
    }
}

/**
 * Load repository information
 */
async function loadRepositoryInfo() {
    const container = document.getElementById('repository-info');
    if (!container) return;
    
    try {
        const response = await fetch('/api/v1/repository');
        const data = await response.json();
        
        if (response.ok) {
            container.innerHTML = `
                <div class="row">
                    <div class="col-sm-6">
                        <strong>Repository:</strong><br>
                        <a href="${data.url}" target="_blank" class="text-decoration-none">
                            <i class="fab fa-github me-1"></i>${data.full_name}
                        </a>
                    </div>
                    <div class="col-sm-6">
                        <strong>Stars:</strong> <span class="badge bg-warning">${data.stars || 0}</span><br>
                        <strong>Forks:</strong> <span class="badge bg-info">${data.forks || 0}</span>
                    </div>
                </div>
                <div class="row mt-3">
                    <div class="col-sm-6">
                        <strong>Default Branch:</strong><br>
                        <code>${data.default_branch || 'main'}</code>
                    </div>
                    <div class="col-sm-6">
                        <strong>Last Updated:</strong><br>
                        <small class="text-muted">${data.updated_at ? new Date(data.updated_at).toLocaleString() : 'Unknown'}</small>
                    </div>
                </div>
            `;
        } else {
            throw new Error(data.detail || 'Failed to load repository info');
        }
    } catch (error) {
        console.error('Repository info error:', error);
        container.innerHTML = `
            <div class="alert alert-warning mb-0">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Unable to load repository information: ${error.message}
            </div>
        `;
    }
}

/**
 * Trigger manual update
 */
async function triggerManualUpdate() {
    if (actionInProgress) {
        showNotification('Another action is already in progress', 'warning');
        return;
    }
    
    const modal = showActionModal('Full Update', 'Performing full update: scraping API documentation, generating CLI, and deploying to GitHub...');
    actionInProgress = true;
    
    try {
        const response = await fetch('/api/v1/actions/full-update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (response.ok && data.status === 'success') {
            showActionResult(modal, 'success', 'Full update completed successfully!', data.message);
            setTimeout(() => {
                refreshStatus();
                loadRepositoryInfo();
            }, 2000);
        } else {
            throw new Error(data.message || 'Update failed');
        }
    } catch (error) {
        console.error('Manual update error:', error);
        showActionResult(modal, 'error', 'Update Failed', error.message);
    } finally {
        actionInProgress = false;
    }
}

/**
 * Trigger GitHub maintenance
 */
async function triggerMaintenance() {
    if (actionInProgress) {
        showNotification('Another action is already in progress', 'warning');
        return;
    }
    
    const modal = showActionModal('GitHub Maintenance', 'Performing GitHub maintenance: handling issues, pull requests, and repository cleanup...');
    actionInProgress = true;
    
    try {
        const response = await fetch('/api/v1/actions/github-maintenance', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (response.ok && data.status === 'success') {
            showActionResult(modal, 'success', 'GitHub maintenance completed!', data.message);
        } else {
            throw new Error(data.message || 'Maintenance failed');
        }
    } catch (error) {
        console.error('GitHub maintenance error:', error);
        showActionResult(modal, 'error', 'Maintenance Failed', error.message);
    } finally {
        actionInProgress = false;
    }
}

/**
 * Scrape API documentation
 */
async function scrapeAPI() {
    if (actionInProgress) {
        showNotification('Another action is already in progress', 'warning');
        return;
    }
    
    const modal = showActionModal('API Scraping', 'Scraping Site24x7 API documentation...');
    actionInProgress = true;
    
    try {
        const response = await fetch('/api/v1/actions/scrape', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (response.ok && data.status === 'success') {
            showActionResult(modal, 'success', 'API scraping completed!', 
                `Found ${data.endpoints_count} endpoints across ${data.categories_count} categories`);
        } else {
            throw new Error(data.message || 'Scraping failed');
        }
    } catch (error) {
        console.error('API scraping error:', error);
        showActionResult(modal, 'error', 'Scraping Failed', error.message);
    } finally {
        actionInProgress = false;
    }
}

/**
 * Generate CLI
 */
async function generateCLI() {
    if (actionInProgress) {
        showNotification('Another action is already in progress', 'warning');
        return;
    }
    
    const modal = showActionModal('CLI Generation', 'Generating CLI from latest API documentation...');
    actionInProgress = true;
    
    try {
        const response = await fetch('/api/v1/actions/generate-cli', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (response.ok && data.status === 'success') {
            showActionResult(modal, 'success', 'CLI generation completed!', 
                `Generated version ${data.version} with ${data.files_count} files covering ${data.endpoints_covered} endpoints`);
        } else {
            throw new Error(data.message || 'CLI generation failed');
        }
    } catch (error) {
        console.error('CLI generation error:', error);
        showActionResult(modal, 'error', 'Generation Failed', error.message);
    } finally {
        actionInProgress = false;
    }
}

/**
 * Show action modal
 */
function showActionModal(title, message) {
    const modal = document.getElementById('actionModal');
    const titleElement = document.getElementById('actionModalTitle');
    const bodyElement = document.getElementById('actionModalBody');
    const footerElement = document.getElementById('actionModalFooter');
    
    titleElement.textContent = title;
    bodyElement.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-3 mb-0">${message}</p>
        </div>
    `;
    footerElement.style.display = 'none';
    
    const bootstrapModal = new bootstrap.Modal(modal, {
        backdrop: 'static',
        keyboard: false
    });
    bootstrapModal.show();
    
    return { modal, bootstrapModal, titleElement, bodyElement, footerElement };
}

/**
 * Show action result
 */
function showActionResult(modalData, status, title, message) {
    const { bodyElement, footerElement } = modalData;
    
    const alertClass = status === 'success' ? 'alert-success' : 'alert-danger';
    const icon = status === 'success' ? 'check-circle' : 'times-circle';
    
    bodyElement.innerHTML = `
        <div class="alert ${alertClass} mb-0">
            <div class="d-flex align-items-center">
                <i class="fas fa-${icon} fa-2x me-3"></i>
                <div>
                    <h5 class="alert-heading mb-1">${title}</h5>
                    <p class="mb-0">${message}</p>
                </div>
            </div>
        </div>
    `;
    
    footerElement.style.display = 'block';
}

/**
 * Show notification
 */
function showNotification(message, type = 'info', duration = 5000) {
    const alertClass = type === 'success' ? 'alert-success' : 
                     type === 'error' ? 'alert-danger' : 
                     type === 'warning' ? 'alert-warning' : 'alert-info';
    
    const icon = type === 'success' ? 'check-circle' : 
                type === 'error' ? 'times-circle' : 
                type === 'warning' ? 'exclamation-triangle' : 'info-circle';
    
    const notification = document.createElement('div');
    notification.className = `alert ${alertClass} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        <i class="fas fa-${icon} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after duration
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, duration);
}

/**
 * Format timestamp
 */
function formatTimestamp(timestamp) {
    if (!timestamp) return 'Unknown';
    
    const date = new Date(timestamp);
    return date.toLocaleString();
}

/**
 * Format file size
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Copy to clipboard
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showNotification('Copied to clipboard!', 'success', 2000);
    } catch (error) {
        console.error('Copy failed:', error);
        showNotification('Failed to copy to clipboard', 'error');
    }
}

/**
 * Download data as file
 */
function downloadData(data, filename, type = 'application/json') {
    const blob = new Blob([typeof data === 'string' ? data : JSON.stringify(data, null, 2)], { type });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    
    URL.revokeObjectURL(url);
}

/**
 * Debounce function
 */
function debounce(func, wait) {
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

/**
 * Throttle function
 */
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Toggle between OpenAI and Local LLM configuration
 */
function toggleLLMConfig() {
    const useOpenAI = document.getElementById('use_openai').checked;
    const useLocalLLM = document.getElementById('use_local_llm').checked;
    const openaiConfig = document.getElementById('openai_config');
    const localLLMConfig = document.getElementById('local_llm_config');
    const hiddenField = document.getElementById('use_local_llm_hidden');
    
    if (useOpenAI) {
        openaiConfig.classList.remove('collapse');
        localLLMConfig.classList.add('collapse');
        hiddenField.value = 'false';
    } else if (useLocalLLM) {
        openaiConfig.classList.add('collapse');
        localLLMConfig.classList.remove('collapse');
        hiddenField.value = 'true';
    }
}

// Export functions for global use
window.Site24x7Agent = {
    refreshStatus,
    loadRepositoryInfo,
    triggerManualUpdate,
    triggerMaintenance,
    scrapeAPI,
    generateCLI,
    showNotification,
    copyToClipboard,
    downloadData,
    formatTimestamp,
    formatFileSize,
    toggleLLMConfig
};
