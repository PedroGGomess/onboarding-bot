# Dockerfile para o Rasa Action Server
FROM python:3.10-slim

WORKDIR /app

# Instalar dependências de sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar ficheiro de dependências
COPY requirements.txt ./

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código das actions
COPY . .

# Expor a porta do Action Server
EXPOSE 5055

# Utilizador não-root por segurança
RUN useradd -m -u 1001 rasauser
USER rasauser

# Comando por omissão: iniciar o servidor de actions
CMD ["python", "-m", "rasa_sdk", "--actions", "actions", "--port", "5055"]
