from spyne import Application, rpc, ServiceBase, Integer, Unicode, ComplexModel, Array, Boolean
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from wsgiref.simple_server import make_server

class UsuarioModel(ComplexModel):
    __namespace__ = "http://streaming.com/wsdl"
    id = Unicode
    nome = Unicode
    idade = Integer

class MusicaModel(ComplexModel):
    __namespace__ = "http://streaming.com/wsdl"
    id = Unicode
    nome = Unicode
    artista = Unicode

class PlaylistModel(ComplexModel):
    __namespace__ = "http://streaming.com/wsdl"
    id = Unicode
    nome = Unicode
    usuario_id = Unicode

usuarios_db = []
musicas_db = []
playlists_db = []
playlist_musica_db = []

class StreamingService(ServiceBase):
    # USUÁRIOS
    @rpc(_returns=Array(UsuarioModel))
    def ListarUsuarios(ctx):
        return usuarios_db

    @rpc(Unicode, _returns=UsuarioModel)
    def ObterUsuario(ctx, id):
        for u in usuarios_db:
            if u.id == id:
                return u
        raise Exception("Usuário não encontrado")

    @rpc(Unicode, Unicode, Integer, _returns=UsuarioModel)
    def CriarUsuario(ctx, id, nome, idade):
        if any(u.id == id for u in usuarios_db):
            raise Exception("Usuário já existe")
        u = UsuarioModel(id=id, nome=nome, idade=idade)
        usuarios_db.append(u)
        return u

    @rpc(Unicode, Unicode, Integer, _returns=UsuarioModel)
    def AtualizarUsuario(ctx, id, nome, idade):
        for u in usuarios_db:
            if u.id == id:
                u.nome = nome
                u.idade = idade
                return u
        raise Exception("Usuário não encontrado")

    @rpc(Unicode, _returns=Boolean)
    def DeletarUsuario(ctx, id):
        global usuarios_db, playlists_db
        if not any(u.id == id for u in usuarios_db):
            raise Exception("Usuário não encontrado")
        usuarios_db = [u for u in usuarios_db if u.id != id]
        playlists_db[:] = [p for p in playlists_db if p.usuario_id != id]
        return True

    # MÚSICAS
    @rpc(_returns=Array(MusicaModel))
    def ListarMusicas(ctx):
        return musicas_db

    @rpc(Unicode, _returns=MusicaModel)
    def ObterMusica(ctx, id):
        for m in musicas_db:
            if m.id == id:
                return m
        raise Exception("Música não encontrada")

    @rpc(Unicode, Unicode, Unicode, _returns=MusicaModel)
    def CriarMusica(ctx, id, nome, artista):
        if any(m.id == id for m in musicas_db):
            raise Exception("Música já existe")
        m = MusicaModel(id=id, nome=nome, artista=artista)
        musicas_db.append(m)
        return m

    @rpc(Unicode, Unicode, Unicode, _returns=MusicaModel)
    def AtualizarMusica(ctx, id, nome, artista):
        for m in musicas_db:
            if m.id == id:
                m.nome = nome
                m.artista = artista
                return m
        raise Exception("Música não encontrada")

    @rpc(Unicode, _returns=Boolean)
    def DeletarMusica(ctx, id):
        global musicas_db, playlist_musica_db
        if not any(m.id == id for m in musicas_db):
            raise Exception("Música não encontrada")
        musicas_db = [m for m in musicas_db if m.id != id]
        playlist_musica_db[:] = [pm for pm in playlist_musica_db if pm[1] != id]
        return True

    # PLAYLISTS
    @rpc(_returns=Array(PlaylistModel))
    def ListarPlaylists(ctx):
        return playlists_db

    @rpc(Unicode, _returns=PlaylistModel)
    def ObterPlaylist(ctx, id):
        for p in playlists_db:
            if p.id == id:
                return p
        raise Exception("Playlist não encontrada")

    @rpc(Unicode, Unicode, Unicode, _returns=PlaylistModel)
    def CriarPlaylist(ctx, id, nome, usuario_id):
        if not any(u.id == usuario_id for u in usuarios_db):
            raise Exception("Usuário não existe")
        if any(p.id == id for p in playlists_db):
            raise Exception("Playlist já existe")
        p = PlaylistModel(id=id, nome=nome, usuario_id=usuario_id)
        playlists_db.append(p)
        return p

    @rpc(Unicode, Unicode, _returns=PlaylistModel)
    def AtualizarPlaylist(ctx, id, nome):
        for p in playlists_db:
            if p.id == id:
                p.nome = nome
                return p
        raise Exception("Playlist não encontrada")

    @rpc(Unicode, _returns=Boolean)
    def DeletarPlaylist(ctx, id):
        global playlists_db, playlist_musica_db
        if not any(p.id == id for p in playlists_db):
            raise Exception("Playlist não encontrada")
        playlists_db = [p for p in playlists_db if p.id != id]
        playlist_musica_db[:] = [pm for pm in playlist_musica_db if pm[0] != id]
        return True

    # RELAÇÕES
    @rpc(Unicode, _returns=Array(PlaylistModel))
    def ListarPlaylistsPorUsuario(ctx, usuario_id):
        return [p for p in playlists_db if p.usuario_id == usuario_id]

    @rpc(Unicode, _returns=Array(MusicaModel))
    def ListarMusicasPorPlaylist(ctx, playlist_id):
        m_ids = [pm[1] for pm in playlist_musica_db if pm[0] == playlist_id]
        return [m for m in musicas_db if m.id in m_ids]

    @rpc(Unicode, _returns=Array(PlaylistModel))
    def ListarPlaylistsPorMusica(ctx, musica_id):
        p_ids = [pm[0] for pm in playlist_musica_db if pm[1] == musica_id]
        return [p for p in playlists_db if p.id in p_ids]

    @rpc(Unicode, Unicode, _returns=PlaylistModel)
    def AdicionarMusicaPlaylist(ctx, playlist_id, musica_id):
        if not any(p.id == playlist_id for p in playlists_db):
            raise Exception("Playlist não encontrada")
        if not any(m.id == musica_id for m in musicas_db):
            raise Exception("Música não encontrada")
        if any(pm == (playlist_id, musica_id) for pm in playlist_musica_db):
            raise Exception("Música já existe na playlist")
        playlist_musica_db.append((playlist_id, musica_id))
        return next(p for p in playlists_db if p.id == playlist_id)

    @rpc(Unicode, Unicode, _returns=PlaylistModel)
    def RemoverMusicaPlaylist(ctx, playlist_id, musica_id):
        global playlist_musica_db
        if not any(p.id == playlist_id for p in playlists_db):
            raise Exception("Playlist não encontrada")
        if not any(m.id == musica_id for m in musicas_db):
            raise Exception("Música não encontrada")
        if not any(pm == (playlist_id, musica_id) for pm in playlist_musica_db):
            raise Exception("Música não está na playlist")
        playlist_musica_db = [pm for pm in playlist_musica_db if pm != (playlist_id, musica_id)]
        return next(p for p in playlists_db if p.id == playlist_id)

application = Application(
    [StreamingService],
    tns='http://streaming.com/wsdl',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)

wsgi_application = WsgiApplication(application)

if __name__ == '__main__':
    print("SOAP server (Python) started on port 8004")
    server = make_server('0.0.0.0', 8004, wsgi_application)
    server.serve_forever()