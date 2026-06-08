#!/bin/bash

# Script para abrir cada API em um terminal separado
# Isso facilita os testes de carga com o Locust

# Detectar qual emulador de terminal está disponível
if command -v gnome-terminal >/dev/null 2>&1; then
    TERM_CMD="gnome-terminal --"
elif command -v xfce4-terminal >/dev/null 2>&1; then
    TERM_CMD="xfce4-terminal -e"
elif command -v konsole >/dev/null 2>&1; then
    TERM_CMD="konsole -e"
else
    TERM_CMD="xterm -e"
fi

echo "Iniciando as 8 APIs em terminais separados..."

# --- APIs em Python ---
$TERM_CMD bash -c "echo 'Python REST API (8001)'; cd APIs/python && uv run python rest_api.py; exec bash" &
$TERM_CMD bash -c "echo 'Python GraphQL API (8002)'; cd APIs/python && uv run python graphql_api.py; exec bash" &
$TERM_CMD bash -c "echo 'Python gRPC API (50051)'; cd APIs/python && uv run python grpc_api.py; exec bash" &
$TERM_CMD bash -c "echo 'Python SOAP API (8003)'; cd APIs/python && uv run python soap_api.py; exec bash" &

# --- APIs em JavaScript (Node.js) ---
$TERM_CMD bash -c "echo 'Node.js REST API (8011)'; cd APIs/javascript && node rest_api.js; exec bash" &
$TERM_CMD bash -c "echo 'Node.js GraphQL API (8012)'; cd APIs/javascript && node graphql_api.js; exec bash" &
$TERM_CMD bash -c "echo 'Node.js gRPC API (50052)'; cd APIs/javascript && node grpc_api.js; exec bash" &
$TERM_CMD bash -c "echo 'Node.js SOAP API (8013)'; cd APIs/javascript && node soap_api.js; exec bash" &

echo "Feito! Verifique as janelas de terminal abertas."
