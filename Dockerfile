# NOVO DOCKERFILE - COM REQUESTS
FROM python:3.11-slim

# Cache buster crítico
ENV CACHE_BUSTER=v20250917_REQUESTS_FIX

WORKDIR /app

# Copia requirements primeiro
COPY requirements.simple.txt .

# Instala dependências incluindo requests
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.simple.txt

# Copia app
COPY app.py .

# Env vars críticas
ENV PYTHONUNBUFFERED=1
ENV PORT=5000

EXPOSE 5000

# Comando com flag verbosa
CMD ["python", "-u", "app.py"]