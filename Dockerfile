# Use Python 3.11 (mais estável)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies first
RUN apt-get update && apt-get install -y \
    gcc \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Configurar Nginx como proxy reverso ouvindo na porta 8080 e encaminhando para a app na 8000
RUN rm -f /etc/nginx/sites-enabled/default /etc/nginx/conf.d/default.conf || true && \
    mkdir -p /var/log/nginx && \
    printf '%s\n' \
      'server {' \
      '    listen 8080;  # Porta externa' \
      '    server_name _;' \
      '' \
      '    # Ajuste conforme necessário para limites/headers' \
      '    client_max_body_size 50m;' \
      '' \
      '    location / {' \
      '        proxy_pass http://127.0.0.1:8000;' \
      '        proxy_set_header Host $host;' \
      '        proxy_set_header X-Real-IP $remote_addr;' \
      '        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;' \
      '        proxy_set_header X-Forwarded-Proto $scheme;' \
      '        proxy_read_timeout 300;' \
      '    }' \
      '}' \
      > /etc/nginx/conf.d/app.conf

# Expose port
EXPOSE 8080

# Simple startup command
# Inicia a app Python na 8000 e o Nginx em primeiro plano na 8080
CMD bash -lc "python -u app.py & nginx -g 'daemon off;'"