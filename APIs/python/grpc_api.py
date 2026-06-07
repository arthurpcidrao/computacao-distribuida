import grpc
from concurrent import futures
import uuid
import sys
import os

# Generates stubs automatically at runtime if needed, but assuming they are compiled
# python -m grpc_tools.protoc -I../shared --python_out=. --grpc_python_out=. ../shared/streaming.proto
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

    def CriarUsuario(self, request, context):
        u = {'id': str(uuid.uuid4()), 'nome': request.nome, 'idade': request.idade}
        usuarios_db.append(u)
        return streaming_pb2.Usuario(**u)

    def CriarMusica(self, request, context):
        m = {'id': str(uuid.uuid4()), 'nome': request.nome, 'artista': request.artista}
        musicas_db.append(m)
        return streaming_pb2.Musica(**m)

    def CriarPlaylist(self, request, context):
        p = {'id': str(uuid.uuid4()), 'nome': request.nome, 'usuario_id': request.usuario_id}
        playlists_db.append(p)
        return streaming_pb2.Playlist(**p)

    def AdicionarMusicaPlaylist(self, request, context):
        playlist_musica_db.append((request.playlist_id, request.musica_id))
        p = next(p for p in playlists_db if p['id'] == request.playlist_id)
        return streaming_pb2.Playlist(**p)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    streaming_pb2_grpc.add_StreamingServiceServicer_to_server(StreamingService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("gRPC server (Python) started on port 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()