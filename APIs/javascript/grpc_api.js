const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');
const path = require('path');

const PROTO_PATH = path.resolve(__dirname, '../shared/streaming.proto');

const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
    keepCase: true, longs: String, enums: String, defaults: true, oneofs: true
});

const streaming_proto = grpc.loadPackageDefinition(packageDefinition).streaming;

const usuarios_db = [];
const musicas_db = [];
const playlists_db = [];
const playlist_musica_db = [];

function listarUsuarios(call, callback) { callback(null, { usuarios: usuarios_db }); }
function listarMusicas(call, callback) { callback(null, { musicas: musicas_db }); }

function listarPlaylistsPorUsuario(call, callback) {
    const p = playlists_db.filter(p => p.usuario_id === call.request.id);
    callback(null, { playlists: p });
}

function listarMusicasPorPlaylist(call, callback) {
    const m_ids = playlist_musica_db.filter(pm => pm[0] === call.request.id).map(pm => pm[1]);
    const m = musicas_db.filter(m => m_ids.includes(m.id));
    callback(null, { musicas: m });
}

function listarPlaylistsPorMusica(call, callback) {
    const p_ids = playlist_musica_db.filter(pm => pm[1] === call.request.id).map(pm => pm[0]);
    const p = playlists_db.filter(p => p_ids.includes(p.id));
    callback(null, { playlists: p });
}

function criarUsuario(call, callback) { usuarios_db.push(call.request); callback(null, call.request); }
function criarMusica(call, callback) { musicas_db.push(call.request); callback(null, call.request); }
function criarPlaylist(call, callback) { playlists_db.push(call.request); callback(null, call.request); }

function adicionarMusicaPlaylist(call, callback) {
    playlist_musica_db.push([call.request.playlist_id, call.request.musica_id]);
    const p = playlists_db.find(p => p.id === call.request.playlist_id);
    callback(null, p);
}

function main() {
    const server = new grpc.Server();
    server.addService(streaming_proto.StreamingService.service, {
        listarUsuarios, listarMusicas, listarPlaylistsPorUsuario,
        listarMusicasPorPlaylist, listarPlaylistsPorMusica,
        criarUsuario, criarMusica, criarPlaylist, adicionarMusicaPlaylist
    });
    server.bindAsync('0.0.0.0:9003', grpc.ServerCredentials.createInsecure(), () => {
        console.log('gRPC server (Node.js) running on port 9003');
        server.start();
    });
}

main();