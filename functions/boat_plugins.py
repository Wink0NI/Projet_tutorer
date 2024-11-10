from datetime import datetime
from requests_html import AsyncHTMLSession
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv
import os

# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

DEFAULT_LAT = os.getenv("DEFAULT_LAT")
DEFAULT_LON = os.getenv("DEFAULT_LON")

SHIPTYPES = {
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

URL_MMSI = lambda mmsi: f"https://www.vesselfinder.com/vessels/details/{mmsi}"

async def get_ship_type(mmsi, session=None):
    """
    Récupère le type de navire à partir du MMSI.
    Retourne None si le type est introuvable ou si vous êtes fait ip ban
    """
    if session is None:
        session = AsyncHTMLSession()

    url = URL_MMSI(mmsi)

    try:
        # demarrer une session 
        response = await session.get(url, timeout=10)
        
        # pour exploiter avec BeautifulSoup
        soup = BeautifulSoup(response.html.html, 'html.parser')

        # Recherche du shiptype
        details = soup.find_all('tr')
        for detail in details:
            cells = detail.find_all('td')
            if cells and cells[0].text.strip() == "Ship Type":
                return cells[1].text.strip()  # Retourner le shiptype
        return None  # Sinon None

    except requests.exceptions.ConnectionError as e:
        print(f"Connection error: {e}")
        return None  # Handle connection error
    except:
        print(f"YOU GOT IP BANNED FROM vesslfinder {mmsi}")
        return None  # Handle timeout error
    finally:
        if session is None:
            await session.close()


def assign_ship_type_number(ship_type):
    """
    Associe un shiptype en fonction de son numéro
    """
    if not ship_type:
        return None 
    ship_type = ship_type.lower()  # Pour une meilleure comparaison
    for number, types in SHIPTYPES.items():
        if isinstance(types, list):
            for t in types:
                if t.lower() in ship_type: 
                    return number
        else:
            if types.lower() in ship_type: 
                return number
    return None  # Retourner "NULL" si aucun match trouvé



