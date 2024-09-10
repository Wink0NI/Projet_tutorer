import psycopg2

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

import csv

convert_null = lambda x: None if x == "NULL" else x
convert_int = lambda x: None if x == "NULL" else int(x)
convert_float = lambda x: None if x == "NULL" else float(x)

# Ouvrir le fichier CSV
with open('db/ais_information_vessel_ptutore.csv', 'r') as f:
    reader = csv.reader(f)
    
    # Sauter la ligne d'en-tête
    header = next(reader)
    
    # Afficher la ligne d'en-tête
    print("En-tête : ", header)
    
    # Lire et afficher chaque ligne du fichier CSV
    for row in reader:
        print(row[0].split(";"))



# Importer le fichier CSV pour la table ais_positions_noumea
with open('db/ais_positions_noumea_ptutore.csv', 'r') as f:

    reader = csv.reader(f)
    
    # Sauter la ligne d'en-tête
    header = next(reader)
    
    # Afficher la ligne d'en-tête
    print("En-tête : ", header)
    
    # Lire et afficher chaque ligne du fichier CSV
    for row in reader:
        print(row[0].split(";"))

# Valider et fermer
conn.commit()
cur.close()
conn.close()
