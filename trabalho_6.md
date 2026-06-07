# Trabalho 6 - APIs Distribuídas

## 1. Introdução Geral ao Cenário de Streaming

Este trabalho apresenta o desenvolvimento, análise comparativa e testes de carga de um serviço de streaming de música baseado em arquiteturas distribuídas. O sistema gerencia três entidades principais: **Usuários**, **Músicas** e **Playlists**, mapeadas de acordo com as regras de negócio e cardinalidades especificadas na modelagem do sistema:

* **Usuário (1..1) ➔ (0..*) Playlists:** Um usuário pode possuir nenhuma ou várias playlists, mas uma playlist pertence obrigatoriamente a um único usuário.
* **Playlist (0..*) ➔ (1..*) Músicas:** Uma playlist pode conter várias músicas, e uma mesma música pode fazer parte de múltiplas playlists do sistema.

Para validar a eficiência, escalabilidade e consumo de recursos dessas abordagens em cenários reais, o mesmo serviço foi implementado em **duas linguagens de programação (Python e JavaScript/Node.js)** sob **quatro tecnologias de comunicação distintas**: REST, GraphQL, gRPC e SOAP.

---

## 2. Abordagem Teórica e Comparativa das Tecnologias

A escolha da tecnologia de comunicação ideal para um sistema distribuído depende diretamente dos requisitos de latência, volume de dados, infraestrutura e acoplamento entre os sistemas. Com base nas análises de mercado documentadas por Ignacio (2023), Postman (2024) e GeeksforGeeks (2024), são detalhadas a seguir a origem, características, vantagens e desvantagens de cada abordagem.

### 2.1 Estilo Arquitetural REST (Representational State Transfer)

#### Origem e Características
Definido por Roy Fielding em sua tese de doutorado em 2000, o REST não é um protocolo, mas sim um **estilo arquitetural** construído sobre o protocolo HTTP. Ele utiliza os métodos nativos do HTTP (GET, POST, PUT, DELETE) para operar sobre **recursos**, identificados por URIs únicas (Postman, 2024). É inerentemente *stateless* (cada requisição contém toda a informação necessária para ser processada) e baseia-se fortemente em cache para otimização de performance.

#### Vantagens e Desvantagens
* **Vantagens:** Alta escalabilidade, desacoplamento completo entre cliente e servidor, suporte nativo a cache HTTP, curva de aprendizado baixa e ampla adoção pelo mercado, utilizando predominantemente o formato JSON para intercâmbio de dados (GeeksforGeeks, 2024).
* **Desvantagens:** Propensão a problemas de *Overfetching* (trazer mais dados do que o necessário) e *Underfetching* (exigir múltiplas requisições sequenciais para montar uma tela, como buscar o usuário e depois suas playlists), além da falta de um contrato de tipagem estrito nativo (Ignacio, 2023).

---

### 2.2 Linguagem de Consulta GraphQL

#### Origem e Características
Criado pelo Facebook em 2012 e lançado como código aberto em 2015, o GraphQL surgiu para resolver as limitações de redes móveis instáveis e os problemas de múltiplas requisições do REST. Trata-se de uma **linguagem de consulta para APIs** e um ambiente de execução (*runtime*) para responder a essas consultas usando um sistema de tipagem estrito (Schema) definido no servidor (Postman, 2024). Ele expõe um **único endpoint** (geralmente `/graphql`) onde o cliente dita exatamente o formato da resposta de que precisa.

#### Vantagens e Desvantagens
* **Vantagens:** Elimina completamente o *Overfetching* e o *Underfetching*, permitindo que o cliente solicite apenas os campos específicos de Usuários ou Músicas em uma única viagem de rede (*round-trip*). Possui auto-documentação nativa através de introspecção (GeeksforGeeks, 2024).
* **Desvantagens:** Complexidade considerável no backend para implementar seleções eficientes (risco do problema de performance $N+1$ nas consultas ao banco de dados), dificuldade em implementar cache HTTP nativo (já que a maioria das requisições são POST enviadas ao mesmo endpoint) (Ignacio, 2023).

---

### 2.3 Plataforma de Comunicação gRPC (Google Remote Procedure Call)

#### Origem e Características
Desenvolvido pelo Google em 2015 como uma evolução do seu framework interno *Stubby*, o gRPC é um framework de **chamada de procedimento remoto** de código aberto e alto desempenho. Ele roda nativamente sobre o **HTTP/2**, o que possibilita multiplexação de requisições na mesma conexão TCP e streams bidirecionais (Postman, 2024). Por padrão, utiliza o **Protocol Buffers (Protobuf)** como linguagem de definição de interface (IDL) e formato de serialização de dados binários, em vez de texto plano como JSON ou XML (Ignacio, 2023).

#### Vantagens e Desvantagens
* **Vantagens:** Performance extremamente elevada e baixíssima latência devido à serialização binária compacta; contratos estritos em arquivos `.proto` com geração automática de código para dezenas de linguagens; ideal para comunicação *microserviço-para-microserviço* (GeeksforGeeks, 2024).
* **Desvantagens:** Suporte limitado e complexo diretamente em navegadores web (exigindo proxies como gRPC-Web); payloads binários não são legíveis por humanos sem ferramentas de decodificação, dificultando o processo de debug inicial (Ignacio, 2023).

---

### 2.4 Protocolo SOAP (Simple Object Access Protocol)

#### Origem e Características
Criado pela Microsoft e outros no fim dos anos 1990, e posteriormente padronizado pela W3C, o SOAP é um **protocolo estrito baseado em mensagens**. Ao contrário do REST, ele define regras rígidas de segurança e estrutura de mensagens. Ele depende exclusivamente do formato **XML** para empacotar os dados dentro de uma estrutura conhecida como *SOAP Envelope* (Postman, 2024). A descrição do serviço e de suas operações é rigidamente governada por um arquivo de contrato chamado **WSDL** (Web Services Description Language).

#### Vantagens e Desvantagens
* **Vantagens:** Conversão e conformidade estritas baseadas em contratos (WSDL); segurança corporativa robusta integrada (WS-Security); suporte nativo a transações ACID complexas distribuídas (WS-AtomicTransaction), tornando-o ideal para sistemas bancários e legados críticos (GeeksforGeeks, 2024).
* **Desvantagens:** Payload extremamente pesado devido à verbosidade do XML, o que degrada a performance e aumenta o consumo de banda; alta complexidade de implementação e acoplamento rígido entre o cliente e o servidor (Ignacio, 2023).

---

## 3. Definição dos Contratos e Schemas Base

Para garantir o alinhamento exato entre os componentes construídos nas duas linguagens de programação, estabeleceu-se as estruturas estáticas de dados que regem os protocolos com contratos rígidos (gRPC e GraphQL), além dos contratos para REST (OpenAPI) e SOAP (WSDL).

### 3.1 Schema de Tipos GraphQL (Schema Definition Language - SDL)
Este schema unificado é utilizado tanto pelo servidor Python (Strawberry/Ariadne) quanto pelo JavaScript (Apollo Server).

```graphql
type Usuario {
  id: ID!
  nome: String!
  idade: Int!
  playlists: [Playlist!]!
}

type Musica {
  id: ID!
  nome: String!
  artista: String!
}

type Playlist {
  id: ID!
  nome: String!
  usuario: Usuario!
  musicas: [Musica!]!
}

type Query {
  listarUsuarios: [Usuario!]!
  listarMusicas: [Musica!]!
  listarPlaylistsPorUsuario(usuarioId: ID!): [Playlist!]!
  listarMusicasPorPlaylist(playlistId: ID!): [Musica!]!
  listarPlaylistsPorMusica(musicaId: ID!): [Playlist!]!
}

type Mutation {
  criarUsuario(nome: String!, idade: Int!): Usuario!
  criarMusica(nome: String!, artista: String!): Musica!
  criarPlaylist(nome: String!, usuarioId: ID!): Playlist!
  adicionarMusicaPlaylist(playlistId: ID!, musicaId: ID!): Playlist!
}
```

### 3.2 Protocol Buffers gRPC (streaming.proto)
Contrato de interface utilizado pelo compilador gRPC para gerar os stubs em Python (grpcio-tools) e carregar dinamicamente em JavaScript (@grpc/proto-loader).

```protobuf
syntax = "proto3";

package streaming;

// Entidades
message Usuario {
  string id = 1;
  string nome = 2;
  int32 idade = 3;
}

message Musica {
  string id = 1;
  string nome = 2;
  string artista = 3;
}

message Playlist {
  string id = 1;
  string nome = 2;
  string usuario_id = 3;
}

// Mensagens de Requisição e Resposta
message Vazio {}

message IdRequest {
  string id = 1;
}

message ListaUsuariosResponse {
  repeated Usuario usuarios = 1;
}

message ListaMusicasResponse {
  repeated Musica musicas = 1;
}

message ListaPlaylistsResponse {
  repeated Playlist playlists = 1;
}

message CriarUsuarioRequest {
  string nome = 1;
  int32 idade = 2;
}

message CriarMusicaRequest {
  string nome = 1;
  string artista = 2;
}

message CriarPlaylistRequest {
  string nome = 1;
  string usuario_id = 2;
}

message RelacaoPlaylistMusicaRequest {
  string playlist_id = 1;
  string musica_id = 2;
}

// Serviço de Transmissão Remota
service StreamingService {
  rpc ListarUsuarios(Vazio) returns (ListaUsuariosResponse);
  rpc ListarMusicas(Vazio) returns (ListaMusicasResponse);
  rpc ListarPlaylistsPorUsuario(IdRequest) returns (ListaPlaylistsResponse);
  rpc ListarMusicasPorPlaylist(IdRequest) returns (ListaMusicasResponse);
  rpc ListarPlaylistsPorMusica(IdRequest) returns (ListaPlaylistsResponse);
  
  rpc CriarUsuario(CriarUsuarioRequest) returns (Usuario);
  rpc CriarMusica(CriarMusicaRequest) returns (Musica);
  rpc CriarPlaylist(CriarPlaylistRequest) returns (Playlist);
  rpc AdicionarMusicaPlaylist(RelacaoPlaylistMusicaRequest) returns (Playlist);
}
```

### 3.3 Especificação REST (OpenAPI 3.0)
Documentação das rotas REST utilizadas na implementação.

```yaml
openapi: 3.0.0
info:
  title: Streaming Service API
  version: 1.0.0
paths:
  /usuarios:
    get:
      summary: Listar todos os usuários
      responses:
        '200':
          description: Sucesso
    post:
      summary: Criar um novo usuário
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                nome:
                  type: string
                idade:
                  type: integer
      responses:
        '201':
          description: Usuário criado

  /musicas:
    get:
      summary: Listar todas as músicas
      responses:
        '200':
          description: Sucesso
    post:
      summary: Criar uma nova música
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                nome:
                  type: string
                artista:
                  type: string
      responses:
        '201':
          description: Música criada

  /usuarios/{id}/playlists:
    get:
      summary: Listar playlists de um usuário
      parameters:
        - in: path
          name: id
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Sucesso

  /playlists:
    post:
      summary: Criar uma nova playlist
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                nome:
                  type: string
                usuario_id:
                  type: string
      responses:
        '201':
          description: Playlist criada

  /playlists/{id}/musicas:
    get:
      summary: Listar músicas de uma playlist
      parameters:
        - in: path
          name: id
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Sucesso
    post:
      summary: Adicionar música à playlist
      parameters:
        - in: path
          name: id
          required: true
          schema:
            type: string
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                musica_id:
                  type: string
      responses:
        '201':
          description: Música adicionada

  /musicas/{id}/playlists:
    get:
      summary: Listar playlists em que uma música está presente
      parameters:
        - in: path
          name: id
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Sucesso
```

### 3.4 Especificação SOAP (WSDL Simplificado)
Definição dos serviços baseados em mensagens estruturadas XML.

```xml
<definitions name="StreamingService"
             targetNamespace="http://streaming.com/wsdl"
             xmlns:tns="http://streaming.com/wsdl"
             xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
             xmlns:xsd="http://www.w3.org/2001/XMLSchema"
             xmlns="http://schemas.xmlsoap.org/wsdl/">

    <!-- Types -->
    <types>
        <xsd:schema targetNamespace="http://streaming.com/wsdl">
            <xsd:element name="ListarUsuariosRequest" type="xsd:anyType"/>
            <xsd:element name="ListarUsuariosResponse">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="usuarios" minOccurs="0" maxOccurs="unbounded">
                            <xsd:complexType>
                                <xsd:sequence>
                                    <xsd:element name="id" type="xsd:string"/>
                                    <xsd:element name="nome" type="xsd:string"/>
                                    <xsd:element name="idade" type="xsd:int"/>
                                </xsd:sequence>
                            </xsd:complexType>
                        </xsd:element>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
            <!-- Outros tipos omitidos para brevidade (Músicas, Playlists, etc.) -->
        </xsd:schema>
    </types>

    <!-- Messages -->
    <message name="ListarUsuariosInput">
        <part name="parameters" element="tns:ListarUsuariosRequest"/>
    </message>
    <message name="ListarUsuariosOutput">
        <part name="parameters" element="tns:ListarUsuariosResponse"/>
    </message>

    <!-- PortType -->
    <portType name="StreamingPortType">
        <operation name="ListarUsuarios">
            <input message="tns:ListarUsuariosInput"/>
            <output message="tns:ListarUsuariosOutput"/>
        </operation>
    </portType>

    <!-- Binding -->
    <binding name="StreamingBinding" type="tns:StreamingPortType">
        <soap:binding style="document" transport="http://schemas.xmlsoap.org/soap/http"/>
        <operation name="ListarUsuarios">
            <soap:operation soapAction="http://streaming.com/ListarUsuarios"/>
            <input>
                <soap:body use="literal"/>
            </input>
            <output>
                <soap:body use="literal"/>
            </output>
        </operation>
    </binding>

    <!-- Service -->
    <service name="StreamingService">
        <port name="StreamingPort" binding="tns:StreamingBinding">
            <soap:address location="http://localhost:8000/soap"/>
        </port>
    </service>
</definitions>
```

## 4. Guia de Execução e Testes de Carga das APIs

Este documento explica como executar cada uma das 8 APIs criadas (4 em Python, 4 em Node.js) e fornece um guia básico de como estruturar seus testes de carga utilizando o Locust.

### 4.1. Subindo os Servidores

Antes de iniciar qualquer API, abra um terminal e navegue até a pasta do projeto:
```bash
cd /home/arthurpcidrao/projetos/computacao-distribuida/
```

#### 4.1.1. APIs em Python
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

#### 4.1.2. APIs em Node.js
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

### 4.2. Mapa de Rotas e Endpoints

#### APIs REST
- **Base URL (Python):** `http://localhost:8001`
- **Base URL (Node.js):** `http://localhost:8011`
- **Endpoints:**
  - `GET /usuarios`: Lista todos os usuários
  - `POST /usuarios`: Cria um novo usuário `{"nome": "Nome", "idade": 20}`
  - `GET /musicas`: Lista todas as músicas
  - `POST /musicas`: Cria uma música `{"nome": "Musica", "artista": "Artista"}`
  - `POST /playlists`: Cria uma playlist `{"nome": "Nome", "usuario_id": "ID"}`

#### APIs GraphQL
- **Endpoint (Python):** `http://localhost:8002/graphql`
- **Endpoint (Node.js):** `http://localhost:8012/`
- **Operações:**
  - `Query: listarUsuarios`, `listarMusicas`, `listarPlaylistsPorUsuario(usuarioId)`
  - `Mutation: criarUsuario(nome, idade)`, `criarMusica(nome, artista)`

#### APIs gRPC
- **Servidor (Python):** `localhost:50051`
- **Servidor (Node.js):** `localhost:50052`
- **Contrato:** `APIs/shared/streaming.proto`

#### APIs SOAP
- **WSDL (Python):** `http://localhost:8003/?wsdl`
- **WSDL (Node.js):** `http://localhost:8013/soap?wsdl`
- **Serviço:** `StreamingService`

---

### 4.3. Testes de Carga com Locust

Para avaliar o desempenho dessas 4 abordagens distintas de comunicação, você deve usar a ferramenta **Locust**.

#### Preparação do Locustfile
Você precisará criar ou modificar o arquivo `locustfile.py` na raiz do seu projeto. Como cada tecnologia (REST, GraphQL, gRPC, SOAP) exige um cliente (cliente HTTP, cliente gRPC, cliente Zeep/SOAP) diferente, o seu `locustfile.py` deverá contemplar classes para cada uma delas.

#### Exemplos de Requisições por Tecnologia

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

Com os serviços no air e o arquivo `locustfile.py` configurado, inicie o Locust:

```bash
uv run locust -f locustfile.py
```

Em seguida, abra o navegador em `http://localhost:8089` para acessar a interface web do Locust, onde você poderá configurar:
1. Número de usuários simultâneos
2. Taxa de criação de usuários (Ramp up)
3. Escolher qual host/tecnologia você estará testando (basta alterar a URL na interface).

Repita os testes alternando o alvo entre os servidores Python e Node.js para comparar as latências e a capacidade de suportar requisições concorrentes entre as 4 tecnologias.