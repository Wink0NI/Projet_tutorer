from datetime import datetime


def str_to_none(value):
    return None if value in ['NULL', ''] else value

def str_to_nbr(value):
    try:
        return float(value) if '.' in value else int(value)
    except:
        return value
    
def convert_custom_datetime(date_str):
    try:
        # Convertir le format '04-24T17:30Z' en '2024-04-24 17:30:00'
        dt = datetime.strptime(date_str, '%m-%dT%H:%MZ')
        return dt.strftime("%Y-%m-%d %H:%M:%S") # SUR MACOS mettre "" au lieu de ''
    except:
        return None# Retourner une valeur string en Int ou Float