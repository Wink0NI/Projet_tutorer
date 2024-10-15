from datetime import datetime
from requests_html import AsyncHTMLSession
from bs4 import BeautifulSoup

ship_types = {
    0: "Not available (default)",
    20: "Wing in ground (WIG)",
    30: "Fish",
    31: "Towing",
    32: "Towing: length exceeds 200m or breadth exceeds 25m",
    33: "Dredging or underwater operations",
    34: "Diving operations",
    35: "Military operations",
    36: "Sailing",
    37: ["Pleasure Craft", "Yacht"],
    40: "High speed craft (HSC)",
    50: "Pilot Vessel",
    51: "Search and Rescue vessel",
    52: "Tug",
    53: "Port Tender",
    54: "Anti-pollution equipment",
    55: "Law Enforcement",
    56: "Spare - Local Vessel",
    58: "Medical Transport",
    59: "Noncombatant ship according to RR Resolution No. 18",
    60: ["Passenger", "Ferry"],
    70: ["Cargo", "Container", "Carrier"],
    80: "Tanker",
    90: "Other Type"
}

def str_to_none(value):
    return None if value in ['NULL', ''] else value


def str_to_nbr(value):
    try:
        return float(value) if '.' in value else int(value)
    except:
        return value


def convert_custom_datetime(date_str):

    formats = [
        # Format for date with microseconds, timezone offset, and abbreviation
        "%Y-%m-%d %H:%M:%S",
        "%d/%m/%Y %H:%M",               # Other formats you want to try
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
            continue  # Try the next format if this one fails

    print(f"Date format error: {date_str} does not match any known formats.")
    return None



async def get_ship_type(mmsi, session=None):
    # Create a session if one isn't provided
    if session is None:
        session = AsyncHTMLSession()

    url = f"https://www.vesselfinder.com/vessels/details/{mmsi}"
    
    # Make an asynchronous request
    response = await session.get(url)

    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(response.html.html, 'html.parser')

    # Search for the ship type in the details
    details = soup.find_all('tr')
    for detail in details:
        cells = detail.find_all('td')
        if cells and cells[0].text.strip() == "Ship Type":
            print(cells[1].text.strip())
            return cells[1].text.strip()  # Return the ship type found
    return None  # Return None if no ship type is found

#Fonction pour associer le type de navire à son numéro
def assign_ship_type_number(ship_type):
    if not ship_type:
        return None  # Return None if the ship type is not provided
    ship_type = ship_type.lower()  # Convert the ship type to lowercase for case-insensitive comparison
    for number, types in ship_types.items():
        if isinstance(types, list):
            for t in types:
                if t.lower() in ship_type:  # Check if the type is part of the ship_type string
                    return number
        else:
            if types.lower() in ship_type:  # For single string entries, check if it's part of the ship_type string
                return number
    return None  # Retourner "NULL" si aucun match trouvé



