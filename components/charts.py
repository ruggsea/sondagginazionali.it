from fasthtml.common import *
import json

def create_chart_scripts(dates, datasets, coalition_datasets):
    assert isinstance(dates, list), "dates must be a list"
    assert len(dates) > 0, "dates list cannot be empty"
    
    base_chart_config = {
        "type": "line",
        "data": {
            "labels": dates,
            "datasets": datasets
        },
        "options": {
            "responsive": True,
            "maintainAspectRatio": False,
            "interaction": {
                "intersect": False,
                "mode": "index"
            },
            "plugins": {
                "legend": {
                    "position": "bottom",
                    "labels": {
                        "usePointStyle": True,
                        "padding": 20,
                        "boxWidth": 10,
                        "font": {
                            "family": "system-ui, -apple-system, sans-serif",
                            "size": 12
                        }
                    },
                    "align": "center"
                }
            },
            "scales": {
                "x": {
                    "type": "time",
                    "time": {
                        "unit": "month",
                        "displayFormats": {
                            "month": "MMM yy"
                        }
                    },
                    "grid": {
                        "display": True,
                        "color": "rgba(0,0,0,0.1)",
                        "drawBorder": False
                    },
                    "ticks": {
                        "font": {
                            "size": 11
                        }
                    }
                },
                "y": {
                    "min": 0,
                    "max": 50,
                    "ticks": {
                        "stepSize": 5,
                        "callback": "function(value) { return value + '%' }",
                        "font": {
                            "size": 11
                        }
                    },
                    "grid": {
                        "color": "rgba(0,0,0,0.1)",
                        "drawBorder": False
                    }
                }
            }
        }
    }

    return [
        Script("""
            function createPollChartConfig(dates, datasets, isCoalition) {
                const chartConfig = """ + json.dumps(base_chart_config) + """;
                
                // Set the correct datasets
                chartConfig.data.datasets = datasets;
                
                // Adjust y-axis max based on chart type
                chartConfig.options.scales.y.max = isCoalition ? 60 : 50;
                
                // Add the y-axis tick callback
                chartConfig.options.scales.y.ticks.callback = function(value) {
                    return value + '%';
                };
                
                // Hide poll point datasets from legend
                chartConfig.options.plugins.legend.labels.filter = function(item) {
                    return !item.text.endsWith('(polls)');
                };
                
                // Update tooltip configuration
                chartConfig.options.plugins.tooltip = {
                    enabled: true,
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        title: function(context) {
                            const date = new Date(context[0].parsed.x);
                            return date.toLocaleDateString('it-IT', {
                                day: '2-digit',
                                month: '2-digit',
                                year: 'numeric'
                            });
                        },
                        label: function(context) {
                            if (context.dataset.label.includes('(polls)')) return null;
                            return `${context.dataset.label}: ${context.parsed.y.toFixed(1)}%`;
                        }
                    },
                    backgroundColor: 'rgba(255, 255, 255, 0.95)',
                    titleColor: '#000',
                    bodyColor: '#666',
                    borderColor: 'rgba(0,0,0,0.1)',
                    borderWidth: 1,
                    padding: 10,
                    bodySpacing: 4,
                    titleSpacing: 10,
                    cornerRadius: 4
                };
                
                return chartConfig;
            }
        """),
        
        Script(f"""
            const dates = {json.dumps(dates)};
            const datasets = {json.dumps(datasets)};
            const coalitionDatasets = {json.dumps(coalition_datasets)};
            
            // Initialize poll chart
            const pollCtx = document.getElementById('pollChart').getContext('2d');
            const pollConfig = createPollChartConfig(dates, datasets, false);
            new Chart(pollCtx, pollConfig);
            
            // Initialize coalition chart with coalition datasets
            const coalitionCtx = document.getElementById('coalitionChart').getContext('2d');
            const coalitionConfig = createPollChartConfig(dates, coalitionDatasets, true);
            new Chart(coalitionCtx, coalitionConfig);
        """)
    ]