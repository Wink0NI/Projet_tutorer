import asyncio
import websockets
import json
from datetime import datetime, timezone
import psycopg2
import functions.edit_str as edit_str


DATABASE_CONFIG = {
    'host': 'localhost',
    'database': 'Projet_tutorer',
    'user': 'admin',
    'password': 'admin'
}


def get_db_connection():
    conn = psycopg2.connect(**DATABASE_CONFIG)
    return conn

conn = get_db_connection()
cur = conn.cursor()

list_mmsi = {}


insert_query = """
INSERT INTO ais_information_vessel (
    mmsi, signalpower, ppm, received_at, station_id, msg_id, imo, callsign, shipname, shiptype, 
    to_port, to_bow, to_stern, to_starboard, eta, draught, destination, status, turn, speed, 
    lat, lon, course, heading, aid_type, alt, count, msg_types, channels
) VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
    %s, %s, %s, %s, %s, %s, %s, %s, %s
) ON CONFLICT DO NOTHING
"""

insert_query_position = """
        INSERT INTO ais_positions_noumea (
            mmsi, received_at, station_id, msg_id, status, turn, speed, lat, lon, course, heading, geom
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        ) 
        """

async def connect_ais_stream():
    async with websockets.connect("wss://stream.aisstream.io/v0/stream") as websocket:
        # Définir les coordonnées pour la zone de Sydney
        subscribe_message = {
            "APIKey": "96f5646e72d992013ac5c379e357cb553d0339c8",
            "BoundingBoxes": [[[-34.1183, 150.7032], [-33.7030, 151.3427]]]
        }

        subscribe_message_json = json.dumps(subscribe_message)
        await websocket.send(subscribe_message_json)

        async for message_json in websocket:
            message = json.loads(message_json)
            print(message)
            message_type = message["MessageType"]

            if message_type == "PositionReport":
                # Récupérer le message de position
                ais_message = message['Message']['PositionReport']

                mmsi = ais_message["UserID"]
                latitude = ais_message['Latitude']
                longitude = ais_message['Longitude']

                # Vérifier si la position est dans la zone de Sydney
                if -34.1183 <= latitude <= -33.7030 and 150.7032 <= longitude <= 151.3427:
                    print(f"[{datetime.now(timezone.utc)}] ShipId: {ais_message['UserID']} "
                          f"Latitude: {latitude} Longitude: {longitude}")
                    
                    if mmsi not in list_mmsi.keys():
                        
                        row = [mmsi, 0, 0, edit_str.convert_custom_datetime(message["MetaData"]["time_utc"].split(".")[0]), 0, ais_message["MessageID"], None, None, message["MetaData"]["ShipName"], None,
                               None, None, None, None, None, None, None, None, 0, 0,
                               latitude, longitude, None, None, None, None, None, None, None]
                        # Executer la requête d'insertion
                        cur.execute(insert_query, row)
                    else:
                        # calcul de la distance entre le point entrée précédemment et le nouveau point
                        vitesse = 5

                        row = [mmsi, edit_str.convert_custom_datetime(message["MetaData"]["time_utc"].split(".")[0]), 0, ais_message["MessageID"], ais_message["NavigationalStatus"], 0, vitesse, latitude, longitude, None, None, None]

                        cur.execute(insert_query_position, row)

                    conn.commit()
                    # Ajouter la position à la liste
                    list_mmsi[mmsi] = [mmsi, edit_str.convert_custom_datetime(message["MetaData"]["time_utc"].split(".")[0]), 0, ais_message["MessageID"], ais_message["NavigationalStatus"], 0, vitesse, latitude, longitude, None, None, None]
                    



if __name__ == "__main__":
    asyncio.run(connect_ais_stream())
