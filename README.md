# computacao-distribuida
Atividades para ampliar e conhecer as funcionalidades da computação distribuída.

## Grupo:
- Arthur Paraiba Cidrão: 2315035
- Cicero Braule Fernandes Feitoza Junior: 2315719
- Fernando Dutra Cabral De Oliveira Silva: 2316239
- João Guilherme Sales Epifânio: 2220309


## Embasamento teórico:

### Replicação de serviços
Em sistemas distribuídos, um serviço não roda somente em 1 servidor. Ele pode ser replicado em vários.

Assim, mesmo que algum servidor falhe, o serviço ainda continua disponível.

A replicação existe para:
- Aumentar a disponibilidade
- Aumentar tolerância a falhas
- Melhorar latência e escalabilidade

### Disponibilidade
A disponibilidade de um sistema é a probabilidade de que o sistema esteja funcionando em um determinado instante.

```math
Disponibilidade = P(sistema \space está \space operacional)
```

Ou seja:

```math
P(está \space funcionando) = p
```

```math
P(não \space está \space funcionando) = 1 - p
```

Assumimos que:
- Falhas são independentes
- Todos os servidores têm a mesma probabilidade de falhar

### Modelo de Quorum(n,k)

O modelo quorum é muito comum em bancos distribuídos e sistemas replicados.

- Parâmetros:
    - n --> número total de réplicas
    - k --> número mínimo de servidores ativos necessário

O serviço deve funcionar se:

```math
número \space mínimo \space de \space servidores \space disponíveis \geq k
```

### Modelagem Probabilística
Cada servidor é um experimento de Bernoulli

Um servidor pode estar disponível (p) ou indisponível (1-p).

Se temos **n servidores**, o número de servidores ativos segue uma distribuição binomial.

A distribuição binomial calcula:

```math
P(X = i)
```

onde:

- X = número de servidores ativos
- i = quantidade específica

a fórmula é:

```math
P(X = i) = \binom{n}{i} p^i (1-p)^{n-i}
```

onde:
```math
\binom{n}{i} = \frac{n!}{i!(n-i)!}
```
representa o número de combinações possíveis.

#### Quando o sistema fica disponível?
O sistema funciona se pelo menos k servidores estiverem ativos.

Ou seja:

```math
X \geq k
```

Então a disponibilidade do sistema é:

```math
P(X \geq k)
```

Isso representa a soma de probabilidades de todos os casos possíveis.

Pode ser escrita da seguinte forma:

```math
P(X \geq k) = P(X = k) + P(X = k+1) + P(X = k+2) + ... \space + P(X = n)
```

ou então:

```math
P(X \geq k) = \sum_{i=k}^{n} \binom{n}{i}p^i(1-p)^{n-i}
```

Essa é a fórmula de 1.1.

Interpretações:

- k=1 :
    - Alta disponibilidade
    - consistência fraca
- k = n :
    - Alta consistência
    - Baixa disponibilidade

## Trabalho 2 - Docker Compose (Nginx + 3 WordPress + MySQL)

### Arquitetura implementada
- 1 contêiner `nginx` como balanceador de carga
- 3 contêineres `wordpress1`, `wordpress2`, `wordpress3`
- 1 contêiner `mysql`

Total: **5 contêineres**, conforme especificação.

### Pré-requisitos
- Docker Engine instalado
- Docker Compose plugin instalado

### Subir ambiente local
```bash
docker compose up -d
```

Aplicação disponível em `http://localhost:8080`.

### Parar ambiente
```bash
docker compose down
```

### Estrutura criada
- `docker-compose.yml`: define serviços, rede, volumes e healthchecks
- `docker/nginx/default.conf`: upstream com os 3 WordPress

### Validação dos requisitos

#### R1 - 5 contêineres em execução
```bash
docker compose ps
```

#### R2 - Nginx balanceando os 3 WordPress
O Nginx adiciona o cabeçalho `X-Upstream-Addr` em cada resposta com o backend que atendeu.

```bash
for i in (seq 1 30)
    curl -sI http://localhost:8080 | grep -i X-Upstream-Addr
end
```

Critério de aceite: os 3 backends (`wordpress1`, `wordpress2`, `wordpress3`) aparecem ao longo das respostas.

#### R3 - WordPress conectado ao MySQL
```bash
docker compose logs mysql --tail 100
docker compose logs wordpress1 --tail 100
docker compose logs wordpress2 --tail 100
docker compose logs wordpress3 --tail 100
```

Critério de aceite: sem erro de conexão com banco nas instâncias WordPress.

#### R4 - Persistência dos dados
Os volumes `mysql_data` e `wp_data` garantem persistência após reinício da stack.

```bash
docker compose down
docker compose up -d
```

Critério de aceite: dados/configuração permanecem após reinício (sem remover volumes).

#### R5 - Continuidade com falha de 1 instância
```bash
docker stop wordpress2
for i in (seq 1 20)
    curl -sI http://localhost:8080 | grep -i X-Upstream-Addr
end
docker start wordpress2
```

Critério de aceite: serviço continua respondendo via Nginx com `wordpress1` e `wordpress3`.
