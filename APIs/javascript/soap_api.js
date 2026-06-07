const soap = require('soap');
const express = require('express');
const { v4: uuidv4 } = require('uuid');
const fs = require('fs');
const path = require('path');

const usuarios_db = [];
const musicas_db = [];

const service = {
  StreamingService: {
    StreamingPort: {
      ListarUsuarios: function(args) {
        return { usuarios: usuarios_db };
      },
      ListarMusicas: function(args) {
        return { musicas: musicas_db };
      },
      CriarUsuario: function(args) {
        const u = { id: uuidv4(), nome: args.nome, idade: args.idade };
        usuarios_db.push(u);
        return u;
      }
    }
  }
};

const xml = fs.readFileSync(path.resolve(__dirname, '../shared/streaming.wsdl'), 'utf8');

const app = express();

app.listen(8013, function() {
  soap.listen(app, '/soap', service, xml, function() {
    console.log('SOAP API (Node.js) listening on port 8013 /soap');
  });
});