"""Optional bonus: Locust load test against one Reqres endpoint.

Assignment cap: at most 100 API calls in a day. Default run uses 5 concurrent
users and stops after 40 requests so a few local reruns stay under the limit.

Usage:
    locust -f load_test.py --headless -u 5 -r 1 --run-time 20s
"""

import os

from locust import HttpUser, between, events, task

MAX_REQUESTS = int(os.getenv("LOCUST_MAX_REQUESTS", "40"))
REQRES_API_KEY = os.getenv("REQRES_API_KEY", "reqres-free-v1")
_ENV = None


@events.test_start.add_listener
def _announce(environment, **_kwargs):
    global _ENV
    _ENV = environment
    print(
        f"Load plan: 5 users, spawn 1/s, GET /api/users?page=1, "
        f"hard stop at {MAX_REQUESTS} requests."
    )


@events.request.add_listener
def _stop_at_cap(**_kwargs):
    if _ENV and _ENV.runner and _ENV.runner.stats.total.num_requests >= MAX_REQUESTS:
        _ENV.runner.quit()


class ReqresUser(HttpUser):
    host = "https://reqres.in"
    wait_time = between(1, 2)

    def on_start(self):
        self.client.headers.update(
            {
                "Accept": "application/json",
                "x-api-key": REQRES_API_KEY,
            }
        )

    @task
    def list_users(self):
        with self.client.get(
            "/api/users",
            params={"page": 1},
            name="GET /api/users?page=1",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"Unexpected status {response.status_code}")
            elif "data" not in response.json():
                response.failure("Response JSON missing 'data'")
            else:
                response.success()
