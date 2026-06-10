const express = require('express');

const app = express();
app.use(express.json());

const usuarios_db = [];
const musicas_db = [];
const playlists_db = [];
const playlist_musica_db = []; // tuples: [playlist_id, musica_id]

app.get('/usuarios', (req, res) => {
    res.json(usuarios_db);
});

app.post('/usuarios', (req, res) => {
    usuarios_db.push(req.body);
    res.status(201).json(req.body);
});

app.get('/musicas', (req, res) => {
    res.json(musicas_db);
});

app.post('/musicas', (req, res) => {
    musicas_db.push(req.body);
    res.status(201).json(req.body);
});

app.get('/usuarios/:id/playlists', (req, res) => {
    const userPlaylists = playlists_db.filter(p => p.usuario_id === req.params.id);
    res.json(userPlaylists);
});

app.post('/playlists', (req, res) => {
    playlists_db.push(req.body);
    res.status(201).json(req.body);
});

app.get('/playlists/:id/musicas', (req, res) => {
    const m_ids = playlist_musica_db.filter(pm => pm[0] === req.params.id).map(pm => pm[1]);
    const musicas = musicas_db.filter(m => m_ids.includes(m.id));
    res.json(musicas);
});

app.post('/playlists/:id/musicas', (req, res) => {
    playlist_musica_db.push([req.params.id, req.body.musica_id]);
    res.status(201).json({ message: "Música adicionada" });
});

app.get('/musicas/:id/playlists', (req, res) => {
    const p_ids = playlist_musica_db.filter(pm => pm[1] === req.params.id).map(pm => pm[0]);
    const playlists = playlists_db.filter(p => p_ids.includes(p.id));
    res.json(playlists);
});

app.listen(9001, () => {
    console.log('REST API (Node.js) listening on port 9001');
});