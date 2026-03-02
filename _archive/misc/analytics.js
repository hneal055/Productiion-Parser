// Enhanced Analytics Functionality
class AURAAnalytics {
    constructor() {
        this.initializeAnalytics();
    }

    initializeAnalytics() {
        this.setupModalListeners();
        this.initializePredictiveMetrics();
        this.renderEnhancedVisualizations();
    }

    setupModalListeners() {
        // Listen for modal open events
        document.addEventListener('openModal', (event) => {
            switch (event.detail.type) {
                case 'customerHealth':
                    this.openCustomerHealthModal();
                    break;
                case 'geoDistribution':
                    this.openGeoModal();
                    break;
            }
        });

        // Close modal when close button is clicked
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('close-modal') || 
                e.target.closest('.close-modal')) {
                this.closeAllModals();
            }
        });
    }

    openCustomerHealthModal() {
        this.renderCustomerHealthModal();
        const modal = document.getElementById('customerHealthModal');
        if (modal) {
            modal.style.display = 'flex';
        }
    }

    openGeoModal() {
        this.renderGeoModal();
        const modal = document.getElementById('geoModal');
        if (modal) {
            modal.style.display = 'flex';
        }
    }

    closeAllModals() {
        document.querySelectorAll('.modal-overlay').forEach(modal => {
            modal.style.display = 'none';
        });
    }

    renderCustomerHealthModal() {
        const modalContainer = document.getElementById('customerHealthModal');
        if (!modalContainer) {
            this.createCustomerHealthModal();
        }
    }

    createCustomerHealthModal() {
        const modalHTML = `
        <div id="customerHealthModal" class="modal-overlay">
            <div class="modal-content">
                <div class="modal-header">
                    <h3 class="modal-title">Customer Health Dashboard</h3>
                    <button class="close-modal" onclick="closeModal('customerHealthModal')">×</button>
                </div>
                
                <div class="health-grid">
                    <div class="health-metric">
                        <div class="health-value healthy">40</div>
                        <div class="health-label">Healthy</div>
                    </div>
                    <div class="health-metric">
                        <div class="health-value needs-attention">2</div>
                        <div class="health-label">Needs Attention</div>
                    </div>
                    <div class="health-metric">
                        <div class="health-value at-risk">1</div>
                        <div class="health-label">At Risk</div>
                    </div>
                </div>

                <div class="customer-list">
                    <h4>Enterprise Customers</h4>
                    <div class="customer-logos">
                        <div class="logo-placeholder">ACME Corp</div>
                        <div class="logo-placeholder">GlobalTech</div>
                        <div class="logo-placeholder">InnovateLabs</div>
                        <div class="logo-placeholder">ScreenCraft Pro</div>
                        <div class="logo-placeholder">StoryFlow AI</div>
                    </div>
                </div>

                <div class="customer-list">
                    <h4>Customer Tier Distribution</h4>
                    <div class="tier-distribution">
                        <div class="tier-bar enterprise" style="width: 60%">
                            <span>Enterprise: 60%</span>
                        </div>
                        <div class="tier-bar professional" style="width: 30%">
                            <span>Professional: 30%</span>
                        </div>
                        <div class="tier-bar starter" style="width: 10%">
                            <span>Starter: 10%</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHTML);
    }

    renderGeoModal() {
        const modalContainer = document.getElementById('geoModal');
        if (!modalContainer) {
            this.createGeoModal();
        }
    }

    createGeoModal() {
        const modalHTML = `
        <div id="geoModal" class="modal-overlay">
            <div class="modal-content">
                <div class="modal-header">
                    <h3 class="modal-title">Geographic Request Distribution</h3>
                    <button class="close-modal" onclick="closeModal('geoModal')">×</button>
                </div>
                
                <div class="geo-distribution">
                    <div class="region-stats">
                        <div class="region-stat">
                            <span class="region-name">North America</span>
                            <span class="region-percentage">45%</span>
                        </div>
                        <div class="region-stat">
                            <span class="region-name">Europe</span>
                            <span class="region-percentage">33%</span>
                        </div>
                        <div class="region-stat">
                            <span class="region-name">Asia Pacific</span>
                            <span class="region-percentage">22%</span>
                        </div>
                    </div>
                    
                    <div class="geo-map-placeholder">
                        <div class="map-visual">
                            <div class="region na" style="width: 45%">NA - 45%</div>
                            <div class="region eu" style="width: 33%">EU - 33%</div>
                            <div class="region apac" style="width: 22%">APAC - 22%</div>
                        </div>
                    </div>

                    <div class="growth-metrics">
                        <h4>Regional Growth (Last 30 Days)</h4>
                        <div class="growth-stats">
                            <div class="growth-stat">
                                <span class="region-name">North America</span>
                                <span class="growth-percentage positive">+8.2%</span>
                            </div>
                            <div class="growth-stat">
                                <span class="region-name">Europe</span>
                                <span class="growth-percentage positive">+5.7%</span>
                            </div>
                            <div class="growth-stat">
                                <span class="region-name">Asia Pacific</span>
                                <span class="growth-percentage positive">+22.1%</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHTML);
    }

    initializePredictiveMetrics() {
        // Calculate and update predictive metrics
        this.updateRevenueProjection();
        this.updateRequestProjection();
        this.generateAIInsights();
    }

    updateRevenueProjection() {
        const currentRevenue = AURAConfig.mockData.monthlyRevenue;
        const growthRate = 0.042; // 4.2% monthly growth
        const projectedRevenue = currentRevenue * (1 + growthRate);
        
        const projectionElement = document.querySelector('.revenue-card .trend-text');
        if (projectionElement) {
            projectionElement.textContent = `On track for ${DashboardUtils.formatCurrency(projectedRevenue)}`;
        }
    }

    updateRequestProjection() {
        const currentRequests = AURAConfig.mockData.dailyRequests;
        const growthRate = 0.0182; // 1.82% daily growth
        const projectedRequests = currentRequests * Math.pow(1 + growthRate, 30);
        
        const projectionElement = document.querySelector('.requests-card .projection');
        if (projectionElement) {
            projectionElement.textContent = `Projected: ${DashboardUtils.formatNumber(Math.round(projectedRequests / 1000000 * 10) / 10)}M in 30 days`;
        }
    }

    generateAIInsights() {
        // In a real implementation, this would call an AI service
        // For now, we'll use predefined insights that rotate
        const insights = [
            "Revenue growth primarily driven by 15% increase in Enterprise tier usage",
            "APAC region shows highest growth with 22% increase in API calls",
            "All systems performing within optimal parameters",
            "Customer retention rate improved to 94.3% this quarter",
            "Average response time decreased by 12% after latest optimization"
        ];

        // Rotate insights every 30 seconds
        setInterval(() => {
            this.updateInsights(insights);
        }, 30000);
    }

    updateInsights(insights) {
        const insightsContainer = document.querySelector('.insights-content');
        if (!insightsContainer) return;

        // Get 3 random insights (without duplicates)
        const selectedInsights = this.getRandomInsights(insights, 3);
        
        insightsContainer.innerHTML = selectedInsights.map(insight => `
            <div class="insight-item">
                <span class="insight-bullet">•</span>
                <span class="insight-text">${insight}</span>
            </div>
        `).join('');

        // Update timestamp
        const timestampElement = document.querySelector('.insights-timestamp');
        if (timestampElement) {
            const now = new Date();
            timestampElement.textContent = `Updated ${now.toLocaleTimeString()}`;
        }
    }

    getRandomInsights(insights, count) {
        const shuffled = [...insights].sort(() => 0.5 - Math.random());
        return shuffled.slice(0, count);
    }

    renderEnhancedVisualizations() {
        // This would integrate with sparklines.js for advanced charts
        console.log('Enhanced visualizations initialized');
    }
}

// Initialize analytics when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.auraAnalytics = new AURAAnalytics();
});