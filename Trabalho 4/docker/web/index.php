<?php
$backendOptions = [
    'python' => getenv('PYTHON_API_URL') ?: 'http://app-python:5000/extract',
    'ruby' => getenv('RUBY_API_URL') ?: 'http://app-ruby:4567/extract',
];

$defaultUrl = getenv('DEFAULT_SAMPLE_URL') ?: 'http://sample-site/page1.html';
$selectedBackend = $_POST['backend'] ?? 'python';
$selectedBackend = array_key_exists($selectedBackend, $backendOptions) ? $selectedBackend : 'python';
$inputUrl = trim($_POST['url'] ?? $defaultUrl);
$useCache = isset($_POST['cache']) ? $_POST['cache'] === '1' : true;
$result = null;
$error = null;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $query = http_build_query([
        'url' => $inputUrl,
        'cache' => $useCache ? '1' : '0',
    ]);
    $requestUrl = $backendOptions[$selectedBackend] . '?' . $query;
    $context = stream_context_create([
        'http' => [
            'timeout' => 20,
            'ignore_errors' => true,
        ],
    ]);

    $responseBody = @file_get_contents($requestUrl, false, $context);
    if ($responseBody === false) {
        $error = 'Não foi possível consultar a API selecionada.';
    } else {
        $decoded = json_decode($responseBody, true);
        if ($decoded === null && json_last_error() !== JSON_ERROR_NONE) {
            $error = 'Resposta inválida da API.';
        } else {
            // Caso: resposta é um array indexado (lista bruta de links ou objetos)
            if (is_array($decoded) && array_values($decoded) === $decoded) {
                $rawLinks = $decoded;
                $links = array_map(function($item) {
                    if (is_array($item)) {
                        if (isset($item['href'])) return $item['href'];
                        if (isset($item['link'])) return $item['link'];
                        return json_encode($item);
                    }
                    return (string)$item;
                }, $rawLinks);

                $result = [
                    'service' => $selectedBackend === 'python' ? 'linkextractor-python' : 'linkextractor-ruby',
                    'url' => $inputUrl,
                    'cached' => false,
                    'source' => 'web',
                    'link_count' => count($links),
                    'links' => $links,
                ];
            } elseif (isset($decoded['links']) && is_array($decoded['links'])) {
                $result = $decoded;
            } else {
                $error = 'Resposta inválida da API.';
            }
        }
    }
}

function selected(string $current, string $expected): string
{
    return $current === $expected ? 'selected' : '';
}

function checked(bool $value): string
{
    return $value ? 'checked' : '';
}
?>
<!doctype html>
<html lang="pt-BR">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Link Extractor - Trabalho 4</title>
    <style>
        :root {
            color-scheme: light;
            --bg: #f4f1ea;
            --panel: #ffffff;
            --ink: #12212f;
            --muted: #5a6b78;
            --accent: #0f5b78;
            --accent-2: #d04e24;
            --border: #d8e1e8;
        }
        * { box-sizing: border-box; }
        body {
            margin: 0;
            font-family: Arial, Helvetica, sans-serif;
            background: linear-gradient(135deg, #e9f3f8 0%, #f7efe4 100%);
            color: var(--ink);
        }
        .shell {
            max-width: 1100px;
            margin: 0 auto;
            padding: 32px 20px 48px;
        }
        .hero {
            display: grid;
            gap: 16px;
            grid-template-columns: 1.2fr 0.8fr;
            align-items: stretch;
            margin-bottom: 20px;
        }
        .card {
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 18px;
            box-shadow: 0 20px 50px rgba(18, 33, 47, 0.08);
            padding: 24px;
        }
        h1, h2, h3 { margin-top: 0; }
        h1 { font-size: 2.3rem; }
        .lead { color: var(--muted); line-height: 1.6; }
        .form-grid { display: grid; gap: 14px; grid-template-columns: 1fr 180px 120px; }
        label { display: block; font-weight: 700; margin-bottom: 6px; }
        input[type="url"], select {
            width: 100%;
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 12px 14px;
            font-size: 1rem;
        }
        .check { display: flex; align-items: center; gap: 10px; margin-top: 8px; color: var(--muted); }
        button {
            border: 0;
            border-radius: 12px;
            padding: 13px 16px;
            font-weight: 700;
            color: white;
            background: linear-gradient(135deg, var(--accent), #0a3448);
            cursor: pointer;
        }
        .meta {
            display: grid;
            gap: 12px;
            grid-template-columns: repeat(3, minmax(0, 1fr));
        }
        .pill {
            border-radius: 999px;
            padding: 10px 14px;
            background: #edf6fa;
            color: var(--ink);
            border: 1px solid var(--border);
        }
        .result {
            margin-top: 20px;
        }
        .result ul {
            margin: 0;
            padding-left: 20px;
            line-height: 1.7;
        }
        .notice {
            padding: 12px 14px;
            border-radius: 12px;
            margin: 12px 0;
        }
        .error { background: #ffe7e1; color: #7b2d18; }
        .ok { background: #e5f6ed; color: #1b5f38; }
        .sample-links { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
        .sample-links a {
            display: block;
            padding: 10px 12px;
            border-radius: 10px;
            background: #f7fafc;
            border: 1px solid var(--border);
            color: var(--accent);
            text-decoration: none;
        }
        code {
            background: #f1f5f9;
            padding: 2px 6px;
            border-radius: 6px;
        }
        @media (max-width: 900px) {
            .hero, .form-grid, .meta, .sample-links { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <main class="shell">
        <section class="hero">
            <div class="card">
                <h1>Link Extractor</h1>
                <p class="lead">Front-end PHP para comparar as versões Python e Ruby do serviço de extração de links, com suporte a cache Redis e cenários de teste de desempenho.</p>

                <form method="post">
                    <div class="form-grid">
                        <div>
                            <label for="url">URL de origem</label>
                            <input id="url" name="url" type="url" value="<?php echo htmlspecialchars($inputUrl, ENT_QUOTES); ?>" placeholder="http://sample-site/page1.html" required>
                        </div>
                        <div>
                            <label for="backend">Backend</label>
                            <select id="backend" name="backend">
                                <option value="python" <?php echo selected($selectedBackend, 'python'); ?>>Python</option>
                                <option value="ruby" <?php echo selected($selectedBackend, 'ruby'); ?>>Ruby</option>
                            </select>
                        </div>
                        <div style="display:flex;align-items:end;">
                            <button type="submit">Extrair links</button>
                        </div>
                    </div>
                    <label class="check">
                        <input type="checkbox" name="cache" value="1" <?php echo checked($useCache); ?>>
                        usar cache Redis
                    </label>
                </form>
            </div>

            <aside class="card">
                <h2>Arquitetura</h2>
                <div class="meta">
                    <div class="pill"><strong>PHP</strong><br>Interface web</div>
                    <div class="pill"><strong>Python/Ruby</strong><br>APIs de extração</div>
                    <div class="pill"><strong>Redis</strong><br>Cache de links</div>
                </div>
                <h3 style="margin-top:18px;">URLs de exemplo</h3>
                <div class="sample-links">
                    <a href="?url=<?php echo urlencode(getenv('DEFAULT_SAMPLE_URL') ?: 'http://sample-site/page1.html'); ?>">Página 1</a>
                    <a href="?url=http://sample-site/page2.html">Página 2</a>
                    <a href="?url=http://sample-site/page3.html">Página 3</a>
                    <a href="?url=http://sample-site/page4.html">Página 4</a>
                </div>
            </aside>
        </section>

        <section class="card result">
            <h2>Resultado</h2>
            <?php if ($error): ?>
                <div class="notice error"><?php echo htmlspecialchars($error, ENT_QUOTES); ?></div>
            <?php elseif ($result): ?>
                <div class="notice ok">
                    Serviço: <strong><?php echo htmlspecialchars($result['service'] ?? ''); ?></strong> |
                    Fonte: <strong><?php echo htmlspecialchars($result['source'] ?? ''); ?></strong> |
                    Cache: <strong><?php echo !empty($result['cached']) ? 'hit' : 'miss'; ?></strong> |
                    Links encontrados: <strong><?php echo (int)($result['link_count'] ?? 0); ?></strong>
                </div>
                <p><strong>URL:</strong> <?php echo htmlspecialchars($result['url'] ?? '', ENT_QUOTES); ?></p>
                <ul>
                    <?php foreach (($result['links'] ?? []) as $link): ?>
                        <li><a href="<?php echo htmlspecialchars($link, ENT_QUOTES); ?>" target="_blank" rel="noopener noreferrer"><?php echo htmlspecialchars($link, ENT_QUOTES); ?></a></li>
                    <?php endforeach; ?>
                </ul>
            <?php else: ?>
                <p class="lead">Preencha a URL e escolha o backend para extrair os links.</p>
            <?php endif; ?>
        </section>
    </main>
</body>
</html>