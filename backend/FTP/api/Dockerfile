FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema para pillow-heif
RUN apt-get update && apt-get install -y \
    libheif-dev \
    libheif1 \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Reinstalar pillow-heif para asegurar que se compile con libheif
RUN pip uninstall -y pillow-heif && pip install --no-cache-dir pillow-heif==0.18.0

# Copiar código de la aplicación
COPY app/ ./app/

# Exponer puerto
EXPOSE 8007

# Comando para iniciar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8007", "--reload"]
