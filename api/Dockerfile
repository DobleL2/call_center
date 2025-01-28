FROM python:3.10-slim

WORKDIR /app

# Crear un directorio temporal escribible
RUN mkdir -p /tmp/pip-cache
ENV TMPDIR=/tmp/pip-cache

RUN apt-get update && apt-get install -y \
    unixodbc \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de los archivos
COPY . .

# Comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
