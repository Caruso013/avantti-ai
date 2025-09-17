# NOVO DOCKERFILE - FORÇA REBUILD TOTAL v4
FROM python:3.11-slim

# Cache buster crítico
ENV CACHE_BUSTER=v20250917_FINAL_FIX

WORKDIR /app

# Copia requirements
COPY requirements.simple.txt requirements.txt

# Força reinstalação
RUN pip install --no-cache-dir --force-reinstall flask

# Copia app
COPY app.py .

# Env vars críticas
ENV PYTHONUNBUFFERED=1
ENV PORT=5000

EXPOSE 5000

# Comando com flag verbosa
CMD ["python", "-u", "app.py"]