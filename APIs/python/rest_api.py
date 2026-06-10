from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import uuid

app = FastAPI(title="Streaming REST API (Python)")

class Usuario(BaseModel):
    id: str
    nome: str
    idade: int

class Musica(BaseModel):
    id: str
    nome: str
    artista: str

class Playlist(BaseModel):
    id: str
    nome: str
    usuario_id: str

class MusicaPlaylist(BaseModel):
    musica_id: str

# Database in-memory
usuarios_db = []
musicas_db = []
playlists_db = []
playlist_musica_db = [] # tuples of (playlist_id, musica_id)

@app.get("/usuarios", response_model=List[Usuario])
def listar_usuarios():
    return usuarios_db

@app.post("/usuarios", response_model=Usuario, status_code=201)
def criar_usuario(user: Usuario):
    usuarios_db.append(user)
    return user

@app.get("/musicas", response_model=List[Musica])
def listar_musicas():
    return musicas_db

@app.post("/musicas", response_model=Musica, status_code=201)
def criar_musica(musica: Musica):
    musicas_db.append(musica)
    return musica

@app.get("/usuarios/{id}/playlists", response_model=List[Playlist])
def listar_playlists_usuario(id: str):
    return [p for p in playlists_db if p.usuario_id == id]

@app.post("/playlists", response_model=Playlist, status_code=201)
def criar_playlist(playlist: Playlist):
    playlists_db.append(playlist)
    return playlist

@app.get("/playlists/{id}/musicas", response_model=List[Musica])
def listar_musicas_playlist(id: str):
    musica_ids = [pm[1] for pm in playlist_musica_db if pm[0] == id]
    return [m for m in musicas_db if m.id in musica_ids]

@app.post("/playlists/{id}/musicas", status_code=201)
def adicionar_musica_playlist(id: str, payload: MusicaPlaylist):
    playlist_musica_db.append((id, payload.musica_id))
    return {"message": "Música adicionada"}

@app.get("/musicas/{id}/playlists", response_model=List[Playlist])
def listar_playlists_musica(id: str):
    playlist_ids = [pm[0] for pm in playlist_musica_db if pm[1] == id]
    return [p for p in playlists_db if p.id in playlist_ids]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)