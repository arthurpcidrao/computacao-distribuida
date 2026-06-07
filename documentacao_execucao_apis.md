# Guia de Execução e Testes de Carga das APIs

Este documento explica como executar cada uma das 8 APIs criadas (4 em Python, 4 em Node.js) e fornece um guia básico de como estruturar seus testes de carga utilizando o Locust.

## 1. Subindo os Servidores

Antes de iniciar qualquer API, abra um terminal e navegue até a pasta do projeto:
```bash
cd /home/arthurpcidrao/projetos/computacao-distribuida/
```

### 1.1. APIs em Python
Como as dependências do Python foram instaladas via `uv`, você deve rodar os comandos com o prefixo `uv run python`. Navegue até a pasta `APIs/python`:

```bash
cd APIs/python
```

1. **REST API (Porta 8001):**
   ```bash
   uv run python rest_api.py
   ```
2. **GraphQL API (Porta 8002):**
   ```bash
   uv run python graphql_api.py
   ```
3. **gRPC API (Porta 50051):**
   ```bash
   uv run python grpc_api.py
   ```
4. **SOAP API (Porta 8003):**
   ```bash
   uv run python soap_api.py
   ```

### 1.2. APIs em Node.js
Abra um novo terminal e navegue até a pasta `APIs/javascript`:

```bash
cd APIs/javascript
```

1. **REST API (Porta 8011):**
   ```bash
   node rest_api.js
   ```
2. **GraphQL API (Porta 8012):**
   ```bash
   node graphql_api.js
   ```
3. **gRPC API (Porta 50052):**
   ```bash
   node grpc_api.js
   ```
4. **SOAP API (Porta 8013):**
   ```bash
   node soap_api.js
   ```

---

## 2. Mapa de Rotas e Endpoints

### APIs REST
- **Base URL (Python):** `http://localhost:8001`
- **Base URL (Node.js):** `http://localhost:8011`
- **Endpoints:**
  - `GET /usuarios`: Lista todos os usuários
  - `POST /usuarios`: Cria um novo usuário `{"nome": "Nome", "idade": 20}`
  - `GET /musicas`: Lista todas as músicas
  - `POST /musicas`: Cria uma música `{"nome": "Musica", "artista": "Artista"}`
  - `POST /playlists`: Cria uma playlist `{"nome": "Nome", "usuario_id": "ID"}`

### APIs GraphQL
- **Endpoint (Python):** `http://localhost:8002/graphql`
- **Endpoint (Node.js):** `http://localhost:8012/`
- **Operações:**
  - `Query: listarUsuarios`, `listarMusicas`, `listarPlaylistsPorUsuario(usuarioId)`
  - `Mutation: criarUsuario(nome, idade)`, `criarMusica(nome, artista)`

### APIs gRPC
- **Servidor (Python):** `localhost:50051`
- **Servidor (Node.js):** `localhost:50052`
- **Contrato:** `APIs/shared/streaming.proto`

### APIs SOAP
- **WSDL (Python):** `http://localhost:8003/?wsdl`
- **WSDL (Node.js):** `http://localhost:8013/soap?wsdl`
- **Serviço:** `StreamingService`

---

## 3. Testes de Carga com Locust

Para avaliar o desempenho dessas 4 abordagens distintas de comunicação, você deve usar a ferramenta **Locust**.

### Preparação do Locustfile
Você precisará criar ou modificar o arquivo `locustfile.py` na raiz do seu projeto. Como cada tecnologia (REST, GraphQL, gRPC, SOAP) exige um cliente (cliente HTTP, cliente gRPC, cliente Zeep/SOAP) diferente, o seu `locustfile.py` deverá contemplar classes para cada uma delas.

### Exemplos de Requisições por Tecnologia

**1. Testando REST:**
```python
from locust import HttpUser, task, between

class RestUser(HttpUser):
    wait_time = between(1, 2)
    host = "http://localhost:8001" # ou 8011 para Node

    @task
    def listar_usuarios(self):
        self.client.get("/usuarios")
        
    @task
    def criar_usuario(self):
        self.client.post("/usuarios", json={"nome": "Teste", "idade": 25})
```

**2. Testando GraphQL:**
Requisições GraphQL são essencialmente `POST` contendo a query no corpo da requisição.
```python
class GraphQLUser(HttpUser):
    host = "http://localhost:8002"
    
    @task
    def listar_usuarios(self):
        query = """
        query {
            listarUsuarios {
                id
                nome
                idade
            }
        }
        """
        self.client.post("/graphql", json={'query': query})
```

**3. Testando gRPC e SOAP:**
Para gRPC e SOAP, será necessário estender o cliente base do Locust (`User` ao invés de `HttpUser`), abrindo os canais gRPC (utilizando a biblioteca `grpcio`) e SOAP (utilizando a biblioteca `zeep`) dentro do método `on_start` do usuário simulado e chamando os métodos correspondentes através de eventos customizados do Locust.

### Executando o Teste de Carga

Com os serviços no ar e o arquivo `locustfile.py` configurado, inicie o Locust:

```bash
uv run locust -f locustfile.py
```

Em seguida, abra o navegador em `http://localhost:8089` para acessar a interface web do Locust, onde você poderá configurar:
1. Número de usuários simultâneos
2. Taxa de criação de usuários (Ramp up)
3. Escolher qual host/tecnologia você estará testando (basta alterar a URL na interface).

Repita os testes alternando o alvo entre os servidores Python e Node.js para comparar as latências e a capacidade de suportar requisições concorrentes entre as 4 tecnologias.