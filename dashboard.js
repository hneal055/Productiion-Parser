// Main Dashboard JavaScript
class AURADashboard {
    constructor() {
        this.initializeDashboard();
    }

    initializeDashboard() {
        console.log('🚀 AURA Enterprise Dashboard Initialized');
        this.setupEventListeners();
        this.loadRealTimeData();
        this.initializeModals();
    }

    setupEventListeners() {
        // Quick Actions event listeners
        document.querySelectorAll('.action-btn').forEach(button => {
            button.addEventListener('click', (e) => {
                this.handleQuickAction(e.target.textContent);
            });
        });

        // Global click handlers for modals
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-overlay')) {
                this.closeAllModals();
            }
        });

        // Escape key to close modals
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAllModals();
            }
        });
    }

    handleQuickAction(action) {
        const actions = {
            'System Health': () => this.showSystemHealth(),
            'AI Analysis': () => this.runAIAnalysis(),
            'Batch Test': () => this.runBatchTest(),
            'Full Test Suite': () => this.runFullTestSuite()
        };

        if (actions[action]) {
            actions[action]();
        } else {
            console.log(`Action triggered: ${action}`);
        }
    }

    showSystemHealth() {
        // In a real app, this would fetch actual health data
        const healthData = {
            status: 'healthy',
            components: {
                api: { status: 'operational', responseTime: '45ms' },
                database: { status: 'operational', connections: '24' },
                cache: { status: 'operational', hitRate: '98.2%' },
                ai_model: { status: 'operational', latency: '120ms' }
            }
        };
        
        alert('System Health: All systems operational ✅\n\n' +
              `API: ${healthData.components.api.status} (${healthData.components.api.responseTime})\n` +
              `Database: ${healthData.components.database.status} (${healthData.components.database.connections} connections)\n` +
              `Cache: ${healthData.components.cache.status} (${healthData.components.cache.hitRate} hit rate)\n` +
              `AI Model: ${healthData.components.ai_model.status} (${healthData.components.ai_model.latency} latency)`);
    }

    runAIAnalysis() {
        alert('AI Analysis: Launching analysis interface...\nThis would open the screenplay analysis tool in a real implementation.');
    }

    runBatchTest() {
        alert('Batch Test: Starting batch processing test...\nThis would execute a batch analysis test suite.');
    }

    runFullTestSuite() {
        alert('Full Test Suite: Executing comprehensive tests...\nThis would run the complete test suite including integration tests.');
    }

    loadRealTimeData() {
        // Simulate real-time data updates
        setInterval(() => {
            this.updateRequestCount();
        }, 30000); // Update every 30 seconds
    }

    updateRequestCount() {
        const requestsElement = document.querySelector('.requests');
        if (requestsElement) {
            const current = parseInt(requestsElement.textContent.match(/\d+/)[0]);
            const newCount = current + Math.floor(Math.random() * 5) + 1;
            requestsElement.textContent = `• ${newCount.toLocaleString()} Requests Today`;
        }
    }

    initializeModals() {
        // Modal initialization will be handled by the Analytics class
        console.log('Modals initialized');
    }

    closeAllModals() {
        document.querySelectorAll('.modal-overlay').forEach(modal => {
            modal.style.display = 'none';
        });
    }
}

// Utility functions
const DashboardUtils = {
    formatCurrency: (amount) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(amount);
    },

    formatNumber: (number) => {
        return new Intl.NumberFormat('en-US').format(number);
    },

    formatPercentage: (number) => {
        return new Intl.NumberFormat('en-US', {
            style: 'percent',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(number);
    }
};

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.auraDashboard = new AURADashboard();
});

// Global modal functions (for HTML onclick handlers)
function openCustomerHealthModal() {
    const event = new CustomEvent('openModal', { detail: { type: 'customerHealth' } });
    document.dispatchEvent(event);
}

function openGeoModal() {
    const event = new CustomEvent('openModal', { detail: { type: 'geoDistribution' } });
    document.dispatchEvent(event);
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}