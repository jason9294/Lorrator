from locust import HttpUser, between, task


class AuthenticatedUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.headers = self.login()

    def login(self) -> dict[str, str]:
        response = self.client.post(
            "/auth/login",
            json={"username": "123", "password": "123123"},
            name="/auth/login",
        )

        if response.status_code != 200:
            raise RuntimeError(f"Login failed: {response.status_code} {response.text}")

        access_token = response.json()["access_token"]

        return {"Authorization": f"Bearer {access_token}"}

    @task
    def get_current_user(self):
        self.client.get("/auth/me", headers=self.headers, name="/auth/me")
