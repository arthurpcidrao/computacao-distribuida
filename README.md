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
