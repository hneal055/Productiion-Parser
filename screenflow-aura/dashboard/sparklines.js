// Sparkline Chart Utilities
class SparklineCharts {
    constructor() {
        this.colors = AURAConfig.ui.colors;
    }

    initSparklines() {
        this.renderRevenueSparkline();
        this.renderRequestsSparkline();
    }

    renderRevenueSparkline() {
        const element = document.getElementById('revenue-sparkline');
        if (!element) return;

        // Mock revenue data (last 7 days in thousands)
        const revenueData = [11.8, 12.0, 12.1, 12.2, 12.3, 12.4, 12.5];
        this.createSparkline(element, revenueData, this.colors.revenue);
    }

    renderRequestsSparkline() {
        const element = document.getElementById('requests-sparkline');
        if (!element) return;

        // Mock requests data (last 7 days in millions)
        const requestsData = [1.15, 1.16, 1.17, 1.18, 1.19, 1.20, 1.22];
        this.createSparkline(element, requestsData, this.colors.requests);
    }

    createSparkline(element, data, color) {
        const width = element.clientWidth || 200;
        const height = element.clientHeight || 30;
        
        const max = Math.max(...data);
        const min = Math.min(...data);
        const range = max - min || 1;

        // Create SVG
        const svgNS = "http://www.w3.org/2000/svg";
        const svg = document.createElementNS(svgNS, "svg");
        svg.setAttribute("width", "100%");
        svg.setAttribute("height", "100%");
        svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
        svg.setAttribute("preserveAspectRatio", "none");

        // Create path for sparkline
        const points = data.map((value, index) => {
            const x = (index / (data.length - 1)) * width;
            const y = height - ((value - min) / range) * height;
            return `${x},${y}`;
        }).join(' ');

        const polyline = document.createElementNS(svgNS, "polyline");
        polyline.setAttribute("points", points);
        polyline.setAttribute("fill", "none");
        polyline.setAttribute("stroke", color);
        polyline.setAttribute("stroke-width", "2");
        polyline.setAttribute("stroke-linecap", "round");
        polyline.setAttribute("stroke-linejoin", "round");

        // Add gradient area under the line
        const areaPoints = `${points} ${width},${height} 0,${height}`;
        const polygon = document.createElementNS(svgNS, "polygon");
        polygon.setAttribute("points", areaPoints);
        polygon.setAttribute("fill", this.hexToRgba(color, 0.1));
        polygon.setAttribute("stroke", "none");

        svg.appendChild(polygon);
        svg.appendChild(polyline);

        // Clear existing content and append new SVG
        element.innerHTML = '';
        element.appendChild(svg);
    }

    hexToRgba(hex, alpha) {
        const r = parseInt(hex.slice(1, 3), 16);
        const g = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }

    // Method to update sparklines with new data
    updateSparkline(elementId, newData) {
        const element = document.getElementById(elementId);
        if (element) {
            const color = elementId.includes('revenue') ? this.colors.revenue : this.colors.requests;
            this.createSparkline(element, newData, color);
        }
    }
}

// Additional chart utilities
const ChartUtils = {
    // Generate random data for demonstration
    generateMockData: (points = 7, min = 10, max = 20) => {
        return Array.from({ length: points }, () => 
            Math.random() * (max - min) + min
        );
    },

    // Calculate trend from data
    calculateTrend: (data) => {
        if (data.length < 2) return 0;
        const first = data[0];
        const last = data[data.length - 1];
        return ((last - first) / first) * 100;
    },

    // Format trend for display
    formatTrend: (trend) => {
        const sign = trend >= 0 ? '+' : '';
        return `${sign}${trend.toFixed(2)}%`;
    }
};

// Initialize sparklines when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const sparklines = new SparklineCharts();
    sparklines.initSparklines();
    
    // Store in global scope for updates
    window.auraSparklines = sparklines;
});