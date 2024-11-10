import psycopg2
from dotenv import load_dotenv
import os

# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

# informations bdd
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_DATABASE'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD')
}

# Creation table ais_information_vessel
CREATE_TABLE_INFORMATION = """
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
    """

# Creation table ais_positions
CREATE_TABLE_POSITIONS = """
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
    """

# Creation table shiptype
CREATE_TABLE_SHIPTYPE = """
    CREATE TABLE IF NOT EXISTS shiptype (
        id_shiptype INT NOT NULL PRIMARY KEY,
        shiptype VARCHAR(255) NOT NULL
    );
    """

# requete info mmsi
MMSI_INFO_QUERY = """
        SELECT mmsi, shipname, received_at, lat, lon, speed 
        FROM ais_information_vessel 
        WHERE mmsi = %s;
    """

# requete  shiptype
SHIPTYPE_QUERY = """
        SELECT DISTINCT s.shiptype
        FROM shiptype s
        JOIN ais_information_vessel aiv ON s.id_shiptype = aiv.shiptype
    """

# requete  ais_information_vessel
INSERT_INFORMATION = """
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

# requete  ais_positions
INSERT_POSITION = """
        INSERT INTO ais_positions (
            mmsi, received_at, station_id, msg_id, status, turn, speed, lat, lon, course, heading, geom
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        ) 
        """
# requete  ais_information_vessel pour voir si le mmsi existe, recupere le point le plus recent
SELECT_MMSI = """
        SELECT mmsi FROM ais_information_vessel WHERE mmsi = %s
        """
                   
def get_db_connection():
    """
    Connexion à la base de données PostgreSQL
    
     :return: conn: connexion à la base de données
    """
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cur = conn.cursor()
    return conn, cur

def close_db_connection(conn, cur):
    """
    Fermeture de la connexion à la base de données PostgreSQL
    
     :param conn: connexion à la base de données
     :param cur: curseur de la connexion
    """
    cur.close()
    conn.close()


def execute_query(query, variables=[], one=False):
    """
    Exécuter une requête SQL
    
     :param query: requête SQL à exécuter
     :param variables: variables à passer à la requête
     :param one: Permettre de retourner une ou plusieurs lignes. True => 1 ligne
     :return: rows: résultats de la requête
    """
    conn, cur = get_db_connection()

    # Exécuter la requête SQL pour obtenir les positions du bateau
    if variables:
        cur.execute(query, variables)
    else:
        cur.execute(query)

    # retourner les lignes en fonction si on souhaite retourner une ou plusieurs lignes
    rows = cur.fetchone() if one else cur.fetchall()

    close_db_connection(conn, cur)

    return rows