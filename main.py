from fasthtml.common import *
import pandas as pd
from datetime import datetime
from moving_average import calculate_weighted_ma
import json
import os

# Import configurations and components
from config.party_config import PARTY_CONFIG, COALITION_CONFIG
from components.data_processing import (
    load_and_preprocess_data,
    filter_data,
    prepare_chart_datasets
)

app, rt = fast_app()

@rt('/')
def home():
    # Load and process data
    df, all_party_columns = load_and_preprocess_data()
    df = filter_data(df, all_party_columns)
    assert not df.empty, "df is empty"
    
    # Calculate moving averages
    df_weighted_ma = calculate_weighted_ma(df)
    
    # Get latest values and dates
    latest_date = df_weighted_ma['date'].max()
    latest_values = df_weighted_ma.iloc[-1]
    dates = df['date'].dt.strftime('%Y-%m-%d').tolist()
    today = datetime.now()
    today_str = today.strftime('%d/%m/%Y')

    # Get list of party full names
    party_names = [config['name'] for config in PARTY_CONFIG.values()]
    
    party_config = PARTY_CONFIG
    
    # Prepare data for Chart.js using normalized data
    datasets = prepare_chart_datasets(df, df_weighted_ma, dates, party_config)
    
    # Format the debug text in a more presentable way
    info_text = f"""
    Oggi è il {today_str}. La media dei sondaggi è la seguente:

    Fratelli d'Italia: {latest_values['FDI_MA']:.1f}%
    Partito Democratico: {latest_values['PD_MA']:.1f}%
    Movimento 5 Stelle: {latest_values['M5S_MA']:.1f}%
    Forza Italia: {latest_values['FI_MA']:.1f}%
    Lega: {latest_values['LEGA_MA']:.1f}%
    Alleanza Verdi Sinistra: {latest_values['AVS_MA']:.1f}%

    Ultimo sondaggio raccolto: {latest_date.strftime('%d/%m/%Y')}
    """

    # Calculate coalition values
    coalition_data = {}
    for date in df_weighted_ma['date']:
        row = df_weighted_ma[df_weighted_ma['date'] == date].iloc[0]
        for coalition, config in COALITION_CONFIG.items():
            value = sum(row[f'{party}_MA'] for party in config['parties'] if f'{party}_MA' in row)
            if coalition not in coalition_data:
                coalition_data[coalition] = []
            coalition_data[coalition].append(round(value, 1))

    # Prepare coalition datasets
    coalition_datasets = []
    for coalition, config in COALITION_CONFIG.items():
        coalition_datasets.append({
            'label': coalition,
            'data': coalition_data[coalition],
            'borderColor': config['color'],
            'backgroundColor': config['color'],
            'borderWidth': 2,
            'tension': 0.4,
            'fill': False,
            'pointRadius': 0
        })

    # Calculate latest coalition values
    latest_coalition_values = {}
    latest_row = df_weighted_ma.iloc[-1]
    for coalition, config in COALITION_CONFIG.items():
        value = sum(latest_row[f'{party}_MA'] for party in config['parties'] if f'{party}_MA' in latest_row)
        latest_coalition_values[coalition] = round(value, 1)

    # Update the style to make the info section look better
    return Div(
        Script(src="https://cdn.jsdelivr.net/npm/chart.js"),
        Script(src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns"),
        
        Style("""
            body { 
                margin: 0;
                padding: 20px;
                font-family: system-ui, -apple-system, sans-serif;
                background-color: #f5f5f5;
                min-height: 100vh;
            }
            .container {
                max-width: 1000px;
                margin: 0 auto;
                padding: 2rem;
                display: flex;
                flex-direction: column;
                min-height: 100vh;
            }
            .title {
                text-align: center;
                font-size: 2.25rem;
                margin-bottom: 2rem;
                color: #111;
                font-weight: 700;
            }
            .content {
                flex-grow: 1;
                display: flex;
                flex-direction: column;
                gap: 1.5rem;
            }
            .chart-card {
                background: white;
                border-radius: 0.75rem;
                padding: 1.5rem 1.5rem 2.5rem 1.5rem;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                height: calc(55vh - 11rem);
                min-height: 400px;
            }
            .chart-container {
                position: relative;
                height: 100%;
                width: 100%;
                margin-bottom: 2rem;
            }
            .summary-card {
                background: white;
                border-radius: 0.75rem;
                padding: 0.75rem;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                flex-shrink: 0;
                max-width: 600px;
                margin: 0 auto;
                width: 100%;
            }
            .summary-title {
                font-size: 1.1rem;
                font-weight: 600;
                margin-bottom: 0.75rem;
                color: #000;
            }
            .party-row {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin: 0.4rem 0;
                padding: 0.3rem 0;
                border-bottom: 1px solid #eee;
            }
            .party-row:last-child {
                border-bottom: none;
            }
            .party-name {
                font-weight: 500;
                color: #1a1a1a;
                font-size: 0.95rem;
            }
            .party-value {
                font-weight: 600;
                color: #1a1a1a;
                font-size: 0.95rem;
            }
            .last-update {
                margin-top: 0.75rem;
                padding-top: 0.75rem;
                font-size: 0.85rem;
                color: #444;
                border-top: 1px solid #eee;
            }
            .footer {
                margin-top: 2rem;
                padding: 1.5rem;
                background: white;
                border-radius: 0.75rem;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                text-align: center;
            }
            .footer-text {
                color: #666;
                font-size: 0.9rem;
                margin: 0;
            }
            .footer-links {
                display: flex;
                gap: 1rem;
                justify-content: center;
                margin-top: 0.5rem;
            }
            .footer-link {
                color: #1a1a1a;
                text-decoration: none;
                display: flex;
                align-items: center;
                gap: 0.25rem;
                font-size: 0.9rem;
            }
            .footer-link:hover {
                color: #0066cc;
            }
        """),
        
        Div(
            H1("Sondaggi Politici Italiani", cls="title"),
            Div(
                # Grafico partiti
                Div(
                    Canvas(id="pollChart"),
                    cls="chart-card chart-container"
                ),
                # Riepilogo partiti
                Div(
                    P(f"Oggi è il {today_str}. La media dei sondaggi è la seguente:", cls="summary-title"),
                    *[
                        Div(
                            Span(f"{party_config[abbr]['name']}:", cls="party-name"),
                            Span(f"{latest_values[abbr]:.1f}%", cls="party-value"),
                            cls="party-row"
                        ) for abbr in party_config
                    ],
                    P(f"Ultimo sondaggio raccolto: {latest_date.strftime('%d/%m/%Y')}", cls="last-update"),
                    cls="summary-card"
                ),
                # Grafico coalizioni
                Div(
                    Canvas(id="coalitionChart"),
                    cls="chart-card chart-container"
                ),
                # Riepilogo coalizioni
                Div(
                    P("Media delle coalizioni:", cls="summary-title"),
                    *[
                        Div(
                            Span(f"{coalition}:", cls="party-name"),
                            Span(f"{value:.1f}%", cls="party-value"),
                            cls="party-row"
                        ) for coalition, value in latest_coalition_values.items()
                    ],
                    cls="summary-card"
                ),
                cls="content"
            ),
            Div(
                P("Sviluppato da Ruggero Marino Lazzaroni", cls="footer-text"),
                Div(
                    A(
                        I(cls="fab fa-twitter"), 
                        "Twitter", 
                        href="https://twitter.com/ruggsea", 
                        target="_blank",
                        cls="footer-link"
                    ),
                    A(
                        I(cls="fab fa-linkedin"), 
                        "LinkedIn", 
                        href="https://www.linkedin.com/in/ruggsea/", 
                        target="_blank",
                        cls="footer-link"
                    ),
                    cls="footer-links"
                ),
                cls="footer"
            ),
            cls="container"
        ),
        
        Link(
            rel="stylesheet",
            href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css"
        ),
        
        Script("""
            const ctx = document.getElementById('pollChart').getContext('2d');
            const chartConfig = """ + json.dumps({
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
                                "boxWidth": 30,
                                "font": {
                                    "family": "system-ui, -apple-system, sans-serif",
                                    "size": 13
                                }
                            },
                            "align": "center",
                            "maxHeight": 50
                        }
                    },
                    "layout": {
                        "padding": {
                            "top": 30,
                            "bottom": 30,
                            "left": 15,
                            "right": 15
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
                                "color": "rgba(0,0,0,0.1)"
                            },
                            "ticks": {
                                "font": {
                                    "family": "system-ui, -apple-system, sans-serif"
                                }
                            }
                        },
                        "y": {
                            "min": 0,
                            "max": 50,
                            "ticks": {
                                "stepSize": 5,
                                "padding": 10,
                                "callback": "function(value) { return value + '%' }",
                                "font": {
                                    "family": "system-ui, -apple-system, sans-serif",
                                    "size": 12
                                }
                            },
                            "grid": {
                                "color": "rgba(0,0,0,0.1)"
                            }
                        }
                    }
                }
            }) + """;
            
            // Add the y-axis tick callback after the JSON config
            chartConfig.options.scales.y.ticks.callback = function(value) {
                return value + '%';
            };
            
            // Add the filter function
            chartConfig.options.plugins.legend.labels.filter = function(item) {
                return !item.text.endsWith('(polls)');
            };
            
            // Update tooltip configuration to match coalition style
            chartConfig.options.plugins.tooltip = {
                callbacks: {
                    title: function(context) {
                        const point = context[0];
                        let date;
                        
                        if (point.raw && point.raw.x) {
                            date = point.raw.x;
                        } else {
                            date = chartConfig.data.labels[point.dataIndex];
                        }
                        
                        if (!date) return 'Data non disponibile';
                        
                        // Format date as dd/mm/yyyy
                        const dateObj = new Date(date);
                        return dateObj.toLocaleDateString('it-IT', {
                            day: '2-digit',
                            month: '2-digit',
                            year: 'numeric'
                        });
                    },
                    label: function(context) {
                        const value = context.parsed.y;
                        if (!value || context.dataset.label.includes('(polls)')) return null;
                        return `${context.dataset.label}: ${value.toFixed(1)}%`;
                    }
                },
                backgroundColor: 'rgba(255, 255, 255, 0.98)',
                titleColor: '#000',
                titleAlign: 'center',
                titleMarginBottom: 6,
                bodyColor: '#666',
                bodySpacing: 4,
                padding: 10,
                borderColor: 'rgba(0, 0, 0, 0.1)',
                borderWidth: 1,
                displayColors: true,
                cornerRadius: 4,
                bodyFont: {
                    family: 'system-ui, -apple-system, sans-serif',
                    size: 13
                },
                titleFont: {
                    family: 'system-ui, -apple-system, sans-serif',
                    weight: 'bold',
                    size: 14
                }
            };
            
            new Chart(ctx, chartConfig);
            
            // Coalition chart with matching tooltip style
            const coalitionCtx = document.getElementById('coalitionChart').getContext('2d');
            const coalitionConfig = {
                type: 'line',
                data: {
                    labels: """ + json.dumps(dates) + """,
                    datasets: """ + json.dumps(coalition_datasets) + """
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {
                        intersect: false,
                        mode: 'index'
                    },
                    plugins: {
                        title: {
                            display: true,
                            text: 'Coalizioni',
                            font: {
                                size: 16,
                                weight: 'bold'
                            },
                            padding: {
                                top: 10,
                                bottom: 30
                            }
                        },
                        legend: {
                            position: 'bottom',
                            labels: {
                                usePointStyle: true,
                                padding: 20,
                                boxWidth: 30,
                                font: {
                                    family: 'system-ui, -apple-system, sans-serif',
                                    size: 13
                                }
                            }
                        },
                        tooltip: {
                            callbacks: {
                                title: function(context) {
                                    const date = context[0].label;
                                    if (!date) return 'Data non disponibile';
                                    
                                    // Format date as dd/mm/yyyy
                                    const dateObj = new Date(date);
                                    return dateObj.toLocaleDateString('it-IT', {
                                        day: '2-digit',
                                        month: '2-digit',
                                        year: 'numeric'
                                    });
                                },
                                label: function(context) {
                                    const value = context.parsed.y;
                                    if (!value) return null;
                                    return `${context.dataset.label}: ${value.toFixed(1)}%`;
                                }
                            },
                            backgroundColor: 'rgba(255, 255, 255, 0.98)',
                            titleColor: '#000',
                            titleAlign: 'center',
                            titleMarginBottom: 6,
                            bodyColor: '#666',
                            bodySpacing: 4,
                            padding: 10,
                            borderColor: 'rgba(0, 0, 0, 0.1)',
                            borderWidth: 1,
                            displayColors: true,
                            cornerRadius: 4,
                            bodyFont: {
                                family: 'system-ui, -apple-system, sans-serif',
                                size: 13
                            },
                            titleFont: {
                                family: 'system-ui, -apple-system, sans-serif',
                                weight: 'bold',
                                size: 14
                            }
                        }
                    }
                }
            };
            
            new Chart(coalitionCtx, coalitionConfig);
        """)
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    serve(host="0.0.0.0", port=port) 