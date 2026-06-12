# Especificação do Projeto: Benchmark de Estilos de Arquitetura de APIs (Sistemas Distribuídos)

## 1. Visão Geral do Projeto
O objetivo deste projeto é comparar a performance, latência (com foco no percentil 95 - p95) e o tamanho das respostas (Average Content Size) de 4 estilos de arquitetura de APIs (REST, GraphQL, gRPC e SOAP) implementados em duas linguagens distintas: Python e JavaScript (Node.js). 

No total, serão desenvolvidas **8 APIs** que expõem os mesmos dados de um serviço de streaming de música em memória. O fluxo completo de execução de orquestração, população, testes e consolidação de dados será gerenciado de forma totalmente automatizada por um script em lote (Bash).

---

## 2. Entidades e Modelagem de Dados
Para garantir que o `Average Content Size` seja maior que zero e que todas as APIs trafeguem exatamente os mesmos dados, a massa de dados mockados deve conter:
* **1000 Usuários**
* **1000 Músicas**
* **100 Playlists**
* **Vínculos de músicas dentro das playlists**

### Atributos por Entidade (Todos devem ser retornados nos GETs):
* **Usuário**: `id` (string/UUID), `nome` (string), `idade` (integer).
* **Música**: `id` (string/UUID), `nome` (string), `artista` (string).
* **Playlist**: `id` (string/UUID), `nome` (string), `usuario_id` (string/UUID).
* **MusicaPlaylist (Relacionamento)**: `playlist_id` (string), `musica_id` (string).

---

## 3. Matriz de APIs e Endpoints/Contratos

Cada uma das 8 APIs deve rodar em uma porta exclusiva e expor métodos equivalentes para consulta (GET) e população inicial (POST/Mutations/Métodos gRPC/SOAP).

### Portas Sugeridas:
* **Python (FastAPI/etc):** REST (8001), GraphQL (8002), gRPC (8003), SOAP (8004)
* **JavaScript (Express/Apollo/etc):** REST (9001), GraphQL (9002), gRPC (9003), SOAP (9004)

### Contrato das Rotas de Consulta (Foco do Teste de Carga):
1.  **Listar todos os usuários**
2.  **Listar todas as músicas**
3.  **Listar playlists de um usuário específico** (passando `usuario_id`)
4.  **Listar músicas de uma playlist específica** (passando `playlist_id`)
5.  **Listar playlists que contêm uma música específica** (passando `musica_id`)

> ⚠️ **Atenção para o SOAP:** A API SOAP deve responder estritamente em formato XML (Envelope/Body) seguindo o WSDL definido. Não deve retornar JSON sob nenhuma circunstância.

---

## 4. Estratégia de Ingestão de Dados (Seeding)
Para evitar gargalos de IO ou persistência durante o benchmark, os dados devem residir estritamente **em memória** (`in-memory DB` usando listas/arrays/dicionários). Os dados serão injetados de forma programática pelo script de automação central através dos endpoints de inserção específicos de cada arquitetura.

---

## 5. Plano de Testes de Carga (Locust)

### Regras do Arquivo do Locust (`locustfile.py`):
* **Apenas requisições de leitura (GET / Consultas equivalentes)**.
* Todas as `@task` devem ter peso igual a `1` (`@task(1)`).
* As consultas que exigem IDs (como buscar músicas de uma playlist) devem sortear IDs válidos de uma lista carregada previamente no início do script do Locust para evitar respostas `404` (o tamanho do conteúdo precisa ser testado com dados reais trafegando).

### Cenários de Carga (Por API):
Cada API passará por 3 baterias de testes distintas baseadas no volume de concorrência:
1.  **Carga Alta:** 50 usuários simultâneos.
2.  **Carga Média:** 40 usuários simultâneos.
3.  **Carga Baixa:** 30 usuários simultâneos.

**Parâmetros de rampa e tempo:**
* **Spawn Rate (Taxa de subida):** 10 usuários por segundo.
* **Duração do teste:** 2 minutos (`2m`).
* **Limite de Erro:** 10% (0.1). Testes que excederem este valor serão invalidados na conclusão.

---

## 6. Pipeline de Automação de Ciclo Completo (`run_tests.sh`)

Você deve gerar um script Bash único (`run_tests.sh`) que orquestre o ciclo de vida completo do benchmark de forma linear e limpa, executando os seguintes passos na ordem exata definida:

1. **Iniciar os Serviços:** Iniciar em background as 8 instâncias de APIs em suas portas específicas (4 em Python e 4 em JavaScript/Node.js). Aguardar até que todas as portas estejam prontas e aceitando conexões.
2. **Ingestão e Carga de Dados (Seeding):** Chamar o script ou comando de carga (ex: `seed_data.py`) que preencherá cada uma das 8 APIs em memória usando o formato e protocolo exigido por cada uma (JSON para REST, Mutations para GraphQL, chamadas binárias para gRPC e XML Envelope para SOAP) com a volumetria estipulada.
3. **Execução Automatizada dos Testes:** Rodar sequencialmente os 24 cenários do Locust de modo headless (sem interface gráfica), iterando sobre cada API e injetando as 3 volumetrias de carga (100, 200 e 300 usuários concorrentes) por 2 minutos cada.
4. **Agregação e Coleta:** Extrair a linha de dados agregados de cada relatório gerado pelo Locust e salvar tudo em um único arquivo de dados consolidado `.csv`.
5. **Geração das Análises Gráficas:** Chamar o script Python (`consolidar_resultados.py`) responsável por ler o arquivo `.csv` unificado e compilar as imagens comparativas finais.

---

## 7. Consolidação de Dados e Análise (Pandas & Matplotlib)

O script de pós-processamento executado pelo pipeline Bash deve extrair a linha consolidada (`Aggregated`) de cada um dos 24 testes e gerar o arquivo `dashboard_data.csv` unificado com as colunas obrigatórias: `Linguagem`, `Estilo_API` e `Carga_Usuarios`.

### Métricas obrigatórias no CSV Final:
* `Linguagem` (Python / JavaScript)
* `Estilo_API` (REST / GraphQL / gRPC / SOAP)
* `Carga_Usuarios` (100 / 200 / 300)
* `Total Request Count`
* `Failure Count`
* `Median Response Time` (p50)
* `95% Response Time` (p95) -> **Métrica Principal**
* `Average Response Time`
* `Average Content Size` -> **Deve ser > 0**
* `Requests/s` (Throughput)

### Geração de Gráficos:
O script deve usar `matplotlib`/`seaborn` para gerar e salvar gráficos comparativos na pasta `charts/` focados em:
* Comparação direta do **p95 Response Time** por Estilo de API e Carga para definir qual API e linguagem entregam a resposta mais rápida.
* Comportamento e degradação das APIs sob o **aumento progressivo de carga** (100 -> 200 -> 300 usuários).
* Comparativo de **Average Content Size** para expor a eficiência de transporte de cada protocolo.

---

## 8. Entregáveis Esperados do Agente de IA e Relatório Final

Após a finalização do script Bash e geração de todos os arquivos, **o agente de IA deve coletar e embutir as imagens geradas em um relatório estruturado fora do script**, chamado `trabalho_6.md`.

Este documento markdown final deve obrigatoriamente apresentar:
* **Metodologia Empregada:** Descrição clara da configuração do ambiente de testes e infraestrutura.
* **Resultados Visuais:** Exibição ordenada dos gráficos comparativos salvos.
* **Insights Técnicos Baseados nos Dados:** Análise crítica pontuando o comportamento de cada paradigma de comunicação (ex: o impacto de overhead do XML no SOAP versus a eficiência binária do gRPC).
* **Conclusão de Performance (Foco no p95):** Resposta objetiva de qual arquitetura e ecossistema (Python vs JavaScript) demonstrou maior resiliência e velocidade com o aumento de usuários e qual apresentou maior degradação ou incidência de falhas em alta concorrência.



## 9. Definição dos Contratos e Schemas Base

Para garantir o alinhamento exato entre os componentes construídos nas duas linguagens de programação, estabeleceu-se as estruturas estáticas de dados que regem os protocolos com contratos rígidos (gRPC e GraphQL).

### 9.1 Schema de Tipos GraphQL (Schema Definition Language - SDL)
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


### 3.2 Protocol Buffers gRPC (streaming.proto)
Contrato de interface utilizado pelo compilador gRPC para gerar os stubs em Python (grpcio-tools) e carregar dinamicamente em JavaScript (@grpc/proto-loader).

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