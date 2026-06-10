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
      ListarUsuarios: function(args) { return { usuarios: usuarios_db }; },
      ListarMusicas: function(args) { return { musicas: musicas_db }; },
      ListarPlaylistsPorUsuario: function(args) {
          return { playlists: playlists_db.filter(p => p.usuario_id === args.id) };
      },
      ListarMusicasPorPlaylist: function(args) {
          const m_ids = playlist_musica_db.filter(pm => pm[0] === args.id).map(pm => pm[1]);
          return { musicas: musicas_db.filter(m => m_ids.includes(m.id)) };
      },
      ListarPlaylistsPorMusica: function(args) {
          const p_ids = playlist_musica_db.filter(pm => pm[1] === args.id).map(pm => pm[0]);
          return { playlists: playlists_db.filter(p => p_ids.includes(p.id)) };
      },
      CriarUsuario: function(args) { 
          const u = { id: args.id, nome: args.nome, idade: args.idade };
          usuarios_db.push(u); 
          return u; 
      },
      CriarMusica: function(args) { 
          const m = { id: args.id, nome: args.nome, artista: args.artista };
          musicas_db.push(m); 
          return m; 
      },
      CriarPlaylist: function(args) { 
          const p = { id: args.id, nome: args.nome, usuario_id: args.usuario_id };
          playlists_db.push(p); 
          return p; 
      },
      AdicionarMusicaPlaylist: function(args) {
          playlist_musica_db.push([args.playlist_id, args.musica_id]);
          return playlists_db.find(p => p.id === args.playlist_id) || {id: args.playlist_id, nome:"", usuario_id:""};
      }
    }
  }
};

const xml = fs.readFileSync(path.resolve(__dirname, '../shared/streaming.wsdl'), 'utf8');

const app = express();
app.listen(9004, function() {
  soap.listen(app, '/soap', service, xml, function() {
    console.log('SOAP API (Node.js) listening on port 9004 /soap');
  });
});