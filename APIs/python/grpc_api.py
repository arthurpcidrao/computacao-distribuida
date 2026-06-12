import grpc
from concurrent import futures
import sys
import os

import streaming_pb2
import streaming_pb2_grpc

usuarios_db = []
musicas_db = []
playlists_db = []
playlist_musica_db = []

class StreamingService(streaming_pb2_grpc.StreamingServiceServicer):
    # USUÁRIOS
    def ListarUsuarios(self, request, context):
        response = streaming_pb2.ListaUsuariosResponse()
        for u in usuarios_db:
            response.usuarios.add(id=u['id'], nome=u['nome'], idade=u['idade'])
        return response

    def ObterUsuario(self, request, context):
        for u in usuarios_db:
            if u['id'] == request.id:
                return streaming_pb2.Usuario(**u)
        context.abort(grpc.StatusCode.NOT_FOUND, "Usuário não encontrado")

    def CriarUsuario(self, request, context):
        if any(u['id'] == request.id for u in usuarios_db):
            context.abort(grpc.StatusCode.ALREADY_EXISTS, "Usuário já existe")
        u = {'id': request.id, 'nome': request.nome, 'idade': request.idade}
        usuarios_db.append(u)
        return streaming_pb2.Usuario(**u)

    def AtualizarUsuario(self, request, context):
        for u in usuarios_db:
            if u['id'] == request.id:
                u['nome'] = request.nome
                u['idade'] = request.idade
                return streaming_pb2.Usuario(**u)
        context.abort(grpc.StatusCode.NOT_FOUND, "Usuário não encontrado")

    def DeletarUsuario(self, request, context):
        global usuarios_db, playlists_db
        if not any(u['id'] == request.id for u in usuarios_db):
            context.abort(grpc.StatusCode.NOT_FOUND, "Usuário não encontrado")
        usuarios_db = [u for u in usuarios_db if u['id'] != request.id]
        playlists_db[:] = [p for p in playlists_db if p['usuario_id'] != request.id]
        return streaming_pb2.Empty()

    # MÚSICAS
    def ListarMusicas(self, request, context):
        response = streaming_pb2.ListaMusicasResponse()
        for m in musicas_db:
            response.musicas.add(id=m['id'], nome=m['nome'], artista=m['artista'])
        return response

    def ObterMusica(self, request, context):
        for m in musicas_db:
            if m['id'] == request.id:
                return streaming_pb2.Musica(**m)
        context.abort(grpc.StatusCode.NOT_FOUND, "Música não encontrada")

    def CriarMusica(self, request, context):
        if any(m['id'] == request.id for m in musicas_db):
            context.abort(grpc.StatusCode.ALREADY_EXISTS, "Música já existe")
        m = {'id': request.id, 'nome': request.nome, 'artista': request.artista}
        musicas_db.append(m)
        return streaming_pb2.Musica(**m)

    def AtualizarMusica(self, request, context):
        for m in musicas_db:
            if m['id'] == request.id:
                m['nome'] = request.nome
                m['artista'] = request.artista
                return streaming_pb2.Musica(**m)
        context.abort(grpc.StatusCode.NOT_FOUND, "Música não encontrada")

    def DeletarMusica(self, request, context):
        global musicas_db, playlist_musica_db
        if not any(m['id'] == request.id for m in musicas_db):
            context.abort(grpc.StatusCode.NOT_FOUND, "Música não encontrada")
        musicas_db = [m for m in musicas_db if m['id'] != request.id]
        playlist_musica_db[:] = [pm for pm in playlist_musica_db if pm[1] != request.id]
        return streaming_pb2.Empty()

    # PLAYLISTS
    def ListarPlaylists(self, request, context):
        response = streaming_pb2.ListaPlaylistsResponse()
        for p in playlists_db:
            response.playlists.add(id=p['id'], nome=p['nome'], usuario_id=p['usuario_id'])
        return response

    def ObterPlaylist(self, request, context):
        for p in playlists_db:
            if p['id'] == request.id:
                return streaming_pb2.Playlist(**p)
        context.abort(grpc.StatusCode.NOT_FOUND, "Playlist não encontrada")

    def CriarPlaylist(self, request, context):
        if not any(u['id'] == request.usuario_id for u in usuarios_db):
            context.abort(grpc.StatusCode.NOT_FOUND, "Usuário não existe")
        if any(p['id'] == request.id for p in playlists_db):
            context.abort(grpc.StatusCode.ALREADY_EXISTS, "Playlist já existe")
        p = {'id': request.id, 'nome': request.nome, 'usuario_id': request.usuario_id}
        playlists_db.append(p)
        return streaming_pb2.Playlist(**p)

    def AtualizarPlaylist(self, request, context):
        for p in playlists_db:
            if p['id'] == request.id:
                p['nome'] = request.nome
                return streaming_pb2.Playlist(**p)
        context.abort(grpc.StatusCode.NOT_FOUND, "Playlist não encontrada")

    def DeletarPlaylist(self, request, context):
        global playlists_db, playlist_musica_db
        if not any(p['id'] == request.id for p in playlists_db):
            context.abort(grpc.StatusCode.NOT_FOUND, "Playlist não encontrada")
        playlists_db = [p for p in playlists_db if p['id'] != request.id]
        playlist_musica_db[:] = [pm for pm in playlist_musica_db if pm[0] != request.id]
        return streaming_pb2.Empty()

    # RELAÇÕES
    def ListarPlaylistsPorUsuario(self, request, context):
        response = streaming_pb2.ListaPlaylistsResponse()
        for p in playlists_db:
            if p['usuario_id'] == request.id:
                response.playlists.add(id=p['id'], nome=p['nome'], usuario_id=p['usuario_id'])
        return response

    def ListarMusicasPorPlaylist(self, request, context):
        response = streaming_pb2.ListaMusicasResponse()
        m_ids = [pm[1] for pm in playlist_musica_db if pm[0] == request.id]
        for m in musicas_db:
            if m['id'] in m_ids:
                response.musicas.add(id=m['id'], nome=m['nome'], artista=m['artista'])
        return response

    def ListarPlaylistsPorMusica(self, request, context):
        response = streaming_pb2.ListaPlaylistsResponse()
        p_ids = [pm[0] for pm in playlist_musica_db if pm[1] == request.id]
        for p in playlists_db:
            if p['id'] in p_ids:
                response.playlists.add(id=p['id'], nome=p['nome'], usuario_id=p['usuario_id'])
        return response

    def AdicionarMusicaPlaylist(self, request, context):
        if not any(p['id'] == request.playlist_id for p in playlists_db):
            context.abort(grpc.StatusCode.NOT_FOUND, "Playlist não encontrada")
        if not any(m['id'] == request.musica_id for m in musicas_db):
            context.abort(grpc.StatusCode.NOT_FOUND, "Música não encontrada")
        if any(pm == (request.playlist_id, request.musica_id) for pm in playlist_musica_db):
            context.abort(grpc.StatusCode.ALREADY_EXISTS, "Música já existe na playlist")
        playlist_musica_db.append((request.playlist_id, request.musica_id))
        p = next(p for p in playlists_db if p['id'] == request.playlist_id)
        return streaming_pb2.Playlist(**p)

    def RemoverMusicaPlaylist(self, request, context):
        global playlist_musica_db
        if not any(p['id'] == request.playlist_id for p in playlists_db):
            context.abort(grpc.StatusCode.NOT_FOUND, "Playlist não encontrada")
        if not any(m['id'] == request.musica_id for m in musicas_db):
            context.abort(grpc.StatusCode.NOT_FOUND, "Música não encontrada")
        if not any(pm == (request.playlist_id, request.musica_id) for pm in playlist_musica_db):
            context.abort(grpc.StatusCode.NOT_FOUND, "Música não está na playlist")
        playlist_musica_db = [pm for pm in playlist_musica_db if pm != (request.playlist_id, request.musica_id)]
        p = next(p for p in playlists_db if p['id'] == request.playlist_id)
        return streaming_pb2.Playlist(**p)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    streaming_pb2_grpc.add_StreamingServiceServicer_to_server(StreamingService(), server)
    server.add_insecure_port('0.0.0.0:8003')
    server.start()
    print("gRPC server (Python) started on port 8003")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()