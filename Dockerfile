# /Sistema-hospitalar/Dockerfile (VERSÃO CORRIGIDA)
FROM python:3.11-slim

WORKDIR /app

# CORREÇÃO AQUI: Copia o 'requirements.txt' da raiz
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# CORREÇÃO AQUI: Copia o 'application.py' da raiz
COPY application.py .

EXPOSE 8000

CMD ["gunicorn", "application:application", "--bind", "0.0.0.0:8000", "--workers", "4"]