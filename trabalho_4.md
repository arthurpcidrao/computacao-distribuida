# Trabalho 4 - Testes de Desempenho: Link Extractor

Relatório final dos testes de carga realizados na aplicação Link Extractor. Este documento reúne: contexto do ambiente, metodologia, matriz de testes, conteúdo do `locustfile.py`, gráficos gerados, análise detalhada, limitações e recomendações.

---

**Estrutura do Relatório**

- Ambiente e configurações
- URLs testadas e contagem de links
- `locustfile.py` (link e conteúdo)
- Metodologia e matriz de testes
- Resultados (gráficos incorporados) e análise detalhada
- Limitações, observações e recomendações

---

**Ambiente de Teste**

- Plataforma: Docker Compose (conjuntos em `Trabalho 4/linkextractor/*`).
- Gerador de carga: Locust (scripts em `Trabalho 4/locust/`).
- Máquinas: testes executados localmente no notebook dentro do WSL (Windows Subsystem for Linux).
- Serviços testados: APIs Python e Ruby, com e sem Redis (veja `linkextractor/` para configurações e Dockerfiles).
- Recursos do host: compartilhados entre Locust, containers das APIs, Nginx (se usado) e serviços de apoio (Redis/MySQL quando aplicável).

**Matriz de Testes**

- Implementações: `python-with-redis`, `python-without-redis`, `ruby-with-redis`, `ruby-without-redis`.
- Cenários de usuários simultâneos: baixo (10), médio (50), alto (100).
- Duração por execução: 120s (configurado em `run_tests.sh`).
- Métricas coletadas: P95, média, mediana, P99, RPS e taxa de falhas (CSV gerados em `Trabalho 4/locust/results`).

**URLs testadas e quantidade de links extraídos**

As URLs selecionadas pelo `locustfile.py` e as contagens aproximadas (comentários no arquivo):

- https://docs.python.org/3/ — 92 links
- https://developer.mozilla.org/ — 173 links
- https://curlie.org/ — 12 links
- https://wiki.archlinux.org/ — 108 links
- https://help.ubuntu.com/ — 29 links
- https://ftp.gnu.org/gnu/ — 392 links
- https://news.ycombinator.com/ — 225 links
- https://archive.apache.org/dist/ — 305 links
- https://edition.cnn.com/ — 491 links
- https://www.bbc.com/ — 291 links

Esses pontos cobrem páginas com baixo a muito alto número de links, exercitando parsing, I/O e tráfego de rede.

**`locustfile.py` — link e conteúdo**

Arquivo: [Trabalho 4/locust/locustfile.py](Trabalho%204/locust/locustfile.py#L1-L200)

Conteúdo principal utilizado (trecho completo salvo no repositório):

```
import os
from locust import HttpUser, task, between

SAMPLE_URLS = [
	"https://docs.python.org/3/",  # 92 links
	"https://developer.mozilla.org/",  # 173 links
	"https://curlie.org/",  # 12 links
	"https://wiki.archlinux.org/",  # 108 links
	"https://help.ubuntu.com/",  # 29 links
	"https://ftp.gnu.org/gnu/",  # 392 links
	"https://news.ycombinator.com/",  # 225 links
	"https://archive.apache.org/dist/",  # 305 links
	"https://edition.cnn.com/",  # 491 links
	"https://www.bbc.com/",  # 291 links
]

APIs = {
	"python-with-redis": "http://localhost:5000",
	"python-without-redis": "http://localhost:5001",
	"ruby-with-redis": "http://localhost:4567",
	"ruby-without-redis": "http://localhost:4568",
}

class LinkExtractorUser(HttpUser):
	wait_time = between(0.5, 1.5)

	def on_start(self):
		api_name = os.getenv("API_UNDER_TEST", "python-with-redis")
		if api_name not in APIs:
			raise ValueError(f"API '{api_name}' não configurada. Opções: {list(APIs.keys())}")
		self.base_url = APIs[api_name]
		self.url_index = 0

	@task
	def extract_links(self):
		current_url = SAMPLE_URLS[self.url_index % len(SAMPLE_URLS)]
		self.url_index += 1
		with self.client.get(f"/api/{current_url}", name="/api/<url> (extract)", catch_response=True) as response:
			if response.status_code == 200:
				try:
					data = response.json()
					links_count = len(data)
					response.success()
				except Exception as e:
					response.failure(f"Erro ao processar resposta JSON: {e}")
			else:
				response.failure(f"Status code: {response.status_code}")
```

**Como reproduzir os testes**

1. Subir os ambientes em `Trabalho 4/linkextractor/*` conforme a variante desejada (cada pasta tem `docker-compose.yml`).
2. Ir em `Trabalho 4/locust` e executar `./run_tests.sh` (o script automatiza as execuções para 10/50/100 usuários e gera CSVs em `results/`).

Comandos rápidos:

```bash
cd "Trabalho 4/locust"
./run_tests.sh
python3 generate_charts.py
```

Observação: o `run_tests.sh` usa `uv run locust` e define a variável de ambiente `API_UNDER_TEST` para alternar as APIs.

---

**Resultados — gráficos incorporados e análise detalhada**

Os gráficos a seguir foram gerados com `generate_charts.py` a partir dos CSVs em `Trabalho 4/locust/results`.

1) P95 por Usuários (todas as configurações)

![P95 por Usuários](Trabalho%204/images/chart_1_p95_all.png)

Análise: as variantes com Redis (Python+Redis, Ruby+Redis) apresentam latências extremamente baixas e estáveis (≈8–10 ms). As variantes sem Redis mostram comportamento degradado e não-linear: `python-without-redis` cresce fortemente (≈1.1s → 7s → 16s) com o aumento de carga, e `ruby-without-redis` cresce também (≈1.6s → 1.4s → 7.4s), indicando que a falta de caching persistente e/ou otimizações de I/O aumenta dramaticamente a latência sob concorrência.

2) Taxa de Falha por Usuários

![Taxa de Falha por Usuários](Trabalho%204/images/chart_2_failures_all.png)

Análise: as configurações com Redis apresentam taxa de falhas próxima de zero. As variantes sem Redis acumulam falhas significativas conforme a carga cresce — isso sugere timeouts, erros de processamento ou esgotamento de recursos, especialmente em `ruby-without-redis` e `python-without-redis` em 50/100 usuários.

3) P95 com Redis (comparativo)

![P95 com Redis](Trabalho%204/images/chart_3_p95_with_redis.png)

Análise: ambas as stacks com Redis mantêm P95 consistentemente baixos em todos os níveis de carga testados. Essa estabilidade indica que o Redis reduz operações repetidas de parsing/IO e diminui latência de resposta ao fornecer resultados em cache.

4) P95 sem Redis (comparativo)

![P95 sem Redis](Trabalho%204/images/chart_4_p95_without_redis.png)

Análise: sem Redis, a latência escala mal. `python-without-redis` é o caso extremo, provavelmente por realizar parsing/requests síncronas sem cache, o que aumenta espera por I/O e CPU; `ruby-without-redis` também sofre, mas apresentou valores um pouco mais moderados em alguns pontos.

**Sumário numérico (valores aproximados extraídos dos gráficos)**

- `Python + Redis` P95: ~10 ms (10 users), ~9 ms (50), ~9 ms (100)
- `Python sem Redis` P95: ~1100 ms, ~7000 ms, ~16000 ms (10 / 50 / 100 users)
- `Ruby + Redis` P95: ~8 ms consistente
- `Ruby sem Redis` P95: ~1600 ms, ~1400 ms, ~7400 ms
- Taxa de falha nas versões sem Redis: chega a ~3–6% (Python) e ~8–10% (Ruby) em cargas maiores

Esses números confirmam: Redis reduz latência e falhas; sem cache, o sistema degrada rapidamente.

---

**Limitações e observações**

- Execução local no WSL: o Locust e os containers rodaram no mesmo host dentro do WSL. Por padrão, o WSL aloca/gerencia memória de forma diferente de um Linux nativo, o que pode ter limitado a RAM disponível e aumentado contenção.
- Ambiente não distribuído: o gerador de carga também consumiu recursos no mesmo host, influenciando latência e RPS.
- Dados amostrais: gráficos foram gerados a partir de execuções de 120s; repetições adicionais podem reduzir variância estatística.
- Dependências de rede: a extração de muitos links depende de conectividade externa (por exemplo, acessar `edition.cnn.com`), o que pode introduzir variabilidade por latência de terceiros.

**Recomendações**

1. Repetir testes com gerador de carga em máquina separada (remota) para isolar impacto do Locust.
2. Em produção, habilitar cache (Redis) quando o workload envolve parsing/requests caros.
3. Fazer profiling das implementações sem Redis para identificar pontos de bloqueio (I/O síncrono, parsing ineficiente, bloqueios de GC).
4. Se for necessário suportar alto throughput, distribuir containers em hosts distintos e usar um banco de dados dedicado.

