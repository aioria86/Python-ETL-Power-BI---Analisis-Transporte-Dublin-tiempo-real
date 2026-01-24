import pandas as pd
import requests
import os
from datetime import datetime, timedelta

def descargar_clima_ayer():
    # 1. Definir la fecha de ayer automáticamente
    ayer = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    print(f"Iniciando descarga de clima para la fecha: {ayer}")

    # 2. Leer la tabla de dimensiones para obtener las coordenadas
    # Asegúrate de que la ruta sea correcta según tu estructura
    df_dims = pd.read_csv('master_data/Dim_Geografia.csv')
    
    # Filtrar solo las regiones que tienen coordenadas
    regiones = df_dims[df_dims['Lat_Referencia'].notnull()]
    
    resultados_clima = []

    for _, fila in regiones.iterrows():
        ciudad = fila['Ciudad_ID']
        lat = fila['Lat_Referencia']
        lon = fila['Lon_Referencia']
        
        # 3. Llamada a la API de Open-Meteo (Versión Archive para datos históricos)
        url = (f"https://archive-api.open-meteo.com/v1/archive?"
               f"latitude={lat}&longitude={lon}&start_date={ayer}&end_date={ayer}"
               f"&hourly=temperature_2m,precipitation&timezone=Europe%2FLondon")
        
        try:
            response = requests.get(url)
            data = response.json()
            
            # 4. Procesar la respuesta horaria
            df_temp = pd.DataFrame({
                'timestamp': pd.to_datetime(data['hourly']['time']),
                'temperatura': data['hourly']['temperature_2m'],
                'lluvia_mm': data['hourly']['precipitation'],
                'Ciudad_ID': ciudad
            })
            
            resultados_clima.append(df_temp)
            print(f"✔ Datos obtenidos para {ciudad}")
            
        except Exception as e:
            print(f"❌ Error al obtener datos para {ciudad}: {e}")

    # 5. Consolidar y guardar en formato Parquet
    if resultados_clima:
        df_final = pd.concat(resultados_clima)
        
        # Crear carpeta por fecha (formato Hive)
        ruta_clima = f"data_clima/fecha={ayer}"
        os.makedirs(ruta_clima, exist_ok=True)
        
        df_final.to_parquet(f"{ruta_clima}/clima.parquet", index=False)
        print(f"🚀 Proceso completado. Archivo guardado en: {ruta_clima}/clima.parquet")

if __name__ == "__main__":
    descargar_clima_ayer()