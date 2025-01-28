FROM python:3.10-slim

WORKDIR /app

# Crear un directorio temporal escribible
RUN mkdir -p /tmp/pip-cache
ENV TMPDIR=/tmp/pip-cache

# Copiar e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de los archivos
COPY . .

# Comando para ejecutar la aplicación
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
