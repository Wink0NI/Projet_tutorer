import asyncio
import websockets
import json
from datetime import datetime, timezone


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
                latitude = ais_message['Latitude']
                longitude = ais_message['Longitude']

                # Vérifier si la position est dans la zone de Sydney
                if -34.1183 <= latitude <= -33.7030 and 150.7032 <= longitude <= 151.3427:
                    print(f"[{datetime.now(timezone.utc)}] ShipId: {ais_message['UserID']} "
                          f"Latitude: {latitude} Longitude: {longitude}")

{
    'Message': {
        'PositionReport': {
            'Cog': 360, 'CommunicationState': 59916, 'Latitude': -33.968243333333334, 'Longitude': 151.22058666666666, 'MessageID': 1, 'NavigationalStatus': 0, 'PositionAccuracy': True, 'Raim': True, 'RateOfTurn': 0, 'RepeatIndicator': 0, 'Sog': 0, 'Spare': 0, 'SpecialManoeuvreIndicator': 0,
            'Timestamp': 29, 'TrueHeading': 325, 'UserID': 503650800, 'Valid': True}
    },
    'MessageType': 'PositionReport',
    'MetaData': {
        'MMSI': 503650800, 'MMSI_String': 503650800, 'ShipName': 'RESPONSE 2          ', 'latitude': -33.968243333333334, 'longitude': 151.22058666666666, 'time_utc': '2024-10-01 05:25:29.724562978 +0000 UTC'
        }}

if __name__ == "__main__":
    asyncio.run(connect_ais_stream())
