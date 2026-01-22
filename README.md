# 🚌 Monitor de Transporte en Tiempo Real - Dublín

Este proyecto es un pipeline de datos híbrido que extrae información en tiempo real de la flota de autobuses de Irlanda, la visualiza en un Dashboard de Power BI y almacena un histórico localmente en formato Parquet.

## 🚀 Características
- **Streaming en tiempo real:** Envío de datos cada 20 segundos a Power BI.
- **Data Lake Local:** Almacenamiento automático en archivos **Parquet** particionados por fecha.
- **Filtro Operativo:** El guardado histórico solo se activa de 10:00 a 18:00 (ajustable en el código).
- **Contenerización:** Ejecución aislada mediante **Docker**.

## 🛠️ Requisitos Previos

1. **API Key de la NTA:**
   - Regístrate en el [Portal de Desarrolladores de la NTA](https://developer.nationaltransport.ie/api-details#api=gtfsr&operation=gtfsr-v2).
   - Suscríbete a la API **GTFS Realtime v2**.
   - Obtén tu `Primary Key`.

2. **Power BI Service:**
   - Cuenta Pro o Premium para usar conjuntos de datos de streaming.

## 📊 Configuración de Power BI (Estructura de Datos)

Para que el reporte reciba la data correctamente, el conjunto de datos de streaming debe tener la siguiente estructura exacta:

1. En Power BI Service: **Nuevo** > **Conjunto de datos de streaming** > **API**.
2. Configura los campos con estos nombres y tipos (sensible a mayúsculas/minúsculas según el código):

| Campo | Tipo de datos | Descripción |
| :--- | :--- | :--- |
| `bus_id` | Texto | Identificador único del vehículo |
| `route_id` | Texto | Identificador de la línea de bus |
| `trip_id` | Texto | ID del viaje específico (nuevo) |
| `start_time` | Texto | Hora programada de salida (nuevo) |
| `direction` | Número | Sentido de la ruta: 0 o 1 (nuevo) |
| `latitude` | Número | GPS Latitud |
| `longitude` | Número | GPS Longitud |
| `timestamp` | Fecha y hora | Momento de la captura |


3. **Análisis de datos históricos:** Activa esta opción para permitir que Power BI cree un informe con "memoria" sobre los datos recibidos.

## ⚙️ Configuración del Proyecto

1. **Variables de Entorno:**
   Crea un archivo `.env` en la raíz (usa `.env.example` como guía):
   ```env
   NTA_API_KEY=tu_clave_aqui
   POWERBI_URL=tu_url_de_insercion_aqui

2. **Ejecución con Docker::**
   Construye y corre el contenedor vinculando el volumen para el histórico:
   
     docker build -t transporte-irlanda .

   
     docker run --env-file .env -v "${PWD}/data:/app/data" transporte-irlanda python src/main.py


## 📂 Almacenamiento Histórico (Parquet)

El script crea automáticamente una estructura de carpetas tipo Data Lake para facilitar la lectura masiva: data/fecha=YYYY-MM-DD/HH_MM_SS.parquet

Esta estructura permite a Power BI Desktop cargar la carpeta completa y reconocer automáticamente la columna de fecha por el nombre de la subcarpeta (Hive Partitioning).
