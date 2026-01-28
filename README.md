# 🚌 Sistema de Inteligencia de Transporte - Irlanda (NTA)

Este proyecto es un ecosistema de datos de alto rendimiento que integra telemetría en tiempo real (GTFS-R) con la estructura oficial de horarios y rutas (GTFS Static) de la National Transport Authority de Irlanda. El pipeline automatiza la captura, el enriquecimiento climático y el almacenamiento en un Data Lake local para análisis avanzado en Power BI.

## 🚀 Características y Capacidades
- **Streaming Híbrido:** Captura de datos cada 20 segundos y envío a Power BI Service para monitoreo "Live".
- **Integración GTFS Pro:** Uso de archivos maestros (`agency`, `routes`, `trips`, `stops`) para normalizar la telemetría.
- **Data Lake con Hive Partitioning:** Almacenamiento en archivos **Parquet** particionados por fecha para optimizar lecturas masivas.
- **Correlación Meteorológica:** Integración con Open-Meteo API para cruzar retrasos de flota con intensidad de lluvia (mm/h).
- **Modelo Relacional 2.0:** Esquema en estrella puro con relaciones unidireccionales de integridad referencial.

## 🛠️ Requisitos e Infraestructura

1. **Datos Maestros (GTFS Static):**
   - Descarga los archivos `.txt` oficiales de la [NTA Developer Portal](https://developer.nationaltransport.ie/api-details#api=gtfsr&operation=gtfsr-v2).
   - Estos archivos (`routes`, `agency`, `trips`, `calendar`, `stops`) son la base de las Dimensiones del modelo.

2. **API Key de la NTA:**
   - Suscríbete a la API **GTFS Realtime v2** para obtener tu `Primary Key`.

3. **Power BI Desktop & Service:**
   - Modelo configurado para manejar conjuntos de datos de streaming y almacenamiento local histórico.

## 📊 Arquitectura del Modelo de Datos (Esquema en Estrella)

El modelo en Power BI ha sido optimizado para eliminar redundancias y permitir análisis de causa-efecto:

### Tablas de Hechos (Facts)
- **Fact_Monitoreo_Buses:** Telemetría GPS histórica y estado de puntualidad (delay_min).
- **Fact_Clima:** Histórico de precipitaciones y temperatura por hora y región.

### Dimensiones Maestras (GTFS Based)
- **Dim_GTFS_Routes:** Nombres reales de rutas (ej. "L12: Ballywaltrim - Bray").
- **Dim_GTFS_Agency:** Operadores de transporte (Dublin Bus, Go-Ahead, Irish Rail).
- **Dim_GTFS_Trips:** Relación de viajes programados vs. ejecutados.
- **Dim_GTFS_Stops:** Coordenadas de paradas oficiales para análisis geográfico.
- **Dim_Calendario_Universal:** Dimensión temporal única para sincronización de hechos.
- **Dim_Operativa_Dias (Calendar):** Reglas de servicio por service_id (L-D).



## 🏗️ Estructura del Data Lake (Parquet)

El sistema utiliza una estructura de carpetas optimizada para Power BI (Hive Partitioning), permitiendo cargar años de datos en segundos:

```text
data/
 └── fecha=YYYY-MM-DD/
      └── HH_MM_SS_buses.parquet
data_clima/
 └── fecha=YYYY-MM-DD/
      └── clima_regional.parquet
```

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




## Nota Operativa:

Los datos de buses se recolectan preferentemente en la ventana crítica de 10:00 a 18:00 para optimizar el almacenamiento del Data Lake.
