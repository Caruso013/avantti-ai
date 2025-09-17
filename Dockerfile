FROM python:3.13-slim

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos de dependências
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY app.py .
COPY .env .

# Expõe a porta 5000
EXPOSE 5000

# Define variáveis de ambiente
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000
ENV PORT=5000

# Comando para executar a aplicação
CMD ["python", "app.py"]