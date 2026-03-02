// AURA Enterprise Dashboard Configuration
const AURAConfig = {
    // API Configuration
    api: {
        baseURL: 'https://api.aura-enterprise.com/v1',
        endpoints: {
            health: '/api/health',
            analyze: '/api/analyze',
            metrics: '/api/metrics',
            customers: '/api/customers'
        },
        timeout: 30000,
        retryAttempts: 3
    },

    // Feature Flags
    features: {
        enhancedAnalytics: true,
        realTimeUpdates: true,
        predictiveMetrics: true,
        geographicInsights: true,
        customerHealthScoring: true
    },

    // Analytics Configuration
    analytics: {
        updateInterval: 30000, // 30 seconds
        sparklinePoints: 7, // Number of data points for sparklines
        predictionHorizon: 30 // Days for projections
    },

    // UI Configuration
    ui: {
        theme: 'light',
        colors: {
            primary: '#007acc',
            success: '#10b981',
            warning: '#f59e0b',
            error: '#ef4444',
            revenue: '#10b981',
            customers: '#8b5cf6',
            requests: '#007acc',
            uptime: '#6b7280'
        },
        breakpoints: {
            mobile: 768,
            tablet: 1024,
            desktop: 1200
        }
    },

    // Mock Data (for development)
    mockData: {
        monthlyRevenue: 12500,
        activeCustomers: 43,
        dailyRequests: 1200000,
        serviceUptime: 99.98
    }
};

// Export configuration
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AURAConfig;
}