# ✅ Cliente gRPC Implementado e Pronto para Uso

## 📋 O que foi desenvolvido

Um **cliente gRPC completo em Python** (`grpc_client.py`) que:

✅ Suporta **Python (porta 8003)** e **JavaScript (porta 9003)**  
✅ Implementa todas as operações CRUD  
✅ Acessa todos os serviços (Usuários, Músicas, Playlists, Relações)  
✅ Interface CLI intuitiva com `--porta {PORTA} {SERVICO} {OPERACAO} [PARAMS]`  
✅ Tratamento de erros e mensagens amigáveis  
✅ Documentação completa com exemplos  

---

## 🎯 Sintaxe

```bash
python grpc_client.py --porta {PORTA} {SERVICO} {OPERACAO} [PARAMETROS]
```

### Portas
- `8003` - API gRPC Python
- `9003` - API gRPC JavaScript

---

## 📚 Exemplos Rápidos

### Usuários
```bash
# Listar
python grpc_client.py --porta 8003 usuarios listar

# Obter um
python grpc_client.py --porta 8003 usuarios obter --id u1

# Criar
python grpc_client.py --porta 8003 usuarios criar --id u1 --nome "João" --idade 30

# Atualizar
python grpc_client.py --porta 8003 usuarios atualizar --id u1 --nome "Silva" --idade 31

# Deletar
python grpc_client.py --porta 8003 usuarios deletar --id u1
```

### Músicas
```bash
# Listar
python grpc_client.py --porta 8003 musicas listar

# Criar
python grpc_client.py --porta 8003 musicas criar --id m1 --nome "Imagine" --artista "Lennon"

# Atualizar
python grpc_client.py --porta 8003 musicas atualizar --id m1 --nome "Imagine" --artista "Lennon Updated"

# Deletar
python grpc_client.py --porta 8003 musicas deletar --id m1
```

### Playlists
```bash
# Listar
python grpc_client.py --porta 8003 playlists listar

# Criar (requer usuário existente)
python grpc_client.py --porta 8003 playlists criar --id p1 --nome "Favorites" --usuario_id u1

# Atualizar
python grpc_client.py --porta 8003 playlists atualizar --id p1 --nome "My Favorites"

# Deletar
python grpc_client.py --porta 8003 playlists deletar --id p1
```

### Relações
```bash
# Playlists de um usuário
python grpc_client.py --porta 8003 relacoes usuarios-playlists --usuario_id u1

# Músicas de uma playlist
python grpc_client.py --porta 8003 relacoes playlist-musicas --playlist_id p1

# Playlists com uma música
python grpc_client.py --porta 8003 relacoes musica-playlists --musica_id m1

# Adicionar música à playlist
python grpc_client.py --porta 8003 relacoes adicionar-musica --playlist_id p1 --musica_id m1

# Remover música de playlist
python grpc_client.py --porta 8003 relacoes remover-musica --playlist_id p1 --musica_id m1
```

---

## 🔄 Fluxo Completo de Teste

```bash
# 1. Criar usuário
python grpc_client.py --porta 8003 usuarios criar --id u1 --nome "João" --idade 30

# 2. Criar música
python grpc_client.py --porta 8003 musicas criar --id m1 --nome "Imagine" --artista "Lennon"

# 3. Criar playlist
python grpc_client.py --porta 8003 playlists criar --id p1 --nome "Favorites" --usuario_id u1

# 4. Adicionar música à playlist
python grpc_client.py --porta 8003 relacoes adicionar-musica --playlist_id p1 --musica_id m1

# 5. Listar músicas da playlist
python grpc_client.py --porta 8003 relacoes playlist-musicas --playlist_id p1

# 6. Listar playlists do usuário
python grpc_client.py --porta 8003 relacoes usuarios-playlists --usuario_id u1

# 7. Remover música da playlist
python grpc_client.py --porta 8003 relacoes remover-musica --playlist_id p1 --musica_id m1

# 8. Deletar playlist
python grpc_client.py --porta 8003 playlists deletar --id p1

# 9. Deletar música
python grpc_client.py --porta 8003 musicas deletar --id m1

# 10. Deletar usuário
python grpc_client.py --porta 8003 usuarios deletar --id u1
```

---

## 🔀 Funciona com Ambas as APIs

O mesmo cliente funciona com Python e JavaScript, apenas mudando a porta:

```bash
# Python API (gRPC)
python grpc_client.py --porta 8003 usuarios listar

# JavaScript API (gRPC)
python grpc_client.py --porta 9003 usuarios listar
```

---

## 📖 Documentação Completa

Veja `APIs/GRPC_CLIENT.md` para:
- Detalhes de cada operação
- Parâmetros necessários
- Formatos de saída
- Tratamento de erros
- Tabela de referência rápida

---

## 📁 Arquivos

- **`APIs/grpc_client.py`** - Cliente implementado (330+ linhas, 5 serviços)
- **`APIs/GRPC_CLIENT.md`** - Documentação completa com exemplos

---

## ✨ Características

✅ **Interface CLI intuitiva** - Subcomandos e flags nomeadas  
✅ **Parâmetros opcionais** - `--porta` com padrão 8003  
✅ **Mensagens amigáveis** - Erros claros e resultados formatados  
✅ **Validação automática** - Requer parâmetros obrigatórios  
✅ **Ajuda integrada** - `--help` em todos os níveis  
✅ **Compatible com ambas as APIs** - Mesma interface para Python e JS  

---

## 🚀 Próximos Passos (Opcional)

1. **Testar o cliente** - Execute alguns comandos do exemplo acima
2. **Explorar ajuda** - `python grpc_client.py --help`
3. **Ler a documentação** - `APIs/GRPC_CLIENT.md`
4. **Integrar com scripts** - Use o cliente em pipelines ou testes automatizados

---

## 📞 Resumo

| Item | Status |
|------|--------|
| Cliente Python gRPC | ✅ Implementado |
| Suporte Python (8003) | ✅ Testado |
| Suporte JavaScript (9003) | ✅ Testado |
| CRUD Usuários | ✅ Completo |
| CRUD Músicas | ✅ Completo |
| CRUD Playlists | ✅ Completo |
| Relações | ✅ Completo (5 operações) |
| Documentação | ✅ Detalhada |
| Exemplos | ✅ Múltiplos |
| Tratamento Erros | ✅ Implementado |

---

**✅ Cliente gRPC 100% PRONTO PARA USO**
