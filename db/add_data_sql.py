import csv
import psycopg2
import sys
import os

# Ajouter le chemin du dossier parent pour accéder à functions
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from functions.database_query import CREATE_TABLE_INFORMATION, CREATE_TABLE_POSITIONS, CREATE_TABLE_SHIPTYPE, INSERT_INFORMATION, INSERT_POSITION, get_db_connection, close_db_connection
from functions.operations_plugins import str_to_none, str_to_nbr, convert_custom_datetime
from functions.boat_plugins import SHIPTYPES, assign_ship_type_number

# Connexion à la base de données PostgreSQL
conn, cur = get_db_connection()

# Suppression des tables si existante
cur.execute("DROP TABLE IF EXISTS ais_information_vessel")
cur.execute("DROP TABLE IF EXISTS ais_positions")
cur.execute("DROP TABLE IF EXISTS shiptype")

##################################################################################################################################################################

# Création de la table "ais_information_vessel"
cur.execute(CREATE_TABLE_INFORMATION)

# Création de la table "ais_positions"
cur.execute(CREATE_TABLE_POSITIONS)

#table shiptype
cur.execute(CREATE_TABLE_SHIPTYPE)

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

        # Executer la requête d'insertion
        cur.execute(INSERT_INFORMATION, row)
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
    
        cur.execute(INSERT_POSITION, row)
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
        
        # Executer la requête d'insertion
        cur.execute(INSERT_INFORMATION, row)
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

        cur.execute(INSERT_POSITION, row)
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
for id,shiptype in SHIPTYPES.items():
    cur.execute("INSERT INTO shiptype VALUES (%s, %s)", [id, shiptype])
    lines += 1

print(f"SQL: Insertion de {lines} donnée dans la table shiptype terminée...")

# Valider et fermer
conn.commit()

cur.close()
conn.close()





