# Documentação do Trabalho 6

## O que foi realizado

A partir da leitura do arquivo `instrucoes_6.md`, notou-se que o documento introduzia um sistema distribuído para streaming de música que seria avaliado em **quatro tecnologias distintas**: REST, GraphQL, gRPC e SOAP. Entretanto, na "Seção 3 - Definição dos Contratos e Schemas Base", apenas os contratos de **GraphQL** (schema types) e **gRPC** (arquivo `.proto`) haviam sido definidos, enquanto as abordagens baseadas em REST e SOAP estavam ausentes do documento, além de haver problemas de formatação Markdown nas delimitações de blocos de código.

Sendo assim, interpretando o comando "faça o que se pede", as seguintes ações foram executadas:

1. **Correção de Formatação**: O texto original foi recuperado e os blocos de código para a sintaxe de GraphQL e gRPC foram devidamente delimitados e fechados para garantir uma visualização adequada.
2. **Definição da Especificação REST**: Foi adicionada a Seção 3.3 ao documento, contemplando os contratos para a API REST utilizando o padrão de especificação **OpenAPI 3.0**. Os mesmos endpoints/operações (CRUD de Usuários, Músicas e relacionamentos de Playlists) foram mapeados em rotas e verbos HTTP consistentes (`GET`, `POST`).
3. **Definição da Especificação SOAP**: Foi adicionada a Seção 3.4 contendo um **WSDL (Web Services Description Language)** simplificado para descrever os serviços SOAP, complementando assim o leque de 4 tecnologias citadas pela introdução do trabalho.
4. **Geração dos Resultados**: Todo o texto unificado (introdução + os 4 schemas/contratos corrigidos e implementados) foi escrito no arquivo `trabalho_6.md`, conforme solicitado.

Estas etapas garantem o alinhamento de base necessário caso se deseje implementar ou gerar o código dos microsserviços em Python e Node.js para qualquer um desses quatro protocolos, mantendo o estrito cumprimento das regras de negócios definidas.