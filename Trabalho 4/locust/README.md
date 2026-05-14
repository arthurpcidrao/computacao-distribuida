# Testes de Desempenho - Link Extractor com Locust

## Instalação

```bash
pip install locust matplotlib pandas
```

## Como Executar

### Opção 1: Executar todos os testes (recomendado)

Dar permissão ao script:
```bash
chmod +x run_tests.sh
```

Rodar todos os 12 testes (50, 200 e 300 usuários em 4 APIs):
```bash
./run_tests.sh
```

Tempo total: ~24 minutos

### Opção 2: Teste manual individual

Para testar uma API específica:

```bash
# Python com Redis
API_UNDER_TEST=python-with-redis locust -f locustfile.py \
  --host=http://localhost:5000 \
  -u 50 -r 2 -t 120s \
  --csv=results/meu_teste \
  --headless

# Python sem Redis
API_UNDER_TEST=python-without-redis locust -f locustfile.py \
  --host=http://localhost:5001 \
  -u 50 -r 2 -t 120s \
  --csv=results/meu_teste \
  --headless

# Ruby com Redis
API_UNDER_TEST=ruby-with-redis locust -f locustfile.py \
  --host=http://localhost:4567 \
  -u 50 -r 2 -t 120s \
  --csv=results/meu_teste \
  --headless

# Ruby sem Redis
API_UNDER_TEST=ruby-without-redis locust -f locustfile.py \
  --host=http://localhost:4568 \
  -u 50 -r 2 -t 120s \
  --csv=results/meu_teste \
  --headless
```

**Parâmetros:**
- `-u 50`: 50 usuários simultâneos (altere conforme necessário)
- `-r 2`: 2 usuários criados por segundo (ramp-up)
- `-t 120s`: teste dura 120 segundos
- `--csv=results/meu_teste`: salva resultados em CSV
- `--headless`: sem interface web

## Arquivos CSV Gerados

Cada teste gera 2 arquivos:
- `*_stats.csv` - Estatísticas agregadas
- `*_stats_history.csv` - Histórico temporal

Colunas importantes em `*_stats.csv`:
- `Requests`: total de requisições
- `Failures`: total de falhas
- `Average Response Time`: tempo médio (ms)
- `95%`: percentil 95 (ms)
- `99%`: percentil 99 (ms)

Exemplo:
```bash
# Ver dados
cat results/python_redis_50users_stats.csv

# Formatado
column -t -s',' results/python_redis_50users_stats.csv
```

## Gerar Gráficos

Após executar os testes, gerar os 4 gráficos:

```bash
python3 generate_charts.py
```

Será gerado:
1. `chart_1_p95_all.png` - P95 todos os cenários
2. `chart_2_failures_all.png` - Taxa de falha todos
3. `chart_3_p95_with_redis.png` - P95 com Redis
4. `chart_4_p95_without_redis.png` - P95 sem Redis

## APIs Disponíveis

```
python-with-redis    → http://localhost:5000
python-without-redis → http://localhost:5001
ruby-with-redis      → http://localhost:4567
ruby-without-redis   → http://localhost:4568
```

Certifique-se de que estão rodando via Docker antes de executar os testes!

## Extrair Dados via CLI

```bash
# Ver tempo médio
awk -F',' 'NR==2 {print $5}' results/python_redis_50users_stats.csv

# Ver P95
awk -F',' 'NR==2 {print $(NF-3)}' results/python_redis_50users_stats.csv

# Ver taxa de falhas
awk -F',' 'NR==2 {print ($4/$3)*100 "%"}' results/python_redis_50users_stats.csv

# Comparar múltiplos
for f in results/*_stats.csv; do
  echo "$(basename $f)"
  awk -F',' 'NR==2 {print "  Média: " $5 "ms, P95: " $(NF-3) "ms"}' "$f"
done
```
