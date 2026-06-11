const soap = require('soap');
const express = require('express');
const fs = require('fs');
const path = require('path');

const usuarios_db = [];
const musicas_db = [];
const playlists_db = [];
const playlist_musica_db = [];

const service = {
  StreamingService: {
    StreamingPort: {
      ListarUsuarios: function(args, callback) { 
        console.log(`[SOAP] ListarUsuarios. Total: ${usuarios_db.length}`);
        callback({ usuarios: usuarios_db });
      },
      ListarMusicas: function(args, callback) { 
        callback({ musicas: musicas_db });
      },
      ListarPlaylistsPorUsuario: function(args, callback) {
        callback({ playlists: playlists_db.filter(p => p.usuario_id === args.id) });
      },
      ListarMusicasPorPlaylist: function(args, callback) {
        const m_ids = playlist_musica_db.filter(pm => pm[0] === args.id).map(pm => pm[1]);
        callback({ musicas: musicas_db.filter(m => m.id in m_ids) });
      },
      ListarPlaylistsPorMusica: function(args, callback) {
        const p_ids = playlist_musica_db.filter(pm => pm[1] === args.id).map(pm => pm[0]);
        callback({ playlists: playlists_db.filter(p => p.id in p_ids) });
      },
      CriarUsuario: function(args, callback) { 
        const u = { id: args.id, nome: args.nome, idade: args.idade };
        usuarios_db.push(u); 
        callback(u); 
      },
      CriarMusica: function(args, callback) { 
        const m = { id: args.id, nome: args.nome, artista: args.artista };
        musicas_db.push(m); 
        callback(m); 
      },
      CriarPlaylist: function(args, callback) { 
        const p = { id: args.id, nome: args.nome, usuario_id: args.usuario_id };
        playlists_db.push(p); 
        callback(p); 
      },
      AdicionarMusicaPlaylist: function(args, callback) {
        playlist_musica_db.push([args.playlist_id, args.musica_id]);
        const p = playlists_db.find(p => p.id === args.playlist_id);
        callback(p || { id: args.playlist_id, nome: "Added", usuario_id: "" });
      }
    }
  }
};

const xml = fs.readFileSync(path.resolve(__dirname, '../shared/streaming.wsdl'), 'utf8');

const app = express();

// Removido o middleware que causava o hang
app.listen(9004, function() {
  soap.listen(app, '/soap', service, xml, function() {
    console.log('SOAP API (Node.js) listening on port 9004 /soap');
  });
});