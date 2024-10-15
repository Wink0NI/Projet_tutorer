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

# Suppression des tables si existante
cur.execute("DROP TABLE IF EXISTS ais_information_vessel")
cur.execute("DROP TABLE IF EXISTS ais_positions")
cur.execute("DROP TABLE IF EXISTS shiptype")

##################################################################################################################################################################

# Création de la table "ais_information_vessel"
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


#table shiptype
cur.execute("""
CREATE TABLE IF NOT EXISTS shiptype (
    id_shiptype INT NOT NULL PRIMARY KEY,
    shiptype VARCHAR(255) NOT NULL
);
""")

# Commit les créations des tables
conn.commit()

##################################################################################################################################################################

lines = 0

# Insérer les données du fichier ais_information_vessel_ptutore.csv
with open('db/ais_information_vessel_ptutore.csv', 'r') as f:
    reader = csv.reader(f, delimiter=";")

    print("SQL: Insertion de données de ais_information_vessel_ptutore en cours...")

    # Sauter la ligne d'en-tête
    header = next(reader)
    print("En-tête : ", header)

    # Lire et traiter chaque ligne
    for row in reader:
        # Transformer les données
        row = [str_to_none(cell) for cell in row]  # Utilisation de la méthode str_to_none
        row = [str_to_nbr(cell) for cell in row]   # Utilisation de la méthode str_to_nbr
        if row[3] is not None:
            row[3] = convert_custom_datetime(row[3])   # Utilisation de la méthode convert_custom_datetime
        
        if row[14] is not None:
            row[14] = convert_custom_datetime(row[14])   # Utilisation de la méthode convert_custom_datetime

        # Ajout des données csv transformé à la table sql
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
        # Executer la requête d'insertion
        cur.execute(insert_query, row)
        lines += 1

print(f"SQL: Insertion de {lines} données de ais_information_vessel_ptutore terminée...")

# Valider et fermer
conn.commit()

##################################################################################################################################################################

lines = 0

# Insérer les données du fichier ais_positions_noumea_ptutore.csv
with open('db/ais_positions_noumea_ptutore.csv', 'r') as f:
    reader = csv.reader(f, delimiter=";")

    print("SQL: Insertion de données de ais_positions_noumea_ptutore en cours...")
    # Sauter la ligne d'en-tête
    header = next(reader)
    print("En-tête : ", header)

    # Lire et traiter chaque ligne
    for row in reader:
        # Transformer les données
        row = [str_to_none(cell) for cell in row]  # Utilisation de la méthode str_to_none
        row = [str_to_nbr(cell) for cell in row]   # Utilisation de la méthode str_to_nbr
        if row[1] is not None:
            row[1] = convert_custom_datetime(row[1])   # utilisation de la méthode convert_custom_datetime
    
        # Ajout des données csv transformé à la table sql
        insert_query = """
            INSERT INTO ais_positions (
                mmsi, received_at, station_id, msg_id, status, turn, speed, lat, lon, course, heading, geom
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) 
            """

        cur.execute(insert_query, row)
        lines += 1

print(f"SQL: Insertion de {lines} donnée dans la table ais_positions terminée...")

# Valider et fermer
conn.commit()
##################################################################################################################################################################

lines = 0

# Insérer les données du fichier ais_vessel_aus_nz.csv
with open('db/ais_vessel_aus_nz.csv', 'r') as f:
    reader = csv.reader(f, delimiter=",")

    print("SQL: Insertion de données de ais_vessel en cours...")

    # Sauter la ligne d'en-tête
    header = next(reader)
    print("En-tête : ", header)

    # Lire et traiter chaque ligne
    for row in reader:
        # Transformer les données
        row = [str_to_none(cell) for cell in row]  # Utilisation de la méthode str_to_none
        row = [str_to_nbr(cell) for cell in row]   # Utilisation de la méthode str_to_nbr
        if row[3] is not None:
            row[3] = convert_custom_datetime(row[3])  # Utilisation de la méthode convert_custom_datetime
        
        if row[14] is not None:
            row[14] = convert_custom_datetime(row[14])   # Utilisation de la méthode convert_custom_datetime
        
        # Ajout des données csv transformé à la table sql
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
        # Executer la requête d'insertion
        cur.execute(insert_query, row)
        lines += 1

print(f"SQL: Insertion de {lines} données de ais_vessel terminée...")

# Valider et fermer
conn.commit()

##################################################################################################################################################################

lines = 0

# Insérer les données du fichier ais_position_aus_nz.csv
with open('db/ais_position_aus_nz.csv', 'r') as f:
    reader = csv.reader(f, delimiter=",")

    print("SQL: Insertion de données de ais_position_aus_nz en cours...")
    # Sauter la ligne d'en-tête
    header = next(reader)
    print("En-tête : ", header)

    # Lire et traiter chaque ligne
    for row in reader:
        # Transformer les données
        row = [str_to_none(cell) for cell in row]  # Utilisation de la méthode str_to_none
        row = [str_to_nbr(cell) for cell in row]   # Utilisation de la méthode str_to_nbr
        if row[1] is not None:
            row[1] = convert_custom_datetime(row[1])   # Utilisation de la méthode convert_custom_datetime
        
        # Ajout des données csv transformé à la table sql
        insert_query = """
            INSERT INTO ais_positions (
                mmsi, received_at, station_id, msg_id, status, turn, speed, lat, lon, course, heading, geom
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) 
            """

        cur.execute(insert_query, row)
        lines += 1
print(f"SQL: Insertion de {lines} donnée dans la table ais_position terminée...")


lines = 0

with open('db/shiptype.csv', 'r') as f:
    reader = csv.reader(f, delimiter=";")

    print(f"SQL: Injection de  donnée shiptype dans la table ais_position en cours...")

    

    for line in reader:
        line = [str_to_none(cell) for cell in line]  # Utilisation de la méthode str_to_none
        line = [str_to_nbr(cell) for cell in line]
        cur.execute("UPDATE ais_information_vessel SET shiptype = %s WHERE mmsi = %s", [assign_ship_type_number(line[1]),  line[0]])
        lines += 1

print(f"SQL: Injection de {lines} donnée shiptype dans la table ais_position terminée...")


lines = 0
print(f"SQL: Insertion de  donnée dans la table shiptype...")
for id,shiptype in ship_types.items():
    cur.execute("INSERT INTO shiptype VALUES (%s, %s)", [id, shiptype])
    lines += 1

print(f"SQL: Insertion de {lines} donnée dans la table shiptype terminée...")

# Valider et fermer
conn.commit()

cur.close()
conn.close()





