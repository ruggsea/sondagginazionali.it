"""Configuration for political parties and coalitions"""

# Party configuration with colors and display settings
PARTY_CONFIG = {
    'FDI': {'name': "Fratelli d'Italia", 'color': '#0066CC', 'show_in_graph': True},
    'PD': {'name': 'Partito Democratico', 'color': '#FF0000', 'show_in_graph': True},
    'M5S': {'name': 'Movimento 5 Stelle', 'color': '#FFD700', 'show_in_graph': True},
    'FI': {'name': 'Forza Italia', 'color': '#00BFFF', 'show_in_graph': True},
    'LEGA': {'name': 'Lega', 'color': '#004225', 'show_in_graph': True},
    'AVS': {'name': 'Alleanza Verdi Sinistra', 'color': '#00B050', 'show_in_graph': True},
    '+Europa': {'name': '+Europa', 'color': '#800080', 'show_in_graph': False},
    'Azione': {'name': 'Azione', 'color': '#FFA500', 'show_in_graph': False},
    'Italia Viva': {'name': 'Italia Viva', 'color': '#800000', 'show_in_graph': False},
    'Altri': {'name': 'Altri', 'color': '#808080', 'show_in_graph': False}
}

# Coalition configuration
COALITION_CONFIG = {
    'Centrosinistra': {
        'color': '#FF0000',
        'parties': ['PD', 'AVS', '+Europa']
    },
    'Movimento 5 Stelle': {
        'color': '#FFD700',
        'parties': ['M5S']
    },
    'Terzo Polo': {
        'color': '#FF69B4',
        'parties': ['Azione', 'Italia Viva']
    },
    'Centrodestra': {
        'color': '#00BFFF',
        'parties': ['FDI', 'LEGA', 'FI']
    },
    'Altri': {
        'color': '#808080',
        'parties': ['Altri']
    }
} 