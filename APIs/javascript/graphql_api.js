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
    listarMusicas: [Musica!]!
    listarPlaylistsPorUsuario(usuarioId: ID!): [Playlist!]!
    listarMusicasPorPlaylist(playlistId: ID!): [Musica!]!
    listarPlaylistsPorMusica(musicaId: ID!): [Playlist!]!
  }

  type Mutation {
    criarUsuario(id: ID!, nome: String!, idade: Int!): Usuario!
    criarMusica(id: ID!, nome: String!, artista: String!): Musica!
    criarPlaylist(id: ID!, nome: String!, usuarioId: ID!): Playlist!
    adicionarMusicaPlaylist(playlistId: ID!, musicaId: ID!): Playlist!
  }
`;

const resolvers = {
  Query: {
    listarUsuarios: () => usuarios_db,
    listarMusicas: () => musicas_db,
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
    criarUsuario: (_, args) => { usuarios_db.push(args); return args; },
    criarMusica: (_, args) => { musicas_db.push(args); return args; },
    criarPlaylist: (_, args) => { playlists_db.push(args); return args; },
    adicionarMusicaPlaylist: (_, { playlistId, musicaId }) => {
      playlist_musica_db.push([playlistId, musicaId]);
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