#!/bin/bash

# Script para iniciar as 8 APIs e popular os dados iniciais
# Útil para testes manuais via cURL ou outras ferramentas

echo "🧹 Limpando processos antigos..."
pkill -f "api.py" || true
pkill -f "api.js" || true
sleep 2

echo "🚀 Iniciando APIs em background..."

# Python: REST (8001), GraphQL (8002), gRPC (8003), SOAP (8004)
uv run python APIs/python/rest_api.py > /dev/null 2>&1 &
uv run python APIs/python/graphql_api.py > /dev/null 2>&1 &
uv run python APIs/python/grpc_api.py > /dev/null 2>&1 &
uv run python APIs/python/soap_api.py > /dev/null 2>&1 &

# Node: REST (9001), GraphQL (9002), gRPC (9003), SOAP (9004)
node APIs/javascript/rest_api.js > /dev/null 2>&1 &
node APIs/javascript/graphql_api.js > /dev/null 2>&1 &
node APIs/javascript/grpc_api.js > /dev/null 2>&1 &
node APIs/javascript/soap_api.js > /dev/null 2>&1 &

echo "⏳ Aguardando serviços (15s)..."
sleep 15

echo "🌱 Injetando dados (1000 users, 1000 songs, 100 playlists)..."
uv run python seed_data.py

echo "✅ APIs prontas para teste local!"
echo "Portas Python: 8001-8004"
echo "Portas Node.js: 9001-9004"
