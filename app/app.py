from flask import Flask, render_template, send_from_directory, request, redirect, url_for, render_template_string, jsonify
from flask_cors import CORS
import psycopg2
import folium

import datetime
from geopy.distance import geodesic

from rdp import rdp



# Convert RGBA colors to HEX format
list_colors = ['red', 'gray', 'green', 'darkgreen', 'darkpurple', 'lightblue', 'black', 'blue', 'lightgreen', 'darkred', 'pink', 'cadetblue', 'darkblue', 'white', 'lightgray', 'orange', 'purple', 'beige']

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


@app.route('/')
def index():
    return render_template("index.html")




@app.route('/get_map', methods=['GET', 'POST'])
def get_map():
    data = request.get_json()

    if 'includeStops' not in data or 'date' not in data:
        return jsonify({'error': 'MMSI ou date manquants'}), 400

    mmsi = data['mmsi']
    date = convertir_date(data['date'])
    include_stops = data['includeStops']

    conn = get_db_connection()
    cur = conn.cursor()

    # Exécuter la requête SQL pour obtenir les positions du bateau
    cur.execute(f"""
        SELECT apn.lat, apn.lon, apn.received_at, shipname, aiv.mmsi
        FROM ais_positions_noumea apn
        JOIN ais_information_vessel aiv ON apn.mmsi = aiv.mmsi
        WHERE apn.received_at::date = '{date}' {f" AND apn.mmsi = {mmsi}" if len(mmsi) > 0 else ""} {" AND apn.speed > 0.5" if not include_stops else ""}
        ORDER BY apn.received_at
    """)

    rows = cur.fetchall()

    # Définir le point de départ du bateau
    direction = [-22.2711, 166.4380, datetime.datetime.now()] if len(rows) == 0 else [rows[0][0], rows[0][1], rows[0][2]]

    # Créer une carte Folium de Nouméa
    m = folium.Map(location=[direction[0], direction[1]], zoom_start=15)

    # Fermer la connexion à la base de données
    cur.close()
    conn.close()

    shipname_color = {}
    trajectory = {}
    i = 0

    # Parcourir les données pour chaque ligne (chaque point GPS)
    for row in rows:
        lat, lon, received_at, shipname, current_mmsi = row

        if current_mmsi not in shipname_color:
            try:
                shipname_color[current_mmsi] = list_colors[i]
            except:
                i = 0

            trajectory[current_mmsi] = []
            shipname_color[current_mmsi] = list_colors[i]
            i += 1

        # Si le navire a déjà un point dans sa trajectoire, on vérifie la distance
        if len(trajectory[current_mmsi]) > 0:
            last_point = [trajectory[current_mmsi][-1][0], trajectory[current_mmsi][-1][1]]  # Lat/Lon only
            distance_km = geodesic(last_point, (lat, lon)).km

            # Ajouter le point seulement si la distance dépasse 1 km
            if distance_km > 0.001:
                trajectory[current_mmsi].append((lat, lon, received_at, shipname))
        else:
            # Ajouter le premier point sans vérifier la distance
            trajectory[current_mmsi].append((lat, lon, received_at, shipname))

    # Ajout des lignes et marqueurs sur la carte
    for mmsi, points in trajectory.items():
        # Collect all (lat, lon) points for the PolyLine
        polyline_points = [(lat, lon) for lat, lon, _, _ in points]
        
        # Simplify the polyline using rdp if needed
        simplified_points = rdp(polyline_points, epsilon=0.001)

        # Ajouter une ligne pour le trajet
        folium.PolyLine(
            locations=simplified_points,  # Use the simplified list of points
            color=shipname_color[mmsi],
            weight=2.5,
            opacity=0.8
        ).add_to(m)

        # Ajouter des marqueurs avec opacité
        for idx, (lat, lon, received_at, shipname
                  ) in enumerate(points):
            opacity = 1 if idx == 0 or idx == len(points) - 1 else 0
            received_at_str = received_at.strftime('%Y-%m-%d %H:%M:%S')
  

            folium.Marker(
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
                icon=folium.Icon(color=shipname_color[mmsi], icon='ship'),
                opacity=opacity
            ).add_to(m)

    # Générer le HTML de la carte
    map_html = m._repr_html_()

    # Retourner le HTML
    return render_template_string(map_html)




if __name__ == '__main__':
    app.run(debug=True)
