import requests
import grpc
import uuid
import random
import time
import json
import os
import sys

# For gRPC
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'APIs', 'python')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'APIs', 'shared')))
import streaming_pb2
import streaming_pb2_grpc

# For SOAP
from zeep import Client

APIS = [
    {"name": "py_rest", "type": "rest", "url": "http://localhost:8001"},
    {"name": "py_graphql", "type": "graphql", "url": "http://localhost:8002/graphql"},
    {"name": "py_grpc", "type": "grpc", "host": "localhost:8003"},
    {"name": "py_soap", "type": "soap", "wsdl": "http://localhost:8004/?wsdl", "address": "http://localhost:8004/", "binding": "Application"},
    {"name": "node_rest", "type": "rest", "url": "http://localhost:9001"},
    {"name": "node_graphql", "type": "graphql", "url": "http://localhost:9002"},
    {"name": "node_grpc", "type": "grpc", "host": "localhost:9003"},
    {"name": "node_soap", "type": "soap", "wsdl": "http://localhost:9004/soap?wsdl", "address": "http://localhost:9004/soap", "binding": "StreamingBinding"},
]

def seed_api(api, users, music, playlists):
    print(f"Seeding {api['name']}...")
    
    if api['type'] == 'rest':
        for u in users: requests.post(f"{api['url']}/usuarios", json=u)
        for m in music: requests.post(f"{api['url']}/musicas", json=m)
        for p in playlists: requests.post(f"{api['url']}/playlists", json=p)
        for p in playlists:
            for _ in range(3):
                m = random.choice(music)
                requests.post(f"{api['url']}/playlists/{p['id']}/musicas", json={"musica_id": m['id']})

    elif api['type'] == 'graphql':
        for u in users:
            q = f'mutation {{ criarUsuario(id: "{u["id"]}", nome: "{u["nome"]}", idade: {u["idade"]}) {{ id }} }}'
            requests.post(api['url'], json={"query": q})
        for m in music:
            q = f'mutation {{ criarMusica(id: "{m["id"]}", nome: "{m["nome"]}", artista: "{m["artista"]}") {{ id }} }}'
            requests.post(api['url'], json={"query": q})
        for p in playlists:
            q = f'mutation {{ criarPlaylist(id: "{p["id"]}", nome: "{p["nome"]}", usuarioId: "{p["usuario_id"]}") {{ id }} }}'
            requests.post(api['url'], json={"query": q})
            for _ in range(3):
                m = random.choice(music)
                q = f'mutation {{ adicionarMusicaPlaylist(playlistId: "{p["id"]}", musicaId: "{m["id"]}") {{ id }} }}'
                requests.post(api['url'], json={"query": q})

    elif api['type'] == 'grpc':
        channel = grpc.insecure_channel(api['host'])
        stub = streaming_pb2_grpc.StreamingServiceStub(channel)
        for u in users: stub.CriarUsuario(streaming_pb2.CriarUsuarioRequest(id=u['id'], nome=u['nome'], idade=u['idade']))
        for m in music: stub.CriarMusica(streaming_pb2.CriarMusicaRequest(id=m['id'], nome=m['nome'], artista=m['artista']))
        for p in playlists:
            stub.CriarPlaylist(streaming_pb2.CriarPlaylistRequest(id=p['id'], nome=p['nome'], usuario_id=p['usuario_id']))
            for _ in range(3):
                m = random.choice(music)
                stub.AdicionarMusicaPlaylist(streaming_pb2.RelacaoPlaylistMusicaRequest(playlist_id=p['id'], musica_id=m['id']))
        channel.close()

    elif api['type'] == 'soap':
        client = Client(api['wsdl'])
        # Bind specifically to ensure correct address and port
        service = client.create_service('{http://streaming.com/wsdl}' + api['binding'], api['address'])
        for u in users:
            service.CriarUsuario(id=u['id'], nome=u['nome'], idade=u['idade'])
        for m in music:
            service.CriarMusica(id=m['id'], nome=m['nome'], artista=m['artista'])
        for p in playlists:
            service.CriarPlaylist(id=p['id'], nome=p['nome'], usuario_id=p['usuario_id'])
            for _ in range(3):
                m = random.choice(music)
                service.AdicionarMusicaPlaylist(playlist_id=p['id'], musica_id=m['id'])

def main():
    users = [{"id": str(uuid.uuid4()), "nome": f"User_{i}", "idade": random.randint(18, 70)} for i in range(1000)]
    music = [{"id": str(uuid.uuid4()), "nome": f"Song_{i}", "artista": f"Artist_{i}"} for i in range(1000)]
    playlists = [{"id": str(uuid.uuid4()), "nome": f"Playlist_{i}", "usuario_id": random.choice(users)["id"]} for i in range(100)]

    with open("prepopulated_user_ids.json", "w") as f: json.dump([u['id'] for u in users], f)
    with open("prepopulated_music_ids.json", "w") as f: json.dump([m['id'] for m in music], f)
    with open("prepopulated_playlist_ids.json", "w") as f: json.dump([p['id'] for p in playlists], f)

    for api in APIS:
        try:
            seed_api(api, users, music, playlists)
        except Exception as e:
            print(f"Error seeding {api['name']}: {e}")

if __name__ == "__main__":
    main()
