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

// USUÁRIOS
function listarUsuarios(call, callback) {
    callback(null, { usuarios: usuarios_db });
}

function obterUsuario(call, callback) {
    const u = usuarios_db.find(u => u.id === call.request.id);
    if (!u) {
        return callback({
            code: grpc.status.NOT_FOUND,
            message: "Usuário não encontrado"
        });
    }
    callback(null, u);
}

function criarUsuario(call, callback) {
    if (usuarios_db.find(u => u.id === call.request.id)) {
        return callback({
            code: grpc.status.ALREADY_EXISTS,
            message: "Usuário já existe"
        });
    }
    usuarios_db.push(call.request);
    callback(null, call.request);
}

function atualizarUsuario(call, callback) {
    const u = usuarios_db.find(u => u.id === call.request.id);
    if (!u) {
        return callback({
            code: grpc.status.NOT_FOUND,
            message: "Usuário não encontrado"
        });
    }
    u.nome = call.request.nome;
    u.idade = call.request.idade;
    callback(null, u);
}

function deletarUsuario(call, callback) {
    const idx = usuarios_db.findIndex(u => u.id === call.request.id);
    if (idx === -1) {
        return callback({
            code: grpc.status.NOT_FOUND,
            message: "Usuário não encontrado"
        });
    }
    usuarios_db.splice(idx, 1);
    playlists_db.splice(0, playlists_db.length, ...playlists_db.filter(p => p.usuario_id !== call.request.id));
    callback(null, {});
}

// MÚSICAS
function listarMusicas(call, callback) {
    callback(null, { musicas: musicas_db });
}

function obterMusica(call, callback) {
    const m = musicas_db.find(m => m.id === call.request.id);
    if (!m) {
        return callback({
            code: grpc.status.NOT_FOUND,
            message: "Música não encontrada"
        });
    }
    callback(null, m);
}

function criarMusica(call, callback) {
    if (musicas_db.find(m => m.id === call.request.id)) {
        return callback({
            code: grpc.status.ALREADY_EXISTS,
            message: "Música já existe"
        });
    }
    musicas_db.push(call.request);
    callback(null, call.request);
}

function atualizarMusica(call, callback) {
    const m = musicas_db.find(m => m.id === call.request.id);
    if (!m) {
        return callback({
            code: grpc.status.NOT_FOUND,
            message: "Música não encontrada"
        });
    }
    m.nome = call.request.nome;
    m.artista = call.request.artista;
    callback(null, m);
}

function deletarMusica(call, callback) {
    const idx = musicas_db.findIndex(m => m.id === call.request.id);
    if (idx === -1) {
        return callback({
            code: grpc.status.NOT_FOUND,
            message: "Música não encontrada"
        });
    }
    musicas_db.splice(idx, 1);
    playlist_musica_db.splice(0, playlist_musica_db.length, ...playlist_musica_db.filter(pm => pm[1] !== call.request.id));
    callback(null, {});
}

// PLAYLISTS
function listarPlaylists(call, callback) {
    callback(null, { playlists: playlists_db });
}

function obterPlaylist(call, callback) {
    const p = playlists_db.find(p => p.id === call.request.id);
    if (!p) {
        return callback({
            code: grpc.status.NOT_FOUND,
            message: "Playlist não encontrada"
        });
    }
    callback(null, p);
}

function criarPlaylist(call, callback) {
    if (!usuarios_db.find(u => u.id === call.request.usuario_id)) {
        return callback({
            code: grpc.status.NOT_FOUND,
            message: "Usuário não existe"
        });
    }
    if (playlists_db.find(p => p.id === call.request.id)) {
        return callback({
            code: grpc.status.ALREADY_EXISTS,
            message: "Playlist já existe"
        });
    }
    playlists_db.push(call.request);
    callback(null, call.request);
}

function atualizarPlaylist(call, callback) {
    const p = playlists_db.find(p => p.id === call.request.id);
    if (!p) {
        return callback({
            code: grpc.status.NOT_FOUND,
            message: "Playlist não encontrada"
        });
    }
    p.nome = call.request.nome;
    callback(null, p);
}

function deletarPlaylist(call, callback) {
    const idx = playlists_db.findIndex(p => p.id === call.request.id);
    if (idx === -1) {
        return callback({
            code: grpc.status.NOT_FOUND,
            message: "Playlist não encontrada"
        });
    }
    playlists_db.splice(idx, 1);
    playlist_musica_db.splice(0, playlist_musica_db.length, ...playlist_musica_db.filter(pm => pm[0] !== call.request.id));
    callback(null, {});
}

// RELAÇÕES
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

function adicionarMusicaPlaylist(call, callback) {
    if (!playlists_db.find(p => p.id === call.request.playlist_id)) {
        return callback({
            code: grpc.status.NOT_FOUND,
            message: "Playlist não encontrada"
        });
    }
    if (!musicas_db.find(m => m.id === call.request.musica_id)) {
        return callback({
            code: grpc.status.NOT_FOUND,
            message: "Música não encontrada"
        });
    }
    if (playlist_musica_db.some(pm => pm[0] === call.request.playlist_id && pm[1] === call.request.musica_id)) {
        return callback({
            code: grpc.status.ALREADY_EXISTS,
            message: "Música já existe na playlist"
        });
    }
    playlist_musica_db.push([call.request.playlist_id, call.request.musica_id]);
    const p = playlists_db.find(p => p.id === call.request.playlist_id);
    callback(null, p);
}

function removerMusicaPlaylist(call, callback) {
    if (!playlists_db.find(p => p.id === call.request.playlist_id)) {
        return callback({
            code: grpc.status.NOT_FOUND,
            message: "Playlist não encontrada"
        });
    }
    if (!musicas_db.find(m => m.id === call.request.musica_id)) {
        return callback({
            code: grpc.status.NOT_FOUND,
            message: "Música não encontrada"
        });
    }
    const idx = playlist_musica_db.findIndex(pm => pm[0] === call.request.playlist_id && pm[1] === call.request.musica_id);
    if (idx === -1) {
        return callback({
            code: grpc.status.NOT_FOUND,
            message: "Música não está na playlist"
        });
    }
    playlist_musica_db.splice(idx, 1);
    const p = playlists_db.find(p => p.id === call.request.playlist_id);
    callback(null, p);
}

function main() {
    const server = new grpc.Server();
    server.addService(streaming_proto.StreamingService.service, {
        listarUsuarios, obterUsuario, criarUsuario, atualizarUsuario, deletarUsuario,
        listarMusicas, obterMusica, criarMusica, atualizarMusica, deletarMusica,
        listarPlaylists, obterPlaylist, criarPlaylist, atualizarPlaylist, deletarPlaylist,
        listarPlaylistsPorUsuario, listarMusicasPorPlaylist, listarPlaylistsPorMusica,
        adicionarMusicaPlaylist, removerMusicaPlaylist
    });
    server.bindAsync('0.0.0.0:9003', grpc.ServerCredentials.createInsecure(), () => {
        console.log('gRPC server (Node.js) running on port 9003');
        server.start();
    });
}

main();