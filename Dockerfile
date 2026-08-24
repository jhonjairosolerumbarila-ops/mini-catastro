#  Imagen del servicio web (Django + GeoDjango)
#  Incluye las librerías nativas que GeoDjango necesita:
#  GDAL, GEOS y PROJ.

FROM python:3.12-slim

# Evita .pyc y fuerza logs sin buffer (se ven en tiempo real)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Librerías del sistema para GeoDjango + cliente de Postgres
RUN apt-get update && apt-get install -y --no-install-recommends \
        binutils \
        gdal-bin \
        libgdal-dev \
        libgeos-dev \
        libproj-dev \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar dependencias primero para aprovechar la caché de capas
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
