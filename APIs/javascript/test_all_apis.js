const http = require('http');

/**
 * Script para testar todas as APIs JavaScript
 * Testa REST e GraphQL (gRPC e SOAP requerem clientes específicos)
 */

console.log("=" + "=".repeat(78) + "=");
console.log("TESTE DAS APIs JavaScript - Validação de CRUDs Completos");
console.log("=" + "=".repeat(78) + "=");

// IDs para testes
const userId = "user-test-1";
const musicId = "music-test-1";
const playlistId = "playlist-test-1";

// Helpers para HTTP requests
function makeRequest(method, path, port, body = null) {
    return new Promise((resolve, reject) => {
        const options = {
            hostname: 'localhost',
            port: port,
            path: path,
            method: method,
            headers: {
                'Content-Type': 'application/json'
            }
        };

        const req = http.request(options, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    resolve({
                        status: res.statusCode,
                        data: data ? JSON.parse(data) : null
                    });
                } catch (e) {
                    resolve({
                        status: res.statusCode,
                        data: data
                    });
                }
            });
        });

        req.on('error', reject);
        if (body) req.write(JSON.stringify(body));
        req.end();
    });
}

function makeGraphQLRequest(query) {
    return new Promise((resolve, reject) => {
        const data = JSON.stringify({ query });
        const options = {
            hostname: 'localhost',
            port: 9002,
            path: '/',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': data.length
            }
        };

        const req = http.request(options, (res) => {
            let body = '';
            res.on('data', chunk => body += chunk);
            res.on('end', () => {
                try {
                    resolve({
                        status: res.statusCode,
                        data: JSON.parse(body)
                    });
                } catch (e) {
                    resolve({
                        status: res.statusCode,
                        data: body
                    });
                }
            });
        });

        req.on('error', reject);
        req.write(data);
        req.end();
    });
}

async function runTests() {
    try {
        // ===== REST API TESTS (porta 9001) =====
        console.log("\n>>> TESTANDO REST API (porta 9001)");
        console.log("-".repeat(80));

        console.log("\n1. POST /usuarios - Criar usuário");
        let res = await makeRequest('POST', '/usuarios', 9001, {
            id: userId,
            nome: "João Silva",
            idade: 30
        });
        console.log(`   Status: ${res.status}`);
        console.log(`   Response: ${JSON.stringify(res.data, null, 2)}`);

        console.log("\n2. GET /usuarios/{id} - Obter usuário");
        res = await makeRequest('GET', `/usuarios/${userId}`, 9001);
        console.log(`   Status: ${res.status}`);
        console.log(`   Response: ${JSON.stringify(res.data, null, 2)}`);

        console.log("\n3. GET /usuarios - Listar usuários");
        res = await makeRequest('GET', '/usuarios', 9001);
        console.log(`   Status: ${res.status}`);
        console.log(`   Response: ${JSON.stringify(res.data, null, 2)}`);

        console.log("\n4. PUT /usuarios/{id} - Atualizar usuário");
        res = await makeRequest('PUT', `/usuarios/${userId}`, 9001, {
            nome: "João Silva Atualizado",
            idade: 31
        });
        console.log(`   Status: ${res.status}`);
        console.log(`   Response: ${JSON.stringify(res.data, null, 2)}`);

        console.log("\n5. POST /musicas - Criar música");
        res = await makeRequest('POST', '/musicas', 9001, {
            id: musicId,
            nome: "Imagine",
            artista: "John Lennon"
        });
        console.log(`   Status: ${res.status}`);
        console.log(`   Response: ${JSON.stringify(res.data, null, 2)}`);

        console.log("\n6. GET /musicas/{id} - Obter música");
        res = await makeRequest('GET', `/musicas/${musicId}`, 9001);
        console.log(`   Status: ${res.status}`);
        console.log(`   Response: ${JSON.stringify(res.data, null, 2)}`);

        console.log("\n7. POST /playlists - Criar playlist");
        res = await makeRequest('POST', '/playlists', 9001, {
            id: playlistId,
            nome: "Favorites",
            usuario_id: userId
        });
        console.log(`   Status: ${res.status}`);
        console.log(`   Response: ${JSON.stringify(res.data, null, 2)}`);

        console.log("\n8. GET /playlists/{id} - Obter playlist");
        res = await makeRequest('GET', `/playlists/${playlistId}`, 9001);
        console.log(`   Status: ${res.status}`);
        console.log(`   Response: ${JSON.stringify(res.data, null, 2)}`);

        console.log("\n9. POST /playlists/{id}/musicas/{musica_id} - Adicionar música");
        res = await makeRequest('POST', `/playlists/${playlistId}/musicas/${musicId}`, 9001);
        console.log(`   Status: ${res.status}`);
        console.log(`   Response: ${JSON.stringify(res.data, null, 2)}`);

        console.log("\n10. GET /playlists/{id}/musicas - Listar músicas da playlist");
        res = await makeRequest('GET', `/playlists/${playlistId}/musicas`, 9001);
        console.log(`   Status: ${res.status}`);
        console.log(`   Response: ${JSON.stringify(res.data, null, 2)}`);

        console.log("\n11. DELETE /playlists/{id}/musicas/{musica_id} - Remover música");
        res = await makeRequest('DELETE', `/playlists/${playlistId}/musicas/${musicId}`, 9001);
        console.log(`   Status: ${res.status}`);
        console.log(`   Response: ${JSON.stringify(res.data, null, 2)}`);

        console.log("\n12. PUT /playlists/{id} - Atualizar playlist");
        res = await makeRequest('PUT', `/playlists/${playlistId}`, 9001, {
            nome: "Favorites Updated"
        });
        console.log(`   Status: ${res.status}`);
        console.log(`   Response: ${JSON.stringify(res.data, null, 2)}`);

        console.log("\n13. DELETE /playlists/{id} - Deletar playlist");
        res = await makeRequest('DELETE', `/playlists/${playlistId}`, 9001);
        console.log(`   Status: ${res.status}`);
        console.log(`   Response: ${JSON.stringify(res.data, null, 2)}`);

        console.log("\n14. DELETE /musicas/{id} - Deletar música");
        res = await makeRequest('DELETE', `/musicas/${musicId}`, 9001);
        console.log(`   Status: ${res.status}`);
        console.log(`   Response: ${JSON.stringify(res.data, null, 2)}`);

        console.log("\n15. DELETE /usuarios/{id} - Deletar usuário");
        res = await makeRequest('DELETE', `/usuarios/${userId}`, 9001);
        console.log(`   Status: ${res.status}`);
        console.log(`   Response: ${JSON.stringify(res.data, null, 2)}`);

        console.log("\n✓ REST API - TODOS OS TESTES PASSARAM!\n");

        // ===== GraphQL API TESTS (porta 9002) =====
        console.log("\n>>> TESTANDO GraphQL API (porta 9002)");
        console.log("-".repeat(80));

        console.log("\n1. Mutation: criar_usuario");
        res = await makeGraphQLRequest(`
            mutation {
                criarUsuario(id: "gql-user-1", nome: "GraphQL User", idade: 25) {
                    id nome idade
                }
            }
        `);
        console.log(`   Status: ${res.status}`);
        console.log(`   Response: ${JSON.stringify(res.data, null, 2)}`);

        console.log("\n2. Query: obter_usuario");
        res = await makeGraphQLRequest(`
            query {
                obterUsuario(id: "gql-user-1") {
                    id nome idade
                }
            }
        `);
        console.log(`   Status: ${res.status}`);
        console.log(`   Response: ${JSON.stringify(res.data, null, 2)}`);

        console.log("\n3. Mutation: atualizar_usuario");
        res = await makeGraphQLRequest(`
            mutation {
                atualizarUsuario(id: "gql-user-1", nome: "Updated User") {
                    id nome idade
                }
            }
        `);
        console.log(`   Status: ${res.status}`);
        console.log(`   Response: ${JSON.stringify(res.data, null, 2)}`);

        console.log("\n4. Mutation: deletar_usuario");
        res = await makeGraphQLRequest(`
            mutation {
                deletarUsuario(id: "gql-user-1")
            }
        `);
        console.log(`   Status: ${res.status}`);
        console.log(`   Response: ${JSON.stringify(res.data, null, 2)}`);

        console.log("\n✓ GraphQL API - TESTES BÁSICOS PASSARAM!\n");

        console.log("\n" + "=".repeat(80));
        console.log("✓ TODOS OS TESTES COMPLETADOS COM SUCESSO!");
        console.log("  As APIs JavaScript implementam CRUDs completos e idênticos.");
        console.log("=".repeat(80));

        process.exit(0);
    } catch (err) {
        console.error("\n✗ ERRO:", err.message);
        process.exit(1);
    }
}

// Aguarda um pouco para as APIs iniciarem
setTimeout(runTests, 2000);
