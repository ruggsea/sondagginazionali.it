"""Functions for loading and preprocessing polling data"""
import pandas as pd
from datetime import datetime, timedelta

def load_and_preprocess_data():
    """Load and preprocess polling data"""
    # Read polling data from the repo
    df = pd.read_csv('https://raw.githubusercontent.com/ruggsea/llm_italian_poll_scraper/main/italian_polls.csv')
    
    # Convert date column - using Data Inserimento
    df['date'] = pd.to_datetime(df['Data Inserimento'], format='%d/%m/%Y')
    df = df[['date'] + [col for col in df.columns if col != 'date']]
    
    # Get party columns
    all_party_columns = df.columns[df.columns.get_loc('Partito Democratico'):]
    
    # Convert percentages to floats
    for party in all_party_columns:
        for i, row in df.iterrows():
            if isinstance(row[party], str):
                try:
                    df.at[i, party] = float(row[party].replace("%", "").replace(",", "."))
                except ValueError:
                    df.at[i, party] = None
            elif isinstance(row[party], int):
                df.at[i, party] = float(row[party])
    
    return df, all_party_columns

def filter_data(df, all_party_columns):
    """Apply filters to the dataset"""
    # Filter missing key parties
    df = df[df['Partito Democratico'].notna() & df['Fratelli d\'Italia'].notna()]
    
    # Filter by total percentage
    df = df[df[all_party_columns].sum(axis=1) > 90]
    df = df[df[all_party_columns].sum(axis=1) < 110]
    
    # Filter by date
    three_years_ago = datetime.now() - timedelta(days=3*365)
    df = df[df['date'] >= three_years_ago]
    
    return df.sort_values('date')

def prepare_chart_datasets(df, df_weighted_ma, dates, party_config):
    """Prepare datasets for the party chart"""
    datasets = []
    
    for abbr, config in party_config.items():
        if not config['show_in_graph']:
            continue
            
        # Line dataset (moving average)
        party_data = {
            'label': abbr,
            'data': df_weighted_ma[f'{abbr}_MA'].round(1).tolist(),
            'borderColor': config['color'],
            'backgroundColor': config['color'],
            'borderWidth': 1.5,
            'tension': 0.4,
            'fill': False,
            'order': 1,
            'pointRadius': 0
        }
        
        # Scatter points dataset (polls)
        scatter_data = []
        if config['name'] in df.columns:
            for i, value in enumerate(df[config['name']]):
                if pd.notna(value):
                    scatter_data.append({
                        'x': dates[i],
                        'y': round(value, 1)
                    })
        
        if scatter_data:
            datasets.append({
                'label': f'{abbr} (polls)',
                'data': scatter_data,
                'backgroundColor': config['color'] + '40',
                'borderColor': 'transparent',
                'pointRadius': 2,
                'pointStyle': 'circle',
                'order': 2
            })
        
        datasets.append(party_data)
    
    return datasets 