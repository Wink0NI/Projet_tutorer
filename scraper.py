from requests_html import HTMLSession
from bs4 import BeautifulSoup
import csv

# Fonction pour récupérer le type de navire à partir du MMSI
def get_ship_type(mmsi):
    # Créer une session et obtenir la page
    session = HTMLSession()
    url = f"https://www.vesselfinder.com/vessels/details/{mmsi}"
    response = session.get(url)

    # Analysez le HTML avec BeautifulSoup
    soup = BeautifulSoup(response.html.html, 'html.parser')

    # Chercher le type de navire dans les détails
    details = soup.find_all('tr')
    for detail in details:
        cells = detail.find_all('td')
        if cells and cells[0].text.strip() == "Ship Type":
            return cells[1].text.strip()  # Retourner le type de navire trouvé

    return "NULL"

# Ouvrir le fichier CSV et lire les MMSI
with open('db/ais_vessel_aus_nz.csv', 'r') as f:
    reader = csv.reader(f, delimiter=',')
    header = next(reader)  # Ignorer la première ligne (en-têtes)
    
    # Lire chaque ligne et récupérer le MMSI
    
    for row in reader:
        mmsi = row[0]  # Supposons que le MMSI soit dans la première colonne
        ship_type = get_ship_type(mmsi)
        print(f"MMSI: {mmsi}, Ship Type: {ship_type}")