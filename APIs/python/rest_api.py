from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid

app = FastAPI(title="Streaming REST API (Python)")

class Usuario(BaseModel):
    id: str
    nome: str
    idade: int

class UsuarioUpdate(BaseModel):
    nome: Optional[str] = None
    idade: Optional[int] = None

class Musica(BaseModel):
    id: str
    nome: str
    artista: str

class MusicaUpdate(BaseModel):
    nome: Optional[str] = None
    artista: Optional[str] = None

class Playlist(BaseModel):
    id: str
    nome: str
    usuario_id: str

class PlaylistUpdate(BaseModel):
    nome: Optional[str] = None

class MusicaPlaylist(BaseModel):
    musica_id: str

usuarios_db = []
musicas_db = []
playlists_db = []
playlist_musica_db = []

# USUÁRIOS - CRUD
@app.get("/usuarios", response_model=List[Usuario])
def listar_usuarios():
    return usuarios_db

@app.get("/usuarios/{id}", response_model=Usuario)
def obter_usuario(id: str):
    for u in usuarios_db:
        if u.id == id:
            return u
    raise HTTPException(status_code=404, detail="Usuário não encontrado")

@app.post("/usuarios", response_model=Usuario, status_code=201)
def criar_usuario(user: Usuario):
    if any(u.id == user.id for u in usuarios_db):
        raise HTTPException(status_code=400, detail="Usuário já existe")
    usuarios_db.append(user)
    return user

@app.put("/usuarios/{id}", response_model=Usuario)
def atualizar_usuario(id: str, update: UsuarioUpdate):
    for u in usuarios_db:
        if u.id == id:
            if update.nome is not None:
                u.nome = update.nome
            if update.idade is not None:
                u.idade = update.idade
            return u
    raise HTTPException(status_code=404, detail="Usuário não encontrado")

@app.delete("/usuarios/{id}")
def deletar_usuario(id: str):
    global usuarios_db
    if not any(u.id == id for u in usuarios_db):
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    usuarios_db = [u for u in usuarios_db if u.id != id]
    playlists_db[:] = [p for p in playlists_db if p.usuario_id != id]
    return {"message": "Usuário deletado"}

# MÚSICAS - CRUD
@app.get("/musicas", response_model=List[Musica])
def listar_musicas():
    return musicas_db

@app.get("/musicas/{id}", response_model=Musica)
def obter_musica(id: str):
    for m in musicas_db:
        if m.id == id:
            return m
    raise HTTPException(status_code=404, detail="Música não encontrada")

@app.post("/musicas", response_model=Musica, status_code=201)
def criar_musica(musica: Musica):
    if any(m.id == musica.id for m in musicas_db):
        raise HTTPException(status_code=400, detail="Música já existe")
    musicas_db.append(musica)
    return musica

@app.put("/musicas/{id}", response_model=Musica)
def atualizar_musica(id: str, update: MusicaUpdate):
    for m in musicas_db:
        if m.id == id:
            if update.nome is not None:
                m.nome = update.nome
            if update.artista is not None:
                m.artista = update.artista
            return m
    raise HTTPException(status_code=404, detail="Música não encontrada")

@app.delete("/musicas/{id}")
def deletar_musica(id: str):
    global musicas_db, playlist_musica_db
    if not any(m.id == id for m in musicas_db):
        raise HTTPException(status_code=404, detail="Música não encontrada")
    musicas_db = [m for m in musicas_db if m.id != id]
    playlist_musica_db[:] = [pm for pm in playlist_musica_db if pm[1] != id]
    return {"message": "Música deletada"}

# PLAYLISTS - CRUD
@app.get("/playlists", response_model=List[Playlist])
def listar_playlists():
    return playlists_db

@app.get("/playlists/{id}", response_model=Playlist)
def obter_playlist(id: str):
    for p in playlists_db:
        if p.id == id:
            return p
    raise HTTPException(status_code=404, detail="Playlist não encontrada")

@app.post("/playlists", response_model=Playlist, status_code=201)
def criar_playlist(playlist: Playlist):
    if not any(u.id == playlist.usuario_id for u in usuarios_db):
        raise HTTPException(status_code=400, detail="Usuário não existe")
    if any(p.id == playlist.id for p in playlists_db):
        raise HTTPException(status_code=400, detail="Playlist já existe")
    playlists_db.append(playlist)
    return playlist

@app.put("/playlists/{id}", response_model=Playlist)
def atualizar_playlist(id: str, update: PlaylistUpdate):
    for p in playlists_db:
        if p.id == id:
            if update.nome is not None:
                p.nome = update.nome
            return p
    raise HTTPException(status_code=404, detail="Playlist não encontrada")

@app.delete("/playlists/{id}")
def deletar_playlist(id: str):
    global playlists_db, playlist_musica_db
    if not any(p.id == id for p in playlists_db):
        raise HTTPException(status_code=404, detail="Playlist não encontrada")
    playlists_db = [p for p in playlists_db if p.id != id]
    playlist_musica_db[:] = [pm for pm in playlist_musica_db if pm[0] != id]
    return {"message": "Playlist deletada"}

# RELAÇÕES - GET playlists by usuario
@app.get("/usuarios/{usuario_id}/playlists", response_model=List[Playlist])
def listar_playlists_usuario(usuario_id: str):
    if not any(u.id == usuario_id for u in usuarios_db):
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return [p for p in playlists_db if p.usuario_id == usuario_id]

# RELAÇÕES - GET músicas by playlist
@app.get("/playlists/{playlist_id}/musicas", response_model=List[Musica])
def listar_musicas_playlist(playlist_id: str):
    if not any(p.id == playlist_id for p in playlists_db):
        raise HTTPException(status_code=404, detail="Playlist não encontrada")
    musica_ids = [pm[1] for pm in playlist_musica_db if pm[0] == playlist_id]
    return [m for m in musicas_db if m.id in musica_ids]

# RELAÇÕES - GET playlists by música
@app.get("/musicas/{musica_id}/playlists", response_model=List[Playlist])
def listar_playlists_musica(musica_id: str):
    if not any(m.id == musica_id for m in musicas_db):
        raise HTTPException(status_code=404, detail="Música não encontrada")
    playlist_ids = [pm[0] for pm in playlist_musica_db if pm[1] == musica_id]
    return [p for p in playlists_db if p.id in playlist_ids]

# RELAÇÕES - POST música in playlist
@app.post("/playlists/{playlist_id}/musicas/{musica_id}", status_code=201)
def adicionar_musica_playlist(playlist_id: str, musica_id: str):
    if not any(p.id == playlist_id for p in playlists_db):
        raise HTTPException(status_code=404, detail="Playlist não encontrada")
    if not any(m.id == musica_id for m in musicas_db):
        raise HTTPException(status_code=404, detail="Música não encontrada")
    if any(pm == (playlist_id, musica_id) for pm in playlist_musica_db):
        raise HTTPException(status_code=400, detail="Música já existe na playlist")
    playlist_musica_db.append((playlist_id, musica_id))
    return {"message": "Música adicionada à playlist"}

# RELAÇÕES - DELETE música from playlist
@app.delete("/playlists/{playlist_id}/musicas/{musica_id}")
def remover_musica_playlist(playlist_id: str, musica_id: str):
    global playlist_musica_db
    if not any(p.id == playlist_id for p in playlists_db):
        raise HTTPException(status_code=404, detail="Playlist não encontrada")
    if not any(m.id == musica_id for m in musicas_db):
        raise HTTPException(status_code=404, detail="Música não encontrada")
    if not any(pm == (playlist_id, musica_id) for pm in playlist_musica_db):
        raise HTTPException(status_code=404, detail="Música não está na playlist")
    playlist_musica_db = [pm for pm in playlist_musica_db if pm != (playlist_id, musica_id)]
    return {"message": "Música removida da playlist"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)