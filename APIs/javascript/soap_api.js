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
      ListarUsuarios: function(args) {
        return { usuarios: usuarios_db };
      },
      ObterUsuario: function(args) {
        const u = usuarios_db.find(u => u.id === args.id);
        if (!u) throw new Error("Usuário não encontrado");
        return u;
      },
      CriarUsuario: function(args) {
        if (usuarios_db.find(u => u.id === args.id)) throw new Error("Usuário já existe");
        const u = { id: args.id, nome: args.nome, idade: args.idade };
        usuarios_db.push(u);
        return u;
      },
      AtualizarUsuario: function(args) {
        const u = usuarios_db.find(u => u.id === args.id);
        if (!u) throw new Error("Usuário não encontrado");
        u.nome = args.nome;
        u.idade = args.idade;
        return u;
      },
      DeletarUsuario: function(args) {
        const idx = usuarios_db.findIndex(u => u.id === args.id);
        if (idx === -1) throw new Error("Usuário não encontrado");
        usuarios_db.splice(idx, 1);
        playlists_db.splice(0, playlists_db.length, ...playlists_db.filter(p => p.usuario_id !== args.id));
        return true;
      },

      // MÚSICAS
      ListarMusicas: function(args) {
        return { musicas: musicas_db };
      },
      ObterMusica: function(args) {
        const m = musicas_db.find(m => m.id === args.id);
        if (!m) throw new Error("Música não encontrada");
        return m;
      },
      CriarMusica: function(args) {
        if (musicas_db.find(m => m.id === args.id)) throw new Error("Música já existe");
        const m = { id: args.id, nome: args.nome, artista: args.artista };
        musicas_db.push(m);
        return m;
      },
      AtualizarMusica: function(args) {
        const m = musicas_db.find(m => m.id === args.id);
        if (!m) throw new Error("Música não encontrada");
        m.nome = args.nome;
        m.artista = args.artista;
        return m;
      },
      DeletarMusica: function(args) {
        const idx = musicas_db.findIndex(m => m.id === args.id);
        if (idx === -1) throw new Error("Música não encontrada");
        musicas_db.splice(idx, 1);
        playlist_musica_db.splice(0, playlist_musica_db.length, ...playlist_musica_db.filter(pm => pm[1] !== args.id));
        return true;
      },

      // PLAYLISTS
      ListarPlaylists: function(args) {
        return { playlists: playlists_db };
      },
      ObterPlaylist: function(args) {
        const p = playlists_db.find(p => p.id === args.id);
        if (!p) throw new Error("Playlist não encontrada");
        return p;
      },
      CriarPlaylist: function(args) {
        if (!usuarios_db.find(u => u.id === args.usuario_id)) throw new Error("Usuário não existe");
        if (playlists_db.find(p => p.id === args.id)) throw new Error("Playlist já existe");
        const p = { id: args.id, nome: args.nome, usuario_id: args.usuario_id };
        playlists_db.push(p);
        return p;
      },
      AtualizarPlaylist: function(args) {
        const p = playlists_db.find(p => p.id === args.id);
        if (!p) throw new Error("Playlist não encontrada");
        p.nome = args.nome;
        return p;
      },
      DeletarPlaylist: function(args) {
        const idx = playlists_db.findIndex(p => p.id === args.id);
        if (idx === -1) throw new Error("Playlist não encontrada");
        playlists_db.splice(idx, 1);
        playlist_musica_db.splice(0, playlist_musica_db.length, ...playlist_musica_db.filter(pm => pm[0] !== args.id));
        return true;
      },

      // RELAÇÕES
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
      AdicionarMusicaPlaylist: function(args) {
        if (!playlists_db.find(p => p.id === args.playlist_id)) throw new Error("Playlist não encontrada");
        if (!musicas_db.find(m => m.id === args.musica_id)) throw new Error("Música não encontrada");
        if (playlist_musica_db.some(pm => pm[0] === args.playlist_id && pm[1] === args.musica_id)) {
          throw new Error("Música já existe na playlist");
        }
        playlist_musica_db.push([args.playlist_id, args.musica_id]);
        return playlists_db.find(p => p.id === args.playlist_id);
      },
      RemoverMusicaPlaylist: function(args) {
        if (!playlists_db.find(p => p.id === args.playlist_id)) throw new Error("Playlist não encontrada");
        if (!musicas_db.find(m => m.id === args.musica_id)) throw new Error("Música não encontrada");
        const idx = playlist_musica_db.findIndex(pm => pm[0] === args.playlist_id && pm[1] === args.musica_id);
        if (idx === -1) throw new Error("Música não está na playlist");
        playlist_musica_db.splice(idx, 1);
        return playlists_db.find(p => p.id === args.playlist_id);
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