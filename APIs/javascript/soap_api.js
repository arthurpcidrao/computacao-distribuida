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
      // USUÁRIOS
      ListarUsuarios: function(args, callback) {
        callback({ usuarios: usuarios_db });
      },
      ObterUsuario: function(args, callback) {
        const u = usuarios_db.find(u => u.id === args.id);
        if (!u) return callback(new Error("Usuário não encontrado"));
        callback(null, u);
      },
      CriarUsuario: function(args, callback) {
        if (usuarios_db.find(u => u.id === args.id)) return callback(new Error("Usuário já existe"));
        const u = { id: args.id, nome: args.nome, idade: args.idade };
        usuarios_db.push(u);
        callback(null, u);
      },
      AtualizarUsuario: function(args, callback) {
        const u = usuarios_db.find(u => u.id === args.id);
        if (!u) return callback(new Error("Usuário não encontrado"));
        u.nome = args.nome;
        u.idade = args.idade;
        callback(null, u);
      },
      DeletarUsuario: function(args, callback) {
        const idx = usuarios_db.findIndex(u => u.id === args.id);
        if (idx === -1) return callback(new Error("Usuário não encontrado"));
        usuarios_db.splice(idx, 1);
        playlists_db.splice(0, playlists_db.length, ...playlists_db.filter(p => p.usuario_id !== args.id));
        callback(null, true);
      },

      // MÚSICAS
      ListarMusicas: function(args, callback) {
        callback({ musicas: musicas_db });
      },
      ObterMusica: function(args, callback) {
        const m = musicas_db.find(m => m.id === args.id);
        if (!m) return callback(new Error("Música não encontrada"));
        callback(null, m);
      },
      CriarMusica: function(args, callback) {
        if (musicas_db.find(m => m.id === args.id)) return callback(new Error("Música já existe"));
        const m = { id: args.id, nome: args.nome, artista: args.artista };
        musicas_db.push(m);
        callback(null, m);
      },
      AtualizarMusica: function(args, callback) {
        const m = musicas_db.find(m => m.id === args.id);
        if (!m) return callback(new Error("Música não encontrada"));
        m.nome = args.nome;
        m.artista = args.artista;
        callback(null, m);
      },
      DeletarMusica: function(args, callback) {
        const idx = musicas_db.findIndex(m => m.id === args.id);
        if (idx === -1) return callback(new Error("Música não encontrada"));
        musicas_db.splice(idx, 1);
        playlist_musica_db.splice(0, playlist_musica_db.length, ...playlist_musica_db.filter(pm => pm[1] !== args.id));
        callback(null, true);
      },

      // PLAYLISTS
      ListarPlaylists: function(args, callback) {
        callback({ playlists: playlists_db });
      },
      ObterPlaylist: function(args, callback) {
        const p = playlists_db.find(p => p.id === args.id);
        if (!p) return callback(new Error("Playlist não encontrada"));
        callback(null, p);
      },
      CriarPlaylist: function(args, callback) {
        if (!usuarios_db.find(u => u.id === args.usuario_id)) return callback(new Error("Usuário não existe"));
        if (playlists_db.find(p => p.id === args.id)) return callback(new Error("Playlist já existe"));
        const p = { id: args.id, nome: args.nome, usuario_id: args.usuario_id };
        playlists_db.push(p);
        callback(null, p);
      },
      AtualizarPlaylist: function(args, callback) {
        const p = playlists_db.find(p => p.id === args.id);
        if (!p) return callback(new Error("Playlist não encontrada"));
        p.nome = args.nome;
        callback(null, p);
      },
      DeletarPlaylist: function(args, callback) {
        const idx = playlists_db.findIndex(p => p.id === args.id);
        if (idx === -1) return callback(new Error("Playlist não encontrada"));
        playlists_db.splice(idx, 1);
        playlist_musica_db.splice(0, playlist_musica_db.length, ...playlist_musica_db.filter(pm => pm[0] !== args.id));
        callback(null, true);
      },

      // RELAÇÕES
      ListarPlaylistsPorUsuario: function(args, callback) {
        const playlists = playlists_db.filter(p => p.usuario_id === args.id);
        callback({ playlists: playlists });
      },
      ListarMusicasPorPlaylist: function(args, callback) {
        const m_ids = playlist_musica_db.filter(pm => pm[0] === args.id).map(pm => pm[1]);
        const musicas = musicas_db.filter(m => m_ids.includes(m.id));
        callback({ musicas: musicas });
      },
      ListarPlaylistsPorMusica: function(args, callback) {
        const p_ids = playlist_musica_db.filter(pm => pm[1] === args.id).map(pm => pm[0]);
        const playlists = playlists_db.filter(p => p_ids.includes(p.id));
        callback({ playlists: playlists });
      },
      AdicionarMusicaPlaylist: function(args, callback) {
        if (!playlists_db.find(p => p.id === args.playlist_id)) return callback(new Error("Playlist não encontrada"));
        if (!musicas_db.find(m => m.id === args.musica_id)) return callback(new Error("Música não encontrada"));
        if (playlist_musica_db.some(pm => pm[0] === args.playlist_id && pm[1] === args.musica_id)) {
          return callback(new Error("Música já existe na playlist"));
        }
        playlist_musica_db.push([args.playlist_id, args.musica_id]);
        const p = playlists_db.find(p => p.id === args.playlist_id);
        callback(null, p);
      },
      RemoverMusicaPlaylist: function(args, callback) {
        if (!playlists_db.find(p => p.id === args.playlist_id)) return callback(new Error("Playlist não encontrada"));
        if (!musicas_db.find(m => m.id === args.musica_id)) return callback(new Error("Música não encontrada"));
        const idx = playlist_musica_db.findIndex(pm => pm[0] === args.playlist_id && pm[1] === args.musica_id);
        if (idx === -1) return callback(new Error("Música não está na playlist"));
        playlist_musica_db.splice(idx, 1);
        const p = playlists_db.find(p => p.id === args.playlist_id);
        callback(null, p);
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
