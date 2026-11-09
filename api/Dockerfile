FROM python:3.11-slim

# Evitar prompts interactivos y buffering de Python
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Instalar cliente OpenSSH para la comunicación entre contenedores (Parte B)
RUN apt-get update -o Acquire::Retries=3 && apt-get install -y --no-install-recommends --fix-missing -o Acquire::Retries=3 \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la API y scripts
COPY app.py .
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Exponer puerto de la API
EXPOSE 5000

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["python", "app.py"]
