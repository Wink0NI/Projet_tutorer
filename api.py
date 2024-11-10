import ssl
import websockets
import asyncio
import json
from requests_html import AsyncHTMLSession

from functions.boat_plugins import get_ship_type, assign_ship_type_number
from functions.database_query import INSERT_INFORMATION, INSERT_POSITION, MMSI_INFO_QUERY
from functions.operations_plugins import calculate_speed, convert_custom_datetime

from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv('API_KEY')

from functions.database_query import get_db_connection

ssl_context = ssl._create_unverified_context()

# Démarrage de la base  de donnée
conn, cur = get_db_connection()

# Liste des MMSI pour lesquels on va récupérer les positions
list_mmsi = {}

async def connect_ais_stream():
    """
    Permettre de se connecter sur aisstream.io
    """
    session = AsyncHTMLSession()

    # Se connecter à aisstream.io
    async with websockets.connect("wss://stream.aisstream.io/v0/stream",ssl=ssl_context) as websocket:

        # Définir les coordonnées pour la zone de Sydney
        subscribe_message = {
            "APIKey": API_KEY,
            "BoundingBoxes": [[[-39.0, 141.0], [-10.0, 154.0]]]
        }

        # En attente des réponses données par aisstream.io
        subscribe_message_json = json.dumps(subscribe_message)
        await websocket.send(subscribe_message_json)

        # Pour chaque information données
        async for message_json in websocket:
            message = json.loads(message_json)
            message_type = message["MessageType"]

            # Récupérer le message de position
            if message_type == "PositionReport":
                ais_message = message['Message']['PositionReport']

                # Récolter les informations nécessaires
                mmsi = ais_message["UserID"]
                latitude = ais_message['Latitude']
                longitude = ais_message['Longitude']
                date = convert_custom_datetime(message["MetaData"]["time_utc"].split(".")[0])

                # Vérifier si la position est dans la zone de Sydney
                if -39.0 <= latitude <= -10.0 and 141.0 <= longitude <= 154.0:
                    
                    # Afficher les informations de la position
                    print(f"[{ date }] ShipId: {ais_message['UserID']} ShipName: {message['MetaData']['ShipName']} "
                          f"Latitude: {latitude} Longitude: {longitude}")
                    
                    # Si c'est la prmière fois qu'on voit ce mmsi dans le script
                    if mmsi not in list_mmsi.keys():
                         # On vérifie si le mmsi existe dans ais_information_vessel
                        cur.execute(MMSI_INFO_QUERY, [mmsi])
                        vessel_info = cur.fetchone()
                        
                        if not vessel_info:
                            # Récupérer le shiptype
                            shiptype = await get_ship_type(mmsi, session=session) 
                            shiptype = assign_ship_type_number(shiptype)
                            
                            row = [mmsi, 0, 0, date, 0, ais_message["MessageID"], None, None, message["MetaData"]["ShipName"], shiptype,
                                None, None, None, None, None, None, None, None, 0, 0,
                                latitude, longitude, None, None, None, None, None, None, None]
                            
                            # Insérer le nouveau bateau
                            cur.execute(INSERT_INFORMATION, row)
                        vitesse  = 1
                    else:

                        # Récupérer les coordonnées de l'ancien bateau
                        prev_lat = list_mmsi[mmsi][7]
                        prev_lon = list_mmsi[mmsi][8]
                        prev_time = list_mmsi[mmsi][1]

                        # Calculate speed
                        vitesse = calculate_speed(prev_lat, prev_lon, prev_time, latitude, longitude, date)


                    row = [mmsi, date, 0, ais_message["MessageID"], ais_message["NavigationalStatus"], 0, vitesse, latitude, longitude, None, None, None]

                    # Ajouter la nouvelle position
                    cur.execute(INSERT_POSITION, row)
                    conn.commit()

                    # Ajouter la position à la liste
                    list_mmsi[mmsi] = row
                    



if __name__ == "__main__":
    asyncio.run(connect_ais_stream())
