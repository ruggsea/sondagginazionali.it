from fasthtml.common import *
from fasthtml.js import run_js
import pandas as pd
from datetime import datetime, timedelta
from moving_average import calculate_weighted_ma
import json
import os

app, rt = fast_app()

@rt('/')
def home():
    # Read polling data from the repo
    df = pd.read_csv('https://raw.githubusercontent.com/ruggsea/llm_italian_poll_scraper/main/italian_polls.csv')
    
    # Convert date column - using Data Inserimento
    df['date'] = pd.to_datetime(df['Data Inserimento'], format='%d/%m/%Y')
    
    # Filter last 3 years
    three_years_ago = datetime.now() - timedelta(days=3*365)
    df = df[df['date'] >= three_years_ago]
    
    # Sort by date before calculating moving averages
    df = df.sort_values('date')
    
    # Calculate moving averages
    df = calculate_weighted_ma(df)
    
    # Get latest values for debug section
    latest_date = df['date'].max()
    latest_values = {
        'FDI': df[df['date'] == latest_date]['FDI_MA'].iloc[0],
        'PD': df[df['date'] == latest_date]['PD_MA'].iloc[0],
        'M5S': df[df['date'] == latest_date]['M5S_MA'].iloc[0],
        'FI': df[df['date'] == latest_date]['FI_MA'].iloc[0],
        'LEGA': df[df['date'] == latest_date]['LEGA_MA'].iloc[0],
        'AVS': df[df['date'] == latest_date]['AVS_MA'].iloc[0],
    }
    
    # Create debug text
    debug_text = f"""
    Media di oggi ({latest_date.strftime('%d/%m/%Y')})
    Fratelli d'Italia: {latest_values['FDI']:.2f}%
    Partito Democratico: {latest_values['PD']:.2f}%
    Movimento 5 Stelle: {latest_values['M5S']:.2f}%
    Forza Italia: {latest_values['FI']:.2f}%
    Lega: {latest_values['LEGA']:.2f}%
    Alleanza Verdi Sinistra: {latest_values['AVS']:.2f}%
    """
    
    # Define party names and colors
    party_config = {
        'FDI': {'name': "Fratelli d'Italia", 'color': '#0066CC'},
        'PD': {'name': 'Partito Democratico', 'color': '#FF0000'},
        'M5S': {'name': 'Movimento 5 Stelle', 'color': '#FFD700'},
        'FI': {'name': 'Forza Italia', 'color': '#00BFFF'},
        'LEGA': {'name': 'Lega', 'color': '#004225'},
        'AVS': {'name': 'Alleanza Verdi Sinistra', 'color': '#00B050'}
    }
    
    # Function to normalize poll data
    def normalize_poll_row(row, party_names):
        total = sum(row[name] for name in party_names if pd.notna(row[name]))
        if total == 0:
            return row
        for name in party_names:
            if pd.notna(row[name]):
                row[name] = (row[name] / total) * 100
        return row

    # Get list of party full names
    party_names = [config['name'] for config in party_config.values()]
    
    # Normalize individual poll data
    df_normalized = df.copy()
    df_normalized = df_normalized.apply(
        lambda row: normalize_poll_row(row, party_names), 
        axis=1
    )
    
    # Recalculate moving averages with normalized data
    df_normalized = calculate_weighted_ma(df_normalized)
    
    # Update latest values with normalized data
    latest_date = df_normalized['date'].max()
    latest_values = {
        'FDI': df_normalized[df_normalized['date'] == latest_date]['FDI_MA'].iloc[0],
        'PD': df_normalized[df_normalized['date'] == latest_date]['PD_MA'].iloc[0],
        'M5S': df_normalized[df_normalized['date'] == latest_date]['M5S_MA'].iloc[0],
        'FI': df_normalized[df_normalized['date'] == latest_date]['FI_MA'].iloc[0],
        'LEGA': df_normalized[df_normalized['date'] == latest_date]['LEGA_MA'].iloc[0],
        'AVS': df_normalized[df_normalized['date'] == latest_date]['AVS_MA'].iloc[0],
    }
    
    # Prepare data for Chart.js using normalized data
    dates = df_normalized['date'].dt.strftime('%Y-%m-%d').tolist()
    datasets = []
    
    for abbr, config in party_config.items():
        # Line dataset (moving average)
        party_data = {
            'label': abbr,
            'data': df_normalized[f'{abbr}_MA'].round(2).tolist(),
            'borderColor': config['color'],
            'backgroundColor': config['color'],
            'borderWidth': 1.5,
            'tension': 0.4,
            'fill': False,
            'order': 1,
            'pointRadius': 0,  # Remove points from the line
            'pointHoverRadius': 0  # Remove hover points from the line
        }
        
        # Scatter points dataset (actual polls)
        scatter_data = []
        if config['name'] in df_normalized.columns:
            for i, value in enumerate(df_normalized[config['name']]):
                if pd.notna(value):
                    scatter_data.append({
                        'x': dates[i],
                        'y': round(value, 2)
                    })
        
        # Add scatter points first (so they appear under the lines)
        if scatter_data:
            datasets.append({
                'label': f'{abbr} (polls)',
                'data': scatter_data,
                'backgroundColor': config['color'] + '40',
                'borderColor': 'transparent',
                'pointRadius': 2.5,
                'pointStyle': 'circle',
                'pointBackgroundColor': config['color'] + '40',
                'pointBorderColor': 'transparent',
                'pointHoverRadius': 3.5,
                'pointHoverBorderWidth': 1,
                'pointHoverBorderColor': config['color'],
                'showLine': False,
                'order': 2,
                'hidden': False
            })
        
        # Add the line dataset after scatter points
        datasets.append(party_data)

    # Format the current date in Italian
    today = datetime.now()
    today_str = today.strftime('%d/%m/%Y')
    
    # Format the debug text in a more presentable way
    info_text = f"""
    Oggi è il {today_str}. La media dei sondaggi è la seguente:

    Fratelli d'Italia: {latest_values['FDI']:.1f}%
    Partito Democratico: {latest_values['PD']:.1f}%
    Movimento 5 Stelle: {latest_values['M5S']:.1f}%
    Forza Italia: {latest_values['FI']:.1f}%
    Lega: {latest_values['LEGA']:.1f}%
    Alleanza Verdi Sinistra: {latest_values['AVS']:.1f}%

    Ultimo sondaggio raccolto: {latest_date.strftime('%d/%m/%Y')}
    """

    # Update the style to make the info section look better
    return Div(
        Script(src="https://cdn.jsdelivr.net/npm/chart.js"),
        Script(src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns"),
        
        Style("""
            body { 
                margin: 0;
                padding: 20px;
                font-family: Arial, sans-serif;
                background-color: #f5f5f5;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .title {
                text-align: center;
                font-size: 24px;
                margin-bottom: 20px;
                color: #333;
                font-weight: bold;
            }
            .chart-container {
                position: relative;
                height: 60vh;
                width: 90%;
                margin: 0 auto 20px auto;
                padding: 0 20px;
            }
            .info-section {
                margin-top: 20px;
                padding: 20px;
                background-color: #f8f9fa;
                border-radius: 8px;
                font-family: 'Segoe UI', Arial, sans-serif;
                white-space: pre-line;
                color: #333;
                line-height: 1.6;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
            .info-section strong {
                color: #000;
                font-weight: 600;
            }
        """),
        
        Div(
            H1("Media Sondaggi Nazionali", cls="title"),
            Div(
                Canvas(id="pollChart"),
                cls="chart-container"
            ),
            Div(info_text, cls="info-section"),  # Changed from debug-section to info-section
            cls="container"
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
                            "position": "right",
                            "labels": {
                                "usePointStyle": True,
                                "padding": 15
                            }
                        },
                        "title": {
                            "display": False
                        }
                    },
                    "layout": {
                        "padding": {
                            "left": 15,
                            "right": 30,
                            "top": 10,
                            "bottom": 10
                        }
                    },
                    "scales": {
                        "x": {
                            "type": "time",
                            "time": {
                                "unit": "month",
                                "displayFormats": {
                                    "month": "MM/yy"
                                }
                            },
                            "grid": {
                                "display": True,
                                "drawOnChartArea": True,
                                "drawTicks": True,
                                "color": "rgba(0,0,0,0.1)"
                            },
                            "ticks": {
                                "maxRotation": 45,
                                "minRotation": 45,
                                "source": "auto",
                                "autoSkip": True,
                                "maxTicksLimit": 12
                            },
                            "border": {
                                "display": True
                            }
                        },
                        "y": {
                            "min": 0,
                            "max": 50,
                            "grid": {
                                "display": True,
                                "drawBorder": True,
                                "color": "rgba(0,0,0,0.1)",
                                "lineWidth": 1
                            },
                            "border": {
                                "display": True,
                                "color": "rgba(0,0,0,0.3)"
                            },
                            "ticks": {
                                "display": True,
                                "stepSize": 10,
                                "font": {
                                    "size": 12
                                },
                                "padding": 8,
                                "color": "rgba(0,0,0,0.7)",
                                "major": {
                                    "enabled": True
                                },
                                "align": "center",
                                "crossAlign": "center",
                                "z": 1
                            },
                            "display": True,
                            "position": "left",
                            "beginAtZero": True,
                            "title": {
                                "display": True,
                                "text": "Percentuale (%)",
                                "color": "rgba(0,0,0,0.7)",
                                "font": {
                                    "size": 14,
                                    "weight": "normal"
                                }
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
            
            // Update tooltip date format
            chartConfig.options.plugins.tooltip = {
                callbacks: {
                    title: function(context) {
                        const date = new Date(context[0].label);
                        const day = String(date.getDate()).padStart(2, '0');
                        const month = String(date.getMonth() + 1).padStart(2, '0');
                        const year = String(date.getFullYear()).slice(2);
                        return day + '/' + month + '/' + year;
                    },
                    label: function(context) {
                        return context.dataset.label + ': ' + context.parsed.y.toFixed(1) + '%';
                    }
                }
            };
            
            new Chart(ctx, chartConfig);
        """)
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    serve(host="0.0.0.0", port=port) 