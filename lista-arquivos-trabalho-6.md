# Lista de Arquivos do Trabalho 6

Esta é a relação de todos os arquivos desenvolvidos e utilizados para a realização do Trabalho 6 - APIs Distribuídas (Streaming de Música).

## 1. Contratos e Definições Compartilhadas
- `APIs/shared/streaming.proto`: Definição de interface Protocol Buffers para gRPC.
- `APIs/shared/streaming.wsdl`: Contrato Web Services Description Language para SOAP.

## 2. Implementações das APIs (Python)
- `APIs/python/rest_api.py`: API REST implementada com FastAPI.
- `APIs/python/graphql_api.py`: API GraphQL implementada com Strawberry e FastAPI.
- `APIs/python/grpc_api.py`: Servidor gRPC implementado com grpcio.
- `APIs/python/soap_api.py`: API SOAP implementada com Spyne.
- `APIs/python/streaming_pb2.py`: Stub gRPC gerado pelo compilador Protobuf.
- `APIs/python/streaming_pb2_grpc.py`: Stub de serviço gRPC gerado pelo compilador.

## 3. Implementações das APIs (Node.js/JavaScript)
- `APIs/javascript/rest_api.js`: API REST implementada com Express.
- `APIs/javascript/graphql_api.js`: API GraphQL implementada com Apollo Server.
- `APIs/javascript/grpc_api.js`: Servidor gRPC implementado com @grpc/grpc-js.
- `APIs/javascript/soap_api.js`: API SOAP implementada com o módulo soap do Node.js.
- `APIs/javascript/package.json`: Manifesto de dependências do ambiente Node.js.

## 4. Automação e Testes de Carga
- `locustfile.py`: Script do Locust contendo os usuários e tarefas para os 4 protocolos.
- `prepopulate_data.py`: Script para popular os bancos de dados em memória antes dos testes.
- `run_test_suite.py`: Orquestrador que executa a bateria de 8 testes (2 min cada) sequencialmente.
- `generate_results_charts.py`: Script para processar os CSVs do Locust e gerar os gráficos comparativos.

## 5. Documentação e Relatórios
- `instrucoes_6.md`: Documento original com as orientações do trabalho.
- `trabalho_6.md`: Relatório final unificado com teoria, guia de execução, resultados e análises.
- `documentacao_execucao_apis.md`: Guia técnico detalhado de como rodar e testar os serviços.
- `documentacao_trabalho_6.md`: Registro histórico das ações tomadas durante o desenvolvimento.
- `lista-arquivos-trabalho-6.md`: Este arquivo, listando a estrutura do projeto.

## 6. Resultados (Gerados dinamicamente)
- `locust_results/`: Pasta contendo os arquivos CSV brutos gerados pelo Locust.
- `comparativo_linguagens.png`: Gráfico de latência Python vs Node.js.
- `comparativo_tecnologias_python.png`: Comparativo interno de tecnologias em Python.
- `comparativo_tecnologias_node.png`: Comparativo interno de tecnologias em Node.js.
- `comparativo_falhas.png`: Gráfico de taxa de erros por tecnologia/linguagem.
- `prepopulated_user_ids.json`: IDs de usuários criados durante o setup.
- `prepopulated_music_ids.json`: IDs de músicas criados durante o setup.
- `prepopulated_playlist_ids.json`: IDs de playlists criados durante o setup.
