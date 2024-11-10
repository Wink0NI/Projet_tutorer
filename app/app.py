from flask import Flask, render_template, request, render_template_string, jsonify, render_template
from flask_cors import CORS
import psycopg2
import folium

from datetime import datetime
from datetime import timedelta

from geopy.distance import geodesic
from folium.plugins import HeatMapWithTime, HeatMap

import os
import sys

# Ajouter le chemin du dossier parent pour accéder à functions
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

#Importations de fonctions crées
from functions.boat_plugins import DEFAULT_LAT, DEFAULT_LON
from functions.database_query import CREATE_TABLE_INFORMATION, CREATE_TABLE_POSITIONS, CREATE_TABLE_SHIPTYPE, MMSI_INFO_QUERY, SHIPTYPE_QUERY, get_db_connection, execute_query, close_db_connection
from functions.operations_plugins import convertir_date

from dotenv import load_dotenv

# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

# informations bdd
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_DATABASE'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD')
}

# Liste des couleurs possible sur folium
LIST_COLORS = ['red', 'gray', 'green', 'darkgreen', 'darkpurple', 'lightblue', 'black', 'blue', 'lightgreen',
               'darkred', 'pink', 'cadetblue', 'darkblue', 'white', 'lightgray', 'orange', 'purple', 'beige']

# CORS pour permettre le cross origin
app = Flask(__name__)
CORS(app)

try:
    conn, cur = get_db_connection()

    # Création de la table "ais_informations"
    cur.execute(CREATE_TABLE_INFORMATION)

    # Création de la table "ais_positions"
    cur.execute(CREATE_TABLE_POSITIONS)

    # table shiptype
    cur.execute(CREATE_TABLE_SHIPTYPE)

    conn.commit()
except:
    print("Erreur lors de la connexion à la base de données")
    exit(-1)
finally:
    close_db_connection(conn, cur)


@app.route('/')
def index():
    return render_template("index.html")


def get_boat_info(mmsi):
    """
    Récupère les informations d'un bateau en fonction du mmsi donné
    :param mmsi: le mmsi du bateau
    :return: les informations du bateau sous forme de dictionnaire
    """

    # Récupérer les informations d'un bateau
    boat_info = execute_query(MMSI_INFO_QUERY, [mmsi], one=True)

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
    """
    Récupère le mmsi du bateau en fonction de son nom. Récupère le bateau reçu par la BDD la plus récente
    :param mmsi_name: le nom du bateau
    :return: le mmsi du bateau
    """

    # Execute query with mmsi_name parameter
    result = execute_query(
        f"""
        SELECT *
        FROM ais_information_vessel
        WHERE UPPER(shipname) LIKE '%{mmsi_name.upper()}%'
        AND UPPER(shipname) NOT LIKE '%TEST%'
        ORDER BY received_at DESC
        """,
        one=True)

    # Le nom du bateau est introuvable
    if result is None:
        return jsonify({'error': 'Vessel not found'}), 404

    # retourner le mmsi
    vessel_info = {
        'mmsi': result[0]
    }

    return jsonify(vessel_info)


@app.route('/mmsi/<mmsi>', methods=['GET'])
def info_boat(mmsi):
    """
    Récupère les informations d'un bateau en fonction du mmsi donné
    :param mmsi: le mmsi du bateau
    :return: un template jinja
    """
    try:
        boat_info = get_boat_info(mmsi)
    except psycopg2.errors.InvalidTextRepresentation as sql_error:
        return render_template('error.jinja.html', error={"title": "sql_error", "message": "Failed to fetch boat information"}), 500
    except:
        return render_template('error.jinja.html', error={"title": "sql_error", "message": f"Boat with MMSI {mmsi} not found"}); 404

    if boat_info:
        return render_template('boat_info.jinja.html', boat=boat_info)
    else:
        return render_template('error.jinja.html', error={"title": "sql_error", "message": f"Boat with MMSI {mmsi} not found"}), 404


@app.route('/get_map', methods=['GET', 'POST'])
def get_map():
    """
    Génère une carte des bateaux en fonction de la date et du shiptype
    """
    # récupérer les informations
    data = request.get_json()

    # Pour inclure les bateaux qui ne sont pas en mouvement OBLIGATOIRE
    if 'includeStops' not in data:
        return jsonify({'error': 'MMSI'}), 400

    # Récupérer le shiptype et includeStops
    shiptype = data['shiptype']
    includeStops = data['includeStops']

    # recuperer la date, envoie none si aucune reponse
    date = data.get('date', None)

    # Timestamp condition
    if not date:
        # Dernieres 24h
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        stamp = f"ap.received_at BETWEEN '{current_time}'::timestamp - INTERVAL '24 hours' AND '{current_time}'::timestamp"
    else:
        # Convertir la date en datetime
        date = convertir_date(date)

        # Les 24h de cette date
        stamp = f"ap.received_at BETWEEN '{date} 00:00:00'::timestamp AND '{date} 23:59:59'::timestamp"

    rows = execute_query(
        f"""
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

    # Point de départ du bateau
    direction = [DEFAULT_LAT, # latitude
                 DEFAULT_LON, # longitude
                 datetime.now() # date
                ] if len(rows) == 0 else [ # si aucun point a été enregistré à ce moment
                rows[0][0],
                rows[0][1],
                rows[0][2]
                ]

    # Créer une carte Folium de Nouméa
    m = folium.Map(location=[direction[0], direction[1]], zoom_start=15)

    # indice de couleur pour chaque bateau
    i = 0

    # Parcourir les données pour chaque ligne (chaque point GPS)
    for row in rows:
        lat, lon, received_at, shipname, current_mmsi = row

        # On remet le i à 0 si i <= len(LIST_COLORS)
        if i >= len(LIST_COLORS):
            i = 0

        # date -> String
        received_at_str = received_at.strftime('%Y-%m-%d %H:%M:%S')

        # Ajouter un marqueur à la carte Folium
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
            color=LIST_COLORS[i],  # couleur
            fill=True,
            opacity=0.6
        ).add_to(m)

        # On change de couleur
        i += 1

    # Générer le HTML de la carte
    map_html = m._repr_html_()

    # Retourner le HTML
    return render_template_string(map_html)


@app.route('/get_map_mmsi', methods=['GET', 'POST'])
def get_map_mmsi():
    """
    Génère la carte du trajet d'un bateau à une certaine date
    """
    data = request.get_json()

    # MMSI obligatoire
    if 'mmsi' not in data:
        return jsonify({'error': 'MMSI not provided'}), 400

    # Récupération du mmsi et de la date
    mmsi = data['mmsi']
    date = data.get('date', None)

    # Pas de date entree
    if not date:
        # dernieres 24h
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        stamp = f"ap.received_at BETWEEN '{current_time}'::timestamp - INTERVAL '24 hours' AND '{current_time}'::timestamp"
    else:
        # Convertir la date en datetime -> les 24h de cette date
        date = convertir_date(date)
        stamp = f"ap.received_at BETWEEN '{date} 00:00:00'::timestamp AND '{date} 23:59:59'::timestamp"

    rows = execute_query(
        f"""
        SELECT ap.lat, ap.lon, ap.received_at, aiv.shipname, ap.mmsi
        FROM ais_positions ap
        JOIN ais_information_vessel aiv ON ap.mmsi = aiv.mmsi
        WHERE aiv.shipname NOT LIKE '%TEST%'
        AND {stamp} 
        AND ap.mmsi = {mmsi}
        ORDER BY ap.received_at DESC
        """)

    # Point de départ de la carte
    direction = [DEFAULT_LAT, DEFAULT_LON, datetime.now() # Position de Nouméa si aucun bateau recu à la date donnée
                 ] if len(rows) == 0 else [rows[0][0], rows[0][1], rows[0][2]] # Position du premier point
    
    # Carte folium
    m = folium.Map(location=[direction[0], direction[1]], zoom_start=15)

    # Liste pour stocker les points
    trajectory = []
    for row in rows:
        lat, lon, received_at, shipname, current_mmsi = row

        # Gestion en cas si des données erronnées sont présentes
        try:
            lat = float(lat)
            lon = float(lon)
        except ValueError:
            continue
        
        # Calculer la distance entre le dernier point et le nouveau point
        if len(trajectory) > 0:
            last_point = [trajectory[-1][0], trajectory[-1][1]]
            distance_km = geodesic(last_point, (lat, lon)).km

            if distance_km > 0.01:
                trajectory.append((lat, lon, received_at, shipname))
        else:
            trajectory.append((lat, lon, received_at, shipname))

    # Récupérer les latitudes et longitudes
    valid_locations = [(lat, lon) for lat, lon, _,
                       _ in trajectory if lat is not None and lon is not None]

    # Ajouter la trajectoire à la carte
    if valid_locations:
        folium.PolyLine(
            locations=valid_locations,
            color=LIST_COLORS[0], 
            weight=2.5,
            opacity=0.5
        ).add_to(m)

    # Points - Pour chaque points
    for idx, (lat, lon, received_at, shipname) in enumerate(trajectory):
        if lat is None or lon is None:
            continue  # Passer les points incorrects
        
        # Afficher que le premier et dernier point
        opacity = 1 if idx == 0 or idx == len(trajectory) - 1 else 0

        # Convertir la date en string
        received_at_str = received_at.strftime('%Y-%m-%d %H:%M:%S')

        # Ajouter un marqueur pour chaque position avec popup stylisé
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
            color=LIST_COLORS[0],
            fill=True,
            fill_opacity=opacity,
            radius=8
        ).add_to(m)

    # Générer le HTML de la carte
    map_html = m._repr_html_()
    return render_template_string(map_html)


@app.route('/get_heatmap', methods=['GET', 'POST'])
def get_heatmap():
    """
    Récupère les données de la carte de heatmap
    """
    data = request.get_json()

    # Récupérer les données du body
    shiptype = data['shiptype']
    includeStops = data['includeStops']
    date = data.get('date', None)

    # Pointeur qui indique si date => None, servira pour gérérer le timestamp du heatmap
    date_cree = False

    # Si date donnée en parametre
    if not date:
        # derniere 24h
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        stamp = f"ap.received_at BETWEEN '{date}'::timestamp - INTERVAL '24 hours' AND '{date}'::timestamp"
    else:
        # Convertir la date en datetime
        date = convertir_date(date)

        # Stamp pour la date, indique que la date a bien été donné en paramètre
        stamp = f"ap.received_at BETWEEN '{date}'::timestamp AND '{date} 23:59:59'::timestamp"
        date_cree = True

    #Tous les points d'une date
    rows = execute_query(f"""
    SELECT ap.lat, ap.lon, ap.received_at
    FROM ais_positions ap
    JOIN ais_information_vessel aiv ON ap.mmsi = aiv.mmsi
    {f" JOIN shiptype s ON aiv.shiptype = s.id_shiptype" if len(shiptype) > 0 else ""}
    WHERE aiv.shipname NOT LIKE '%TEST%'
    AND {stamp}
    {f" AND s.shiptype = '{shiptype}'" if len(shiptype) > 0 else ""}
    {f" AND ap.speed > 0.5" if includeStops else ""}
    ORDER BY ap.received_at
    """)

    # Initialise un dictionnaire qui récupère le data pour chaque moment d'un jour
    heat_data = {}  

    # Définir un point de départ par défaut si aucune donnée n’est trouvée
    direction = [DEFAULT_LAT,
                 DEFAULT_LON] if len(rows) == 0 else [rows[0][0], rows[0][1]]

    # Créer une carte centrée sur la région spécifiée
    m = folium.Map(location=direction, zoom_start=10)

    if rows:
        # Transformer la date en datetime
        if date_cree:
            date = date + " 00:00:00"
        date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        
        # Si la date n'a pas été donné en paramètre
        if not date_cree:
            # On crée une liste sur les dernier 24h
            time_labels = [
                (date - timedelta(hours=i)).strftime('%A, %B %d, %I %p')
                for i in range(24)
            ]

            # Inverser la liste
            time_labels.reverse()
        else:
            # Sinon on cree sur sur l'intervalle des 24h
            time_labels = [
                (date + timedelta(hours=i)).strftime('%A, %B %d, %I %p')
                for i in range(24)
            ]

        # Créer une liste vide pour chaque heure
        for hour in time_labels:
            heat_data[hour] = []  

        # pour chaque points
        for lat, lon, timestamp in rows:
            # Format the timestamp to "Friday, November 1st, 1 AM" style
            time_label = timestamp.strftime('%A, %B %d, %I %p')
            # Append lat/lon to the correct hour's list
            heat_data[time_label].append([lat, lon])

        # Ajouter la heatmap avec le temps
        HeatMapWithTime(list(heat_data.values()), radius=15,
                        auto_play=True, max_opacity=0.8, index=time_labels).add_to(m)
    else:
        # Pas de points
        HeatMap(heat_data, radius=15, max_opacity=0.8).add_to(m)

    # Générer le code HTML de la carte
    map_html = m._repr_html_()

    # Retourner la carte en tant que chaîne HTML
    return render_template_string(map_html)


@app.route('/get_shiptypes', methods=['GET'])
def get_shiptype():
    """
    Récupère les types de bateaux disponibles
    """
    
    rows = execute_query(SHIPTYPE_QUERY)

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
