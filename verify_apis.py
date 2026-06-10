import requests
import grpc
import uuid
import sys
import os
import json
from zeep import Client

# Add paths for gRPC stubs
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'APIs', 'python')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'APIs', 'shared')))
import streaming_pb2
import streaming_pb2_grpc

def test_rest(name, url):
    print(f"--- Testing REST: {name} ({url}) ---")
    user_id = str(uuid.uuid4())
    try:
        r = requests.post(f"{url}/usuarios", json={"id": user_id, "nome": "TestUser", "idade": 30}, timeout=5)
        print(f"  POST /usuarios: {r.status_code}")
        r = requests.get(f"{url}/usuarios", timeout=5)
        print(f"  GET /usuarios: {r.status_code} - Found {len(r.json())} users")
        return r.status_code == 200
    except Exception as e:
        print(f"  REST FAILED: {e}")
        return False

def test_graphql(name, url):
    print(f"--- Testing GraphQL: {name} ({url}) ---")
    user_id = str(uuid.uuid4())
    q_mut = f'mutation {{ criarUsuario(id: "{user_id}", nome: "GQLUser", idade: 25) {{ id nome }} }}'
    try:
        r = requests.post(url, json={"query": q_mut}, timeout=5)
        print(f"  Mutation: {r.status_code}")
        q_list = "{ listarUsuarios { id nome idade } }"
        r = requests.post(url, json={"query": q_list}, timeout=5)
        users = r.json().get('data', {}).get('listarUsuarios', [])
        print(f"  Query: {r.status_code} - Found {len(users)} users")
        return r.status_code == 200
    except Exception as e:
        print(f"  GraphQL FAILED: {e}")
        return False

def test_grpc(name, host):
    print(f"--- Testing gRPC: {name} ({host}) ---")
    user_id = str(uuid.uuid4())
    try:
        channel = grpc.insecure_channel(host)
        stub = streaming_pb2_grpc.StreamingServiceStub(channel)
        stub.CriarUsuario(streaming_pb2.CriarUsuarioRequest(id=user_id, nome="gRPCUser", idade=40))
        print("  CriarUsuario: Success")
        res = stub.ListarUsuarios(streaming_pb2.Vazio())
        print(f"  ListarUsuarios: Found {len(res.usuarios)} users")
        channel.close()
        return True
    except Exception as e:
        print(f"  gRPC FAILED: {e}")
        return False

def test_soap(name, wsdl, address):
    print(f"--- Testing SOAP: {name} ({wsdl}) ---")
    user_id = str(uuid.uuid4())
    try:
        client = Client(wsdl)
        # Try to find the correct binding
        binding_name = 'StreamingBinding'
        if '8004' in address: # Python Spyne typically uses 'Application' or similar
             # Get the first available binding if StreamingBinding is not there
             if '{http://streaming.com/wsdl}Application' in client.wsdl.bindings:
                 binding_name = 'Application'
        
        service = client.create_service('{http://streaming.com/wsdl}' + binding_name, address)
        
        res = service.CriarUsuario(id=user_id, nome="SOAPUser", idade=50)
        # res might be a dictionary or object
        print(f"  CriarUsuario: Success")
        
        res_list = service.ListarUsuarios()
        # Handle different response structures
        users = []
        if isinstance(res_list, dict) and 'usuarios' in res_list:
            users = res_list['usuarios']
        elif hasattr(res_list, 'usuarios'):
            users = res_list.usuarios
        elif isinstance(res_list, list):
            users = res_list
        else:
            # Maybe the list is inside another attribute
            # Spyne often returns a list directly or wrapped
            users = res_list
            
        print(f"  ListarUsuarios: Found {len(users) if users else 0} users")
        return True
    except Exception as e:
        print(f"  SOAP FAILED: {e}")
        return False

def main():
    success = True
    print("\nStarting Verification...")
    
    # Python
    if not test_rest("Python", "http://localhost:8001"): success = False
    if not test_graphql("Python", "http://localhost:8002/graphql"): success = False
    if not test_grpc("Python", "localhost:8003"): success = False
    if not test_soap("Python", "http://localhost:8004/?wsdl", "http://localhost:8004/"): success = False
    
    # Node.js
    if not test_rest("Node.js", "http://localhost:9001"): success = False
    if not test_graphql("Node.js", "http://localhost:9002"): success = False
    if not test_grpc("Node.js", "localhost:9003"): success = False
    if not test_soap("Node.js", "http://localhost:9004/soap?wsdl", "http://localhost:9004/soap"): success = False

    if success:
        print("\n✅ ALL APIS VERIFIED SUCCESSFULLY!")
    else:
        print("\n❌ SOME APIS FAILED VERIFICATION.")
        sys.exit(1)

if __name__ == "__main__":
    main()
