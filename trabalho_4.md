# Trabalho 4 - Realização de Testes de Desempenho com a Aplicação Link Extractor

## Objetivo
Executar e documentar testes de desempenho com as duas versões do serviço de extração de links da aplicação Link Extractor, conforme o enunciado do Trabalho 4.

## Arquitetura entregue
A solução final foi montada em [Trabalho 4/docker-compose.yml](Trabalho%204/docker-compose.yml) com os seguintes componentes:
- Front-end web em PHP.
- Serviço de extração em Python.
- Serviço de extração em Ruby.
- Cache Redis compartilhado.
- Site estático de apoio com 10 páginas para os cenários do Locust.

## Requisitos do enunciado
1. Comparar as duas versões do serviço de extração de links.
2. Usar uma ferramenta de teste de carga configurável por script.
3. Implementar um usuário virtual com 10 invocações sequenciais a URLs diferentes.
4. Executar cenários variando quantidade de usuários, linguagem do serviço e uso de cache.
5. Armazenar as métricas e produzir gráficos para análise.

## Estrutura criada em Trabalho 4
- [docker-compose.yml](Trabalho%204/docker-compose.yml) para orquestração dos serviços.
- [docker/app-python/app.py](Trabalho%204/docker/app-python/app.py) com a API em Python.
- [docker/app-ruby/app.rb](Trabalho%204/docker/app-ruby/app.rb) com a API em Ruby.
- [docker/web/index.php](Trabalho%204/docker/web/index.php) com o front-end web.
- [sample-site/](Trabalho%204/sample-site/) com 10 páginas de entrada para os testes.
- [locust/locustfile.py](Trabalho%204/locust/locustfile.py) com o script de carga.
- [locust/plot_results.py](Trabalho%204/locust/plot_results.py) com a geração dos gráficos.
- [results/final_summary.csv](Trabalho%204/results/final_summary.csv) com o consolidado final.
- [images/](Trabalho%204/images/) com os gráficos gerados.

## Como executar
1. Subir a stack: `docker compose -f "Trabalho 4/docker-compose.yml" up -d --build`
2. Acessar o front-end: `http://localhost:8080`
3. Executar o Locust em modo headless para o backend Python ou Ruby.

## Validação executada
A stack foi construída e validada com sucesso. Os testes feitos localmente confirmaram:
- O front-end abre em `http://localhost:8080`.
- As APIs Python e Ruby respondem corretamente ao endpoint `/extract`.
- O Redis armazena e devolve o cache quando `cache=1`.
- O usuário virtual do Locust faz 10 requisições sequenciais por ciclo.
- Os quatro cenários finais foram executados e gravados em CSV.

## Resultados finais
| Backend | Cache | Requisições | Falhas | Mediana (ms) | Média (ms) | RPS |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Python | Ligado | 525 | 0 | 3 | 3.88 | 58.27 |
| Python | Desligado | 430 | 0 | 5 | 6.89 | 48.20 |
| Ruby | Ligado | 450 | 0 | 4 | 5.53 | 50.34 |
| Ruby | Desligado | 440 | 0 | 4 | 5.63 | 49.55 |

Os gráficos consolidados foram gerados em [Trabalho 4/images/median-response-time.png](Trabalho%204/images/median-response-time.png), [Trabalho 4/images/average-response-time.png](Trabalho%204/images/average-response-time.png) e [Trabalho 4/images/requests-per-second.png](Trabalho%204/images/requests-per-second.png).

## Conclusão
O requisito central foi atendido: as duas versões do Link Extractor funcionam com Redis, o Locust executa 10 URLs por usuário virtual e os cenários com e sem cache foram medidos e documentados. O backend Python apresentou melhor latência e maior RPS no ambiente testado, enquanto o Ruby também permaneceu estável após a correção da autorização de host no Docker.
