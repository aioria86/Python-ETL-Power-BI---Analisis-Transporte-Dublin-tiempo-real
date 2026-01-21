# Usamos una imagen base de Python ligera
FROM python:3.9-slim

# Creamos una carpeta de trabajo dentro del contenedor
WORKDIR /app

# Copiamos los requerimientos e instalamos las librerías
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código (lo crearemos luego)
COPY . .

# Comando por defecto (deja el contenedor encendido esperando instrucciones)
CMD ["tail", "-f", "/dev/null"]