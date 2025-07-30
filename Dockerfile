# Dockerfile

# Usar uma imagem base oficial do Python
FROM python:3.9-slim

# Instalar o cliente do PostgreSQL para que o wait-for-it funcione
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

# Definir o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copiar o script de espera e dar permissão de execução
COPY ./wait-for-it.sh .
RUN chmod +x wait-for-it.sh

# Copiar o arquivo de dependências
COPY requirements.txt .

# Instalar as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o resto dos arquivos do projeto para o diretório de trabalho
COPY . .

# O comando CMD será movido para o docker-compose.yml