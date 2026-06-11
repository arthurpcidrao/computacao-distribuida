#!/usr/bin/env python3
"""
Cliente gRPC para StreamingService
Funciona com APIs gRPC do Python (porta 8003) e JavaScript (porta 9003)

Uso:
  python grpc_client.py --porta 8003 usuarios listar
  python grpc_client.py --porta 8003 usuarios obter --id u1
  python grpc_client.py --porta 8003 usuarios criar --id u1 --nome "João" --idade 30
  python grpc_client.py --porta 8003 usuarios atualizar --id u1 --nome "Silva" --idade 31
  python grpc_client.py --porta 8003 usuarios deletar --id u1

  python grpc_client.py --porta 8003 musicas listar
  python grpc_client.py --porta 8003 musicas obter --id m1
  python grpc_client.py --porta 8003 musicas criar --id m1 --nome "Imagine" --artista "John Lennon"
  python grpc_client.py --porta 8003 musicas atualizar --id m1 --nome "Imagine" --artista "Lennon"
  python grpc_client.py --porta 8003 musicas deletar --id m1

  python grpc_client.py --porta 8003 playlists listar
  python grpc_client.py --porta 8003 playlists obter --id p1
  python grpc_client.py --porta 8003 playlists criar --id p1 --nome "Favorites" --usuario_id u1
  python grpc_client.py --porta 8003 playlists atualizar --id p1 --nome "My Favorites"
  python grpc_client.py --porta 8003 playlists deletar --id p1

  python grpc_client.py --porta 8003 relacoes usuarios-playlists --usuario_id u1
  python grpc_client.py --porta 8003 relacoes playlist-musicas --playlist_id p1
  python grpc_client.py --porta 8003 relacoes musica-playlists --musica_id m1
  python grpc_client.py --porta 8003 relacoes adicionar-musica --playlist_id p1 --musica_id m1
  python grpc_client.py --porta 8003 relacoes remover-musica --playlist_id p1 --musica_id m1
"""

import argparse
import sys
import os

import python.streaming_pb2 as streaming_pb2
import python.streaming_pb2_grpc as streaming_pb2_grpc
import grpc


# ============================================================================
# USUÁRIOS
# ============================================================================

def usuarios_listar(stub):
    """Lista todos os usuários"""
    response = stub.ListarUsuarios(streaming_pb2.Empty())
    if not response.usuarios:
        print("Nenhum usuário encontrado.")
        return
    print(f"Total de usuários: {len(response.usuarios)}")
    for u in response.usuarios:
        print(f"  id={u.id}, nome={u.nome}, idade={u.idade}")


def usuarios_obter(stub, id):
    """Obtém um usuário pelo ID"""
    try:
        request = streaming_pb2.IdRequest(id=id)
        usuario = stub.ObterUsuario(request)
        print(f"Usuário: id={usuario.id}, nome={usuario.nome}, idade={usuario.idade}")
    except grpc.RpcError as e:
        print(f"Erro: {e.details()}")


def usuarios_criar(stub, id, nome, idade):
    """Cria um novo usuário"""
    try:
        request = streaming_pb2.CriarUsuarioRequest(id=id, nome=nome, idade=int(idade))
        usuario = stub.CriarUsuario(request)
        print(f"Usuário criado: id={usuario.id}, nome={usuario.nome}, idade={usuario.idade}")
    except grpc.RpcError as e:
        print(f"Erro: {e.details()}")


def usuarios_atualizar(stub, id, nome, idade):
    """Atualiza um usuário"""
    try:
        request = streaming_pb2.AtualizarUsuarioRequest(id=id, nome=nome, idade=int(idade))
        usuario = stub.AtualizarUsuario(request)
        print(f"Usuário atualizado: id={usuario.id}, nome={usuario.nome}, idade={usuario.idade}")
    except grpc.RpcError as e:
        print(f"Erro: {e.details()}")


def usuarios_deletar(stub, id):
    """Deleta um usuário"""
    try:
        request = streaming_pb2.IdRequest(id=id)
        stub.DeletarUsuario(request)
        print(f"Usuário {id} deletado com sucesso")
    except grpc.RpcError as e:
        print(f"Erro: {e.details()}")


# ============================================================================
# MÚSICAS
# ============================================================================

def musicas_listar(stub):
    """Lista todas as músicas"""
    response = stub.ListarMusicas(streaming_pb2.Empty())
    if not response.musicas:
        print("Nenhuma música encontrada.")
        return
    print(f"Total de músicas: {len(response.musicas)}")
    for m in response.musicas:
        print(f"  id={m.id}, nome={m.nome}, artista={m.artista}")


def musicas_obter(stub, id):
    """Obtém uma música pelo ID"""
    try:
        request = streaming_pb2.IdRequest(id=id)
        musica = stub.ObterMusica(request)
        print(f"Música: id={musica.id}, nome={musica.nome}, artista={musica.artista}")
    except grpc.RpcError as e:
        print(f"Erro: {e.details()}")


def musicas_criar(stub, id, nome, artista):
    """Cria uma nova música"""
    try:
        request = streaming_pb2.CriarMusicaRequest(id=id, nome=nome, artista=artista)
        musica = stub.CriarMusica(request)
        print(f"Música criada: id={musica.id}, nome={musica.nome}, artista={musica.artista}")
    except grpc.RpcError as e:
        print(f"Erro: {e.details()}")


def musicas_atualizar(stub, id, nome, artista):
    """Atualiza uma música"""
    try:
        request = streaming_pb2.AtualizarMusicaRequest(id=id, nome=nome, artista=artista)
        musica = stub.AtualizarMusica(request)
        print(f"Música atualizada: id={musica.id}, nome={musica.nome}, artista={musica.artista}")
    except grpc.RpcError as e:
        print(f"Erro: {e.details()}")


def musicas_deletar(stub, id):
    """Deleta uma música"""
    try:
        request = streaming_pb2.IdRequest(id=id)
        stub.DeletarMusica(request)
        print(f"Música {id} deletada com sucesso")
    except grpc.RpcError as e:
        print(f"Erro: {e.details()}")


# ============================================================================
# PLAYLISTS
# ============================================================================

def playlists_listar(stub):
    """Lista todas as playlists"""
    response = stub.ListarPlaylists(streaming_pb2.Empty())
    if not response.playlists:
        print("Nenhuma playlist encontrada.")
        return
    print(f"Total de playlists: {len(response.playlists)}")
    for p in response.playlists:
        print(f"  id={p.id}, nome={p.nome}, usuario_id={p.usuario_id}")


def playlists_obter(stub, id):
    """Obtém uma playlist pelo ID"""
    try:
        request = streaming_pb2.IdRequest(id=id)
        playlist = stub.ObterPlaylist(request)
        print(f"Playlist: id={playlist.id}, nome={playlist.nome}, usuario_id={playlist.usuario_id}")
    except grpc.RpcError as e:
        print(f"Erro: {e.details()}")


def playlists_criar(stub, id, nome, usuario_id):
    """Cria uma nova playlist"""
    try:
        request = streaming_pb2.CriarPlaylistRequest(id=id, nome=nome, usuario_id=usuario_id)
        playlist = stub.CriarPlaylist(request)
        print(f"Playlist criada: id={playlist.id}, nome={playlist.nome}, usuario_id={playlist.usuario_id}")
    except grpc.RpcError as e:
        print(f"Erro: {e.details()}")


def playlists_atualizar(stub, id, nome):
    """Atualiza uma playlist"""
    try:
        request = streaming_pb2.AtualizarPlaylistRequest(id=id, nome=nome)
        playlist = stub.AtualizarPlaylist(request)
        print(f"Playlist atualizada: id={playlist.id}, nome={playlist.nome}, usuario_id={playlist.usuario_id}")
    except grpc.RpcError as e:
        print(f"Erro: {e.details()}")


def playlists_deletar(stub, id):
    """Deleta uma playlist"""
    try:
        request = streaming_pb2.IdRequest(id=id)
        stub.DeletarPlaylist(request)
        print(f"Playlist {id} deletada com sucesso")
    except grpc.RpcError as e:
        print(f"Erro: {e.details()}")


# ============================================================================
# RELAÇÕES
# ============================================================================

def relacoes_usuarios_playlists(stub, usuario_id):
    """Lista playlists de um usuário"""
    try:
        request = streaming_pb2.IdRequest(id=usuario_id)
        response = stub.ListarPlaylistsPorUsuario(request)
        if not response.playlists:
            print(f"Nenhuma playlist encontrada para usuário {usuario_id}")
            return
        print(f"Playlists do usuário {usuario_id}:")
        for p in response.playlists:
            print(f"  id={p.id}, nome={p.nome}")
    except grpc.RpcError as e:
        print(f"Erro: {e.details()}")


def relacoes_playlist_musicas(stub, playlist_id):
    """Lista músicas de uma playlist"""
    try:
        request = streaming_pb2.IdRequest(id=playlist_id)
        response = stub.ListarMusicasPorPlaylist(request)
        if not response.musicas:
            print(f"Nenhuma música encontrada na playlist {playlist_id}")
            return
        print(f"Músicas da playlist {playlist_id}:")
        for m in response.musicas:
            print(f"  id={m.id}, nome={m.nome}, artista={m.artista}")
    except grpc.RpcError as e:
        print(f"Erro: {e.details()}")


def relacoes_musica_playlists(stub, musica_id):
    """Lista playlists contendo uma música"""
    try:
        request = streaming_pb2.IdRequest(id=musica_id)
        response = stub.ListarPlaylistsPorMusica(request)
        if not response.playlists:
            print(f"Nenhuma playlist encontrada com a música {musica_id}")
            return
        print(f"Playlists com a música {musica_id}:")
        for p in response.playlists:
            print(f"  id={p.id}, nome={p.nome}")
    except grpc.RpcError as e:
        print(f"Erro: {e.details()}")


def relacoes_adicionar_musica(stub, playlist_id, musica_id):
    """Adiciona uma música a uma playlist"""
    try:
        request = streaming_pb2.RelacaoPlaylistMusicaRequest(
            playlist_id=playlist_id,
            musica_id=musica_id
        )
        playlist = stub.AdicionarMusicaPlaylist(request)
        print(f"Música {musica_id} adicionada à playlist {playlist_id}")
        print(f"Playlist: id={playlist.id}, nome={playlist.nome}")
    except grpc.RpcError as e:
        print(f"Erro: {e.details()}")


def relacoes_remover_musica(stub, playlist_id, musica_id):
    """Remove uma música de uma playlist"""
    try:
        request = streaming_pb2.RelacaoPlaylistMusicaRequest(
            playlist_id=playlist_id,
            musica_id=musica_id
        )
        playlist = stub.RemoverMusicaPlaylist(request)
        print(f"Música {musica_id} removida da playlist {playlist_id}")
        print(f"Playlist: id={playlist.id}, nome={playlist.nome}")
    except grpc.RpcError as e:
        print(f"Erro: {e.details()}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Cliente gRPC para StreamingService (Python 8003 / JavaScript 9003)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  # USUÁRIOS
  python grpc_client.py --porta 8003 usuarios listar
  python grpc_client.py --porta 8003 usuarios obter --id u1
  python grpc_client.py --porta 8003 usuarios criar --id u1 --nome "João" --idade 30
  python grpc_client.py --porta 8003 usuarios atualizar --id u1 --nome "Silva" --idade 31
  python grpc_client.py --porta 8003 usuarios deletar --id u1

  # MÚSICAS
  python grpc_client.py --porta 8003 musicas listar
  python grpc_client.py --porta 8003 musicas criar --id m1 --nome "Imagine" --artista "Lennon"
  python grpc_client.py --porta 8003 musicas atualizar --id m1 --nome "Imagine Updated"
  python grpc_client.py --porta 8003 musicas deletar --id m1

  # PLAYLISTS
  python grpc_client.py --porta 8003 playlists listar
  python grpc_client.py --porta 8003 playlists criar --id p1 --nome "Favorites" --usuario_id u1
  python grpc_client.py --porta 8003 playlists atualizar --id p1 --nome "My Favorites"
  python grpc_client.py --porta 8003 playlists deletar --id p1

  # RELAÇÕES
  python grpc_client.py --porta 8003 relacoes usuarios-playlists --usuario_id u1
  python grpc_client.py --porta 8003 relacoes playlist-musicas --playlist_id p1
  python grpc_client.py --porta 8003 relacoes musica-playlists --musica_id m1
  python grpc_client.py --porta 8003 relacoes adicionar-musica --playlist_id p1 --musica_id m1
  python grpc_client.py --porta 8003 relacoes remover-musica --playlist_id p1 --musica_id m1

  # FUNCIONA COM PYTHON (8003) E JAVASCRIPT (9003)
  python grpc_client.py --porta 9003 usuarios listar
        """
    )
    parser.add_argument(
        "--porta",
        type=int,
        default=8003,
        help="Porta do servidor gRPC (Python: 8003, JavaScript: 9003)"
    )

    subparsers = parser.add_subparsers(dest="servico", required=True, help="Serviço a acessar")

    # USUÁRIOS
    usuarios_parser = subparsers.add_parser("usuarios", help="Operações com usuários")
    usuarios_subparsers = usuarios_parser.add_subparsers(dest="operacao", required=True)

    usuarios_subparsers.add_parser("listar", help="Lista todos os usuários")

    obter_parser = usuarios_subparsers.add_parser("obter", help="Obtém um usuário")
    obter_parser.add_argument("--id", required=True, help="ID do usuário")

    criar_parser = usuarios_subparsers.add_parser("criar", help="Cria um novo usuário")
    criar_parser.add_argument("--id", required=True, help="ID do usuário")
    criar_parser.add_argument("--nome", required=True, help="Nome do usuário")
    criar_parser.add_argument("--idade", required=True, type=int, help="Idade do usuário")

    atualizar_parser = usuarios_subparsers.add_parser("atualizar", help="Atualiza um usuário")
    atualizar_parser.add_argument("--id", required=True, help="ID do usuário")
    atualizar_parser.add_argument("--nome", required=True, help="Novo nome")
    atualizar_parser.add_argument("--idade", required=True, type=int, help="Nova idade")

    deletar_parser = usuarios_subparsers.add_parser("deletar", help="Deleta um usuário")
    deletar_parser.add_argument("--id", required=True, help="ID do usuário")

    # MÚSICAS
    musicas_parser = subparsers.add_parser("musicas", help="Operações com músicas")
    musicas_subparsers = musicas_parser.add_subparsers(dest="operacao", required=True)

    musicas_subparsers.add_parser("listar", help="Lista todas as músicas")

    obter_musica_parser = musicas_subparsers.add_parser("obter", help="Obtém uma música")
    obter_musica_parser.add_argument("--id", required=True, help="ID da música")

    criar_musica_parser = musicas_subparsers.add_parser("criar", help="Cria uma nova música")
    criar_musica_parser.add_argument("--id", required=True, help="ID da música")
    criar_musica_parser.add_argument("--nome", required=True, help="Nome da música")
    criar_musica_parser.add_argument("--artista", required=True, help="Artista da música")

    atualizar_musica_parser = musicas_subparsers.add_parser("atualizar", help="Atualiza uma música")
    atualizar_musica_parser.add_argument("--id", required=True, help="ID da música")
    atualizar_musica_parser.add_argument("--nome", required=True, help="Novo nome")
    atualizar_musica_parser.add_argument("--artista", required=True, help="Novo artista")

    deletar_musica_parser = musicas_subparsers.add_parser("deletar", help="Deleta uma música")
    deletar_musica_parser.add_argument("--id", required=True, help="ID da música")

    # PLAYLISTS
    playlists_parser = subparsers.add_parser("playlists", help="Operações com playlists")
    playlists_subparsers = playlists_parser.add_subparsers(dest="operacao", required=True)

    playlists_subparsers.add_parser("listar", help="Lista todas as playlists")

    obter_playlist_parser = playlists_subparsers.add_parser("obter", help="Obtém uma playlist")
    obter_playlist_parser.add_argument("--id", required=True, help="ID da playlist")

    criar_playlist_parser = playlists_subparsers.add_parser("criar", help="Cria uma nova playlist")
    criar_playlist_parser.add_argument("--id", required=True, help="ID da playlist")
    criar_playlist_parser.add_argument("--nome", required=True, help="Nome da playlist")
    criar_playlist_parser.add_argument("--usuario_id", required=True, help="ID do usuário")

    atualizar_playlist_parser = playlists_subparsers.add_parser("atualizar", help="Atualiza uma playlist")
    atualizar_playlist_parser.add_argument("--id", required=True, help="ID da playlist")
    atualizar_playlist_parser.add_argument("--nome", required=True, help="Novo nome")

    deletar_playlist_parser = playlists_subparsers.add_parser("deletar", help="Deleta uma playlist")
    deletar_playlist_parser.add_argument("--id", required=True, help="ID da playlist")

    # RELAÇÕES
    relacoes_parser = subparsers.add_parser("relacoes", help="Operações com relações")
    relacoes_subparsers = relacoes_parser.add_subparsers(dest="operacao", required=True)

    usuarios_playlists_parser = relacoes_subparsers.add_parser(
        "usuarios-playlists",
        help="Playlists de um usuário"
    )
    usuarios_playlists_parser.add_argument("--usuario_id", required=True, help="ID do usuário")

    playlist_musicas_parser = relacoes_subparsers.add_parser(
        "playlist-musicas",
        help="Músicas de uma playlist"
    )
    playlist_musicas_parser.add_argument("--playlist_id", required=True, help="ID da playlist")

    musica_playlists_parser = relacoes_subparsers.add_parser(
        "musica-playlists",
        help="Playlists contendo uma música"
    )
    musica_playlists_parser.add_argument("--musica_id", required=True, help="ID da música")

    adicionar_musica_parser = relacoes_subparsers.add_parser(
        "adicionar-musica",
        help="Adiciona música a playlist"
    )
    adicionar_musica_parser.add_argument("--playlist_id", required=True, help="ID da playlist")
    adicionar_musica_parser.add_argument("--musica_id", required=True, help="ID da música")

    remover_musica_parser = relacoes_subparsers.add_parser(
        "remover-musica",
        help="Remove música de playlist"
    )
    remover_musica_parser.add_argument("--playlist_id", required=True, help="ID da playlist")
    remover_musica_parser.add_argument("--musica_id", required=True, help="ID da música")

    args = parser.parse_args()

    # Conecta ao servidor
    with grpc.insecure_channel(f"localhost:{args.porta}") as channel:
        stub = streaming_pb2_grpc.StreamingServiceStub(channel)

        # USUÁRIOS
        if args.servico == "usuarios":
            if args.operacao == "listar":
                usuarios_listar(stub)
            elif args.operacao == "obter":
                usuarios_obter(stub, args.id)
            elif args.operacao == "criar":
                usuarios_criar(stub, args.id, args.nome, args.idade)
            elif args.operacao == "atualizar":
                usuarios_atualizar(stub, args.id, args.nome, args.idade)
            elif args.operacao == "deletar":
                usuarios_deletar(stub, args.id)

        # MÚSICAS
        elif args.servico == "musicas":
            if args.operacao == "listar":
                musicas_listar(stub)
            elif args.operacao == "obter":
                musicas_obter(stub, args.id)
            elif args.operacao == "criar":
                musicas_criar(stub, args.id, args.nome, args.artista)
            elif args.operacao == "atualizar":
                musicas_atualizar(stub, args.id, args.nome, args.artista)
            elif args.operacao == "deletar":
                musicas_deletar(stub, args.id)

        # PLAYLISTS
        elif args.servico == "playlists":
            if args.operacao == "listar":
                playlists_listar(stub)
            elif args.operacao == "obter":
                playlists_obter(stub, args.id)
            elif args.operacao == "criar":
                playlists_criar(stub, args.id, args.nome, args.usuario_id)
            elif args.operacao == "atualizar":
                playlists_atualizar(stub, args.id, args.nome)
            elif args.operacao == "deletar":
                playlists_deletar(stub, args.id)

        # RELAÇÕES
        elif args.servico == "relacoes":
            if args.operacao == "usuarios-playlists":
                relacoes_usuarios_playlists(stub, args.usuario_id)
            elif args.operacao == "playlist-musicas":
                relacoes_playlist_musicas(stub, args.playlist_id)
            elif args.operacao == "musica-playlists":
                relacoes_musica_playlists(stub, args.musica_id)
            elif args.operacao == "adicionar-musica":
                relacoes_adicionar_musica(stub, args.playlist_id, args.musica_id)
            elif args.operacao == "remover-musica":
                relacoes_remover_musica(stub, args.playlist_id, args.musica_id)


if __name__ == "__main__":
    main()
