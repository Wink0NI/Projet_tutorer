import csv
import psycopg2
import sys
import os

# Ajouter le chemin du dossier parent pour accéder à functions
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from functions.edit_str import *


# Connexion à la base de données PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    database="Projet_tutorer",
    user="admin",
    password="admin"
)

# Créer un curseur
cur = conn.cursor()

# Créer les tables
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
    shiptype VARCHAR(255),
    to_port INT,
    to_bow INT,
    to_stern INT,
    to_starboard INT,
    eta TIMESTAMP,
    draught FLOAT,
    destination VARCHAR(255),
    status VARCHAR(255),
    turn FLOAT,
    speed FLOAT,
    lat FLOAT,
    lon FLOAT,
    course FLOAT,
    heading FLOAT,
    aid_type VARCHAR(50),
    alt FLOAT,
    count INT,
    msg_types VARCHAR(255),
    channels VARCHAR(255)
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS ais_positions_noumea (
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
    geom VARCHAR(255), 
    PRIMARY KEY (mmsi, received_at)
);
""")


# Insérer les données du fichier ais_information_vessel_ptutore.csv
with open('db/ais_information_vessel_ptutore.csv', 'r') as f:
    reader = csv.reader(f, delimiter=";")

    # Sauter la ligne d'en-tête
    header = next(reader)
    print("En-tête : ", header)

    # Lire et traiter chaque ligne
    for row in reader:
        # Transformer les données
        row = [str_to_none(cell) for cell in row]  # Utilisation de str_to_none
        row = [str_to_nbr(cell) for cell in row]   # Utilisation de str_to_nbr

        # TODO : Adapter la requête d'insertion aux colonnes de la table
        insert_query = """
        INSERT INTO ais_information_vessel (col1, col2, col3, ...) VALUES (%s, %s, %s, ...)
        """
        cur.execute(insert_query, row)

# Insérer les données du fichier ais_positions_noumea_ptutore.csv
with open('db/ais_positions_noumea_ptutore.csv', 'r') as f:
    reader = csv.reader(f, delimiter=";")

    # Sauter la ligne d'en-tête
    header = next(reader)
    print("En-tête : ", header)

    # Lire et traiter chaque ligne
    for row in reader:
        # Transformer les données
        row = [str_to_none(cell) for cell in row]  # Utilisation de str_to_none
        row = [str_to_nbr(cell) for cell in row]   # Utilisation de str_to_nbr

        # TODO : Adapter la requête d'insertion aux colonnes de la table
        insert_query = """
        INSERT INTO ais_positions_noumea (col1, col2, col3, ...) VALUES (%s, %s, %s, ...)
        """
        cur.execute(insert_query, row)


# Valider et fermer
conn.commit()
cur.close()
conn.close()
