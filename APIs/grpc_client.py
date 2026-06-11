import argparse
import sys
import os

import python.streaming_pb2 as streaming_pb2
import python.streaming_pb2_grpc as streaming_pb2_grpc
import grpc


def listar_usuarios(stub):
    response = stub.ListarUsuarios(streaming_pb2.Vazio())
    if not response.usuarios:
        print("Nenhum usuário encontrado.")
        return
    for u in response.usuarios:
        print(f"  id={u.id}, nome={u.nome}, idade={u.idade}")


def criar_usuario(stub, id, nome, idade):
    request = streaming_pb2.CriarUsuarioRequest(id=id, nome=nome, idade=int(idade))
    usuario = stub.CriarUsuario(request)
    print(f"Usuário criado: id={usuario.id}, nome={usuario.nome}, idade={usuario.idade}")


def main():
    parser = argparse.ArgumentParser(description="Cliente gRPC para StreamingService")
    parser.add_argument("--porta", type=int, default=8003, help="Porta do servidor gRPC (padrão: 8003)")
    subparsers = parser.add_subparsers(dest="acao", required=True, help="Ação a executar")

    subparsers.add_parser("listar-usuarios", help="Lista todos os usuários")

    criar_parser = subparsers.add_parser("criar-usuario", help="Cria um novo usuário")
    criar_parser.add_argument("--id", required=True, help="ID do usuário")
    criar_parser.add_argument("--nome", required=True, help="Nome do usuário")
    criar_parser.add_argument("--idade", required=True, type=int, help="Idade do usuário")

    args = parser.parse_args()

    with grpc.insecure_channel(f"localhost:{args.porta}") as channel:
        stub = streaming_pb2_grpc.StreamingServiceStub(channel)

        if args.acao == "listar-usuarios":
            listar_usuarios(stub)
        elif args.acao == "criar-usuario":
            criar_usuario(stub, args.id, args.nome, args.idade)


if __name__ == "__main__":
    main()



# Listar usuários em porta customizada (exemplo: 8003 - python | 9003 - node)
# uv run python APIs/clients/grpc_client.py --porta 8003 listar-usuarios

# Criar usuário em porta customizada (exemplo: 8003 - python | 9003 - node)
# uv run python APIs/clients/grpc_client.py --porta 9000 criar-usuario --id 2 --nome "Maria" --idade 30