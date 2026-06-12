const express = require('express');

const app = express();
app.use(express.json());

const usuarios_db = [];
const musicas_db = [];
const playlists_db = [];
const playlist_musica_db = [];

// USUÁRIOS - CRUD
app.get('/usuarios', (req, res) => {
    res.json(usuarios_db);
});

app.get('/usuarios/:id', (req, res) => {
    const usuario = usuarios_db.find(u => u.id === req.params.id);
    if (!usuario) return res.status(404).json({ error: "Usuário não encontrado" });
    res.json(usuario);
});

app.post('/usuarios', (req, res) => {
    if (usuarios_db.find(u => u.id === req.body.id)) {
        return res.status(400).json({ error: "Usuário já existe" });
    }
    usuarios_db.push(req.body);
    res.status(201).json(req.body);
});

app.put('/usuarios/:id', (req, res) => {
    const usuario = usuarios_db.find(u => u.id === req.params.id);
    if (!usuario) return res.status(404).json({ error: "Usuário não encontrado" });
    if (req.body.nome) usuario.nome = req.body.nome;
    if (req.body.idade) usuario.idade = req.body.idade;
    res.json(usuario);
});

app.delete('/usuarios/:id', (req, res) => {
    const idx = usuarios_db.findIndex(u => u.id === req.params.id);
    if (idx === -1) return res.status(404).json({ error: "Usuário não encontrado" });
    usuarios_db.splice(idx, 1);
    // Cascata: remover playlists do usuário
    playlists_db.splice(0, playlists_db.length, ...playlists_db.filter(p => p.usuario_id !== req.params.id));
    res.json({ message: "Usuário deletado" });
});

// MÚSICAS - CRUD
app.get('/musicas', (req, res) => {
    res.json(musicas_db);
});

app.get('/musicas/:id', (req, res) => {
    const musica = musicas_db.find(m => m.id === req.params.id);
    if (!musica) return res.status(404).json({ error: "Música não encontrada" });
    res.json(musica);
});

app.post('/musicas', (req, res) => {
    if (musicas_db.find(m => m.id === req.body.id)) {
        return res.status(400).json({ error: "Música já existe" });
    }
    musicas_db.push(req.body);
    res.status(201).json(req.body);
});

app.put('/musicas/:id', (req, res) => {
    const musica = musicas_db.find(m => m.id === req.params.id);
    if (!musica) return res.status(404).json({ error: "Música não encontrada" });
    if (req.body.nome) musica.nome = req.body.nome;
    if (req.body.artista) musica.artista = req.body.artista;
    res.json(musica);
});

app.delete('/musicas/:id', (req, res) => {
    const idx = musicas_db.findIndex(m => m.id === req.params.id);
    if (idx === -1) return res.status(404).json({ error: "Música não encontrada" });
    musicas_db.splice(idx, 1);
    // Cascata: remover relações com essa música
    playlist_musica_db.splice(0, playlist_musica_db.length, ...playlist_musica_db.filter(pm => pm[1] !== req.params.id));
    res.json({ message: "Música deletada" });
});

// PLAYLISTS - CRUD
app.get('/playlists', (req, res) => {
    res.json(playlists_db);
});

app.get('/playlists/:id', (req, res) => {
    const playlist = playlists_db.find(p => p.id === req.params.id);
    if (!playlist) return res.status(404).json({ error: "Playlist não encontrada" });
    res.json(playlist);
});

app.post('/playlists', (req, res) => {
    if (!usuarios_db.find(u => u.id === req.body.usuario_id)) {
        return res.status(400).json({ error: "Usuário não existe" });
    }
    if (playlists_db.find(p => p.id === req.body.id)) {
        return res.status(400).json({ error: "Playlist já existe" });
    }
    playlists_db.push(req.body);
    res.status(201).json(req.body);
});

app.put('/playlists/:id', (req, res) => {
    const playlist = playlists_db.find(p => p.id === req.params.id);
    if (!playlist) return res.status(404).json({ error: "Playlist não encontrada" });
    if (req.body.nome) playlist.nome = req.body.nome;
    res.json(playlist);
});

app.delete('/playlists/:id', (req, res) => {
    const idx = playlists_db.findIndex(p => p.id === req.params.id);
    if (idx === -1) return res.status(404).json({ error: "Playlist não encontrada" });
    playlists_db.splice(idx, 1);
    // Cascata: remover relações com essa playlist
    playlist_musica_db.splice(0, playlist_musica_db.length, ...playlist_musica_db.filter(pm => pm[0] !== req.params.id));
    res.json({ message: "Playlist deletada" });
});

// RELAÇÕES
app.get('/usuarios/:usuario_id/playlists', (req, res) => {
    if (!usuarios_db.find(u => u.id === req.params.usuario_id)) {
        return res.status(404).json({ error: "Usuário não encontrado" });
    }
    const userPlaylists = playlists_db.filter(p => p.usuario_id === req.params.usuario_id);
    res.json(userPlaylists);
});

app.get('/playlists/:playlist_id/musicas', (req, res) => {
    if (!playlists_db.find(p => p.id === req.params.playlist_id)) {
        return res.status(404).json({ error: "Playlist não encontrada" });
    }
    const m_ids = playlist_musica_db.filter(pm => pm[0] === req.params.playlist_id).map(pm => pm[1]);
    const musicas = musicas_db.filter(m => m_ids.includes(m.id));
    res.json(musicas);
});

app.get('/musicas/:musica_id/playlists', (req, res) => {
    if (!musicas_db.find(m => m.id === req.params.musica_id)) {
        return res.status(404).json({ error: "Música não encontrada" });
    }
    const p_ids = playlist_musica_db.filter(pm => pm[1] === req.params.musica_id).map(pm => pm[0]);
    const playlists = playlists_db.filter(p => p_ids.includes(p.id));
    res.json(playlists);
});

app.post('/playlists/:playlist_id/musicas/:musica_id', (req, res) => {
    if (!playlists_db.find(p => p.id === req.params.playlist_id)) {
        return res.status(404).json({ error: "Playlist não encontrada" });
    }
    if (!musicas_db.find(m => m.id === req.params.musica_id)) {
        return res.status(404).json({ error: "Música não encontrada" });
    }
    if (playlist_musica_db.some(pm => pm[0] === req.params.playlist_id && pm[1] === req.params.musica_id)) {
        return res.status(400).json({ error: "Música já existe na playlist" });
    }
    playlist_musica_db.push([req.params.playlist_id, req.params.musica_id]);
    res.status(201).json({ message: "Música adicionada à playlist" });
});

app.delete('/playlists/:playlist_id/musicas/:musica_id', (req, res) => {
    if (!playlists_db.find(p => p.id === req.params.playlist_id)) {
        return res.status(404).json({ error: "Playlist não encontrada" });
    }
    if (!musicas_db.find(m => m.id === req.params.musica_id)) {
        return res.status(404).json({ error: "Música não encontrada" });
    }
    const idx = playlist_musica_db.findIndex(pm => pm[0] === req.params.playlist_id && pm[1] === req.params.musica_id);
    if (idx === -1) {
        return res.status(404).json({ error: "Música não está na playlist" });
    }
    playlist_musica_db.splice(idx, 1);
    res.json({ message: "Música removida da playlist" });
});

app.listen(9001, () => {
    console.log('REST API (Node.js) listening on port 9001');
});