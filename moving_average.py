import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def calculate_weighted_ma(df, span=10):
    """
    Calculate exponentially weighted moving average (EWMA) for each party
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame containing polling data
    span : int
        Span parameter for exponential weighting (default: 10)
        
    Returns:
    --------
    pandas.DataFrame
        DataFrame with EWMA values and original columns
    """
    # List of main parties and their abbreviations
    party_mapping = {
        "Fratelli d'Italia": 'FDI',
        'Partito Democratico': 'PD',
        'Movimento 5 Stelle': 'M5S',
        'Forza Italia': 'FI',
        'Lega': 'LEGA',
        'Alleanza Verdi Sinistra': 'AVS'
    }
    
    # Keep original columns for scatter plot
    result_df = df[['date'] + list(party_mapping.keys())].copy()
    
    # Calculate EWMA for each party separately without normalization first
    for party, abbr in party_mapping.items():
        ma_col = f'{abbr}_MA'
        result_df[ma_col] = df[party].ewm(span=span, adjust=False).mean()
    
    # Get MA columns
    ma_columns = [col for col in result_df.columns if col.endswith('_MA')]
    
    # Now normalize the MA columns
    ma_sum = result_df[ma_columns].sum(axis=1)
    for col in ma_columns:
        result_df[col] = result_df[col] * 100 / ma_sum
    
    return result_df