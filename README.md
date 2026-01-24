# 🚌 Monitor de Transporte en Tiempo Real - Irlanda

Este proyecto es un pipeline de datos híbrido que extrae información en tiempo real de la flota de autobuses de Irlanda, la visualiza en un Dashboard de Power BI, la enriquece con datos meteorológicos históricos y almacena todo localmente en formato Parquet.

## 🚀 Características
- **Streaming en tiempo real:** Envío de datos cada 20 segundos a Power BI.
- **Data Lake Local:** Almacenamiento automático en archivos **Parquet** particionados por fecha.
- **Enriquecimiento Climático:** Script independiente para capturar temperatura y lluvia (Open-Meteo API) por región.
- **Filtro Operativo:** El guardado histórico de buses se activa de 10:00 a 18:00 (ajustable en el código).
- **Contenerización:** Ejecución aislada mediante **Docker**.
- **Modelo Relacional:** Arquitectura de estrella avanzada con correlación entre transporte y clima.

## 🛠️ Requisitos Previos

1. **API Key de la NTA:**
   - Regístrate en el [Portal de Desarrolladores de la NTA](https://developer.nationaltransport.ie/api-details#api=gtfsr&operation=gtfsr-v2).
   - Suscríbete a la API **GTFS Realtime v2**.
   - Obtén tu `Primary Key`.

2. **Power BI Service:**
   - Cuenta Pro o Premium para usar conjuntos de datos de streaming.

## 📊 Configuración de Power BI (Estructura de Datos)

El conjunto de datos de streaming debe tener la siguiente estructura exacta:

| Campo | Tipo de datos | Descripción |
| :--- | :--- | :--- |
| `bus_id` | Texto | Identificador único del vehículo |
| `route_id` | Texto | Identificador de la línea de bus |
| `trip_id` | Texto | ID del viaje específico |
| `start_time` | Texto | Hora programada de salida |
| `direction` | Número | Sentido de la ruta: 0 o 1 |
| `latitude` | Número | GPS Latitud |
| `longitude` | Número | GPS Longitud |
| `timestamp` | Fecha y hora | Momento de la captura |

## 🏗️ Modelo de Datos y Dimensiones

Se ha implementado un esquema en estrella para optimizar el análisis histórico en Power BI Desktop:

- **Fact_Monitoreo_Buses:** Datos históricos de la flota recolectados por el script principal.
- **Fact_Clima:** Datos de temperatura y precipitaciones (mm) por hora y región.
- **Dim_Geografia:** Cargada desde `master_data/Dim_Geografia.csv`. Clasifica la flota en regiones y provee las coordenadas para la obtención del clima.
- **Jerarquía Temporal:** Normalización de horas para cruzar el estado de los buses con la intensidad de la lluvia en el gráfico de correlación.

## ⚙️ Configuración del Proyecto

1. **Variables de Entorno:**
   Crea un archivo `.env` en la raíz:
   ```env
   NTA_API_KEY=tu_clave_aqui
   POWERBI_URL=tu_url_de_insercion_aqui

2. **Ejecución con Docker::**
   Construye y corre el contenedor vinculando el volumen para el histórico:

**Ejecución con Docker: Construye la imagen:**
     docker build -t transporte-irlanda .

**Captura de buses (Tiempo real):**
     docker run --env-file .env -v "${PWD}/data:/app/data" transporte-irlanda python src/main.py

**Captura de clima (Histórico D-1):**
     docker run --rm -v "${PWD}:/app" transporte-irlanda python src/clima.py


## 📂 Almacenamiento Histórico (Parquet)

El script crea automáticamente una estructura de carpetas tipo Data Lake para facilitar la lectura masiva: data/fecha=YYYY-MM-DD/HH_MM_SS.parquet

**Buses:** data/fecha=YYYY-MM-DD/HH_MM_SS.parquet

**Clima:** data_clima/fecha=YYYY-MM-DD/clima.parquet

Esta estructura permite a Power BI Desktop cargar la carpeta completa y reconocer automáticamente la columna de fecha por el nombre de la subcarpeta (Hive Partitioning).
