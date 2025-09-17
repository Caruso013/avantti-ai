# Dockerfile ULTRA-SIMPLES para funcionar HOJE
FROM python:3.11-slim

# Diretório de trabalho
WORKDIR /app

# Copia requirements simples primeiro
COPY requirements.simple.txt .

# Instala apenas Flask
RUN pip install --no-cache-dir -r requirements.simple.txt

# Copia apenas o arquivo necessário
COPY app_minimal.py .

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

# Expõe porta 5000
EXPOSE 5000

# Comando simples
CMD ["python", "app_minimal.py"]