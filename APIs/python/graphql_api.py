import strawberry
from fastapi import FastAPI
from typing import List, Optional

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
    def obter_usuario(self, id: strawberry.ID) -> Optional[Usuario]:
        for u in usuarios_db:
            if u.id == id:
                return u
        return None

    @strawberry.field
    def listar_musicas(self) -> List[Musica]:
        return musicas_db

    @strawberry.field
    def obter_musica(self, id: strawberry.ID) -> Optional[Musica]:
        for m in musicas_db:
            if m.id == id:
                return m
        return None

    @strawberry.field
    def listar_playlists(self) -> List[Playlist]:
        return playlists_db

    @strawberry.field
    def obter_playlist(self, id: strawberry.ID) -> Optional[Playlist]:
        for p in playlists_db:
            if p.id == id:
                return p
        return None

    @strawberry.field
    def listar_playlists_por_usuario(self, usuario_id: strawberry.ID) -> List[Playlist]:
        return [p for p in playlists_db if p.usuario_id == usuario_id]

    @strawberry.field
    def listar_musicas_por_playlist(self, playlist_id: strawberry.ID) -> List[Musica]:
        m_ids = [pm[1] for pm in playlist_musica_db if pm[0] == playlist_id]
        return [m for m in musicas_db if m.id in m_ids]

    @strawberry.field
    def listar_playlists_por_musica(self, musica_id: strawberry.ID) -> List[Playlist]:
        p_ids = [pm[0] for pm in playlist_musica_db if pm[1] == musica_id]
        return [p for p in playlists_db if p.id in p_ids]

@strawberry.type
class Mutation:
    @strawberry.mutation
    def criar_usuario(self, id: strawberry.ID, nome: str, idade: int) -> Usuario:
        if any(u.id == id for u in usuarios_db):
            raise Exception("Usuário já existe")
        u = Usuario(id=id, nome=nome, idade=idade)
        usuarios_db.append(u)
        return u

    @strawberry.mutation
    def atualizar_usuario(self, id: strawberry.ID, nome: Optional[str] = None, idade: Optional[int] = None) -> Usuario:
        for u in usuarios_db:
            if u.id == id:
                if nome is not None:
                    u.nome = nome
                if idade is not None:
                    u.idade = idade
                return u
        raise Exception("Usuário não encontrado")

    @strawberry.mutation
    def deletar_usuario(self, id: strawberry.ID) -> bool:
        global usuarios_db, playlists_db
        if not any(u.id == id for u in usuarios_db):
            raise Exception("Usuário não encontrado")
        usuarios_db = [u for u in usuarios_db if u.id != id]
        playlists_db[:] = [p for p in playlists_db if p.usuario_id != id]
        return True

    @strawberry.mutation
    def criar_musica(self, id: strawberry.ID, nome: str, artista: str) -> Musica:
        if any(m.id == id for m in musicas_db):
            raise Exception("Música já existe")
        m = Musica(id=id, nome=nome, artista=artista)
        musicas_db.append(m)
        return m

    @strawberry.mutation
    def atualizar_musica(self, id: strawberry.ID, nome: Optional[str] = None, artista: Optional[str] = None) -> Musica:
        for m in musicas_db:
            if m.id == id:
                if nome is not None:
                    m.nome = nome
                if artista is not None:
                    m.artista = artista
                return m
        raise Exception("Música não encontrada")

    @strawberry.mutation
    def deletar_musica(self, id: strawberry.ID) -> bool:
        global musicas_db, playlist_musica_db
        if not any(m.id == id for m in musicas_db):
            raise Exception("Música não encontrada")
        musicas_db = [m for m in musicas_db if m.id != id]
        playlist_musica_db[:] = [pm for pm in playlist_musica_db if pm[1] != id]
        return True

    @strawberry.mutation
    def criar_playlist(self, id: strawberry.ID, nome: str, usuario_id: strawberry.ID) -> Playlist:
        if not any(u.id == usuario_id for u in usuarios_db):
            raise Exception("Usuário não existe")
        if any(p.id == id for p in playlists_db):
            raise Exception("Playlist já existe")
        p = Playlist(id=id, nome=nome, usuario_id=usuario_id)
        playlists_db.append(p)
        return p

    @strawberry.mutation
    def atualizar_playlist(self, id: strawberry.ID, nome: Optional[str] = None) -> Playlist:
        for p in playlists_db:
            if p.id == id:
                if nome is not None:
                    p.nome = nome
                return p
        raise Exception("Playlist não encontrada")

    @strawberry.mutation
    def deletar_playlist(self, id: strawberry.ID) -> bool:
        global playlists_db, playlist_musica_db
        if not any(p.id == id for p in playlists_db):
            raise Exception("Playlist não encontrada")
        playlists_db = [p for p in playlists_db if p.id != id]
        playlist_musica_db[:] = [pm for pm in playlist_musica_db if pm[0] != id]
        return True

    @strawberry.mutation
    def adicionar_musica_playlist(self, playlist_id: strawberry.ID, musica_id: strawberry.ID) -> Playlist:
        if not any(p.id == playlist_id for p in playlists_db):
            raise Exception("Playlist não encontrada")
        if not any(m.id == musica_id for m in musicas_db):
            raise Exception("Música não encontrada")
        if any(pm == (playlist_id, musica_id) for pm in playlist_musica_db):
            raise Exception("Música já existe na playlist")
        playlist_musica_db.append((playlist_id, musica_id))
        return next(p for p in playlists_db if p.id == playlist_id)

    @strawberry.mutation
    def remover_musica_playlist(self, playlist_id: strawberry.ID, musica_id: strawberry.ID) -> Playlist:
        global playlist_musica_db
        if not any(p.id == playlist_id for p in playlists_db):
            raise Exception("Playlist não encontrada")
        if not any(m.id == musica_id for m in musicas_db):
            raise Exception("Música não encontrada")
        if not any(pm == (playlist_id, musica_id) for pm in playlist_musica_db):
            raise Exception("Música não está na playlist")
        playlist_musica_db = [pm for pm in playlist_musica_db if pm != (playlist_id, musica_id)]
        return next(p for p in playlists_db if p.id == playlist_id)

schema = strawberry.Schema(query=Query, mutation=Mutation)

from strawberry.fastapi import GraphQLRouter
graphql_app = GraphQLRouter(schema, path="/")
app = FastAPI(title="Streaming GraphQL API (Python)")
app.include_router(graphql_app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)