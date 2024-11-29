import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def calculate_weighted_ma(df):
    # Create a copy of the dataframe to store moving averages
    df_ma = df.copy()
    
    # Define the mapping of full names to abbreviations
    party_mapping = {
        "Fratelli d'Italia": 'FDI',
        'Partito Democratico': 'PD',
        'Movimento 5 Stelle': 'M5S',
        'Forza Italia': 'FI',
        'Lega': 'LEGA',
        'Alleanza Verdi Sinistra': 'AVS',
        '+Europa': '+Europa',
        'Azione': 'Azione',
        'Italia Viva': 'Italia Viva',
        'Altri': 'Altri'
    }
    
    times=pd.DatetimeIndex(df['date'])
    
    # Calculate weighted moving average for each party
    for party_name, party_abbr in party_mapping.items():
        if party_name in df.columns:
            values=df[party_name].ewm(halflife="14d", times=times).mean()
            # Store the moving average in the new dataframe
            df_ma[f'{party_abbr}_MA'] = values
    # rename the columns
    df_ma.rename(columns=party_mapping, inplace=True)
    return df_ma