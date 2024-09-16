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
    formats = ["%d/%m/%Y %H:%M", "%m-%dT%H:%MZ", "%Y-%m-%d %H:%M:%S","00-00T24:60Z", "00-00T24:45Z","00-00T17:58Z"]
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue  # Essayer le prochain format si celui-ci échoue

    print(f"Date format error: {date_str} does not match any known formats.")
    return None



