import grpc
from concurrent import futures
import uuid
import sys
import os

# Assume stubs are generated in the same directory
import streaming_pb2
import streaming_pb2_grpc

usuarios_db = []
musicas_db = []
playlists_db = []
playlist_musica_db = []

class StreamingService(streaming_pb2_grpc.StreamingServiceServicer):
    def ListarUsuarios(self, request, context):
        response = streaming_pb2.ListaUsuariosResponse()
        for u in usuarios_db:
            response.usuarios.add(id=u['id'], nome=u['nome'], idade=u['idade'])
        return response

    def ListarMusicas(self, request, context):
        response = streaming_pb2.ListaMusicasResponse()
        for m in musicas_db:
            response.musicas.add(id=m['id'], nome=m['nome'], artista=m['artista'])
        return response

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

    def CriarUsuario(self, request, context):
        u = {'id': request.id, 'nome': request.nome, 'idade': request.idade}
        usuarios_db.append(u)
        return streaming_pb2.Usuario(**u)

    def CriarMusica(self, request, context):
        m = {'id': request.id, 'nome': request.nome, 'artista': request.artista}
        musicas_db.append(m)
        return streaming_pb2.Musica(**m)

    def CriarPlaylist(self, request, context):
        p = {'id': request.id, 'nome': request.nome, 'usuario_id': request.usuario_id}
        playlists_db.append(p)
        return streaming_pb2.Playlist(**p)

    def AdicionarMusicaPlaylist(self, request, context):
        playlist_musica_db.append((request.playlist_id, request.musica_id))
        p = next(p for p in playlists_db if p['id'] == request.playlist_id)
        return streaming_pb2.Playlist(**p)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    streaming_pb2_grpc.add_StreamingServiceServicer_to_server(StreamingService(), server)
    server.add_insecure_port('[::]:8003')
    server.start()
    print("gRPC server (Python) started on port 8003")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()