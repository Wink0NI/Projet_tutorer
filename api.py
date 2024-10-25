import ssl
import websockets
import asyncio
import json
from datetime import datetime, timezone
import psycopg2
import functions.boat_plugins as boat_plugins
import math
from requests_html import AsyncHTMLSession

ssl_context = ssl._create_unverified_context()

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
        INSERT INTO ais_positions (
            mmsi, received_at, station_id, msg_id, status, turn, speed, lat, lon, course, heading, geom
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        ) 
        """

select_mmsi = """
        SELECT lat, lon, received_at FROM ais_positions WHERE mmsi = %s ORDER BY received_at DESC LIMIT 1
        """


def haversine_formula(lat1, lat2, lon1, lon2):
    # Earth radius in kilometers
    earth_radius = 6371.0
    
    # Convert degrees to radians
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)
    
    # Difference in coordinates
    diff_lat = lat2 - lat1
    diff_lon = lon2 - lon1

    # Haversine formula
    formula = math.sin(diff_lat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(diff_lon / 2)**2
    celerity = 2 * math.atan2(math.sqrt(formula), math.sqrt(1 - formula))

    distance = earth_radius * celerity

    return distance

def calculate_speed(lat1, lon1, time1, lat2, lon2, time2):
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


async def connect_ais_stream():
    session = AsyncHTMLSession()
    async with websockets.connect("wss://stream.aisstream.io/v0/stream",ssl=ssl_context) as websocket:
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
                        cur.execute("SELECT * FROM ais_information_vessel WHERE mmsi = %s", [mmsi])
                        cur.fetchone()
                        if cur.rowcount > 0:
                            date = boat_plugins.convert_custom_datetime(message["MetaData"]["time_utc"].split(".")[0])

                            shiptype = await boat_plugins.get_ship_type(mmsi, session=session) 
                            shiptype = boat_plugins.assign_ship_type_number(shiptype)
                            
                            row = [mmsi, 0, 0, date, 0, ais_message["MessageID"], None, None, message["MetaData"]["ShipName"], shiptype,
                                None, None, None, None, None, None, None, None, 0, 0,
                                latitude, longitude, None, None, None, None, None, None, None]
                            # Executer la requête d'insertion
                            cur.execute(insert_query, row)
                        vitesse  = 1
                    else:

                        # Get the previous position and time
                        prev_lat = list_mmsi[mmsi][7]
                        prev_lon = list_mmsi[mmsi][8]
                        prev_time = list_mmsi[mmsi][1]

                        # Calculate speed
                        vitesse = calculate_speed(prev_lat, prev_lon, prev_time, latitude, longitude, date)
                        print(vitesse)


                    row = [mmsi, date, 0, ais_message["MessageID"], ais_message["NavigationalStatus"], 0, vitesse, latitude, longitude, None, None, None]

                    cur.execute(insert_query_position, row)

                    conn.commit()
                    # Ajouter la position à la liste
                    list_mmsi[mmsi] = row
                    



if __name__ == "__main__":
    asyncio.run(connect_ais_stream())
