# Relatório de Testes de Carga - Computação Distribuída

Este documento apresenta os resultados dos testes de carga realizados no WordPress utilizando o Locust, variando a quantidade de instâncias e usuários simultâneos para avaliar a escalabilidade horizontal do ambiente.

## Estrutura do Ambiente
- **Balanceador de Carga:** Nginx
- **Aplicação:** WordPress (1, 2 e 3 instâncias)
- **Banco de Dados:** MySQL 8.0
- **Gerador de Carga:** Locust (Python)

## Rotas dos Testes (Cenários)
1. **Texto 1 (323877 bytes):** `http://localhost:8080/?p=13`
2. **Texto 2 (574437 bytes):** `http://localhost:8080/?p=21`
3. **Texto 3 (222862 bytes):** `http://localhost:8080/?p=28`

---

## 1. Cenário: Texto 1 (p=13)
**Objetivo:** Avaliar o desempenho do servidor ao entregar um volume de texto de aproximadamente 323kb.

| Instâncias WP | Usuários Locust | Mediana (ms) | P95 (ms) | RPS | Falhas (%) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1 Instância** | 400 | 76 | 120 | 23.8 | 0.00% |
| **1 Instância** | 500 | 96 | 210 | 27.2 | 0.00% |
| **1 Instância** | 600 | 440 | 1300 | 30.3 | 0.00% |
| **2 Instâncias** | 400 | 78 | 160 | 22.6 | 0.00% |
| **2 Instâncias** | 500 | 98 | 210 | 28.4 | 0.00% |
| **2 Instâncias** | 600 | 790 | 1600 | 29.5 | 0.20% |
| **3 Instâncias** | 400 | 78 | 180 | 20.5 | 0.00% |
| **3 Instâncias** | 500 | 98 | 250 | 25.3 | 0.00% |
| **3 Instâncias** | 600 | 850 | 1900 | 28.8 | 0.56% |

![RPS vs Instâncias - p13](./images/root_p_13/rps_vs_instancias.png)
![Taxa de Falha - p13](./images/root_p_13/failure_rate_vs_usuarios.png)
![P95 Resposta - p13](./images/root_p_13/p95_ms_vs_usuarios.png)

---

## 2. Cenário: Texto 2 (p=21)
**Objetivo:** Avaliar o impacto da transferência de um volume maior de dados (aproximadamente 574kb).

| Instâncias WP | Usuários Locust | Mediana (ms) | P95 (ms) | RPS | Falhas (%) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1 Instância** | 400 | 83 | 130 | 21.1 | 0.00% |
| **1 Instância** | 500 | 110 | 230 | 28.5 | 0.00% |
| **1 Instância** | 600 | 480 | 1500 | 28.5 | 0.00% |
| **2 Instâncias** | 400 | 86 | 130 | 23.2 | 0.00% |
| **2 Instâncias** | 500 | 110 | 250 | 27.3 | 0.00% |
| **2 Instâncias** | 600 | 870 | 1700 | 27.6 | 0.11% |
| **3 Instâncias** | 400 | 87 | 150 | 23.4 | 0.00% |
| **3 Instâncias** | 500 | 110 | 270 | 29.3 | 0.00% |
| **3 Instâncias** | 600 | 940 | 2000 | 28.0 | 0.53% |

![RPS vs Instâncias - p21](./images/root_p_21/rps_vs_instancias.png)
![Taxa de Falha - p21](./images/root_p_21/failure_rate_vs_usuarios.png)
![P95 Resposta - p21](./images/root_p_21/p95_ms_vs_usuarios.png)

---

## 3. Cenário: Texto 3 (p=28)
**Objetivo:** Avaliar o comportamento do sistema com um volume de texto menor (aproximadamente 222kb).

| Instâncias WP | Usuários Locust | Mediana (ms) | P95 (ms) | RPS | Falhas (%) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1 Instância** | 400 | 71 | 130 | 20.8 | 0.00% |
| **1 Instância** | 500 | 91 | 200 | 26.7 | 0.00% |
| **1 Instância** | 600 | 410 | 1300 | 30.6 | 0.00% |
| **2 Instâncias** | 400 | 74 | 130 | 21.8 | 0.00% |
| **2 Instâncias** | 500 | 92 | 210 | 25.9 | 0.00% |
| **2 Instâncias** | 600 | 730 | 1600 | 26.5 | 0.26% |
| **3 Instâncias** | 400 | 73 | 150 | 22.7 | 0.00% |
| **3 Instâncias** | 500 | 94 | 250 | 27.7 | 0.00% |
| **3 Instâncias** | 600 | 820 | 1800 | 26.3 | 0.40% |

![RPS vs Instâncias - p28](./images/root_p_28/rps_vs_instancias.png)
![Taxa de Falha - p28](./images/root_p_28/failure_rate_vs_usuarios.png)
![P95 Resposta - p28](./images/root_p_28/p95_ms_vs_usuarios.png)

---

## Metodologia de Teste
1. **Configuração de Instâncias:** As instâncias foram escaladas horizontalmente através do Docker Compose, com o balanceamento de carga gerenciado pelo Nginx.
2. **Stress Ramp-up:** Com o sistema configurado em 3 instâncias, elevamos a carga a uma taxa de **50 usuários por segundo** até atingirmos o limite de estabilidade.
3. **Identificação do Limite:** Observamos que, ao atingir 600 usuários simultâneos com 3 instâncias wordpress, o sistema começou a apresentar erros de chamadas GET (timeouts ou HTTP 5xx), indicando a saturação da infraestrutura.
4. **Coleta e Comparação:** Após identificar o limite máximo, realizamos testes comparativos com 400 e 500 usuários em 1, 2 e 3 instâncias para analisar como a distribuição de carga afetava o tempo de resposta e a taxa de falhas em artigos de diferentes tamanhos.
5. **Estabilização:** Cada teste foi executado por um período mínimo de 2 minutos para garantir a estabilidade das métricas de média e percentis.