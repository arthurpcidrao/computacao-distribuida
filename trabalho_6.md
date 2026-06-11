# Trabalho 6 - Benchmark de APIs Distribuídas (Streaming de Música)

## 1. Introdução e Objetivo
Este trabalho realiza uma análise comparativa de performance entre quatro estilos arquiteturais de APIs: **REST**, **GraphQL**, **gRPC** e **SOAP**, implementados em duas linguagens distintas: **Python** e **Node.js (JavaScript)**. O foco é avaliar a latência (p95), o throughput (req/s) e a eficiência de transporte (tamanho do conteúdo) sob diferentes níveis de carga (30, 40 e 50 usuários simultâneos).

---

## 2. Inventário de Arquivos
- **`APIs/`**: Código-fonte das 8 instâncias de serviço.
- **`shared/`**: Contratos `streaming.proto` e `streaming.wsdl`.
- **`main.sh`**: Script para iniciar e popular todas as APIs para testes manuais.
- **`seed_data.py`**: Script de ingestão massiva de dados (1000 usuários/músicas).
- **`locustfile.py`**: Definição das tarefas de carga (focadas em leitura).
- **`run_tests.sh`**: Orquestrador em Bash do ciclo completo de benchmark.
- **`consolidar_resultados.py`**: Processador estatístico e gerador de gráficos.
- **`verify_apis.py`**: Script de validação funcional pós-correção.

---

## 3. Como Executar as APIs e os Testes

### 3.1. Inicialização Rápida (Recomendado)
Para subir todas as 8 APIs e popular os dados de uma só vez para testes manuais:
```bash
chmod +x main.sh
./main.sh
```

### 3.2. Execução Automatizada (Benchmark)
Para reproduzir os resultados e gerar os gráficos deste relatório:
```bash
chmod +x run_tests.sh
./run_tests.sh
```

---

## 4. Guia de Teste CRUD via CLI (cURL)

Abaixo estão os comandos para testar a criação (POST/Mutation) e recuperação (GET/Query) de dados em cada arquitetura. 
*Nota: Utilize as portas **8001-8004** para Python e **9001-9004** para Node.js.*

### 4.1. REST (Portas 8001/9001)
- **Criar Usuário (POST):**
```bash
curl -X POST http://localhost:9001/usuarios -H "Content-Type: application/json" -d '{"id":"u1001","nome":"Novo Usuario","idade":30}'
```
- **Recuperar Usuários (GET):**
```bash
curl http://localhost:9001/usuarios
```

### 4.2. GraphQL (Portas 8002/9002)
- **Criar Música (Mutation):**
```bash
curl -X POST http://localhost:9002 -H "Content-Type: application/json" -d '{"query": "mutation { criarMusica(id:\"m1001\", nome:\"Nova Musica\", artista:\"Novo Artista\") { id nome } }"}'
```
- **Listar Usuários (Query):**
```bash
curl -X POST http://localhost:9002 -H "Content-Type: application/json" -d '{"query": "{ listarUsuarios { id nome idade } }"}'
```

### 4.3. gRPC (Portas 8003/9003)
*Requer `grpcurl` instalado.*
- **Criar Playlist:**
```bash
grpcurl -plaintext -proto APIs/shared/streaming.proto -d '{"id": "p101", "nome": "Minha Playlist", "usuario_id": "u1"}' localhost:9003 streaming.StreamingService/CriarPlaylist
```
- **Listar Usuários:**
```bash
grpcurl -plaintext -proto APIs/shared/streaming.proto localhost:9003 streaming.StreamingService/ListarUsuarios
```

### 4.4. SOAP (Portas 8004/9004)
- **Criar Usuário:**
```bash
curl -X POST http://localhost:9004/soap -H "Content-Type: text/xml" -d '<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:wsdl="http://streaming.com/wsdl"><soapenv:Body><wsdl:CriarUsuarioRequest><wsdl:id>u2000</wsdl:id><wsdl:nome>Soap User</wsdl:nome><wsdl:idade>45</wsdl:idade></wsdl:CriarUsuarioRequest></soapenv:Body></soapenv:Envelope>'
```
- **Listar Usuários:**
```bash
curl -X POST http://localhost:9004/soap -H "Content-Type: text/xml" -d '<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:wsdl="http://streaming.com/wsdl"><soapenv:Body><wsdl:ListarUsuarios/></soapenv:Body></soapenv:Envelope>'
```

---

## 5. Metodologia de Benchmark

Os testes foram executados de forma **individual e isolada** para cada carga (30, 40, 50 usuários):
1.  A API era reiniciada.
2.  Seed de **1000 usuários, 1000 músicas e 100 playlists**.
3.  Locust executava apenas requisições de leitura (GETs) por **2 minutos**, com rampa de **10 usuários/s**.
4.  **Limite de Erro**: 10%. Resultados acima deste patamar foram considerados saturação tecnológica.

---

## 6. Resultados e Análises Visuais

*Os números apresentados abaixo são extraídos da coluna **95% Response Time** (p95) do relatório agregado do Locust.*

### 6.1. Performance p95: REST
![p95 REST](charts/p95_rest.png)
**Justificativa**: O JavaScript apresentou latência drasticamente menor. O modelo de Event Loop do Node.js é otimizado para lidar com requisições HTTP de alta frequência sem o overhead de threads do Python.

### 6.2. Performance p95: GraphQL
![p95 GraphQL](charts/p95_graphql.png)
**Justificativa**: O Apollo Server (Node.js) mostrou-se mais resiliente. O aumento da latência no Python (Strawberry) indica um gargalo no processamento da AST (Abstract Syntax Tree) do GraphQL sob concorrência.

### 6.3. Performance p95: gRPC
![p95 gRPC](charts/p95_grpc.png)
**Justificativa**: Em ambas as linguagens, o gRPC foi imbatível (~2ms). O custo de serialização binária é insignificante, tornando o teste limitado apenas pela velocidade da rede local.

### 6.4. Performance p95: SOAP
![p95 SOAP](charts/p95_soap.png)
**Justificativa**: O SOAP apresentou tempos de resposta altíssimos. O custo de serializar/deserializar XML é massivo e escalou exponencialmente em Python para 50 usuários.

### 6.5. Eficiência de Transporte (Payload Size)
![Tamanho do Conteúdo](charts/content_size.png)
**Justificativa**: O gRPC é o mais eficiente (payloads binários compactos). O SOAP é o mais "pesado" devido à verbosidade inerente das tags XML.

---

## 7. Conclusão

### 7.1. Qual API é mais rápida?
**Vencedor: gRPC.** 
Sua arquitetura binária sobre HTTP/2 elimina os gargalos de parsing de texto e latência de conexão.

### 7.2. Qual linguagem é mais rápida?
**Vencedor: JavaScript (Node.js).** 
Apresentou latência consistentemente menor e maior estabilidade sob carga, especialmente em protocolos baseados em texto.

---
*Relatório final gerado em 10 de Junho de 2026.*