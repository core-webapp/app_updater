import os
import requests


class CoreService:
    BASE_URL = "https://core-be-production.up.railway.app/"

    def __init__(self, token=None):
        self.token = token if token else os.getenv("CORE_BE_TOKEN")

    def get_version_control_info(self):
        url = f"{self.BASE_URL}api/company/version-control/me/"
        response = requests.get(url, headers={"Authorization": f"Token {self.token}"})
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                f"ERROR AL OBTENER CONFIGURACION - {response.status_code} - {response.reason()}"
            )
