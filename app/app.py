from flask import Flask, render_template, request, render_template_string, jsonify, render_template
from flask_cors import CORS
import psycopg2
import folium

import datetime

from geopy.distance import geodesic
from folium.plugins import HeatMapWithTime, HeatMap


# Convert RGBA colors to HEX format
list_colors = ['red', 'gray', 'green', 'darkgreen', 'darkpurple', 'lightblue', 'black', 'blue', 'lightgreen',
               'darkred', 'pink', 'cadetblue', 'darkblue', 'white', 'lightgray', 'orange', 'purple', 'beige']

tolerance = 1.0  # Tolérance de 1 km

app = Flask(__name__)
CORS(app)


# Configuration de la connexion à la base de données
DATABASE_CONFIG = {
    'host': 'localhost',
    'database': 'Projet_tutorer',
    'user': 'admin',
    'password': 'admin'
}
conn = psycopg2.connect(
    host="localhost",
    database="Projet_tutorer",
    user="admin",
    password="admin"
)

# Créer un curseur
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS ais_information_vessel (
    mmsi BIGINT,
    signalpower FLOAT,
    ppm FLOAT,
    received_at TIMESTAMP,
    station_id BIGINT,
    msg_id INT,
    imo BIGINT,
    callsign VARCHAR(255),
    shipname VARCHAR(255),
    shiptype INT,
    to_port INT,
    to_bow INT,
    to_stern INT,
    to_starboard INT,
    eta TIMESTAMP,
    draught FLOAT,
    destination VARCHAR(255),
    status INT,
    turn FLOAT,
    speed FLOAT,
    lat FLOAT,
    lon FLOAT,
    course FLOAT,
    heading FLOAT,
    aid_type INT,
    alt FLOAT,
    count INT,
    msg_types INT,
    channels INT,
    PRIMARY KEY (mmsi)
);
""")
##################################################################################################################################################################

# Création de la table "ais_positions"
cur.execute("""
CREATE TABLE IF NOT EXISTS ais_positions (
    mmsi INT NOT NULL,
    received_at TIMESTAMP NOT NULL,
    station_id INT,
    msg_id INT,
    status VARCHAR(50),
    turn FLOAT,
    speed FLOAT,
    lat FLOAT,
    lon FLOAT,
    course FLOAT,
    heading FLOAT,
    geom VARCHAR(255)
);
""")


# table shiptype
cur.execute("""
CREATE TABLE IF NOT EXISTS shiptype (
    id_shiptype INT NOT NULL PRIMARY KEY,
    shiptype VARCHAR(255) NOT NULL
);
""")

conn.commit()

conn.close()
cur.close()


def convertir_date(date_str):
    # Définir le format d'entrée
    format_entree = "%d/%m/%Y"
    # Définir le format de sortie
    format_sortie = "%Y-%m-%d"

    # Convertir la chaîne en objet datetime
    date_obj = datetime.datetime.strptime(date_str, format_entree)

    # Convertir l'objet datetime en chaîne au format souhaité
    date_formatee = date_obj.strftime(format_sortie)

    return date_formatee


def get_db_connection():
    conn = psycopg2.connect(**DATABASE_CONFIG)
    return conn


def execute_query(query):
    conn = get_db_connection()
    cur = conn.cursor()

    # Exécuter la requête SQL pour obtenir les positions du bateau
    cur.execute(query)
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows


@app.route('/')
def index():
    return render_template("index.html")


def get_boat_info(mmsi):
    """Fetch boat information from the ais_information_vessel table."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query to fetch boat information based on MMSI
    cursor.execute("""
        SELECT mmsi, shipname, received_at, lat, lon, speed 
        FROM ais_information_vessel 
        WHERE mmsi = %s
        LIMIT 1;
    """, (mmsi,))

    boat_info = cursor.fetchone()  # Fetch one record
    cursor.close()
    conn.close()

    if boat_info:
        return {
            "mmsi": boat_info[0],
            "shipname": boat_info[1],
            "received_at": boat_info[2],
            "lat": boat_info[3],
            "lon": boat_info[4],
            "speed": boat_info[5]
        }
    else:
        return None


@app.route('/mmsi/name/<string:mmsi_name>', methods=['GET'])
def get_vessel_info(mmsi_name):
    conn = get_db_connection()
    cur = conn.cursor()

    query_name = f"""
    SELECT *
    FROM ais_information_vessel
    WHERE UPPER(shipname) LIKE '%{mmsi_name.upper()}%'
    AND UPPER(shipname) NOT LIKE '%TEST%'
    ORDER BY received_at DESC
"""

    # Execute query with mmsi_name parameter
    cur.execute(query_name)
    result = cur.fetchone()




    cur.close()
    conn.close()

    if result is None:
        return jsonify({'error': 'Vessel not found'}), 404

    # Construct the response dictionary
    vessel_info = {
        'mmsi': result[0]
    }

    return jsonify(vessel_info)


@app.route('/mmsi/<mmsi>', methods=['GET'])
def info_boat(mmsi):
    """Fetch boat data and render it using a Jinja template."""
    try:
        boat_info = get_boat_info(mmsi)
    except psycopg2.errors.InvalidTextRepresentation as sql_error:
        return "Failed to fetch boat information", 500
    except:
        return f"Boat with MMSI {mmsi} not found", 404

    if boat_info:
        return render_template('boat_info.jinja.html', boat=boat_info)
    else:
        return f"Boat with MMSI {mmsi} not found", 404


@app.route('/get_map', methods=['GET', 'POST'])
def get_map():
    data = request.get_json()

    if 'includeStops' not in data:
        return jsonify({'error': 'MMSI'}), 400

    shiptype = data['shiptype']
    includeStops = data['includeStops']

    date = data.get('date', None)  # Expecting date in a specific format

    # Create the timestamp condition based on the presence of the date parameter
    if not date:
        # Get current timestamp for 24 hours interval
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        stamp = f"ap.received_at BETWEEN '{current_time}'::timestamp - INTERVAL '24 hours' AND '{current_time}'::timestamp"
    else:
        date = convertir_date(date)
        stamp = f"ap.received_at BETWEEN '{date} 00:00:00'::timestamp AND '{date} 23:59:59'::timestamp"

    rows = execute_query(f"""
    SELECT DISTINCT ON (ap.mmsi) ap.lat, ap.lon, ap.received_at, aiv.shipname, ap.mmsi
    FROM ais_positions ap
    JOIN ais_information_vessel aiv ON ap.mmsi = aiv.mmsi
    {f" JOIN shiptype s  ON aiv.shiptype = s.id_shiptype" if len(shiptype) > 0 else ""}
    WHERE aiv.shipname NOT LIKE '%TEST%'
    AND  {stamp}
    {f" AND s.shiptype = '{shiptype}'" if len(shiptype) > 0 else ""} 
    {f" AND ap.speed > 0.5" if includeStops else ""}
    ORDER BY ap.mmsi, ap.received_at DESC
""")

    # Définir le point de départ du bateau
    direction = [-22.2711, 166.4380, datetime.datetime.now()
                 ] if len(rows) == 0 else [rows[0][0], rows[0][1], rows[0][2]]

    # Créer une carte Folium de Nouméa
    m = folium.Map(location=[direction[0], direction[1]], zoom_start=15)

    i = 0

    # Parcourir les données pour chaque ligne (chaque point GPS)
    for row in rows:
        lat, lon, received_at, shipname, current_mmsi = row

        try:
            list_colors[i+1]
        except:
            i = 0

        received_at_str = received_at.strftime('%Y-%m-%d %H:%M:%S')

        folium.CircleMarker(
            location=[lat, lon],
            radius=8,  # Size of the circle
            popup=f"""
                    <div style="width: 200px; white-space: nowrap;">
                                <b>MMSI:</b> {current_mmsi}<br>
                                <b>Nom:</b> {shipname}<br>
                                <b>Heure:</b> {received_at_str}<br>
                                <b>Latitude:</b> {lat}<br>
                                <b>Longitude:</b> {lon}<br>
                                <a href="http://localhost:5000/mmsi/{current_mmsi}" target="_blank">
                                    <button type="button">Information bateau</button>
                                </a>
                            </div>
                """,
            color=list_colors[i],  # Circle color (from list)
            fill=True,
            opacity=0.6
        ).add_to(m)

        i += 1

    # Générer le HTML de la carte
    map_html = m._repr_html_()

    # Retourner le HTML
    return render_template_string(map_html)


@app.route('/get_map_mmsi', methods=['GET', 'POST'])
def get_map_mmsi():
    data = request.get_json()

    if 'mmsi' not in data:
        return jsonify({'error': 'MMSI not provided'}), 400

    mmsi = data['mmsi']

    date = data.get('date', None)  # Expecting date in a specific format

    # Create the timestamp condition based on the presence of the date parameter
    if not date:
        # Get current timestamp for 24 hours interval
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        stamp = f"ap.received_at BETWEEN '{current_time}'::timestamp - INTERVAL '24 hours' AND '{current_time}'::timestamp"
    else:
        date = convertir_date(date)
        stamp = f"ap.received_at BETWEEN '{date} 00:00:00'::timestamp AND '{date} 23:59:59'::timestamp"


    rows = execute_query(f"""
    SELECT ap.lat, ap.lon, ap.received_at, aiv.shipname, ap.mmsi
    FROM ais_positions ap
    JOIN ais_information_vessel aiv ON ap.mmsi = aiv.mmsi
    WHERE aiv.shipname NOT LIKE '%TEST%'
    AND {stamp} 
    AND ap.mmsi = {mmsi}
    ORDER BY ap.received_at DESC
    """)

    # Define the starting point of the map
    direction = [-22.2711, 166.4380, datetime.datetime.now()
                 ] if len(rows) == 0 else [rows[0][0], rows[0][1], rows[0][2]]
    m = folium.Map(location=[direction[0], direction[1]], zoom_start=15)

    # Process each row to build the trajectory
    # Initialize trajectory list
    trajectory = []
    for row in rows:
        lat, lon, received_at, shipname, current_mmsi = row

        # Convert lat and lon to floats to avoid type errors
        try:
            lat = float(lat)
            lon = float(lon)
        except ValueError:
            # Skip this point if lat or lon cannot be converted to float
            continue

        if len(trajectory) > 0:
            last_point = [trajectory[-1][0], trajectory[-1][1]]
            distance_km = geodesic(last_point, (lat, lon)).km

            if distance_km > 0.01:
                trajectory.append((lat, lon, received_at, shipname))
        else:
            trajectory.append((lat, lon, received_at, shipname))

    # Now add to the map, filtering only valid (lat, lon) points
    valid_locations = [(lat, lon) for lat, lon, _,
                       _ in trajectory if lat is not None and lon is not None]

    if valid_locations:
        folium.PolyLine(
            locations=valid_locations,
            color=list_colors[0],  # Default color if mmsi color not found
            weight=2.5,
            opacity=0.5
        ).add_to(m)

    # Adding markers
    for idx, (lat, lon, received_at, shipname) in enumerate(trajectory):
        if lat is None or lon is None:
            continue  # Skip invalid points

        opacity = 1 if idx == 0 or idx == len(trajectory) - 1 else 0
        received_at_str = received_at.strftime('%Y-%m-%d %H:%M:%S')

        folium.CircleMarker(
            location=[lat, lon],
            popup=f"""
                <div style="width: 200px; white-space: nowrap;">
                    <b>MMSI:</b> {mmsi}<br>
                    <b>Nom:</b> {shipname}<br>
                    <b>Heure:</b> {received_at_str}<br>
                    <b>Latitude:</b> {lat}<br>
                    <b>Longitude:</b> {lon}<br>
                </div>
            """,
            color=list_colors[0],
            fill=True,
            fill_opacity=opacity,
            radius=8
        ).add_to(m)

    map_html = m._repr_html_()

    return render_template_string(map_html)


@app.route('/get_heatmap', methods=['GET', 'POST'])
def get_heatmap():
    data = request.get_json()

    shiptype = data['shiptype']
    includeStops = data['includeStops']

    date = data.get('date', None)

    # Create the timestamp condition based on the presence of the date parameter
    if not date:
        # Get current timestamp for 24 hours interval
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        stamp = f"ap.received_at BETWEEN '{current_time}'::timestamp - INTERVAL '24 hours' AND '{current_time}'::timestamp"
    else:
        date = convertir_date(date)
        stamp = f"ap.received_at BETWEEN '{date} 00:00:00'::timestamp AND '{date} 23:59:59'::timestamp"

    # SQL query to fetch latitude, longitude, and timestamp from ais_positions
    query = f"""
    SELECT ap.lat, ap.lon, ap.received_at
    FROM ais_positions ap
    JOIN ais_information_vessel aiv ON ap.mmsi = aiv.mmsi
    {f" JOIN shiptype s ON aiv.shiptype = s.id_shiptype" if len(shiptype) > 0 else ""}
    WHERE aiv.shipname NOT LIKE '%TEST%'
    AND {stamp}
    {f" AND s.shiptype = '{shiptype}'" if len(shiptype) > 0 else ""}
    {f" AND ap.speed > 0.5" if includeStops else ""}
    ORDER BY ap.received_at
    """

    # Fetching the data from the database
    rows = execute_query(query)

        # Initialize an empty list to hold data for each hour
    heat_data = [[] for _ in range(24)]  # 24 lists for each hour in the day

    

    # Définir un point de départ par défaut si aucune donnée n’est trouvée
    direction = [-22.2711, 166.4380] if len(rows) == 0 else [rows[0][0], rows[0][1]]

    # Créer une carte centrée sur la région spécifiée
    m = folium.Map(location=direction, zoom_start=10)

    if rows:
        # Group data into 24 hourly intervals
        for lat, lon, timestamp in rows:
            hour = timestamp.hour
            heat_data[hour].append([lat, lon])  # Append lat/lon to the correct hour's list
        

        # Ajouter la heatmap avec le temps
        HeatMapWithTime(heat_data, radius=15, auto_play=True, max_opacity=0.8, index=[f"{hour}h" for hour in range(24)]).add_to(m)
    else:
        HeatMap(heat_data, radius=15, max_opacity=0.8).add_to(m)

    # Générer le code HTML de la carte
    map_html = m._repr_html_()

    # Retourner la carte en tant que chaîne HTML
    return render_template_string(map_html)


@app.route('/get_shiptypes', methods=['GET'])
def get_shiptype():
    conn = get_db_connection()  # Assure-toi que get_db_connection est bien définie
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT s.shiptype
        FROM shiptype s
        JOIN ais_information_vessel aiv ON s.id_shiptype = aiv.shiptype
    """)
    rows = cursor.fetchall()

    # Transformer les résultats en une liste
    shiptypes = [row[0] for row in rows]

    # Retourner les données sous forme de JSON
    return jsonify(shiptypes)


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)


if __name__ == '__main__':
    app.run(debug=True)
