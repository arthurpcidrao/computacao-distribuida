# 🚀 VERSÃO SIMPLIFICADA - Pronto para Usar

## 📁 Arquivos

```
locust/
├── README.md              ← Leia primeiro!
├── locustfile.py          ← Implementação Locust
├── run_tests.sh           ← Script para rodar 12 testes
└── generate_charts.py     ← Gera 4 gráficos PNG
```

## ⚡ Quick Start

```bash
# 1. Instalar
pip install locust matplotlib pandas

# 2. Executar todos os testes (50, 200, 300 usuários)
chmod +x run_tests.sh generate_charts.py
./run_tests.sh

# 3. Gerar gráficos
python3 generate_charts.py

# 4. Resultados
# - results/*.csv  (dados brutos)
# - chart_*.png    (4 gráficos gerados)
```

## 📊 Os 4 Gráficos Gerados

1. **chart_1_p95_all.png**
   - Y: P95 (ms)
   - X: Usuários (50, 200, 300)
   - 4 barras/categoria: Python+Redis, Python-Redis, Ruby+Redis, Ruby-Redis

2. **chart_2_failures_all.png**
   - Y: Taxa de falha (%)
   - X: Usuários (50, 200, 300)
   - 4 barras/categoria (mesma estrutura)

3. **chart_3_p95_with_redis.png**
   - Y: P95 (ms)
   - X: Usuários (50, 200, 300)
   - 2 barras/categoria: Python+Redis, Ruby+Redis

4. **chart_4_p95_without_redis.png**
   - Y: P95 (ms)
   - X: Usuários (50, 200, 300)
   - 2 barras/categoria: Python-Redis, Ruby-Redis

## 🎯 Total de Testes

- **12 testes** (3 quantidades de usuários × 4 APIs)
- **Tempo total:** ~24 minutos (automático)
- **Resultados:** 24 CSVs (2 por teste)

## 📝 Customizar

Para mudar o script `run_tests.sh`:
- Altere as quantidades de usuários (50, 200, 300)
- Altere a duração dos testes (-t 120s)
- Altere o spawn rate (-r valor)

Exemplo:
```bash
API_UNDER_TEST=python-with-redis locust -f locustfile.py \
  --host=http://localhost:5000 \
  -u 100 \
  -r 5 \
  -t 60s \
  --csv=results/meu_teste \
  --headless
```

## ✅ Pronto!

Tudo está pronto. Execute `./run_tests.sh` e espere os resultados!
