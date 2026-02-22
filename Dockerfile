# Dockerfile para o Rasa Server
FROM rasa/rasa:3.6.20-full

# Mudar para root para instalar dependências
USER root

WORKDIR /app

# Copiar os ficheiros de configuração e dados de treino
COPY config.yml ./
COPY domain.yml ./
COPY credentials.yml ./
COPY endpoints.yml ./
COPY data/ ./data/

# Copiar modelos pré-treinados (se existirem)
RUN mkdir -p ./models

# Instalar o modelo spaCy para português
RUN pip install --no-cache-dir spacy>=3.5.0 && \
    python -m spacy download pt_core_news_md

# Voltar ao utilizador rasa
USER 1001

# Expor a porta do Rasa server
EXPOSE 5005

# Comando por omissão: iniciar o servidor Rasa
CMD ["run", "--enable-api", "--cors", "*", \
     "--credentials", "/app/credentials.yml", \
     "--endpoints", "/app/endpoints.yml"]
