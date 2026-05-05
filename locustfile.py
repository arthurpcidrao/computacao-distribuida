from locust import HttpUser, task, between

class WordPressTestUser(HttpUser):
    wait_time = between(4, 8)

    @task(1)
    def test_image_1mb(self):
        self.client.get("/?p=21")

    @task(1)
    def test_text_400kb(self):
        self.client.get("/?p=13")

    @task(1)
    def test_image_300kb(self):
        self.client.get("/?p=28")
