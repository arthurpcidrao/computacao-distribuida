from spyne import Application, rpc, ServiceBase, Integer, Unicode, ComplexModel, Array
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from wsgiref.simple_server import make_server
import uuid

class UsuarioModel(ComplexModel):
    id = Unicode
    nome = Unicode
    idade = Integer

class MusicaModel(ComplexModel):
    id = Unicode
    nome = Unicode
    artista = Unicode

class PlaylistModel(ComplexModel):
    id = Unicode
    nome = Unicode
    usuario_id = Unicode

usuarios_db = []
musicas_db = []
playlists_db = []
playlist_musica_db = []

class StreamingService(ServiceBase):
    @rpc(_returns=Array(UsuarioModel))
    def ListarUsuarios(ctx):
        return usuarios_db

    @rpc(_returns=Array(MusicaModel))
    def ListarMusicas(ctx):
        return musicas_db

    @rpc(Unicode, Integer, _returns=UsuarioModel)
    def CriarUsuario(ctx, nome, idade):
        u = UsuarioModel(id=str(uuid.uuid4()), nome=nome, idade=idade)
        usuarios_db.append(u)
        return u

    @rpc(Unicode, Unicode, _returns=MusicaModel)
    def CriarMusica(ctx, nome, artista):
        m = MusicaModel(id=str(uuid.uuid4()), nome=nome, artista=artista)
        musicas_db.append(m)
        return m

    @rpc(Unicode, Unicode, _returns=PlaylistModel)
    def CriarPlaylist(ctx, nome, usuario_id):
        p = PlaylistModel(id=str(uuid.uuid4()), nome=nome, usuario_id=usuario_id)
        playlists_db.append(p)
        return p

    @rpc(Unicode, Unicode, _returns=PlaylistModel)
    def AdicionarMusicaPlaylist(ctx, playlist_id, musica_id):
        playlist_musica_db.append((playlist_id, musica_id))
        return next(p for p in playlists_db if p.id == playlist_id)

    @rpc(Unicode, _returns=Array(PlaylistModel))
    def ListarPlaylistsPorUsuario(ctx, usuario_id):
        return [p for p in playlists_db if p.usuario_id == usuario_id]

    @rpc(Unicode, _returns=Array(MusicaModel))
    def ListarMusicasPorPlaylist(ctx, playlist_id):
        m_ids = [pm[1] for pm in playlist_musica_db if pm[0] == playlist_id]
        return [m for m in musicas_db if m.id in m_ids]

application = Application(
    [StreamingService],
    tns='http://streaming.com/wsdl',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)

wsgi_application = WsgiApplication(application)

if __name__ == '__main__':
    print("SOAP server (Python) started on port 8003")
    server = make_server('0.0.0.0', 8003, wsgi_application)
    server.serve_forever()