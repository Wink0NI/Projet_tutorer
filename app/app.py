from flask import Flask, render_template, request, render_template_string, jsonify, render_template
from flask_cors import CORS
import psycopg2
import folium

import datetime

from geopy.distance import geodesic
from folium.plugins import HeatMap



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
    if date is None:
        # Get current timestamp for 24 hours interval
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        stamp = f"ap.received_at BETWEEN '{current_time}'::timestamp - INTERVAL '24 hours' AND '{current_time}'::timestamp"
    else:
        date = convertir_date(date)
        stamp = f"'{date}'::timestamp <= ap.received_at AND ap.received_at < '{date}'::timestamp + INTERVAL '24 hours'"

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
    print(stamp)

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
                        <b>MMSI:</b> {current_mmsi}</br>
                        <b>Nom:</b> {shipname}</br>
                        <b>Heure:</b> {received_at_str}<br>
                        <b>Latitude:</b> {lat}<br>
                        <b>Longitude:</b> {lon}
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
        return jsonify({'error': 'MMSI'}), 400

    mmsi = data['mmsi']
    date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    rows = execute_query(f"""
    SELECT ap.lat, ap.lon, ap.received_at, aiv.shipname, ap.mmsi
    FROM ais_positions ap
    JOIN ais_information_vessel aiv ON ap.mmsi = aiv.mmsi
    WHERE aiv.shipname NOT LIKE '%TEST%'
    AND ap.received_at BETWEEN '{date}'::timestamp - INTERVAL '24 hours' AND '{date}'::timestamp
    AND ap.mmsi = {mmsi}
    ORDER BY ap.received_at
    """)

    # Define the starting point of the ship
    direction = [-22.2711, 166.4380, datetime.datetime.now()
                 ] if len(rows) == 0 else [float(rows[0][0]), float(rows[0][1]), rows[0][2]]

    # Create a Folium map
    m = folium.Map(location=[direction[0], direction[1]], zoom_start=15)

    trajectory = []

    # Traverse the data for each row (GPS point)
    for row in rows:
        lat, lon, received_at, shipname, current_mmsi = row

        # Convert lat/lon to floats
        lat = float(lat)
        lon = float(lon)

        # If the ship already has a point in its trajectory, check the distance
        if len(trajectory) > 0:
            last_point = [trajectory[-1][0], trajectory[-1][1]]  # Lat/Lon only
            distance_km = geodesic(last_point, (lat, lon)).km

            # Add the point only if the distance exceeds 1 meter
            if distance_km > 0.001:
                trajectory.append((lat, lon, received_at, shipname))
        else:
            # Add the first point without checking the distance
            trajectory.append((lat, lon, received_at, shipname))


    if trajectory:
        # Add a line for the path
        folium.PolyLine(
            locations=[(point[0], point[1]) for point in trajectory],  # Use the simplified list of points
            color=list_colors[0],
            weight=2.5,
            opacity=0.5
        ).add_to(m)

        # Add markers with opacity
        for idx, (lat, lon, received_at, shipname) in enumerate(trajectory):
            opacity = 1 if idx == 0 or idx == len(trajectory) - 1 else 0
            received_at_str = received_at.strftime('%Y-%m-%d %H:%M:%S')

            folium.CircleMarker(
                location=[lat, lon],
                popup=f"""
                    <div style="width: 200px; white-space: nowrap;">
                        <b>MMSI:</b> {mmsi}</br>
                        <b>Nom:</b> {shipname}</br>
                        <b>Heure:</b> {received_at_str}<br>
                        <b>Latitude:</b> {lat}<br>
                        <b>Longitude:</b> {lon}
                    </div>
                """,
                icon=folium.Icon(color=list_colors[0], icon='ship'),
                opacity=opacity,
                fill=True,
                radius=8
            ).add_to(m)

    # Generate the HTML for the map
    map_html = m._repr_html_()

    # Return the HTML
    return render_template_string(map_html)



@app.route('/get_heatmap', methods=['GET', 'POST'])
def get_heatmap():
    data = request.get_json()

    shiptype = data['shiptype']
    includeStops = data['includeStops']

    date = data.get('date', None)  # Expecting date in a specific format

    # Create the timestamp condition based on the presence of the date parameter
    if date is None:
        # Get current timestamp for 24 hours interval
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        stamp = f"ap.received_at BETWEEN '{current_time}'::timestamp - INTERVAL '24 hours' AND '{current_time}'::timestamp"
    else:
        date = convertir_date(date)
        stamp = f"'{date}'::timestamp <= ap.received_at AND ap.received_at < '{date}'::timestamp + INTERVAL '24 hours'"


    # SQL query to fetch latitude and longitude from ais_positions
    query = f"""
    SELECT ap.lat, ap.lon
    FROM ais_positions ap
    JOIN ais_information_vessel aiv ON ap.mmsi = aiv.mmsi
    {f" JOIN shiptype s  ON aiv.shiptype = s.id_shiptype" if len(shiptype) > 0 else ""}
    WHERE aiv.shipname NOT LIKE '%TEST%'
    AND {stamp}
    {f" AND s.shiptype = '{shiptype}'" if len(shiptype) > 0 else ""} 
    {f" AND ap.speed > 0.5" if includeStops else ""}
    """
    
    # Fetching the data from the database
    rows = execute_query(query)

    # Définir le point de départ du bateau
    direction = [-22.2711, 166.4380
                 ] if len(rows) == 0 else [rows[0][0], rows[0][1]]

    # Créer une carte Folium de Nouméa
    m = folium.Map(location=[direction[0], direction[1]], zoom_start=15)


    # Prepare the data for the heatmap
    heat_data = [[lat, lon] for lat, lon in rows]

    # Create the heatmap layer
    HeatMap(heat_data).add_to(m)

    # Generate the HTML representation of the map
    map_html = m._repr_html_()

    # Return the map as a rendered HTML string
    return render_template_string(map_html)

if __name__ == '__main__':
    app.run(debug=True)


if __name__ == '__main__':
    app.run(debug=True)
