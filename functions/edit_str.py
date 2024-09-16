from datetime import datetime


def str_to_none(value):
    return None if value in ['NULL', ''] else value

def str_to_nbr(value):
    try:
        return float(value) if '.' in value else int(value)
    except:
        return value
    
from datetime import datetime

def convert_custom_datetime(date_str):
    """
    Convert various datetime string formats to PostgreSQL-compatible format.

    Args:
        date_str (str): The input datetime string.

    Returns:
        str: The formatted datetime string in '%Y-%m-%d %H:%M:%S' format or None if conversion fails.
    """
    if date_str is None:  # Si la date est None, retourner None
        return None
    
    # Ajouter ici les formats spécifiques que vous avez rencontrés
    formats = ["%d/%m/%Y %H:%M", "%m-%dT%H:%MZ", "%Y-%m-%d %H:%M:%S"]  # Ajoutez d'autres formats si nécessaire
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue  # Essayer le prochain format si celui-ci échoue
    
    print(f"Date format error: {date_str} does not match any known formats.")
    return None


