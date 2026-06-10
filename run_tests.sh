#!/bin/bash

# Novas Cargas (Maior para Menor)
LOADS=(50 40 30)
SPAWN_RATE=10
RUN_TIME="2m"
ERROR_LIMIT=0.1

mkdir -p locust_results

# Função para matar processos antigos
cleanup() {
    pkill -f "api.py" || true
    pkill -f "api.js" || true
    sleep 2
}

# Função para iniciar as APIs
start_apis() {
    cleanup
    echo "🚀 Reiniciando APIs para novo teste..."
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
    sleep 10
    echo "🌱 Populando dados..."
    uv run python seed_data.py > /dev/null 2>&1
}

# Ordem: SOAP -> GraphQL -> REST -> gRPC (Mais sensíveis primeiro)
TECHS=("soap" "graphql" "rest" "grpc")

echo "🧪 Iniciando bateria de testes priorizando NODE.JS..."

for tech in "${TECHS[@]}"; do
    for users in "${LOADS[@]}"; do
        
        # Teste JavaScript (NODE) Primeiro conforme solicitado
        start_apis
        HOST=""
        CLASS=""
        case $tech in
            rest) HOST="http://localhost:9001"; CLASS="NodeRestUser";;
            graphql) HOST="http://localhost:9002"; CLASS="NodeGraphQLUser";;
            grpc) HOST="localhost:9003"; CLASS="NodeGrpcUser";;
            soap) HOST="http://localhost:9004/soap?wsdl"; CLASS="NodeSoapUser";;
        esac
        
        echo "📊 Testando JavaScript $tech com $users usuários..."
        uv run locust -f locustfile.py --headless -u $users -r $SPAWN_RATE -t $RUN_TIME \
            --host $HOST --csv "locust_results/node_${tech}_${users}" $CLASS > /dev/null 2>&1

        # Teste Python
        start_apis
        case $tech in
            rest) HOST="http://localhost:8001"; CLASS="PythonRestUser";;
            graphql) HOST="http://localhost:8002"; CLASS="PythonGraphQLUser";;
            grpc) HOST="localhost:8003"; CLASS="PythonGrpcUser";;
            soap) HOST="http://localhost:8004/?wsdl"; CLASS="PythonSoapUser";;
        esac
        
        echo "📊 Testando Python $tech com $users usuários..."
        uv run locust -f locustfile.py --headless -u $users -r $SPAWN_RATE -t $RUN_TIME \
            --host $HOST --csv "locust_results/py_${tech}_${users}" $CLASS > /dev/null 2>&1

    done
done

echo "📈 Consolidando resultados..."
uv run python consolidar_resultados.py

cleanup
echo "✅ Benchmark completo!"
