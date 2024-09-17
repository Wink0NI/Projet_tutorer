from flask import Flask, render_template, send_from_directory, request, redirect, url_for, render_template_string
from flask_cors import CORS
import psycopg2
import folium
import os


app = Flask(__name__)
CORS(app)


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
    return render_template("index.html")

@app.route('/get_map')
def get_map():
     # Créer une carte Folium
    m = folium.Map(location=[45.5236, -122.6750], zoom_start=13)
    
    # Générer le HTML de la carte
    map_html = m._repr_html_()

    # Retourner le HTML
    return render_template_string(map_html)

if __name__ == '__main__':
    app.run(debug=True)
