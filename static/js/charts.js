/**
 * AniTrack — Status Distribution Chart
 * Handles Chart.js initialization and dynamic updates with modern anime-inspired styling.
 */

const AnimeCharts = {
    chartInstance: null,

    /**
     * Color configuration for each anime status.
     */
    statusColors: {
        'Watching': {
            bg: '#f59e0b',
            border: '#d97706',
            hover: '#fbbf24'
        },
        'Completed': {
            bg: '#10b981',
            border: '#059669',
            hover: '#34d399'
        },
        'Dropped': {
            bg: '#ef4444',
            border: '#dc2626',
            hover: '#f87171'
        },
        'Plan to Watch': {
            bg: '#a855f7',
            border: '#9333ea',
            hover: '#c084fc'
        }
    },

    /**
     * Initialize the Doughnut Chart on the #statusChart canvas.
     */
    init(canvasId = 'statusChart') {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;

        if (typeof Chart === 'undefined') {
            console.warn('Chart.js is not loaded yet.');
            return;
        }

        const ctx = canvas.getContext('2d');
        const defaultLabels = ['Watching', 'Completed', 'Dropped', 'Plan to Watch'];
        const defaultBg = defaultLabels.map(l => this.statusColors[l].bg);
        const defaultHover = defaultLabels.map(l => this.statusColors[l].hover);

        this.chartInstance = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: defaultLabels,
                datasets: [{
                    data: [0, 0, 0, 0],
                    backgroundColor: defaultBg,
                    hoverBackgroundColor: defaultHover,
                    borderColor: '#111726',
                    borderWidth: 3,
                    borderRadius: 4,
                    spacing: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '72%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#94a3b8',
                            font: {
                                family: "'Outfit', sans-serif",
                                size: 12,
                                weight: '500'
                            },
                            padding: 14,
                            usePointStyle: true,
                            pointStyle: 'circle'
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(17, 23, 38, 0.95)',
                        titleColor: '#ffffff',
                        bodyColor: '#cbd5e1',
                        titleFont: {
                            family: "'Outfit', sans-serif",
                            weight: '700',
                            size: 13
                        },
                        bodyFont: {
                            family: "'JetBrains Mono', monospace",
                            size: 12
                        },
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 1,
                        padding: 10,
                        boxPadding: 4,
                        callbacks: {
                            label: function(context) {
                                const val = context.raw || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const pct = total > 0 ? Math.round((val / total) * 100) : 0;
                                return ` ${context.label}: ${val} (${pct}%)`;
                            }
                        }
                    }
                },
                animation: {
                    animateScale: true,
                    animateRotate: true,
                    duration: 800
                }
            }
        });
    },

    /**
     * Update chart data with new status counts.
     */
    update(distribution = {}) {
        if (!this.chartInstance) {
            this.init();
        }
        if (!this.chartInstance) return;

        const labels = ['Watching', 'Completed', 'Dropped', 'Plan to Watch'];
        const values = labels.map(label => distribution[label] || 0);
        const total = values.reduce((sum, v) => sum + v, 0);

        if (total === 0) {
            // Empty placeholder ring
            this.chartInstance.data.labels = ['No Anime Yet'];
            this.chartInstance.data.datasets[0].data = [1];
            this.chartInstance.data.datasets[0].backgroundColor = ['#222f4d'];
            this.chartInstance.data.datasets[0].hoverBackgroundColor = ['#222f4d'];
        } else {
            this.chartInstance.data.labels = labels;
            this.chartInstance.data.datasets[0].data = values;
            this.chartInstance.data.datasets[0].backgroundColor = labels.map(l => this.statusColors[l].bg);
            this.chartInstance.data.datasets[0].hoverBackgroundColor = labels.map(l => this.statusColors[l].hover);
        }

        this.chartInstance.update();
    }
};

window.AnimeCharts = AnimeCharts;
