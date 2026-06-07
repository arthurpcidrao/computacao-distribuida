const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');
const { v4: uuidv4 } = require('uuid');
const path = require('path');

const PROTO_PATH = path.resolve(__dirname, '../shared/streaming.proto');

const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
    keepCase: true,
    longs: String,
    enums: String,
    defaults: true,
    oneofs: true
});

const streaming_proto = grpc.loadPackageDefinition(packageDefinition).streaming;

const usuarios_db = [];
const musicas_db = [];
const playlists_db = [];
const playlist_musica_db = [];

function listarUsuarios(call, callback) {
    callback(null, { usuarios: usuarios_db });
}

function listarMusicas(call, callback) {
    callback(null, { musicas: musicas_db });
}

function listarPlaylistsPorUsuario(call, callback) {
    const p = playlists_db.filter(p => p.usuario_id === call.request.id);
    callback(null, { playlists: p });
}

function criarUsuario(call, callback) {
    const u = { id: uuidv4(), nome: call.request.nome, idade: call.request.idade };
    usuarios_db.push(u);
    callback(null, u);
}

function criarMusica(call, callback) {
    const m = { id: uuidv4(), nome: call.request.nome, artista: call.request.artista };
    musicas_db.push(m);
    callback(null, m);
}

function criarPlaylist(call, callback) {
    const p = { id: uuidv4(), nome: call.request.nome, usuario_id: call.request.usuario_id };
    playlists_db.push(p);
    callback(null, p);
}

function adicionarMusicaPlaylist(call, callback) {
    playlist_musica_db.push([call.request.playlist_id, call.request.musica_id]);
    const p = playlists_db.find(p => p.id === call.request.playlist_id);
    callback(null, p);
}

function main() {
    const server = new grpc.Server();
    server.addService(streaming_proto.StreamingService.service, {
        listarUsuarios: listarUsuarios,
        listarMusicas: listarMusicas,
        listarPlaylistsPorUsuario: listarPlaylistsPorUsuario,
        criarUsuario: criarUsuario,
        criarMusica: criarMusica,
        criarPlaylist: criarPlaylist,
        adicionarMusicaPlaylist: adicionarMusicaPlaylist
    });
    
    server.bindAsync('0.0.0.0:50052', grpc.ServerCredentials.createInsecure(), () => {
        console.log('gRPC server (Node.js) running on port 50052');
        server.start();
    });
}

main();