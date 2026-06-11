# Cliente gRPC - Documentação Completa

## 🎯 Visão Geral

Cliente Python para comunicação com os serviços gRPC do StreamingService.

**Suporta ambas as APIs:**
- **Python** - gRPC na porta **8003**
- **JavaScript** - gRPC na porta **9003**

---

## 📋 Sintaxe Geral

```bash
python grpc_client.py --porta {PORTA} {SERVICO} {OPERACAO} [PARAMETROS]
```

### Portas
- `8003` - API gRPC Python (padrão)
- `9003` - API gRPC JavaScript

---

## 👤 USUÁRIOS

### Listar Todos
```bash
python grpc_client.py --porta 8003 usuarios listar
```
**Saída:**
```
Total de usuários: 2
  id=u1, nome=João, idade=30
  id=u2, nome=Maria, idade=25
```

### Obter Um Usuário
```bash
python grpc_client.py --porta 8003 usuarios obter --id u1
```
**Parâmetros:**
- `--id` (obrigatório) - ID do usuário

**Saída:**
```
Usuário: id=u1, nome=João, idade=30
```

### Criar Usuário
```bash
python grpc_client.py --porta 8003 usuarios criar --id u3 --nome "Pedro" --idade 28
```
**Parâmetros:**
- `--id` (obrigatório) - ID único
- `--nome` (obrigatório) - Nome
- `--idade` (obrigatório) - Idade (inteiro)

**Saída:**
```
Usuário criado: id=u3, nome=Pedro, idade=28
```

### Atualizar Usuário
```bash
python grpc_client.py --porta 8003 usuarios atualizar --id u1 --nome "João Silva" --idade 31
```
**Parâmetros:**
- `--id` (obrigatório) - ID do usuário
- `--nome` (obrigatório) - Novo nome
- `--idade` (obrigatório) - Nova idade

**Saída:**
```
Usuário atualizado: id=u1, nome=João Silva, idade=31
```

### Deletar Usuário
```bash
python grpc_client.py --porta 8003 usuarios deletar --id u1
```
**Parâmetros:**
- `--id` (obrigatório) - ID do usuário

**Saída:**
```
Usuário u1 deletado com sucesso
```

---

## 🎵 MÚSICAS

### Listar Todas
```bash
python grpc_client.py --porta 8003 musicas listar
```
**Saída:**
```
Total de músicas: 2
  id=m1, nome=Imagine, artista=John Lennon
  id=m2, nome=Bohemian Rhapsody, artista=Queen
```

### Obter Uma Música
```bash
python grpc_client.py --porta 8003 musicas obter --id m1
```
**Parâmetros:**
- `--id` (obrigatório) - ID da música

**Saída:**
```
Música: id=m1, nome=Imagine, artista=John Lennon
```

### Criar Música
```bash
python grpc_client.py --porta 8003 musicas criar --id m3 --nome "Stairway to Heaven" --artista "Led Zeppelin"
```
**Parâmetros:**
- `--id` (obrigatório) - ID único
- `--nome` (obrigatório) - Nome da música
- `--artista` (obrigatório) - Artista

**Saída:**
```
Música criada: id=m3, nome=Stairway to Heaven, artista=Led Zeppelin
```

### Atualizar Música
```bash
python grpc_client.py --porta 8003 musicas atualizar --id m1 --nome "Imagine (Remaster)" --artista "Lennon"
```
**Parâmetros:**
- `--id` (obrigatório) - ID da música
- `--nome` (obrigatório) - Novo nome
- `--artista` (obrigatório) - Novo artista

**Saída:**
```
Música atualizada: id=m1, nome=Imagine (Remaster), artista=Lennon
```

### Deletar Música
```bash
python grpc_client.py --porta 8003 musicas deletar --id m1
```
**Parâmetros:**
- `--id` (obrigatório) - ID da música

**Saída:**
```
Música m1 deletada com sucesso
```

---

## 📻 PLAYLISTS

### Listar Todas
```bash
python grpc_client.py --porta 8003 playlists listar
```
**Saída:**
```
Total de playlists: 2
  id=p1, nome=Favorites, usuario_id=u1
  id=p2, nome=Rock Classics, usuario_id=u2
```

### Obter Uma Playlist
```bash
python grpc_client.py --porta 8003 playlists obter --id p1
```
**Parâmetros:**
- `--id` (obrigatório) - ID da playlist

**Saída:**
```
Playlist: id=p1, nome=Favorites, usuario_id=u1
```

### Criar Playlist
```bash
python grpc_client.py --porta 8003 playlists criar --id p3 --nome "My Collection" --usuario_id u1
```
**Parâmetros:**
- `--id` (obrigatório) - ID único
- `--nome` (obrigatório) - Nome da playlist
- `--usuario_id` (obrigatório) - ID do usuário proprietário

**Saída:**
```
Playlist criada: id=p3, nome=My Collection, usuario_id=u1
```

### Atualizar Playlist
```bash
python grpc_client.py --porta 8003 playlists atualizar --id p1 --nome "My Favorites"
```
**Parâmetros:**
- `--id` (obrigatório) - ID da playlist
- `--nome` (obrigatório) - Novo nome

**Saída:**
```
Playlist atualizada: id=p1, nome=My Favorites, usuario_id=u1
```

### Deletar Playlist
```bash
python grpc_client.py --porta 8003 playlists deletar --id p1
```
**Parâmetros:**
- `--id` (obrigatório) - ID da playlist

**Saída:**
```
Playlist p1 deletada com sucesso
```

---

## 🔗 RELAÇÕES

### Listar Playlists de um Usuário
```bash
python grpc_client.py --porta 8003 relacoes usuarios-playlists --usuario_id u1
```
**Parâmetros:**
- `--usuario_id` (obrigatório) - ID do usuário

**Saída:**
```
Playlists do usuário u1:
  id=p1, nome=Favorites
  id=p2, nome=Rock Collection
```

### Listar Músicas de uma Playlist
```bash
python grpc_client.py --porta 8003 relacoes playlist-musicas --playlist_id p1
```
**Parâmetros:**
- `--playlist_id` (obrigatório) - ID da playlist

**Saída:**
```
Músicas da playlist p1:
  id=m1, nome=Imagine, artista=John Lennon
  id=m2, nome=Bohemian Rhapsody, artista=Queen
```

### Listar Playlists Contendo uma Música
```bash
python grpc_client.py --porta 8003 relacoes musica-playlists --musica_id m1
```
**Parâmetros:**
- `--musica_id` (obrigatório) - ID da música

**Saída:**
```
Playlists com a música m1:
  id=p1, nome=Favorites
  id=p3, nome=Classics
```

### Adicionar Música a Playlist
```bash
python grpc_client.py --porta 8003 relacoes adicionar-musica --playlist_id p1 --musica_id m1
```
**Parâmetros:**
- `--playlist_id` (obrigatório) - ID da playlist
- `--musica_id` (obrigatório) - ID da música

**Saída:**
```
Música m1 adicionada à playlist p1
Playlist: id=p1, nome=Favorites
```

### Remover Música de Playlist
```bash
python grpc_client.py --porta 8003 relacoes remover-musica --playlist_id p1 --musica_id m1
```
**Parâmetros:**
- `--playlist_id` (obrigatório) - ID da playlist
- `--musica_id` (obrigatório) - ID da música

**Saída:**
```
Música m1 removida da playlist p1
Playlist: id=p1, nome=Favorites
```

---

## 🔄 Teste Completo (Fluxo)

### 1. Criar um usuário
```bash
python grpc_client.py --porta 8003 usuarios criar --id u1 --nome "João" --idade 30
```

### 2. Criar uma música
```bash
python grpc_client.py --porta 8003 musicas criar --id m1 --nome "Imagine" --artista "Lennon"
```

### 3. Criar uma playlist para o usuário
```bash
python grpc_client.py --porta 8003 playlists criar --id p1 --nome "Favorites" --usuario_id u1
```

### 4. Adicionar música à playlist
```bash
python grpc_client.py --porta 8003 relacoes adicionar-musica --playlist_id p1 --musica_id m1
```

### 5. Listar músicas da playlist
```bash
python grpc_client.py --porta 8003 relacoes playlist-musicas --playlist_id p1
```

### 6. Remover música da playlist
```bash
python grpc_client.py --porta 8003 relacoes remover-musica --playlist_id p1 --musica_id m1
```

### 7. Deletar playlist
```bash
python grpc_client.py --porta 8003 playlists deletar --id p1
```

### 8. Deletar música
```bash
python grpc_client.py --porta 8003 musicas deletar --id m1
```

### 9. Deletar usuário
```bash
python grpc_client.py --porta 8003 usuarios deletar --id u1
```

---

## ⚠️ Tratamento de Erros

O cliente trata automaticamente erros gRPC e exibe mensagens amigáveis:

### Exemplo: Usuário não encontrado
```bash
python grpc_client.py --porta 8003 usuarios obter --id inexistente
```
**Saída:**
```
Erro: Usuário não encontrado
```

### Exemplo: ID duplicado
```bash
python grpc_client.py --porta 8003 usuarios criar --id u1 --nome "Novo" --idade 25
python grpc_client.py --porta 8003 usuarios criar --id u1 --nome "Outro" --idade 30
```
**Saída (segunda chamada):**
```
Erro: Usuário já existe
```

---

## 🔧 Diferenças entre Python (8003) e JavaScript (9003)

Ambas implementam o mesmo protocolo gRPC, então o cliente funciona idêntico:

```bash
# Python API
python grpc_client.py --porta 8003 usuarios listar

# JavaScript API (mesmos comandos, porta diferente)
python grpc_client.py --porta 9003 usuarios listar
```

A única diferença é a porta:
- **8003** → API gRPC Python (FastAPI/grpcio)
- **9003** → API gRPC JavaScript (Node.js/@grpc/grpc-js)

---

## 📖 Ajuda

Para ver todos os comandos disponíveis:
```bash
python grpc_client.py --help
```

Para ver ajuda de um serviço específico:
```bash
python grpc_client.py usuarios --help
python grpc_client.py musicas --help
python grpc_client.py playlists --help
python grpc_client.py relacoes --help
```

Para ver ajuda de uma operação:
```bash
python grpc_client.py usuarios criar --help
python grpc_client.py relacoes adicionar-musica --help
```

---

## 🚀 Resumo

| Recurso | Operação | Comando |
|---------|----------|---------|
| **Usuário** | Listar | `usuarios listar` |
| | Obter | `usuarios obter --id ID` |
| | Criar | `usuarios criar --id ID --nome NOME --idade IDADE` |
| | Atualizar | `usuarios atualizar --id ID --nome NOME --idade IDADE` |
| | Deletar | `usuarios deletar --id ID` |
| **Música** | Listar | `musicas listar` |
| | Obter | `musicas obter --id ID` |
| | Criar | `musicas criar --id ID --nome NOME --artista ARTISTA` |
| | Atualizar | `musicas atualizar --id ID --nome NOME --artista ARTISTA` |
| | Deletar | `musicas deletar --id ID` |
| **Playlist** | Listar | `playlists listar` |
| | Obter | `playlists obter --id ID` |
| | Criar | `playlists criar --id ID --nome NOME --usuario_id USER_ID` |
| | Atualizar | `playlists atualizar --id ID --nome NOME` |
| | Deletar | `playlists deletar --id ID` |
| **Relações** | User→Playlists | `relacoes usuarios-playlists --usuario_id ID` |
| | Playlist→Músicas | `relacoes playlist-musicas --playlist_id ID` |
| | Música→Playlists | `relacoes musica-playlists --musica_id ID` |
| | Adicionar | `relacoes adicionar-musica --playlist_id ID --musica_id ID` |
| | Remover | `relacoes remover-musica --playlist_id ID --musica_id ID` |
