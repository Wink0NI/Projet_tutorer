import pandas as pd

# Chemins des fichiers
file_vessel_info = 'ais_information_vessel_ptutore.csv'
file_positions = 'ais_positions_noumea_ptutore.csv'

# Chargement des fichiers
df_vessel_info = pd.read_csv(file_vessel_info)
df_positions = pd.read_csv(file_positions)

# Affichage des premières lignes de chaque fichier pour analyser la structure
df_vessel_info_head = df_vessel_info.head()
df_positions_head = df_positions.head()

df_vessel_info_head, df_positions_head


# Convertir les colonnes 'received_at' en datetime pour filtrer par jour
df_vessel_info['received_at'] = pd.to_datetime(df_vessel_info['received_at'])
df_positions['received_at'] = pd.to_datetime(df_positions['received_at'])

# Extraire la date uniquement pour regrouper les données par jour
df_vessel_info['date'] = df_vessel_info['received_at'].dt.date
df_positions['date'] = df_positions['received_at'].dt.date

# Trajectoires par navire et par jour dans le premier fichier
trajectories_vessel_info = df_vessel_info.groupby(['mmsi', 'date'])[['lat', 'lon']].apply(lambda x: x.values.tolist()).reset_index(name='trajectory')

# Trajectoires par navire et par jour dans le second fichier
trajectories_positions = df_positions.groupby(['mmsi', 'date'])[['lat', 'lon']].apply(lambda x: x.values.tolist()).reset_index(name='trajectory')

# Afficher quelques exemples de trajectoires pour vérifier
trajectories_vessel_info.head(), trajectories_positions.head()



import matplotlib.pyplot as plt

# Filtrer les trajectoires d'un échantillon de navires sur une date spécifique
sample_date = 209135000
sample_trajectories = trajectories_vessel_info
print( sample_trajectories)

# Trajectoires pour un sous-ensemble de navires
plt.figure(figsize=(10, 8))
for idx, row in sample_trajectories.iterrows():
    trajectory = row['trajectory']
    lats, lons = zip(*trajectory)
    plt.plot(lons, lats, marker='o', label=f"Navire {row['mmsi']}")

plt.title(f"Trajectoires des navires le {sample_date}")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.legend(loc='best')
plt.grid(True)
plt.show()

