#!/bin/bash

# Script para executar testes de desempenho com Locust
# Testa: Python com/sem Redis e Ruby com/sem Redis
# Com 50, 200 e 300 usuários

cd "$(dirname "$0")" || exit 1
mkdir -p results

# Configurações
SPAWN_RATE_50=2
SPAWN_RATE_200=5
SPAWN_RATE_300=10

echo "🧪 Iniciando testes de desempenho..."
echo ""

# ============ 50 USUÁRIOS ============
echo "📊 Teste 1/4: 50 usuários"
API_UNDER_TEST=python-with-redis uv run locust -f locustfile.py \
  --host=http://localhost:5000 \
  -u 50 -r $SPAWN_RATE_50 -t 120s \
  --csv=results/python_redis_50users \
  --headless

sleep 3

echo "📊 Teste 2/4: 50 usuários (Python sem Redis)"
API_UNDER_TEST=python-without-redis uv run locust -f locustfile.py \
  --host=http://localhost:5001 \
  -u 50 -r $SPAWN_RATE_50 -t 120s \
  --csv=results/python_noredis_50users \
  --headless

sleep 3

echo "📊 Teste 3/4: 50 usuários (Ruby com Redis)"
API_UNDER_TEST=ruby-with-redis uv run locust -f locustfile.py \
  --host=http://localhost:4567 \
  -u 50 -r $SPAWN_RATE_50 -t 120s \
  --csv=results/ruby_redis_50users \
  --headless

sleep 3

echo "📊 Teste 4/4: 50 usuários (Ruby sem Redis)"
API_UNDER_TEST=ruby-without-redis uv run locust -f locustfile.py \
  --host=http://localhost:4568 \
  -u 50 -r $SPAWN_RATE_50 -t 120s \
  --csv=results/ruby_noredis_50users \
  --headless

sleep 3

# ============ 200 USUÁRIOS ============
echo "📊 Teste 5/8: 200 usuários"
API_UNDER_TEST=python-with-redis uv run locust -f locustfile.py \
  --host=http://localhost:5000 \
  -u 200 -r $SPAWN_RATE_200 -t 120s \
  --csv=results/python_redis_200users \
  --headless

sleep 3

echo "📊 Teste 6/8: 200 usuários (Python sem Redis)"
API_UNDER_TEST=python-without-redis uv run locust -f locustfile.py \
  --host=http://localhost:5001 \
  -u 200 -r $SPAWN_RATE_200 -t 120s \
  --csv=results/python_noredis_200users \
  --headless

sleep 3

echo "📊 Teste 7/8: 200 usuários (Ruby com Redis)"
API_UNDER_TEST=ruby-with-redis uv run locust -f locustfile.py \
  --host=http://localhost:4567 \
  -u 200 -r $SPAWN_RATE_200 -t 120s \
  --csv=results/ruby_redis_200users \
  --headless

sleep 3

echo "📊 Teste 8/8: 200 usuários (Ruby sem Redis)"
API_UNDER_TEST=ruby-without-redis uv run locust -f locustfile.py \
  --host=http://localhost:4568 \
  -u 200 -r $SPAWN_RATE_200 -t 120s \
  --csv=results/ruby_noredis_200users \
  --headless

sleep 3

# ============ 300 USUÁRIOS ============
echo "📊 Teste 9/12: 300 usuários"
API_UNDER_TEST=python-with-redis uv run locust -f locustfile.py \
  --host=http://localhost:5000 \
  -u 300 -r $SPAWN_RATE_300 -t 120s \
  --csv=results/python_redis_300users \
  --headless

sleep 3

echo "📊 Teste 10/12: 300 usuários (Python sem Redis)"
API_UNDER_TEST=python-without-redis uv run locust -f locustfile.py \
  --host=http://localhost:5001 \
  -u 300 -r $SPAWN_RATE_300 -t 120s \
  --csv=results/python_noredis_300users \
  --headless

sleep 3

echo "📊 Teste 11/12: 300 usuários (Ruby com Redis)"
API_UNDER_TEST=ruby-with-redis uv run locust -f locustfile.py \
  --host=http://localhost:4567 \
  -u 300 -r $SPAWN_RATE_300 -t 120s \
  --csv=results/ruby_redis_300users \
  --headless

sleep 3

echo "📊 Teste 12/12: 300 usuários (Ruby sem Redis)"
API_UNDER_TEST=ruby-without-redis uv run locust -f locustfile.py \
  --host=http://localhost:4568 \
  -u 300 -r $SPAWN_RATE_300 -t 120s \
  --csv=results/ruby_noredis_300users \
  --headless

echo ""
echo "✅ Todos os testes concluídos!"
echo "📊 Resultados salvos em: results/"
echo ""
echo "Para gerar gráficos:"
echo "  python3 generate_charts.py"
