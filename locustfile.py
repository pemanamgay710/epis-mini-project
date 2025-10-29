from locust import HttpUser, task, between

class StreamlitUser(HttpUser):
    wait_time = between(1, 3)  # wait between each task

    @task
    def load_main_page(self):
        # Visits the main Streamlit page
        self.client.get("/")

    @task
    def refresh_page(self):
        # Simulates refreshing the page or reloading data
        self.client.get("/")
