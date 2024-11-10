from datetime import datetime
from math import radians, cos, sin, sqrt, atan2

def str_to_none(value):
    """
    Convertit une chaine de caractères en None si elle est 'NULL' ou vide.
    Si la chaine de caractères ne contient pas de 'NULL' ou vide, elle renvoie la chaine de caractères.
    """
    return None if value in ['NULL', ''] else value

def str_to_nbr(value):
    """
    Convertit une chaine de caractères en un nombre (si possible)
    Si la conversion ne peut être effectuée, elle renvoie la chaine de caractères.
    """
    try:
        return float(value) if '.' in value else int(value)
    except:
        return value


def convert_custom_datetime(date_str):
    """
    Convertit une date en ce format %Y-%m-%d %H:%M:%S
    Si la date ne correspond pas à un des formats connus, elle renvoie None.
    """

    formats = [
        # Format
        "%Y-%m-%d %H:%M:%S",
        "%d/%m/%Y %H:%M",              
        "%m-%dT%H:%MZ",
        "%Y-%m-%d %H:%M:%S",
        "00-00T24:60Z",
        "00-00T24:45Z",
        "00-00T17:58Z"
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue 

    print(f"Date format error: {date_str} does not match any known formats.")
    return None


# Fonction qui convertit une date entrée en paramètre
def convertir_date(date_str):
    """
    Convertit une date au format '%d/%m/%Y' en '%Y-%m-%d'
    """
    format_entree = "%d/%m/%Y"
    format_sortie = "%Y-%m-%d"

    # Convertir la chaîne en objet datetime
    date_obj = datetime.strptime(date_str, format_entree)

    # Convertir l'objet datetime en chaîne au format souhaité
    date_formatee = date_obj.strftime(format_sortie)

    return date_formatee

def haversine_formula(lat1, lat2, lon1, lon2):
    """
    Calcule la distance entre pos1 et pos2

    :params lat1: latitude de la position 1
    :param lat2: latitude de la position 2
    :param lon1: longitude de la position 1
    :param lon2: longitude de la position 2

    :returns: la distance entre pos1 et pos2
    """
    # Earth radius in kilometers
    earth_radius = 6371.0
    
    # Convert degrees to radians
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)
    
    # Difference in coordinates
    diff_lat = lat2 - lat1
    diff_lon = lon2 - lon1

    # Haversine formula
    formula = sin(diff_lat / 2)**2 + cos(lat1) * cos(lat2) * sin(diff_lon / 2)**2
    celerity = 2 * atan2(sqrt(formula), sqrt(1 - formula))

    distance = earth_radius * celerity

    return distance

def calculate_speed(lat1, lon1, time1, lat2, lon2, time2):
    """
    Calcule la vitesse du bateau en fonction de la distance parcourue entre le point1 et le point2 et le temps

    :params lat1: latitude de la position 1
    :param lat2: latitude de la position 2
    :param lon1: longitude de la position 1
    :param lon2: longitude de la position 2
    :param time1: heure de la position 1
    :param time2: heure de la position 2

    :returns: la vitesse du bateau en km/h
    """
    # Calculate the distance between two points (in kilometers)
    distance = haversine_formula(lat1, lat2, lon1, lon2)
    
    # Convert time strings to datetime objects
    time1 = datetime.strptime(time1, "%Y-%m-%d %H:%M:%S")
    time2 = datetime.strptime(time2, "%Y-%m-%d %H:%M:%S")
    
    # Get the time difference in seconds
    time_diff = (time2 - time1).total_seconds()
    
    # Convert time difference from seconds to hours
    time_diff_hours = time_diff / 3600.0
    
    # Calculate speed in kilometers per hour
    if time_diff_hours > 0:
        speed = distance / time_diff_hours
    else:
        speed = 0
    
    return speed