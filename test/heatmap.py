import folium
from folium.plugins import HeatMap

# Sample data: [(latitude, longitude, frequency)]
# Here, 'frequency' refers to the traffic frequency or intensity at that location.
traffic_data = [
    (37.7749, -122.4194, 100),  # San Francisco, high frequency
    (34.0522, -118.2437, 80),   # Los Angeles, moderate frequency
    (40.7128, -74.0060, 50),    # New York, lower frequency
    (41.8781, -87.6298, 20),    # Chicago, very low frequency
]

# Center the map on an average location (for example, San Francisco in this case)
map_center = [37.7749, -122.4194]

# Create a folium map centered around the map_center
traffic_map = folium.Map(location=map_center, zoom_start=5)

# Prepare data for heatmap (latitude, longitude, frequency converted to a list)
heat_data = [[data[0], data[1], data[2]] for data in traffic_data]

# Add heatmap to the map
HeatMap(heat_data, min_opacity=0.5, max_val=100, radius=20, blur=15, 
        gradient={0.4: 'blue', 0.65: 'lime', 1: 'red'}).add_to(traffic_map)

# Save or display the map
traffic_map.save("traffic_heatmap.html")

# Optionally, you can display the map in a Jupyter notebook using the following line:
# traffic_map
