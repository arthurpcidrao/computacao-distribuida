from locust import HttpUser, User, task, between
import random
import uuid
import time
import os

# --- gRPC imports and client setup ---
import grpc
import sys
sys.path.append('./APIs/python')
sys.path.append('./APIs/shared')
import streaming_pb2
import streaming_pb2_grpc

# --- SOAP imports and client setup ---
from zeep import Client
from zeep.exceptions import Fault

# In-memory data for linking operations
created_user_ids = []
created_music_ids = []
created_playlist_ids = []

# --- Custom gRPC Client for Locust ---
class GrpcClient:
    def __init__(self, environment, host):
        self.environment = environment
        self.host = host
        self.channel = None
        self.stub = None

    def __call__(self):
        if self.channel is None:
            self.channel = grpc.insecure_channel(self.host)
            self.stub = streaming_pb2_grpc.StreamingServiceStub(self.channel)
        return self.stub

    def __del__(self):
        if self.channel:
            self.channel.close()

    def request(self, method, request_data, name):
        start_time = time.time()
        try:
            response = method(request_data)
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
            raise

# --- Custom SOAP Client for Locust ---
class SoapClient:
    def __init__(self, environment, wsdl_url):
        self.environment = environment
        self.wsdl_url = wsdl_url
        self.client = None

    def __call__(self):
        if self.client is None:
            self.client = Client(self.wsdl_url)
        return self.client

    def request(self, method_name, *args, **kwargs):
        start_time = time.time()
        name = f"SOAP {method_name}"
        try:
            method = getattr(self().service, method_name)
            response = method(*args, **kwargs)
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
            raise
        except Exception as e:
            self.environment.events.request.fire(
                request_type="soap",
                name=name,
                response_time=(time.time() - start_time) * 1000,
                response_length=0,
                exception=e,
            )
            raise

# Node.js REST API
class NodeRestUser(HttpUser):
    wait_time = between(0.5, 1.5)
    host = "http://localhost:8011"

    @task(3)
    def listar_usuarios(self):
        self.client.get("/usuarios", name="Listar Usuarios")

    @task(1)
    def criar_usuario(self):
        self.client.post("/usuarios", json={"nome": f"User_{uuid.uuid4()}", "idade": random.randint(18, 60)}, name="Criar Usuario")
    
    @task(2)
    def listar_musicas(self):
        self.client.get("/musicas", name="Listar Musicas")

    @task(1)
    def criar_musica(self):
        self.client.post("/musicas", json={"nome": f"Musica_{uuid.uuid4()}", "artista": f"Artista_{uuid.uuid4()}"}, name="Criar Musica")
