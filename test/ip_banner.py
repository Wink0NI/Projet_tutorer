from requests_html import AsyncHTMLSession
from bs4 import BeautifulSoup
import asyncio
import csv

# Fonction pour récupérer le type de navire à partir du MMSI
async def get_ship_type(mmsi, session):
    url = f"https://www.vesselfinder.com/vessels/details/{mmsi}"
    
    # Faire une requête asynchrone
    response = await session.get(url)

    # Analysez le HTML avec BeautifulSoup
    soup = BeautifulSoup(response.html.html, 'html.parser')

    # Chercher le type de navire dans les détails
    details = soup.find_all('tr')
    for detail in details:
        cells = detail.find_all('td')
        if cells and cells[0].text.strip() == "Ship Type":
            print(cells[1].text.strip() )
            print(f"MMSI: {mmsi}, Ship Type: {cells[1].text.strip()}")
            return cells[1].text.strip()  # Retourner le type de navire trouvé
    print(f"MMSI: {mmsi}, Ship Type: NULL")
    return "NULL"  # Retourner "NULL" si aucun type n'a été trouvé

# Fonction pour traiter les MMSI depuis le fichier CSV
async def process_mmsi_from_csv(csv_file):
    session = AsyncHTMLSession()  # Créer une session pour toute la durée de l'exécution
    tasks = []  # Liste pour stocker les tâches asynchrones
    mmsi_list = []  # Liste pour stocker les MMSI

    # Ouvrir le fichier CSV et lire les MMSI
    with open(csv_file, 'r') as f:
        reader = csv.reader(f, delimiter=',')
        header = next(reader)  # Ignorer la première ligne (en-têtes)

        # Lire chaque ligne et récupérer le MMSI
        for row in reader:
            mmsi = row[0]  # Supposons que le MMSI soit dans la première colonne
            mmsi_list.append(mmsi)  # Stocker le MMSI
            

            # Créer une tâche asynchrone pour chaque requête
            tasks.append(get_ship_type(mmsi, session))

    # Exécuter toutes les tâches asynchrones en parallèle et récupérer les résultats
    results = await asyncio.gather(*tasks)

    # Afficher les résultats
    with open("data.csv", "+a") as f:
        for mmsi, ship_type in zip(mmsi_list, results):  # Utiliser mmsi_list, car reader est fermé
            f.write(f"{mmsi};{ship_type}\n")

asyncio.run(process_mmsi_from_csv('db/ais_vessel_aus_nz.csv'))