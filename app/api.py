import requests

# Replace with your actual API key
API_KEY = 'YOUR_API_KEY'
BASE_URL = 'https://services.marinetraffic.com/api'

# Define the parameters
params = {
    'api_key': API_KEY,
    'lat': -22.0,  # Latitude for New Caledonia
    'lon': 167.0,  # Longitude for New Caledonia
    'distance': 100,  # Distance in km
    'protocol': 'json'  # Specify the format of the response
}

# Fetch vessel positions
def get_vessel_positions():
    endpoint = f'{BASE_URL}/vesseltrack'
    response = requests.get(endpoint, params=params)

    if response.status_code == 200:
        vessels = response.json()
        for vessel in vessels:
            print(f"Vessel ID: {vessel['VesselID']}, "
                  f"Latitude: {vessel['LAT']}, "
                  f"Longitude: {vessel['LON']}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    get_vessel_positions()
