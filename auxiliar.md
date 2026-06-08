# Guia Auxiliar - Trabalho 6 (APIs Distribuídas)

Este documento descreve a organização do projeto para o **Trabalho 6**, detalhando a função de cada arquivo e como as diferentes tecnologias interagem para compor o sistema de streaming de música.

## 1. Estrutura de Pastas e Arquivos

O projeto está dividido em implementações por linguagem e arquivos de contrato compartilhados.

### 📂 `APIs/python/`
Contém as implementações dos servidores utilizando a linguagem **Python**.
*   `rest_api.py`: Implementação REST usando **FastAPI**.
*   `graphql_api.py`: Implementação GraphQL usando **Strawberry**.
*   `grpc_api.py`: Implementação gRPC usando a biblioteca `grpcio`.
*   `soap_api.py`: Implementação SOAP usando **Spyne**.
*   `streaming_pb2.py` e `streaming_pb2_grpc.py`: Arquivos gerados pelo compilador gRPC a partir do `.proto`.

### 📂 `APIs/javascript/`
Contém as implementações dos servidores utilizando **Node.js**.
*   `rest_api.js`: Implementação REST usando **Express**.
*   `graphql_api.js`: Implementação GraphQL usando **Apollo Server**.
*   `grpc_api.js`: Implementação gRPC usando `@grpc/grpc-js` e `@grpc/proto-loader`.
*   `soap_api.js`: Implementação SOAP usando a biblioteca `soap`.

### 📂 `APIs/shared/`
Contém as definições de interface (contratos) que garantem que ambas as linguagens falem a mesma "língua".

*   **`streaming.proto` (gRPC/Protocol Buffers):**
    *   **O que é:** É um arquivo de IDL (*Interface Definition Language*) que utiliza o formato **Protocol Buffers** (Protobuf).
    *   **Função:** Define a estrutura exata das mensagens de dados (como `Usuario`, `Musica`) e as assinaturas dos métodos do serviço (como `ListarUsuarios`). 
    *   **Importância:** Ele é independente de linguagem. A partir dele, o compilador `protoc` gera o código necessário para Python e Node.js, garantindo que o cliente e o servidor concordem exatamente sobre o formato dos dados binários trafegados.

*   **`streaming.wsdl` (SOAP/Web Services Description Language):**
    *   **O que é:** É um documento baseado em **XML** que descreve detalhadamente um serviço web.
    *   **Função:** Especifica as operações disponíveis, o formato das mensagens XML (via XSD - XML Schema Definition), os protocolos de transporte e o endereço (URL) do serviço.
    *   **Importância:** Funciona como um "contrato formal" rígido. Ferramentas e bibliotecas SOAP (como `zeep` no Python ou `soap` no Node.js) lêem este arquivo para saber exatamente como montar as requisições XML e como interpretar as respostas do servidor.

---

## 2. Como o Trabalho Funciona

### Fluxo de Dados
Todas as 8 APIs (4 Python + 4 Node.js) implementam a mesma lógica de negócio:
1.  **Usuários** podem ter **Playlists**.
2.  **Playlists** contêm **Músicas**.
3.  As APIs mantêm o estado **em memória** (in-memory). Isso significa que, se o servidor for reiniciado, os dados serão perdidos. Cada servidor tem seu próprio banco de dados em memória independente.

### Orquestração e Testes
*   `trabalho_6.md`: Contém a documentação principal, teoria sobre os protocolos e o guia de execução manual.
*   `run_apis.sh`: Script bash criado para abrir 8 terminais simultâneos, facilitando a subida de todos os serviços de uma vez para testes.
*   `locustfile.py`: Script de teste de performance que simula usuários acessando as APIs via REST, GraphQL, gRPC e SOAP.
*   `prepopulate_data.py`: Script auxiliar que pode ser usado para inserir dados iniciais (usuários, músicas, playlists) em todas as APIs simultaneamente antes de iniciar o teste de carga.

---

## 3. Resumo das Portas

| Tecnologia | Python | Node.js |
| :--- | :--- | :--- |
| **REST** | 8001 | 8011 |
| **GraphQL** | 8002 | 8012 |
| **gRPC** | 50051 | 50052 |
| **SOAP** | 8003 | 8013 |

---

## 4. Requisitos de Execução

1.  **Python:** É recomendado o uso do gerenciador `uv`. O comando padrão é `uv run python <arquivo>.py`.
2.  **Node.js:** Requer que as dependências tenham sido instaladas via `npm install` dentro da pasta `APIs/javascript/`. O comando padrão é `node <arquivo>.js`.
3.  **Terminal:** O script `run_apis.sh` tenta detectar automaticamente seu emulador de terminal (Gnome, Xfce, Konsole ou Xterm).
