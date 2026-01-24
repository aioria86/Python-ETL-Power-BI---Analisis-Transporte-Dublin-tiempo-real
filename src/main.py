import os
import requests
import time
import pandas as pd
from datetime import datetime, timedelta
from google.transit import gtfs_realtime_pb2
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

API_KEY = os.getenv('NTA_API_KEY').strip()
POWERBI_URL = os.getenv('POWERBI_URL').strip() if os.getenv('POWERBI_URL') else None

URL_VEHICULOS = "https://api.nationaltransport.ie/gtfsr/v2/vehicles"
URL_TRIPS = "https://api.nationaltransport.ie/gtfsr/v2/tripupdates"

def guardar_historico_parquet(lote_datos):
    """Guarda los datos enriquecidos en formato Parquet (10am-6pm)"""
    ahora = datetime.now()
    if 9 <= ahora.hour < 18: 
        fecha_str = ahora.strftime('%Y-%m-%d')
        ruta_carpeta = f"data/fecha={fecha_str}"
        if not os.path.exists(ruta_carpeta):
            os.makedirs(ruta_carpeta)
        
        df = pd.DataFrame(lote_datos)
        nombre_archivo = ahora.strftime('%H_%M_%S') + ".parquet"
        ruta_completa = os.path.join(ruta_carpeta, nombre_archivo)
        
        try:
            df.to_parquet(ruta_completa, index=False)
            print(f"💾 Histórico guardado: {ruta_completa}")
        except Exception as e:
            print(f"⚠️ No se pudo guardar Parquet: {e}")

def obtener_mapa_retrasos():
    """Descarga los Trip Updates y crea un diccionario por trip_id"""
    mapa = {}
    headers = {'x-api-key': API_KEY, 'Cache-Control': 'no-cache'}
    try:
        r = requests.get(URL_TRIPS, headers=headers)
        if r.status_code == 200:
            feed = gtfs_realtime_pb2.FeedMessage()
            feed.ParseFromString(r.content)
            for entity in feed.entity:
                if entity.HasField('trip_update'):
                    tu = entity.trip_update
                    delay_val = 0
                    stop_val = "N/A"
                    if tu.stop_time_update:
                        delay_val = tu.stop_time_update[0].arrival.delay
                        stop_val = tu.stop_time_update[0].stop_id
                    
                    mapa[tu.trip.trip_id] = {
                        "delay_sec": delay_val,
                        "stop_id": stop_val,
                        "rel": str(tu.trip.schedule_relationship)
                    }
    except Exception as e:
        print(f"⚠️ Error obteniendo retrasos: {e}")
    return mapa

def procesar_flujo():
    inicio_ciclo = time.time()
    hora_actual_log = datetime.now().strftime('%H:%M:%S')
    print(f"📡 [{hora_actual_log}] Iniciando extracción enriquecida...")
    
    # 1. Obtenemos los retrasos primero
    mapa_retrasos = obtener_mapa_retrasos()
    
    # --- PAUSA TÁCTICA DE SEGURIDAD (Expert Insight) ---
    # Esperamos 2 segundos entre llamadas para evitar el Error 429 de la NTA
    time.sleep(2)
    
    headers = {'x-api-key': API_KEY, 'Cache-Control': 'no-cache'}

    try:
        response = requests.get(URL_VEHICULOS, headers=headers)
        if response.status_code == 200:
            feed = gtfs_realtime_pb2.FeedMessage()
            feed.ParseFromString(response.content)
            
            lote_enriquecido = []
            fecha_ajustada = (datetime.now() + timedelta(hours=1)).isoformat()

            for entity in feed.entity:
                if entity.HasField('vehicle'):
                    v = entity.vehicle
                    t_id = v.trip.trip_id
                    
                    # 2. CRUCE DE DATOS
                    info_trip = mapa_retrasos.get(t_id, {
                        "delay_sec": 0, 
                        "stop_id": "Desconocida", 
                        "rel": "UNKNOWN"
                    })

                    # 3. CÁLCULOS
                    d_sec = info_trip['delay_sec']
                    d_min = round(d_sec / 60, 2)
                    
                    if d_min > 15: status = "Critico"
                    elif d_min > 5: status = "Retrasado"
                    elif d_min < -2: status = "Adelantado"
                    else: status = "A tiempo"

                    lote_enriquecido.append({
                        "bus_id": str(v.vehicle.id),
                        "route_id": str(v.trip.route_id),
                        "trip_id": str(t_id),
                        "latitude": float(v.position.latitude),
                        "longitude": float(v.position.longitude),
                        "delay_sec": int(d_sec),
                        "delay_min": float(d_min),
                        "stop_id": str(info_trip['stop_id']),
                        "schedule_relationship": str(info_trip['rel']),
                        "punctuality_status": status,
                        "direction": str(v.trip.direction_id),
                        "timestamp": fecha_ajustada 
                    })

            if lote_enriquecido:
                print(f"📦 Procesados {len(lote_enriquecido)} buses enriquecidos.")
                
                # 4. GUARDADO LOCAL
                guardar_historico_parquet(lote_enriquecido)

                # 5. ENVÍO A POWER BI (Bloques optimizados de 25)
                if POWERBI_URL:
                    tamano_bloque = 25 
                    print(f"🚀 Enviando a PBI en mini-bloques...")
                    try:
                        exito_total = True
                        for i in range(0, len(lote_enriquecido), tamano_bloque):
                            bloque = lote_enriquecido[i:i + tamano_bloque]
                            r = requests.post(POWERBI_URL, json=bloque)
                            
                            if r.status_code != 200:
                                print(f"⚠️ Error bloque {i}: {r.status_code} - {r.text}")
                                exito_total = False
                                break
                            
                            # Pausa entre bloques para fluidez de la API
                            time.sleep(0.1)

                        if exito_total:
                            print(f"✅ Súper-Main enviado con éxito.")
                    except Exception as e:
                        print(f"⚠️ Error conexión PBI: {e}")
            
        else:
            print(f"❌ Error NTA: {response.status_code}")

    except Exception as e:
        print(f"❌ Error crítico: {e}")
    
    print(f"⏱️ Ciclo completo: {time.time() - inicio_ciclo:.2f}s\n")

if __name__ == "__main__":
    print("🟢 SISTEMA ENRIQUECIDO INICIADO (Posiciones + Retrasos)")
    while True:
        procesar_flujo()
        # Tiempo aumentado a 60s para estabilidad total
        print(f"⏳ Esperando 60 segundos para evitar saturación...")
        time.sleep(60)