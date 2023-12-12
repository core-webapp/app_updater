import os
import requests


class CoreService:
    BASE_URL = os.getenv("CORE_BE_URL")

    def __init__(self, token=None):
        self.token = token if token else os.getenv("CORE_BE_TOKEN")

    def get_version_control_info(self):
        url = f"{self.BASE_URL}api/company/version-control/me/"
        try:
            response = requests.get(
                url, headers={"Authorization": f"Token {self.token}"}
            )
        except Exception as e:
            raise Exception(f"There was an error calling to core-be - {e}")

        if response.status_code == 200:
            return response.json()
        raise Exception(
            f"There was an error getting the config - {response.status_code} - {response.reason()}"
        )
