import strawberry
from fastapi import FastAPI
from typing import List
import uuid

# Database in-memory
usuarios_db = []
musicas_db = []
playlists_db = []
playlist_musica_db = []

@strawberry.type
class Musica:
    id: strawberry.ID
    nome: str
    artista: str

@strawberry.type
class Playlist:
    id: strawberry.ID
    nome: str
    usuario_id: str

    @strawberry.field
    def musicas(self) -> List[Musica]:
        m_ids = [pm[1] for pm in playlist_musica_db if pm[0] == self.id]
        return [m for m in musicas_db if m.id in m_ids]

@strawberry.type
class Usuario:
    id: strawberry.ID
    nome: str
    idade: int

    @strawberry.field
    def playlists(self) -> List[Playlist]:
        return [p for p in playlists_db if p.usuario_id == self.id]

@strawberry.type
class Query:
    @strawberry.field
    def listar_usuarios(self) -> List[Usuario]:
        return usuarios_db

    @strawberry.field
    def listar_musicas(self) -> List[Musica]:
        return musicas_db

    @strawberry.field
    def listar_playlists_por_usuario(self, usuario_id: strawberry.ID) -> List[Playlist]:
        return [p for p in playlists_db if p.usuario_id == usuario_id]

    @strawberry.field
    def listar_musicas_por_playlist(self, playlist_id: strawberry.ID) -> List[Musica]:
        m_ids = [pm[1] for pm in playlist_musica_db if pm[0] == playlist_id]
        return [m for m in musicas_db if m.id in m_ids]

@strawberry.type
class Mutation:
    @strawberry.mutation
    def criar_usuario(self, nome: str, idade: int) -> Usuario:
        u = Usuario(id=strawberry.ID(str(uuid.uuid4())), nome=nome, idade=idade)
        usuarios_db.append(u)
        return u

    @strawberry.mutation
    def criar_musica(self, nome: str, artista: str) -> Musica:
        m = Musica(id=strawberry.ID(str(uuid.uuid4())), nome=nome, artista=artista)
        musicas_db.append(m)
        return m

    @strawberry.mutation
    def criar_playlist(self, nome: str, usuario_id: strawberry.ID) -> Playlist:
        p = Playlist(id=strawberry.ID(str(uuid.uuid4())), nome=nome, usuario_id=usuario_id)
        playlists_db.append(p)
        return p

    @strawberry.mutation
    def adicionar_musica_playlist(self, playlist_id: strawberry.ID, musica_id: strawberry.ID) -> Playlist:
        playlist_musica_db.append((playlist_id, musica_id))
        return next(p for p in playlists_db if p.id == playlist_id)

schema = strawberry.Schema(query=Query, mutation=Mutation)

from strawberry.fastapi import GraphQLRouter
graphql_app = GraphQLRouter(schema)

app = FastAPI(title="Streaming GraphQL API (Python)")
app.include_router(graphql_app, prefix="/graphql")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)