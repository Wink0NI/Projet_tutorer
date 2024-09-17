from flask import Flask, render_template, send_from_directory, request, redirect, url_for, render_template_string, jsonify
from flask_cors import CORS
import psycopg2
import folium
import datetime

from rdp import rdp



# Convert RGBA colors to HEX format
list_colors = ['red', 'gray', 'green', 'darkgreen', 'darkpurple', 'lightblue', 'black', 'blue', 'lightgreen', 'darkred', 'pink', 'cadetblue', 'darkblue', 'white', 'lightgray', 'orange', 'purple', 'beige']


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

    # Exécuter la requête SQL pour obtenir les positions du bateau le 20 avril 2024
    cur.execute(f"""
        SELECT apn.lat, apn.lon, apn.received_at, shipname, aiv.mmsi
        FROM ais_positions_noumea apn
        JOIN ais_information_vessel aiv ON apn.mmsi = aiv.mmsi
        WHERE apn.received_at::date = '{date}' {f" AND apn.mmsi = {mmsi}" if len(mmsi) > 0 else ""} {" AND apn.speed > 0.5" if not include_stops else ""}
        ORDER BY apn.received_at
    """)

    # Récupérer toutes les lignes de la requête
    rows = cur.fetchall()

    # Définir le point de départ du bateau
    direction = [-22.2711, 166.4380] if len(rows) == 0 else [rows[0][0], rows[0][1]]

    # Créer une carte Folium de noumea
    m = folium.Map(location=direction, zoom_start=15)

    # Fermer la connexion à la base de données
    cur.close()
    conn.close()


    shipname_color = {}
        

    

    # Ajouter une ligne pour représenter le trajet du bateau
    trajectory = {}
    i = 0
    for row in rows:
        lat, lon, received_at, shipname, current_mmsi = row

        if shipname not in shipname_color:
            try:
                shipname_color[shipname] = list_colors[i]
            except:
                i = 0

            trajectory[shipname] = []
            shipname_color[shipname] = list_colors[i]
            i+=1


        trajectory[shipname].append((lat, lon))
        # Convertir datetime en chaîne de caractères
        received_at_str = received_at.strftime('%Y-%m-%d %H:%M:%S')
        # Ajouter un marqueur pour chaque position avec popup stylisé
        folium.Marker(
            location=[lat, lon],
            popup=f"""
                    <div style="width: 200px; white-space: nowrap;">
                        <b>MMSI:</b> {current_mmsi}</br>
                        <b>Nom:</b> {shipname}</br>
                        <b>Heure:</b> {received_at_str}<br>
                        <b>Latitude:</b> {lat}<br>
                        <b>Longitude:</b> {lon}
                    </div>
                """,
            icon=folium.Icon(color=shipname_color[shipname], icon='ship')
        ).add_to(m)

    for shipname in trajectory.keys():
        # Ajouter une ligne pour le trajet
        folium.PolyLine(
            locations=rdp(trajectory[shipname], epsilon=0.001),
            color=shipname_color[shipname],
            weight=2.5,
            opacity=0.8
        ).add_to(m)

    # Générer le HTML de la carte
    map_html = m._repr_html_()

    # Retourner le HTML
    return render_template_string(map_html)


if __name__ == '__main__':
    app.run(debug=True)
