from flask import Flask, render_template, request, redirect, url_for
import psycopg2

app = Flask(__name__)

# Configuration de la connexion à la base de données
DATABASE_CONFIG = {
    'host': 'localhost',
    'database': 'Projet_tutorer',
    'user': 'admin',
    'password': 'admin'
}

def get_db_connection():
    conn = psycopg2.connect(**DATABASE_CONFIG)
    return conn

@app.route('/')
def index():
    return 'Bienvenue sur l\'interface Flask pour la base de données AIS'

if __name__ == '__main__':
    app.run(debug=True)