import os
from locust import HttpUser, task, between


SAMPLE_URLS = [
    "https://docs.python.org/3/",  # 92 links
    "https://developer.mozilla.org/",  # 173 links
    "https://curlie.org/",  # 12 links
    "https://wiki.archlinux.org/",  # 108 links
    "https://help.ubuntu.com/",  # 29 links
    "https://www.gutenberg.org/browse/categories/1.html.utf8",  # 1533 links
    "https://news.ycombinator.com/",  # 225 links
    "https://archive.apache.org/dist/",  # 305 links
    "https://edition.cnn.com/",  # 491 links
    "https://www.bbc.com/",  # 291 links
]

APIs = {
    "python-with-redis": "http://localhost:5000",
    "python-without-redis": "http://localhost:5001",
    "ruby-with-redis": "http://localhost:4567",
    "ruby-without-redis": "http://localhost:4568",
}


class LinkExtractorUser(HttpUser):
    """
    Usuário virtual que simula requisições ao serviço de extração de links.
    Realiza uma sequência de 10 invocações ao serviço de link extraction
    com URLs diferentes.
    """

    wait_time = between(0.5, 1.5)

    def on_start(self):
        """Configuração inicial do usuário virtual."""
        # Obtém a API a ser testada a partir da variável de ambiente
        api_name = os.getenv("API_UNDER_TEST", "python-with-redis")
        
        if api_name not in APIs:
            raise ValueError(f"API '{api_name}' não configurada. Opções: {list(APIs.keys())}")
        
        self.base_url = APIs[api_name]
        self.url_index = 0

    @task
    def extract_links(self):
        """
        Task que extrai links de uma URL.
        Cicla através da lista SAMPLE_URLS, usando uma URL diferente a cada requisição.
        """
        # Seleciona a próxima URL da lista
        current_url = SAMPLE_URLS[self.url_index % len(SAMPLE_URLS)]
        self.url_index += 1

        # Faz a requisição ao endpoint /api/<url> (URL como parte do path)
        # Usamos `catch_response=True` com bloco `with` para poder chamar
        # `response.success()` / `response.failure()` corretamente.
        with self.client.get(f"/api/{current_url}", name="/api/<url> (extract)", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    links_count = len(data)
                    response.success()
                except Exception as e:
                    response.failure(f"Erro ao processar resposta JSON: {e}")
            else:
                response.failure(f"Status code: {response.status_code}")
