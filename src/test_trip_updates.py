import os
import requests
from google.transit import gtfs_realtime_pb2
from dotenv import load_dotenv

# Cargar API KEY
load_dotenv()
API_KEY = os.getenv('NTA_API_KEY').strip()

# URL de Trip Updates
URL_TRIPS = "https://api.nationaltransport.ie/gtfsr/v2/tripupdates"

def scan_trip_updates():
    headers = {
        'x-api-key': API_KEY,
        'Cache-Control': 'no-cache'
    }

    print(f"📡 Escaneando Trip Updates en: {URL_TRIPS}...")

    try:
        response = requests.get(URL_TRIPS, headers=headers)
        
        if response.status_code == 200:
            feed = gtfs_realtime_pb2.FeedMessage()
            feed.ParseFromString(response.content)
            
            # Solo analizaremos los primeros 2 resultados para entender la estructura
            for i, entity in enumerate(feed.entity[:2]):
                print(f"\n--- MUESTRA TRIP UPDATE {i+1} ---")
                print(entity)
                
                if entity.HasField('trip_update'):
                    tu = entity.trip_update
                    print(f"✅ Trip ID: {tu.trip.trip_id}")
                    # Ver si tiene delay en el primer stop_time_update
                    if tu.stop_time_update:
                        first_stop = tu.stop_time_update[0]
                        if first_stop.arrival.delay:
                            print(f"⏱️ Retraso detectado: {first_stop.arrival.delay} segundos")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ Error crítico: {e}")

if __name__ == "__main__":
    scan_trip_updates()