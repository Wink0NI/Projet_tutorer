import psycopg2
import folium
from datetime import datetime

# Connexion à la base de données PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    database="Projet_tutorer",
    user="admin",
    password="admin"
)
cur = conn.cursor()
# Exécuter la requête SQL pour obtenir les positions du bateau le 20 avril 2024
cur.execute(f"""
    SELECT apn.lat, apn.lon, apn.received_at, shipname
    FROM ais_positions_noumea apn
    JOIN ais_information_vessel aiv ON apn.mmsi = aiv.mmsi
    WHERE apn.mmsi = 209591000
    AND apn.speed > 0.5
    AND apn.received_at::date = '2024-03-14'
    ORDER BY apn.received_at
""")

# Récupérer toutes les lignes de la requête
rows = cur.fetchall()

# Fermer la connexion à la base de données
cur.close()
conn.close()

# Créer une carte centrée sur la première position du bateau
if rows:
    first_position = rows[0]
    carte = folium.Map(location=[first_position[0], first_position[1]], zoom_start=12)

    # Ajouter une ligne pour représenter le trajet du bateau
    trajectory = []
    for row in rows:
        lat, lon, received_at, shipname = row
        trajectory.append((lat, lon))
        # Convertir datetime en chaîne de caractères
        received_at_str = received_at.strftime('%Y-%m-%d %H:%M:%S')
        # Ajouter un marqueur pour chaque position avec popup stylisé
        folium.Marker(
            location=[lat, lon],
            popup=f"""
                <div style="width: 200px; white-space: nowrap;">
                    <b>Nom:</b> {shipname}</br>
                    <b>Heure:</b> {received_at_str}<br>
                    <b>Latitude:</b> {lat}<br>
                    <b>Longitude:</b> {lon}
                </div>
            """,
            icon=folium.Icon(color='blue', icon='ship')
        ).add_to(carte)

    # Ajouter une ligne pour le trajet
    folium.PolyLine(
        locations=trajectory,
        color='blue',
        weight=2.5,
        opacity=0.8
    ).add_to(carte)

    # Afficher la carte
    carte.save('trajet_bateau.html')  # Sauvegarder en HTML pour l'afficher dans un navigateur
else:
    print("Aucune donnée disponible pour le bateau avec MMSI 209135000 le 20 avril 2024.")
