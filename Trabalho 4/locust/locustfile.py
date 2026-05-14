import os

from locust import HttpUser, task, between


SAMPLE_URLS = [
    "https://docs.python.org/3/", # 92 links
    "https://developer.mozilla.org/", # 173 links
    "https://curlie.org/", # 12 links
    "https://wiki.archlinux.org/", # 108 links
    "https://help.ubuntu.com/", # 29 links
    "https://www.gutenberg.org/browse/categories/1.html.utf8", # 1533 links
    "https://news.ycombinator.com/", # 225 links
    "https://archive.apache.org/dist/", # 305 links
    "https://edition.cnn.com/", # 491 links
    "https://www.bbc.com/", # 291 links
]

APIs = {
    "python-with-redis": "http://localhost:5000",
    "python-without-redis": "http://localhost:5001",
    "ruby-with-redis": "http://localhost:4567",
    "ruby-without-redis": "http://localhost:4568",
}

class LinkExtractorUser(HttpUser):
    wait_time = between(0.5, 1.5)

    def on_start(self):
        self.use_cache = os.getenv("CACHE_MODE", "on").lower() not in {"0", "false", "off", "no"}

    @task
    def extract_ten_pages(self):
        for index, target_url in enumerate(SAMPLE_URLS, start=1):
            params = {
                "url": target_url,
                "cache": "1" if self.use_cache else "0",
            }
            with self.client.get("/extract", params=params, name=f"extract_page_{index}", catch_response=True) as response:
                if response.status_code != 200:
                    response.failure(f"HTTP {response.status_code}")
                else:
                    response.success()