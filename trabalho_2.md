# Trabalho 2 (AV2)

## Docker Compose (Nginx + 3 WordPress + MySQL)

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