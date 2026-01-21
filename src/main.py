import os
import requests
import time
import pandas as pd
from datetime import datetime, timedelta
from google.transit import gtfs_realtime_pb2
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Limpieza y carga de claves
nta_key = os.getenv('NTA_API_KEY')
API_KEY = nta_key.strip() if nta_key else None

pbi_url = os.getenv('POWERBI_URL')
POWERBI_URL = pbi_url.strip() if pbi_url else None

URL_VEHICULOS = "https://api.nationaltransport.ie/gtfsr/v2/vehicles"

def guardar_historico_parquet(lote_datos):
    """Guarda los datos en formato Parquet siguiendo estructura de Data Lake (10am-6pm)"""
    ahora = datetime.now()
    
    # --- FILTRO DE HORARIO ACTIVADO (10 AM a 6 PM) ---
    if 10 <= ahora.hour < 18: 
        # 1. Crear ruta de carpetas por fecha (Particionamiento Hive)
        fecha_str = ahora.strftime('%Y-%m-%d')
        ruta_carpeta = f"data/fecha={fecha_str}"
        
        if not os.path.exists(ruta_carpeta):
            os.makedirs(ruta_carpeta)
        
        # 2. Convertir a DataFrame y guardar con compresión snappy (por defecto en pandas)
        df = pd.DataFrame(lote_datos)
        nombre_archivo = ahora.strftime('%H_%M_%S') + ".parquet"
        ruta_completa = os.path.join(ruta_carpeta, nombre_archivo)
        
        try:
            df.to_parquet(ruta_completa, index=False)
            print(f"💾 Histórico guardado: {ruta_completa}")
        except Exception as e:
            print(f"⚠️ No se pudo guardar Parquet: {e}")
    else:
        # Mensaje informativo para cuando estés fuera del rango
        print(f"🌙 Fuera de horario de guardado (Hora actual: {ahora.strftime('%H:%M')}). No se genera archivo Parquet.")

def procesar_flujo():
    # ⏱️ Cronómetro de inicio de ciclo
    inicio_ciclo = time.time()
    
    hora_actual_log = datetime.now().strftime('%H:%M:%S')
    print(f"📡 [{hora_actual_log}] Iniciando extracción NTA...")
    
    headers = {
        'x-api-key': API_KEY,
        'Cache-Control': 'no-cache'
    }

    try:
        response = requests.get(URL_VEHICULOS, headers=headers)
        
        if response.status_code == 200:
            feed = gtfs_realtime_pb2.FeedMessage()
            feed.ParseFromString(response.content)
            
            lote_datos = []
            
            # 🕒 CORRECCIÓN DE ZONA HORARIA (+1h para horario local)
            fecha_ajustada = (datetime.now() + timedelta(hours=1)).isoformat()

            for entity in feed.entity:
                if entity.HasField('vehicle'):
                    v = entity.vehicle
                    lote_datos.append({
                        "bus_id": str(v.vehicle.id),
                        "route_id": str(v.trip.route_id),
                        "latitude": float(v.position.latitude),
                        "longitude": float(v.position.longitude),
                        "timestamp": fecha_ajustada 
                    })

            if lote_datos:
                print(f"📦 Procesados {len(lote_datos)} buses.")
                
                # 1. ENVÍO A STREAMING (POWER BI)
                if POWERBI_URL:
                    inicio_subida = time.time()
                    r = requests.post(POWERBI_URL, json=lote_datos)
                    fin_subida = time.time()
                    
                    if r.status_code == 200:
                        print(f"🚀 ¡Enviado a PBI! ({fin_subida - inicio_subida:.2f}s)")
                        # 2. GUARDADO EN HISTÓRICO (PARQUET)
                        guardar_historico_parquet(lote_datos)
                    else:
                        print(f"⚠️ Error enviando a PBI: {r.status_code}")
            
        else:
            print(f"❌ Error NTA: {response.status_code}")

    except Exception as e:
        print(f"❌ Error crítico: {e}")
    
    # ⏱️ Fin de ciclo
    print(f"⏱️ Ciclo completo en: {time.time() - inicio_ciclo:.2f} segundos.\n")

if __name__ == "__main__":
    print("🟢 SISTEMA HÍBRIDO PROFESIONAL INICIADO")
    print("   -> Streaming: Activo 24/7")
    print("   -> Histórico Parquet: Activo 10:00 a 18:00")
    
    while True:
        procesar_flujo()
        print("⏳ Esperando 20 segundos...")
        time.sleep(20)