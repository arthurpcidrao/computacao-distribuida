#!/bin/bash

# Script para executar testes de desempenho com Locust
# Testa: Python com/sem Redis e Ruby com/sem Redis
# Com 10, 50 e 100 usuários

BAIXO=10
MEDIO=50
ALTO=100

cd "$(dirname "$0")" || exit 1
mkdir -p results

# Configurações
SPAWN_RATE_BAIXO=2
SPAWN_RATE_MEDIO=5
SPAWN_RATE_ALTO=10

echo "🧪 Iniciando testes de desempenho..."
echo ""

# ============ BAIXA QUANTIDADE DE USUÁRIOS ============
echo "📊 Teste 1/4: Baixa quantidade de usuários"
API_UNDER_TEST=python-with-redis uv run locust -f locustfile.py \
  --host=http://localhost:5000 \
  -u $BAIXO -r $SPAWN_RATE_BAIXO -t 120s \
  --csv=results/python_redis_baixo_users \
  --headless

sleep 3

echo "📊 Teste 2/4: Baixa quantidade de usuários (Python sem Redis)"
API_UNDER_TEST=python-without-redis uv run locust -f locustfile.py \
  --host=http://localhost:5001 \
  -u $BAIXO -r $SPAWN_RATE_BAIXO -t 120s \
  --csv=results/python_noredis_baixo_users \
  --headless

sleep 3

echo "📊 Teste 3/4: Baixa quantidade de usuários (Ruby com Redis)"
API_UNDER_TEST=ruby-with-redis uv run locust -f locustfile.py \
  --host=http://localhost:4567 \
  -u $BAIXO -r $SPAWN_RATE_BAIXO -t 120s \
  --csv=results/ruby_redis_baixo_users \
  --headless

sleep 3

echo "📊 Teste 4/4: Baixa quantidade de usuários (Ruby sem Redis)"
API_UNDER_TEST=ruby-without-redis uv run locust -f locustfile.py \
  --host=http://localhost:4568 \
  -u $BAIXO -r $SPAWN_RATE_BAIXO -t 120s \
  --csv=results/ruby_noredis_baixo_users \
  --headless

sleep 3

# ============ MÉDIA QUANTIDADE DE USUÁRIOS ============
echo "📊 Teste 5/8: Média quantidade de usuários"
API_UNDER_TEST=python-with-redis uv run locust -f locustfile.py \
  --host=http://localhost:5000 \
  -u $MEDIO -r $SPAWN_RATE_MEDIO -t 120s \
  --csv=results/python_redis_medio_users \
  --headless

sleep 3

echo "📊 Teste 6/8: Média quantidade de usuários (Python sem Redis)"
API_UNDER_TEST=python-without-redis uv run locust -f locustfile.py \
  --host=http://localhost:5001 \
  -u $MEDIO -r $SPAWN_RATE_MEDIO -t 120s \
  --csv=results/python_noredis_medio_users \
  --headless

sleep 3

echo "📊 Teste 7/8: Média quantidade de usuários (Ruby com Redis)"
API_UNDER_TEST=ruby-with-redis uv run locust -f locustfile.py \
  --host=http://localhost:4567 \
  -u $MEDIO -r $SPAWN_RATE_MEDIO -t 120s \
  --csv=results/ruby_redis_medio_users \
  --headless

sleep 3

echo "📊 Teste 8/8: Média quantidade de usuários (Ruby sem Redis)"
API_UNDER_TEST=ruby-without-redis uv run locust -f locustfile.py \
  --host=http://localhost:4568 \
  -u $MEDIO -r $SPAWN_RATE_MEDIO -t 120s \
  --csv=results/ruby_noredis_medio_users \
  --headless

sleep 3

# ============ ALTA QUANTIDADE DE USUÁRIOS ============
echo "📊 Teste 9/12: Alta quantidade de usuários"
API_UNDER_TEST=python-with-redis uv run locust -f locustfile.py \
  --host=http://localhost:5000 \
  -u $ALTO -r $SPAWN_RATE_ALTO -t 120s \
  --csv=results/python_redis_alto_users \
  --headless

sleep 3

echo "📊 Teste 10/12: Alta quantidade de usuários (Python sem Redis)"
API_UNDER_TEST=python-without-redis uv run locust -f locustfile.py \
  --host=http://localhost:5001 \
  -u $ALTO -r $SPAWN_RATE_ALTO -t 120s \
  --csv=results/python_noredis_alto_users \
  --headless

sleep 3

echo "📊 Teste 11/12: Alta quantidade de usuários (Ruby com Redis)"
API_UNDER_TEST=ruby-with-redis uv run locust -f locustfile.py \
  --host=http://localhost:4567 \
  -u $ALTO -r $SPAWN_RATE_ALTO -t 120s \
  --csv=results/ruby_redis_alto_users \
  --headless

sleep 3

echo "📊 Teste 12/12: Alta quantidade de usuários (Ruby sem Redis)"
API_UNDER_TEST=ruby-without-redis uv run locust -f locustfile.py \
  --host=http://localhost:4568 \
  -u $ALTO -r $SPAWN_RATE_ALTO -t 120s \
  --csv=results/ruby_noredis_alto_users \
  --headless

echo ""
echo "✅ Todos os testes concluídos!"
echo "📊 Resultados salvos em: results/"
echo ""
echo "Para gerar gráficos:"
echo "  python3 generate_charts.py"
