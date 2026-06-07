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

Para garantir o alinhamento exato entre os componentes construídos nas duas linguagens de programação, estabeleceu-se as estruturas estáticas de dados que regem os protocolos com contratos rígidos (gRPC e GraphQL).

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