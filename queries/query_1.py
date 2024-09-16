# Connexion à la base de données PostgreSQL
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="Projet_tutorer",
    user="admin",
    password="admin"
)
cur = conn.cursor()

cur.execute("SELECT * FROM ais_positions_noumea")

# Récupérer toutes les lignes de la requête
rows = cur.fetchall()

# Afficher les résultats
for row in rows:
    print(row)

cur.close()
conn.close()