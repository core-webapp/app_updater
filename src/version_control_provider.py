from abc import abstractmethod
import requests
import os
import yaml
from pathlib import Path
from typing import TypedDict

config_file_path = Path() / ".config.yaml"


class VersionControlConfigs(TypedDict):
    token: str
    version: str
    local_repository_path: str


class VersionControlProvider:
    @abstractmethod
    def get_config(self) -> VersionControlConfigs:
        raise NotImplementedError()


class CoreConfigProvider(VersionControlProvider):
    BASE_URL = os.getenv("CORE_BE_URL")

    def __init__(self, token=None):
        self.token = token if token else os.getenv("CORE_BE_TOKEN")
        super().__init__()

    def get_config(self) -> VersionControlConfigs:
        config = self._get_version_control_info()
        return VersionControlConfigs(
            token=config.get("token"),
            version=config.get("version"),
            local_repository_path=Path(config.get("local_repository_path")),
        )

    def _get_version_control_info(self):
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
            f"There was an error getting the config - {response.status_code} - {response.reason}"
        )


class LocalConfigProvider(VersionControlProvider):
    def __init__(self):
        self.config = self._get_config_file_data()

    def _get_config_file_data(self) -> None:
        with open(config_file_path, "rb") as file:
            raw_yaml_config = file.read()
            config = yaml.safe_load(raw_yaml_config)
        return config

    def get_config(self) -> VersionControlConfigs:
        return VersionControlConfigs(
            token=self._get_api_token(),
            version=self._get_version_tag_to_update(),
            local_repository_path=self._get_local_repository_path(),
        )

    def _get_local_repository_path(self) -> str:
        return Path(self.config.get("local_repository_path"))

    def _get_api_token(self) -> str:
        return self.config.get("token")

    def _get_version_tag_to_update(self) -> str:
        return self.config.get("version")
