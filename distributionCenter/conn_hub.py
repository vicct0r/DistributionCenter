import time
import requests
from django.conf import settings

def register_service(retries=5, delay=2):
    for attempt in range(retries):
        try:
            requests.post(
                f"{settings.HUB_URL}/cd/",
                json={"ip": settings.MY_IP},
                timeout=2
            )
            return
        except requests.exceptions.ConnectionError:
            if attempt == retries - 1:
                raise
            time.sleep(delay)
