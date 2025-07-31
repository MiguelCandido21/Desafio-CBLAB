FROM python:3.9-slim

RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ./wait-for-it.sh .
RUN chmod +x wait-for-it.sh

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
