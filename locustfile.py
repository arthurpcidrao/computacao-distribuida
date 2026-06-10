from locust import HttpUser, User, task, between
import random
import time
import os
import json
import grpc
import sys

# Import gRPC stubs
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'APIs', 'python')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'APIs', 'shared')))

try:
    import streaming_pb2
    import streaming_pb2_grpc
except ImportError:
    class Dummy: pass
    streaming_pb2 = Dummy()
    streaming_pb2_grpc = Dummy()

from zeep import Client

# Load valid IDs for randomized GETs
USER_IDS = []
MUSIC_IDS = []
PLAYLIST_IDS = []

try:
    with open("prepopulated_user_ids.json", "r") as f: USER_IDS = json.load(f)
    with open("prepopulated_music_ids.json", "r") as f: MUSIC_IDS = json.load(f)
    with open("prepopulated_playlist_ids.json", "r") as f: PLAYLIST_IDS = json.load(f)
except FileNotFoundError:
    pass

class GrpcClient:
    def __init__(self, environment, host):
        self.environment = environment
        self.host = host
        self.channel = grpc.insecure_channel(self.host)
        self.stub = streaming_pb2_grpc.StreamingServiceStub(self.channel)

    def call(self, method_name, locust_name, request_data):
        method = getattr(self.stub, method_name)
        start_time = time.time()
        try:
            response = method(request_data)
            self.environment.events.request.fire(
                request_type="grpc", name=locust_name,
                response_time=(time.time() - start_time) * 1000,
                response_length=sys.getsizeof(response), exception=None,
            )
            return response
        except grpc.RpcError as e:
            self.environment.events.request.fire(
                request_type="grpc", name=locust_name,
                response_time=(time.time() - start_time) * 1000,
                response_length=0, exception=e,
            )
            raise

class SoapClient:
    def __init__(self, environment, wsdl, address, binding):
        self.environment = environment
        self.wsdl = wsdl
        self.address = address
        self.binding = binding
        self.client = None
        self.service = None

    def _ensure_client(self):
        if self.client is None:
            self.client = Client(self.wsdl)
            self.service = self.client.create_service('{http://streaming.com/wsdl}' + self.binding, self.address)

    def call(self, method_name, locust_name, **kwargs):
        self._ensure_client()
        method = getattr(self.service, method_name)
        start_time = time.time()
        try:
            response = method(**kwargs)
            self.environment.events.request.fire(
                request_type="soap", name=locust_name,
                response_time=(time.time() - start_time) * 1000,
                response_length=sys.getsizeof(str(response)), exception=None,
            )
            return response
        except Exception as e:
            self.environment.events.request.fire(
                request_type="soap", name=locust_name,
                response_time=(time.time() - start_time) * 1000,
                response_length=0, exception=e,
            )
            raise

# --- API USER CLASSES (ONLY GETs) ---

class PythonRestUser(HttpUser):
    wait_time = between(0.1, 0.5)
    @task(1)
    def t1(self): self.client.get("/usuarios", name="GET Users")
    @task(1)
    def t2(self): self.client.get("/musicas", name="GET Music")
    @task(1)
    def t3(self): 
        if USER_IDS: self.client.get(f"/usuarios/{random.choice(USER_IDS)}/playlists", name="GET User Playlists")
    @task(1)
    def t4(self): 
        if PLAYLIST_IDS: self.client.get(f"/playlists/{random.choice(PLAYLIST_IDS)}/musicas", name="GET Playlist Music")
    @task(1)
    def t5(self): 
        if MUSIC_IDS: self.client.get(f"/musicas/{random.choice(MUSIC_IDS)}/playlists", name="GET Music Playlists")

class PythonGraphQLUser(HttpUser):
    wait_time = between(0.1, 0.5)
    def q(self, query, name): self.client.post("/graphql", json={"query": query}, name=name)
    @task(1)
    def t1(self): self.q("{ listarUsuarios { id nome idade } }", "GQL Users")
    @task(1)
    def t2(self): self.q("{ listarMusicas { id nome artista } }", "GQL Music")
    @task(1)
    def t3(self): 
        if USER_IDS: self.q(f'{{ listarPlaylistsPorUsuario(usuarioId: "{random.choice(USER_IDS)}") {{ id nome }} }}', "GQL User Playlists")
    @task(1)
    def t4(self): 
        if PLAYLIST_IDS: self.q(f'{{ listarMusicasPorPlaylist(playlistId: "{random.choice(PLAYLIST_IDS)}") {{ id nome }} }}', "GQL Playlist Music")
    @task(1)
    def t5(self): 
        if MUSIC_IDS: self.q(f'{{ listarPlaylistsPorMusica(musicaId: "{random.choice(MUSIC_IDS)}") {{ id nome }} }}', "GQL Music Playlists")

class PythonGrpcUser(User):
    wait_time = between(0.1, 0.5)
    def on_start(self): self.c = GrpcClient(self.environment, "localhost:8003")
    @task(1)
    def t1(self): self.c.call("ListarUsuarios", "gRPC Users", streaming_pb2.Vazio())
    @task(1)
    def t2(self): self.c.call("ListarMusicas", "gRPC Music", streaming_pb2.Vazio())
    @task(1)
    def t3(self): 
        if USER_IDS: self.c.call("ListarPlaylistsPorUsuario", "gRPC User Playlists", streaming_pb2.IdRequest(id=random.choice(USER_IDS)))
    @task(1)
    def t4(self): 
        if PLAYLIST_IDS: self.c.call("ListarMusicasPorPlaylist", "gRPC Playlist Music", streaming_pb2.IdRequest(id=random.choice(PLAYLIST_IDS)))
    @task(1)
    def t5(self): 
        if MUSIC_IDS: self.c.call("ListarPlaylistsPorMusica", "gRPC Music Playlists", streaming_pb2.IdRequest(id=random.choice(MUSIC_IDS)))

class PythonSoapUser(User):
    wait_time = between(0.1, 0.5)
    def on_start(self): self.c = SoapClient(self.environment, "http://localhost:8004/?wsdl", "http://localhost:8004/", "Application")
    @task(1)
    def t1(self): self.c.call("ListarUsuarios", "SOAP Users")
    @task(1)
    def t2(self): self.c.call("ListarMusicas", "SOAP Music")
    @task(1)
    def t3(self): 
        if USER_IDS: self.c.call("ListarPlaylistsPorUsuario", "SOAP User Playlists", id=random.choice(USER_IDS))
    @task(1)
    def t4(self): 
        if PLAYLIST_IDS: self.c.call("ListarMusicasPorPlaylist", "SOAP Playlist Music", id=random.choice(PLAYLIST_IDS))
    @task(1)
    def t5(self): 
        if MUSIC_IDS: self.c.call("ListarPlaylistsPorMusica", "SOAP Music Playlists", id=random.choice(MUSIC_IDS))

class NodeRestUser(HttpUser):
    wait_time = between(0.1, 0.5)
    @task(1)
    def t1(self): self.client.get("/usuarios", name="GET Users")
    @task(1)
    def t2(self): self.client.get("/musicas", name="GET Music")
    @task(1)
    def t3(self): 
        if USER_IDS: self.client.get(f"/usuarios/{random.choice(USER_IDS)}/playlists", name="GET User Playlists")
    @task(1)
    def t4(self): 
        if PLAYLIST_IDS: self.client.get(f"/playlists/{random.choice(PLAYLIST_IDS)}/musicas", name="GET Playlist Music")
    @task(1)
    def t5(self): 
        if MUSIC_IDS: self.client.get(f"/musicas/{random.choice(MUSIC_IDS)}/playlists", name="GET Music Playlists")

class NodeGraphQLUser(HttpUser):
    wait_time = between(0.1, 0.5)
    def q(self, query, name): self.client.post("/", json={"query": query}, name=name)
    @task(1)
    def t1(self): self.q("{ listarUsuarios { id nome idade } }", "GQL Users")
    @task(1)
    def t2(self): self.q("{ listarMusicas { id nome artista } }", "GQL Music")
    @task(1)
    def t3(self): 
        if USER_IDS: self.q(f'{{ listarPlaylistsPorUsuario(usuarioId: "{random.choice(USER_IDS)}") {{ id nome }} }}', "GQL User Playlists")
    @task(1)
    def t4(self): 
        if PLAYLIST_IDS: self.q(f'{{ listarMusicasPorPlaylist(playlistId: "{random.choice(PLAYLIST_IDS)}") {{ id nome }} }}', "GQL Playlist Music")
    @task(1)
    def t5(self): 
        if MUSIC_IDS: self.q(f'{{ listarPlaylistsPorMusica(musicaId: "{random.choice(MUSIC_IDS)}") {{ id nome }} }}', "GQL Music Playlists")

class NodeGrpcUser(User):
    wait_time = between(0.1, 0.5)
    def on_start(self): self.c = GrpcClient(self.environment, "localhost:9003")
    @task(1)
    def t1(self): self.c.call("ListarUsuarios", "gRPC Users", streaming_pb2.Vazio())
    @task(1)
    def t2(self): self.c.call("ListarMusicas", "gRPC Music", streaming_pb2.Vazio())
    @task(1)
    def t3(self): 
        if USER_IDS: self.c.call("ListarPlaylistsPorUsuario", "gRPC User Playlists", streaming_pb2.IdRequest(id=random.choice(USER_IDS)))
    @task(1)
    def t4(self): 
        if PLAYLIST_IDS: self.c.call("ListarMusicasPorPlaylist", "gRPC Playlist Music", streaming_pb2.IdRequest(id=random.choice(PLAYLIST_IDS)))
    @task(1)
    def t5(self): 
        if MUSIC_IDS: self.c.call("ListarPlaylistsPorMusica", "gRPC Music Playlists", streaming_pb2.IdRequest(id=random.choice(MUSIC_IDS)))

class NodeSoapUser(User):
    wait_time = between(0.1, 0.5)
    def on_start(self): self.c = SoapClient(self.environment, "http://localhost:9004/soap?wsdl", "http://localhost:9004/soap", "StreamingBinding")
    @task(1)
    def t1(self): self.c.call("ListarUsuarios", "SOAP Users")
    @task(1)
    def t2(self): self.c.call("ListarMusicas", "SOAP Music")
    @task(1)
    def t3(self): 
        if USER_IDS: self.c.call("ListarPlaylistsPorUsuario", "SOAP User Playlists", id=random.choice(USER_IDS))
    @task(1)
    def t4(self): 
        if PLAYLIST_IDS: self.c.call("ListarMusicasPorPlaylist", "SOAP Playlist Music", id=random.choice(PLAYLIST_IDS))
    @task(1)
    def t5(self): 
        if MUSIC_IDS: self.c.call("ListarPlaylistsPorMusica", "SOAP Music Playlists", id=random.choice(MUSIC_IDS))
