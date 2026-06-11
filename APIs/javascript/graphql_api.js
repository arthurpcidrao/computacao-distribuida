const { ApolloServer, gql } = require('apollo-server');

const usuarios_db = [];
const musicas_db = [];
const playlists_db = [];
const playlist_musica_db = [];

const typeDefs = gql`
  type Usuario { id: ID!, nome: String!, idade: Int!, playlists: [Playlist!]! }
  type Musica { id: ID!, nome: String!, artista: String! }
  type Playlist { id: ID!, nome: String!, usuario: Usuario!, musicas: [Musica!]! }

  type Query {
    listarUsuarios: [Usuario!]!
    obterUsuario(id: ID!): Usuario
    listarMusicas: [Musica!]!
    obterMusica(id: ID!): Musica
    listarPlaylists: [Playlist!]!
    obterPlaylist(id: ID!): Playlist
    listarPlaylistsPorUsuario(usuarioId: ID!): [Playlist!]!
    listarMusicasPorPlaylist(playlistId: ID!): [Musica!]!
    listarPlaylistsPorMusica(musicaId: ID!): [Playlist!]!
  }

  type Mutation {
    criarUsuario(id: ID!, nome: String!, idade: Int!): Usuario!
    atualizarUsuario(id: ID!, nome: String, idade: Int): Usuario!
    deletarUsuario(id: ID!): Boolean!

    criarMusica(id: ID!, nome: String!, artista: String!): Musica!
    atualizarMusica(id: ID!, nome: String, artista: String): Musica!
    deletarMusica(id: ID!): Boolean!

    criarPlaylist(id: ID!, nome: String!, usuarioId: ID!): Playlist!
    atualizarPlaylist(id: ID!, nome: String): Playlist!
    deletarPlaylist(id: ID!): Boolean!

    adicionarMusicaPlaylist(playlistId: ID!, musicaId: ID!): Playlist!
    removerMusicaPlaylist(playlistId: ID!, musicaId: ID!): Playlist!
  }
`;

const resolvers = {
  Query: {
    listarUsuarios: () => usuarios_db,
    obterUsuario: (_, { id }) => usuarios_db.find(u => u.id === id) || null,
    listarMusicas: () => musicas_db,
    obterMusica: (_, { id }) => musicas_db.find(m => m.id === id) || null,
    listarPlaylists: () => playlists_db,
    obterPlaylist: (_, { id }) => playlists_db.find(p => p.id === id) || null,
    listarPlaylistsPorUsuario: (_, { usuarioId }) => playlists_db.filter(p => p.usuario_id === usuarioId),
    listarMusicasPorPlaylist: (_, { playlistId }) => {
      const m_ids = playlist_musica_db.filter(pm => pm[0] === playlistId).map(pm => pm[1]);
      return musicas_db.filter(m => m_ids.includes(m.id));
    },
    listarPlaylistsPorMusica: (_, { musicaId }) => {
      const p_ids = playlist_musica_db.filter(pm => pm[1] === musicaId).map(pm => pm[0]);
      return playlists_db.filter(p => p_ids.includes(p.id));
    }
  },
  Mutation: {
    criarUsuario: (_, { id, nome, idade }) => {
      if (usuarios_db.find(u => u.id === id)) throw new Error("Usuário já existe");
      const u = { id, nome, idade };
      usuarios_db.push(u);
      return u;
    },
    atualizarUsuario: (_, { id, nome, idade }) => {
      const u = usuarios_db.find(u => u.id === id);
      if (!u) throw new Error("Usuário não encontrado");
      if (nome) u.nome = nome;
      if (idade) u.idade = idade;
      return u;
    },
    deletarUsuario: (_, { id }) => {
      const idx = usuarios_db.findIndex(u => u.id === id);
      if (idx === -1) throw new Error("Usuário não encontrado");
      usuarios_db.splice(idx, 1);
      playlists_db.splice(0, playlists_db.length, ...playlists_db.filter(p => p.usuario_id !== id));
      return true;
    },

    criarMusica: (_, { id, nome, artista }) => {
      if (musicas_db.find(m => m.id === id)) throw new Error("Música já existe");
      const m = { id, nome, artista };
      musicas_db.push(m);
      return m;
    },
    atualizarMusica: (_, { id, nome, artista }) => {
      const m = musicas_db.find(m => m.id === id);
      if (!m) throw new Error("Música não encontrada");
      if (nome) m.nome = nome;
      if (artista) m.artista = artista;
      return m;
    },
    deletarMusica: (_, { id }) => {
      const idx = musicas_db.findIndex(m => m.id === id);
      if (idx === -1) throw new Error("Música não encontrada");
      musicas_db.splice(idx, 1);
      playlist_musica_db.splice(0, playlist_musica_db.length, ...playlist_musica_db.filter(pm => pm[1] !== id));
      return true;
    },

    criarPlaylist: (_, { id, nome, usuarioId }) => {
      if (!usuarios_db.find(u => u.id === usuarioId)) throw new Error("Usuário não existe");
      if (playlists_db.find(p => p.id === id)) throw new Error("Playlist já existe");
      const p = { id, nome, usuario_id: usuarioId };
      playlists_db.push(p);
      return p;
    },
    atualizarPlaylist: (_, { id, nome }) => {
      const p = playlists_db.find(p => p.id === id);
      if (!p) throw new Error("Playlist não encontrada");
      if (nome) p.nome = nome;
      return p;
    },
    deletarPlaylist: (_, { id }) => {
      const idx = playlists_db.findIndex(p => p.id === id);
      if (idx === -1) throw new Error("Playlist não encontrada");
      playlists_db.splice(idx, 1);
      playlist_musica_db.splice(0, playlist_musica_db.length, ...playlist_musica_db.filter(pm => pm[0] !== id));
      return true;
    },

    adicionarMusicaPlaylist: (_, { playlistId, musicaId }) => {
      if (!playlists_db.find(p => p.id === playlistId)) throw new Error("Playlist não encontrada");
      if (!musicas_db.find(m => m.id === musicaId)) throw new Error("Música não encontrada");
      if (playlist_musica_db.some(pm => pm[0] === playlistId && pm[1] === musicaId)) {
        throw new Error("Música já existe na playlist");
      }
      playlist_musica_db.push([playlistId, musicaId]);
      return playlists_db.find(p => p.id === playlistId);
    },
    removerMusicaPlaylist: (_, { playlistId, musicaId }) => {
      if (!playlists_db.find(p => p.id === playlistId)) throw new Error("Playlist não encontrada");
      if (!musicas_db.find(m => m.id === musicaId)) throw new Error("Música não encontrada");
      const idx = playlist_musica_db.findIndex(pm => pm[0] === playlistId && pm[1] === musicaId);
      if (idx === -1) throw new Error("Música não está na playlist");
      playlist_musica_db.splice(idx, 1);
      return playlists_db.find(p => p.id === playlistId);
    }
  },
  Usuario: { playlists: (parent) => playlists_db.filter(p => p.usuario_id === parent.id) },
  Playlist: {
    usuario: (parent) => usuarios_db.find(u => u.id === parent.usuario_id),
    musicas: (parent) => {
      const m_ids = playlist_musica_db.filter(pm => pm[0] === parent.id).map(pm => pm[1]);
      return musicas_db.filter(m => m_ids.includes(m.id));
    }
  }
};

const server = new ApolloServer({ typeDefs, resolvers });

server.listen({ port: 9002 }).then(({ url }) => {
  console.log(`GraphQL API (Node.js) ready at ${url}`);
});