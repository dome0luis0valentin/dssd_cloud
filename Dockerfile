# Dockerfile (simple)
FROM python:3.11-slim

# create app dir
WORKDIR /app

# instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copiar código
COPY . .

# exponer (solo para documentación; Render detecta el puerto automáticamente)
EXPOSE 8000

# usa la variable PORT si está presente; si no, 8000 por defecto
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
