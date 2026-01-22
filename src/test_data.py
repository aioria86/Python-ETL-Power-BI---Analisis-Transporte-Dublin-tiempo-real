import os
import requests
from google.transit import gtfs_realtime_pb2
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('NTA_API_KEY').strip()
URL_VEHICULOS = "https://api.nationaltransport.ie/gtfsr/v2/vehicles"

headers = {'x-api-key': API_KEY}
response = requests.get(URL_VEHICULOS, headers=headers)

if response.status_code == 200:
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(response.content)
    
    # Analizamos los primeros 5 buses para ver la variedad de datos
    for i in range(5):
        v = feed.entity[i].vehicle
        print(f"\n--- BUS {i+1} (ID: {v.vehicle.id}) ---")
        print(v) # Esto imprime TODO lo que el bus está enviando actualmente
else:
    print("Error al conectar")