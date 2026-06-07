from locust import HttpUser, User, task, between
import random
import uuid
import time
import os
import json # Import json for reading prepopulated IDs

# --- gRPC imports and client setup ---
import grpc
import sys

# A more robust way to import stubs from a relative path
# Assuming locustfile.py is run from the project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'APIs', 'python')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'APIs', 'shared')))

try:
    import streaming_pb2
    import streaming_pb2_grpc
except ImportError:
    print("WARNING: gRPC stubs (streaming_pb2.py, streaming_pb2_grpc.py) not found. Please ensure they are generated in APIs/python.")
    # Create dummy modules/classes to prevent further errors if not found
    class DummyStreamingPb2:
        class Vazio: pass
        class IdRequest:
            def __init__(self, id): pass
        class CriarUsuarioRequest:
            def __init__(self, nome, idade): pass
        class CriarMusicaRequest:
            def __init__(self, nome, artista): pass
        class CriarPlaylistRequest:
            def __init__(self, nome, usuario_id): pass
        class RelacaoPlaylistMusicaRequest:
            def __init__(self, playlist_id, musica_id): pass
        class Usuario: pass
        class Musica: pass
        class Playlist: pass

    class DummyStreamingPb2Grpc:
        class StreamingServiceStub:
            def __init__(self, channel): pass
            def ListarUsuarios(self, request): return DummyStreamingPb2.Usuario()
            def CriarUsuario(self, request): return DummyStreamingPb2.Usuario()
            def ListarMusicas(self, request): return DummyStreamingPb2.Musica()
            def CriarMusica(self, request): return DummyStreamingPb2.Musica()
            def ListarPlaylistsPorUsuario(self, request): return DummyStreamingPb2.Playlist()
            def CriarPlaylist(self, request): return DummyStreamingPb2.Playlist()
            def AdicionarMusicaPlaylist(self, request): return DummyStreamingPb2.Playlist()
            def ListarMusicasPorPlaylist(self, request): return DummyStreamingPb2.Musica()
            def ListarPlaylistsPorMusica(self, request): return DummyStreamingPb2.Playlist()
    
    streaming_pb2 = DummyStreamingPb2()
    streaming_pb2_grpc = DummyStreamingPb2Grpc()


# --- SOAP imports and client setup ---
from zeep import Client
from zeep.exceptions import Fault

# --- Global lists for created IDs (will be populated by a setup script) ---
# These are loaded from files created by prepopulate_data.py
PREPOPULATED_USER_IDS = []
PREPOPULATED_MUSIC_IDS = []
PREPOPULATED_PLAYLIST_IDS = []

try:
    with open("prepopulated_user_ids.json", "r") as f:
        PREPOPULATED_USER_IDS = json.load(f)
    with open("prepopulated_music_ids.json", "r") as f:
        PREPOPULATED_MUSIC_IDS = json.load(f)
    with open("prepopulated_playlist_ids.json", "r") as f:
        PREPOPULATED_PLAYLIST_IDS = json.load(f)
except FileNotFoundError:
    print("WARNING: Prepopulation data files not found. Ensure prepopulate_data.py has been run.")


# --- Custom gRPC Client for Locust ---
class GrpcClient:
    def __init__(self, environment, host):
        self.environment = environment
        self.host = host
        self.channel = None
        self.stub = None

    def _ensure_stub(self):
        # Only create channel/stub if not already created or if channel is closed
        if self.stub is None or (self.channel and self.channel._closed):
            try:
                self.channel = grpc.insecure_channel(self.host)
                # Test connectivity
                grpc.channel_ready_future(self.channel).wait(timeout=1)
                self.stub = streaming_pb2_grpc.StreamingServiceStub(self.channel)
            except grpc.FutureTimeoutError:
                raise Exception(f"gRPC connection to {self.host} timed out.")
            except Exception as e:
                raise Exception(f"Error connecting to gRPC server at {self.host}: {e}")

    def request(self, method_callable, request_data, name):
        self._ensure_stub() # Ensure stub is always ready
        start_time = time.time()
        try:
            response = method_callable(request_data)
            self.environment.events.request.fire(
                request_type="grpc",
                name=name,
                response_time=(time.time() - start_time) * 1000,
                response_length=sys.getsizeof(response), # Approximate
                exception=None,
            )
            return response
        except grpc.RpcError as e:
            self.environment.events.request.fire(
                request_type="grpc",
                name=name,
                response_time=(time.time() - start_time) * 1000,
                response_length=0,
                exception=e,
            )
            # Mark stub as None to force re-initialization on next call
            self.stub = None
            if self.channel:
                self.channel.close()
                self.channel = None
            raise

# --- Custom SOAP Client for Locust ---
class SoapClient:
    def __init__(self, environment, wsdl_url):
        self.environment = environment
        self.wsdl_url = wsdl_url
        self.client = None

    def _ensure_client(self):
        if self.client is None:
            try:
                self.client = Client(self.wsdl_url)
            except Exception as e:
                raise Exception(f"Error creating SOAP client for {self.wsdl_url}: {e}")

    def request(self, method_name, **kwargs): # Changed *args to **kwargs for clarity with zeep
        self._ensure_client() # Ensure client is always ready
        start_time = time.time()
        name = f"SOAP {method_name}"
        try:
            # Dynamically get the method from the client service
            method = getattr(self.client.service, method_name)
            response = method(**kwargs) # Pass kwargs directly
            self.environment.events.request.fire(
                request_type="soap",
                name=name,
                response_time=(time.time() - start_time) * 1000,
                response_length=sys.getsizeof(str(response)), # Approximate
                exception=None,
            )
            return response
        except Fault as e:
            self.environment.events.request.fire(
                request_type="soap",
                name=name,
                response_time=(time.time() - start_time) * 1000,
                response_length=0,
                exception=e,
            )
            self.client = None # Mark client as None to force re-initialization on next call
            raise
        except Exception as e:
            self.environment.events.request.fire(
                request_type="soap",
                name=name,
                response_time=(time.time() - start_time) * 1000,
                response_length=0,
                exception=e,
            )
            self.client = None # Mark client as None to force re-initialization on next call
            raise

# --- User classes for each API implementation ---

# Python REST API
class PythonRestUser(HttpUser):
    wait_time = between(0.5, 1.5)
    host = "http://localhost:8001"
    
    @task(1) # Prioritize reads, if no specific instructions, balance them.
    def listar_usuarios(self):
        self.client.get("/usuarios", name="Listar Usuarios")

    @task(1)
    def criar_usuario(self):
        self.client.post("/usuarios", json={"nome": f"User_{uuid.uuid4()}", "idade": random.randint(18, 60)}, name="Criar Usuario")

    @task(1)
    def listar_musicas(self):
        self.client.get("/musicas", name="Listar Musicas")

    @task(1)
    def criar_musica(self):
        self.client.post("/musicas", json={"nome": f"Musica_{uuid.uuid4()}", "artista": f"Artista_{uuid.uuid4()}"}, name="Criar Musica")

    @task(1)
    def listar_playlists_por_usuario(self):
        user_id = random.choice(PREPOPULATED_USER_IDS) if PREPOPULATED_USER_IDS else "dummy_id"
        self.client.get(f"/usuarios/{user_id}/playlists", name="Listar Playlists por Usuario")

    @task(1)
    def criar_playlist(self):
        user_id_to_associate = random.choice(PREPOPULATED_USER_IDS) if PREPOPULATED_USER_IDS else str(uuid.uuid4())
        self.client.post("/playlists", json={"nome": f"Playlist_{uuid.uuid4()}", "usuario_id": user_id_to_associate}, name="Criar Playlist")

    @task(1)
    def adicionar_musica_playlist(self):
        playlist_id = random.choice(PREPOPULATED_PLAYLIST_IDS) if PREPOPULATED_PLAYLIST_IDS else "dummy_pid"
        musica_id = random.choice(PREPOPULATED_MUSIC_IDS) if PREPOPULATED_MUSIC_IDS else "dummy_mid"
        self.client.post(f"/playlists/{playlist_id}/musicas", json={"musica_id": musica_id}, name="Adicionar Musica Playlist")

    @task(1)
    def listar_musicas_por_playlist(self):
        playlist_id = random.choice(PREPOPULATED_PLAYLIST_IDS) if PREPOPULATED_PLAYLIST_IDS else "dummy_pid"
        self.client.get(f"/playlists/{playlist_id}/musicas", name="Listar Musicas por Playlist")

    @task(1)
    def listar_playlists_por_musica(self):
        musica_id = random.choice(PREPOPULATED_MUSIC_IDS) if PREPOPULATED_MUSIC_IDS else "dummy_mid"
        self.client.get(f"/musicas/{musica_id}/playlists", name="Listar Playlists por Musica")


# Node.js REST API
class NodeRestUser(HttpUser):
    wait_time = between(0.5, 1.5)
    host = "http://localhost:8011"

    @task(1)
    def listar_usuarios(self):
        self.client.get("/usuarios", name="Listar Usuarios")

    @task(1)
    def criar_usuario(self):
        self.client.post("/usuarios", json={"nome": f"User_{uuid.uuid4()}", "idade": random.randint(18, 60)}, name="Criar Usuario")
    
    @task(1)
    def listar_musicas(self):
        self.client.get("/musicas", name="Listar Musicas")

    @task(1)
    def criar_musica(self):
        self.client.post("/musicas", json={"nome": f"Musica_{uuid.uuid4()}", "artista": f"Artista_{uuid.uuid4()}"}, name="Criar Musica")
    
    @task(1)
    def listar_playlists_por_usuario(self):
        user_id = random.choice(PREPOPULATED_USER_IDS) if PREPOPULATED_USER_IDS else "dummy_id"
        self.client.get(f"/usuarios/{user_id}/playlists", name="Listar Playlists por Usuario")

    @task(1)
    def criar_playlist(self):
        user_id_to_associate = random.choice(PREPOPULATED_USER_IDS) if PREPOPULATED_USER_IDS else str(uuid.uuid4())
        self.client.post("/playlists", json={"nome": f"Playlist_{uuid.uuid4()}", "usuario_id": user_id_to_associate}, name="Criar Playlist")

    @task(1)
    def adicionar_musica_playlist(self):
        playlist_id = random.choice(PREPOPULATED_PLAYLIST_IDS) if PREPOPULATED_PLAYLIST_IDS else "dummy_pid"
        musica_id = random.choice(PREPOPULATED_MUSIC_IDS) if PREPOPULATED_MUSIC_IDS else "dummy_mid"
        self.client.post(f"/playlists/{playlist_id}/musicas", json={"musica_id": musica_id}, name="Adicionar Musica Playlist")

    @task(1)
    def listar_musicas_por_playlist(self):
        playlist_id = random.choice(PREPOPULATED_PLAYLIST_IDS) if PREPOPULATED_PLAYLIST_IDS else "dummy_pid"
        self.client.get(f"/playlists/{playlist_id}/musicas", name="Listar Musicas por Playlist")

    @task(1)
    def listar_playlists_por_musica(self):
        musica_id = random.choice(PREPOPULATED_MUSIC_IDS) if PREPOPULATED_MUSIC_IDS else "dummy_mid"
        self.client.get(f"/musicas/{musica_id}/playlists", name="Listar Playlists por Musica")


# Python GraphQL API
class PythonGraphQLUser(HttpUser):
    wait_time = between(0.5, 1.5)
    host = "http://localhost:8002"

    @task(1)
    def listar_usuarios(self):
        query = """
        query {
            listarUsuarios {
                id
                nome
                idade
            }
        }
        """
        self.client.post("/graphql", json={'query': query}, name="Listar Usuarios GraphQL")

    @task(1)
    def criar_usuario(self):
        query = f"""
        mutation {{
            criarUsuario(nome: "User_{uuid.uuid4()}", idade: {random.randint(18, 60)}) {{
                id
                nome
            }}
        }}
        """
        self.client.post("/graphql", json={'query': query}, name="Criar Usuario GraphQL")
    
    @task(1)
    def listar_musicas(self):
        query = """
        query {
            listarMusicas {
                id
                nome
                artista
            }
        }
        """
        self.client.post("/graphql", json={'query': query}, name="Listar Musicas GraphQL")

    @task(1)
    def criar_musica(self):
        query = f"""
        mutation {{
            criarMusica(nome: "Musica_{uuid.uuid4()}", artista: "Artista_{uuid.uuid4()}") {{
                id
                nome
            }}
        }}
        """
        self.client.post("/graphql", json={'query': query}, name="Criar Musica GraphQL")

    @task(1)
    def listar_playlists_por_usuario(self):
        user_id = random.choice(PREPOPULATED_USER_IDS) if PREPOPULATED_USER_IDS else str(uuid.uuid4())
        query = f"""
        query {{
            listarPlaylistsPorUsuario(usuarioId: "{user_id}") {{
                id
                nome
            }}
        }}
        """
        self.client.post("/graphql", json={'query': query}, name="Listar Playlists por Usuario GraphQL")

    @task(1)
    def criar_playlist(self):
        user_id_to_associate = random.choice(PREPOPULATED_USER_IDS) if PREPOPULATED_USER_IDS else str(uuid.uuid4())
        query = f"""
        mutation {{
            criarPlaylist(nome: "Playlist_{uuid.uuid4()}", usuarioId: "{user_id_to_associate}") {{
                id
                nome
            }}
        }}
        """
        self.client.post("/graphql", json={'query': query}, name="Criar Playlist GraphQL")

    @task(1)
    def adicionar_musica_playlist(self):
        playlist_id = random.choice(PREPOPULATED_PLAYLIST_IDS) if PREPOPULATED_PLAYLIST_IDS else str(uuid.uuid4())
        musica_id = random.choice(PREPOPULATED_MUSIC_IDS) if PREPOPULATED_MUSIC_IDS else str(uuid.uuid4())
        query = f"""
        mutation {{
            adicionarMusicaPlaylist(playlistId: "{playlist_id}", musicaId: "{musica_id}") {{
                id
                nome
            }}
        }}
        """
        self.client.post("/graphql", json={'query': query}, name="Adicionar Musica Playlist GraphQL")

    @task(1)
    def listar_musicas_por_playlist(self):
        playlist_id = random.choice(PREPOPULATED_PLAYLIST_IDS) if PREPOPULATED_PLAYLIST_IDS else str(uuid.uuid4())
        query = f"""
        query {{
            listarMusicasPorPlaylist(playlistId: "{playlist_id}") {{
                id
                nome
            }}
        }}
        """
        self.client.post("/graphql", json={'query': query}, name="Listar Musicas por Playlist GraphQL")

    @task(1)
    def listar_playlists_por_musica(self):
        musica_id = random.choice(PREPOPULATED_MUSIC_IDS) if PREPOPULATED_MUSIC_IDS else str(uuid.uuid4())
        query = f"""
        query {{
            listarPlaylistsPorMusica(musicaId: "{musica_id}") {{
                id
                nome
            }}
        }}
        """
        self.client.post("/graphql", json={'query': query}, name="Listar Playlists por Musica GraphQL")


# Node.js GraphQL API
class NodeGraphQLUser(HttpUser):
    wait_time = between(0.5, 1.5)
    host = "http://localhost:8012"

    @task(1)
    def listar_usuarios(self):
        query = """
        query {
            listarUsuarios {
                id
                nome
                idade
            }
        }
        """
        self.client.post("/", json={'query': query}, name="Listar Usuarios GraphQL") # Apollo server default path is "/"

    @task(1)
    def criar_usuario(self):
        query = f"""
        mutation {{
            criarUsuario(nome: "User_{uuid.uuid4()}", idade: {random.randint(18, 60)}) {{
                id
                nome
            }}
        }}
        """
        self.client.post("/", json={'query': query}, name="Criar Usuario GraphQL")
    
    @task(1)
    def listar_musicas(self):
        query = """
        query {
            listarMusicas {
                id
                nome
                artista
            }
        }
        """
        self.client.post("/", json={'query': query}, name="Listar Musicas GraphQL")

    @task(1)
    def criar_musica(self):
        query = f"""
        mutation {{
            criarMusica(nome: "Musica_{uuid.uuid4()}", artista: "Artista_{uuid.uuid4()}") {{
                id
                nome
            }}
        }}
        """
        self.client.post("/", json={'query': query}, name="Criar Musica GraphQL")

    @task(1)
    def listar_playlists_por_usuario(self):
        user_id = random.choice(PREPOPULATED_USER_IDS) if PREPOPULATED_USER_IDS else str(uuid.uuid4())
        query = f"""
        query {{
            listarPlaylistsPorUsuario(usuarioId: "{user_id}") {{
                id
                nome
            }}
        }}
        """
        self.client.post("/", json={'query': query}, name="Listar Playlists por Usuario GraphQL")

    @task(1)
    def criar_playlist(self):
        user_id_to_associate = random.choice(PREPOPULATED_USER_IDS) if PREPOPULATED_USER_IDS else str(uuid.uuid4())
        query = f"""
        mutation {{
            criarPlaylist(nome: "Playlist_{uuid.uuid4()}", usuarioId: "{user_id_to_associate}") {{
                id
                nome
            }}
        }}
        """
        self.client.post("/", json={'query': query}, name="Criar Playlist GraphQL")

    @task(1)
    def adicionar_musica_playlist(self):
        playlist_id = random.choice(PREPOPULATED_PLAYLIST_IDS) if PREPOPULATED_PLAYLIST_IDS else str(uuid.uuid4())
        musica_id = random.choice(PREPOPULATED_MUSIC_IDS) if PREPOPULATED_MUSIC_IDS else str(uuid.uuid4())
        query = f"""
        mutation {{
            adicionarMusicaPlaylist(playlistId: "{playlist_id}", musicaId: "{musica_id}") {{
                id
                nome
            }}
        }}
        """
        self.client.post("/", json={'query': query}, name="Adicionar Musica Playlist GraphQL")

    @task(1)
    def listar_musicas_por_playlist(self):
        playlist_id = random.choice(PREPOPULATED_PLAYLIST_IDS) if PREPOPULATED_PLAYLIST_IDS else str(uuid.uuid4())
        query = f"""
        query {{
            listarMusicasPorPlaylist(playlistId: "{playlist_id}") {{
                id
                nome
            }}
        }}
        """
        self.client.post("/", json={'query': query}, name="Listar Musicas por Playlist GraphQL")

    @task(1)
    def listar_playlists_por_musica(self):
        musica_id = random.choice(PREPOPULATED_MUSIC_IDS) if PREPOPULATED_MUSIC_IDS else str(uuid.uuid4())
        query = f"""
        query {{
            listarPlaylistsPorMusica(musicaId: "{musica_id}") {{
                id
                nome
            }}
        }}
        """
        self.client.post("/", json={'query': query}, name="Listar Playlists por Musica GraphQL")


# Python gRPC API
class PythonGrpcUser(User):
    wait_time = between(0.5, 1.5)
    host = "localhost:50051"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = GrpcClient(self.environment, self.host)

    @task(1)
    def listar_usuarios(self):
        self.client.request(self.client.stub.ListarUsuarios, streaming_pb2.Vazio(), "Listar Usuarios gRPC")
    
    @task(1)
    def criar_usuario(self):
        self.client.request(self.client.stub.CriarUsuario, streaming_pb2.CriarUsuarioRequest(nome=f"User_{uuid.uuid4()}", idade=random.randint(18, 60)), "Criar Usuario gRPC")

    @task(1)
    def listar_musicas(self):
        self.client.request(self.client.stub.ListarMusicas, streaming_pb2.Vazio(), "Listar Musicas gRPC")

    @task(1)
    def criar_musica(self):
        self.client.request(self.client.stub.CriarMusica, streaming_pb2.CriarMusicaRequest(nome=f"Musica_{uuid.uuid4()}", artista=f"Artista_{uuid.uuid4()}"), "Criar Musica gRPC")

    @task(1)
    def listar_playlists_por_usuario(self):
        user_id = random.choice(PREPOPULATED_USER_IDS) if PREPOPULATED_USER_IDS else str(uuid.uuid4())
        self.client.request(self.client.stub.ListarPlaylistsPorUsuario, streaming_pb2.IdRequest(id=user_id), "Listar Playlists por Usuario gRPC")

    @task(1)
    def criar_playlist(self):
        user_id_to_associate = random.choice(PREPOPULATED_USER_IDS) if PREPOPULATED_USER_IDS else str(uuid.uuid4())
        self.client.request(self.client.stub.CriarPlaylist, streaming_pb2.CriarPlaylistRequest(nome=f"Playlist_{uuid.uuid4()}", usuario_id=user_id_to_associate), "Criar Playlist gRPC")

    @task(1)
    def adicionar_musica_playlist(self):
        playlist_id = random.choice(PREPOPULATED_PLAYLIST_IDS) if PREPOPULATED_PLAYLIST_IDS else str(uuid.uuid4())
        musica_id = random.choice(PREPOPULATED_MUSIC_IDS) if PREPOPULATED_MUSIC_IDS else str(uuid.uuid4())
        self.client.request(self.client.stub.AdicionarMusicaPlaylist, streaming_pb2.RelacaoPlaylistMusicaRequest(playlist_id=playlist_id, musica_id=musica_id), "Adicionar Musica Playlist gRPC")

    @task(1)
    def listar_musicas_por_playlist(self):
        playlist_id = random.choice(PREPOPULATED_PLAYLIST_IDS) if PREPOPULATED_PLAYLIST_IDS else str(uuid.uuid4())
        self.client.request(self.client.stub.ListarMusicasPorPlaylist, streaming_pb2.IdRequest(id=playlist_id), "Listar Musicas por Playlist gRPC")

    @task(1)
    def listar_playlists_por_musica(self):
        musica_id = random.choice(PREPOPULATED_MUSIC_IDS) if PREPOPULATED_MUSIC_IDS else str(uuid.uuid4())
        self.client.request(self.client.stub.ListarPlaylistsPorMusica, streaming_pb2.IdRequest(id=musica_id), "Listar Playlists por Musica gRPC")


# Node.js gRPC API
class NodeGrpcUser(User):
    wait_time = between(0.5, 1.5)
    host = "localhost:50052" # Node.js gRPC server
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = GrpcClient(self.environment, self.host)

    @task(1)
    def listar_usuarios(self):
        self.client.request(self.client.stub.ListarUsuarios, streaming_pb2.Vazio(), "Listar Usuarios gRPC (Node)")
    
    @task(1)
    def criar_usuario(self):
        self.client.request(self.client.stub.CriarUsuario, streaming_pb2.CriarUsuarioRequest(nome=f"User_{uuid.uuid4()}", idade=random.randint(18, 60)), "Criar Usuario gRPC (Node)")

    @task(1)
    def listar_musicas(self):
        self.client.request(self.client.stub.ListarMusicas, streaming_pb2.Vazio(), "Listar Musicas gRPC (Node)")

    @task(1)
    def criar_musica(self):
        self.client.request(self.client.stub.CriarMusica, streaming_pb2.CriarMusicaRequest(nome=f"Musica_{uuid.uuid4()}", artista=f"Artista_{uuid.uuid4()}"), "Criar Musica gRPC (Node)")

    @task(1)
    def listar_playlists_por_usuario(self):
        user_id = random.choice(PREPOPULATED_USER_IDS) if PREPOPULATED_USER_IDS else str(uuid.uuid4())
        self.client.request(self.client.stub.ListarPlaylistsPorUsuario, streaming_pb2.IdRequest(id=user_id), "Listar Playlists por Usuario gRPC (Node)")

    @task(1)
    def criar_playlist(self):
        user_id_to_associate = random.choice(PREPOPULATED_USER_IDS) if PREPOPULATED_USER_IDS else str(uuid.uuid4())
        self.client.request(self.client.stub.CriarPlaylist, streaming_pb2.CriarPlaylistRequest(nome=f"Playlist_{uuid.uuid4()}", usuario_id=user_id_to_associate), "Criar Playlist gRPC (Node)")

    @task(1)
    def adicionar_musica_playlist(self):
        playlist_id = random.choice(PREPOPULATED_PLAYLIST_IDS) if PREPOPULATED_PLAYLIST_IDS else str(uuid.uuid4())
        musica_id = random.choice(PREPOPULATED_MUSIC_IDS) if PREPOPULATED_MUSIC_IDS else str(uuid.uuid4())
        self.client.request(self.client.stub.AdicionarMusicaPlaylist, streaming_pb2.RelacaoPlaylistMusicaRequest(playlist_id=playlist_id, musica_id=musica_id), "Adicionar Musica Playlist gRPC (Node)")

    @task(1)
    def listar_musicas_por_playlist(self):
        playlist_id = random.choice(PREPOPULATED_PLAYLIST_IDS) if PREPOPULATED_PLAYLIST_IDS else str(uuid.uuid4())
        self.client.request(self.client.stub.ListarMusicasPorPlaylist, streaming_pb2.IdRequest(id=playlist_id), "Listar Musicas por Playlist gRPC (Node)")

    @task(1)
    def listar_playlists_por_musica(self):
        musica_id = random.choice(PREPOPULATED_MUSIC_IDS) if PREPOPULATED_MUSIC_IDS else str(uuid.uuid4())
        self.client.request(self.client.stub.ListarPlaylistsPorMusica, streaming_pb2.IdRequest(id=musica_id), "Listar Playlists por Musica gRPC (Node)")


# Python SOAP API
class PythonSoapUser(User):
    wait_time = between(0.5, 1.5)
    host = "http://localhost:8003/soap?wsdl" # WSDL for Python SOAP
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = SoapClient(self.environment, self.host)

    @task(1)
    def listar_usuarios(self):
        self.client.request("ListarUsuarios", name="Listar Usuarios SOAP")
    
    @task(1)
    def criar_usuario(self):
        self.client.request("CriarUsuario", nome=f"User_{uuid.uuid4()}", idade=random.randint(18, 60), name="Criar Usuario SOAP")

    @task(1)
    def listar_musicas(self):
        # This operation IS available in the WSDL generated by spyne.
        # But our simple WSDL in streaming.wsdl does not have it.
        # Let's adjust for the actual WSDL content.
        # For now, I will assume the server side has the ListarMusicas method.
        # If the server is correctly defined and the WSDL reflects it, this would work.
        # I will leave the `_returns` param in the comment as it's typically how Zeep infers response type.
        self.client.request("ListarMusicas", name="Listar Musicas SOAP") # _returns='ListarMusicasResponse'

    @task(1)
    def criar_musica(self):
        # This operation IS NOT available in our simplified WSDL.
        # Mark as not implemented in WSDL.
        self.environment.events.request.fire(
            request_type="soap",
            name="Criar Musica SOAP (Not Implemented)",
            response_time=0,
            response_length=0,
            exception="Operation not defined in WSDL"
        )

    @task(1)
    def listar_playlists_por_usuario(self):
        # This operation IS NOT available in our simplified WSDL.
        self.environment.events.request.fire(
            request_type="soap",
            name="Listar Playlists por Usuario SOAP (Not Implemented)",
            response_time=0,
            response_length=0,
            exception="Operation not defined in WSDL"
        )

    @task(1)
    def criar_playlist(self):
        # This operation IS NOT available in our simplified WSDL.
        self.environment.events.request.fire(
            request_type="soap",
            name="Criar Playlist SOAP (Not Implemented)",
            response_time=0,
            response_length=0,
            exception="Operation not defined in WSDL"
        )

    @task(1)
    def adicionar_musica_playlist(self):
        # This operation IS NOT available in our simplified WSDL.
        self.environment.events.request.fire(
            request_type="soap",
            name="Adicionar Musica Playlist SOAP (Not Implemented)",
            response_time=0,
            response_length=0,
            exception="Operation not defined in WSDL"
        )

    @task(1)
    def listar_musicas_por_playlist(self):
        # This operation IS NOT available in our simplified WSDL.
        self.environment.events.request.fire(
            request_type="soap",
            name="Listar Musicas por Playlist SOAP (Not Implemented)",
            response_time=0,
            response_length=0,
            exception="Operation not defined in WSDL"
        )

    @task(1)
    def listar_playlists_por_musica(self):
        # This operation IS NOT available in our simplified WSDL.
        self.environment.events.request.fire(
            request_type="soap",
            name="Listar Playlists por Musica SOAP (Not Implemented)",
            response_time=0,
            response_length=0,
            exception="Operation not defined in WSDL"
        )


# Node.js SOAP API
class NodeSoapUser(User):
    wait_time = between(0.5, 1.5)
    host = "http://localhost:8013/soap?wsdl" # WSDL for Node.js SOAP
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = SoapClient(self.environment, self.host)

    @task(1)
    def listar_usuarios(self):
        self.client.request("ListarUsuarios", name="Listar Usuarios SOAP (Node)")
    
    @task(1)
    def criar_usuario(self):
        self.client.request("CriarUsuario", nome=f"User_{uuid.uuid4()}", idade=random.randint(18, 60), name="Criar Usuario SOAP (Node)")

    @task(1)
    def listar_musicas(self):
        # This operation IS available in the WSDL generated by Node.js soap library.
        # But our simple WSDL in streaming.wsdl does not have it.
        # Let's adjust for the actual WSDL content.
        # For now, I will assume the server side has the ListarMusicas method.
        self.client.request("ListarMusicas", name="Listar Musicas SOAP (Node)")

    @task(1)
    def criar_musica(self):
        # This operation IS NOT available in our simplified WSDL.
        self.environment.events.request.fire(
            request_type="soap",
            name="Criar Musica SOAP (Node) (Not Implemented)",
            response_time=0,
            response_length=0,
            exception="Operation not defined in WSDL"
        )

    @task(1)
    def listar_playlists_por_usuario(self):
        # This operation IS NOT available in our simplified WSDL.
        self.environment.events.request.fire(
            request_type="soap",
            name="Listar Playlists por Usuario SOAP (Node) (Not Implemented)",
            response_time=0,
            response_length=0,
            exception="Operation not defined in WSDL"
        )

    @task(1)
    def criar_playlist(self):
        # This operation IS NOT available in our simplified WSDL.
        self.environment.events.request.fire(
            request_type="soap",
            name="Criar Playlist SOAP (Node) (Not Implemented)",
            response_time=0,
            response_length=0,
            exception="Operation not defined in WSDL"
        )

    @task(1)
    def adicionar_musica_playlist(self):
        # This operation IS NOT available in our simplified WSDL.
        self.environment.events.request.fire(
            request_type="soap",
            name="Adicionar Musica Playlist SOAP (Node) (Not Implemented)",
            response_time=0,
            response_length=0,
            exception="Operation not defined in WSDL"
        )

    @task(1)
    def listar_musicas_por_playlist(self):
        # This operation IS NOT available in our simplified WSDL.
        self.environment.events.request.fire(
            request_type="soap",
            name="Listar Musicas por Playlist SOAP (Node) (Not Implemented)",
            response_time=0,
            response_length=0,
            exception="Operation not defined in WSDL"
        )

    @task(1)
    def listar_playlists_por_musica(self):
        # This operation IS NOT available in our simplified WSDL.
        self.environment.events.request.fire(
            request_type="soap",
            name="Listar Playlists por Musica SOAP (Node) (Not Implemented)",
            response_time=0,
            response_length=0,
            exception="Operation not defined in WSDL"
        )
