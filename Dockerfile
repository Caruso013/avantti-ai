# Use Python 3.11 (mais estável)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies first
RUN apt-get update && apt-get install -y \
    gcc \
    nginx \
    supervisor \
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
ENV PORT=8000

# Configurar Nginx como proxy reverso
RUN rm -f /etc/nginx/sites-enabled/default /etc/nginx/conf.d/default.conf || true && \
    mkdir -p /var/log/nginx && \
    printf '%s\n' \
      'server {' \
      '    listen 5000;' \
      '    server_name _;' \
      '' \
      '    client_max_body_size 50m;' \
      '    proxy_read_timeout 300;' \
      '    proxy_connect_timeout 300;' \
      '    proxy_send_timeout 300;' \
      '' \
      '    location / {' \
      '        proxy_pass http://127.0.0.1:3000;' \
      '        proxy_set_header Host $host;' \
      '        proxy_set_header X-Real-IP $remote_addr;' \
      '        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;' \
      '        proxy_set_header X-Forwarded-Proto $scheme;' \
      '        proxy_buffering off;' \
      '    }' \
      '}' \
      > /etc/nginx/conf.d/app.conf

# Configurar supervisor para gerenciar ambos os processos
RUN printf '%s\n' \
      '[supervisord]' \
      'nodaemon=true' \
      'user=root' \
      '' \
      '[program:flask_app]' \
      'command=python -u app.py' \
      'directory=/app' \
      'autostart=true' \
      'autorestart=true' \
      'stdout_logfile=/dev/stdout' \
      'stdout_logfile_maxbytes=0' \
      'stderr_logfile=/dev/stderr' \
      'stderr_logfile_maxbytes=0' \
      '' \
      '[program:nginx]' \
      'command=nginx -g "daemon off;"' \
      'autostart=true' \
      'autorestart=true' \
      'stdout_logfile=/dev/stdout' \
      'stdout_logfile_maxbytes=0' \
      'stderr_logfile=/dev/stderr' \
      'stderr_logfile_maxbytes=0' \
      > /etc/supervisor/conf.d/supervisord.conf

# Expose port
EXPOSE 5000

# Start both services with supervisor
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]