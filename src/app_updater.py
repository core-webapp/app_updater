import os
import yaml

from packaging import version
from pwinput import pwinput

from src.data_protocols import UserMessages

from .github_repository import GithubRepository


class AppUpdater:
    max_input_retries = 3
    organization_name = "core-webapp"
    repository_name = "app_updater"
    user_input_true = 'y'

    def install_source_code(self):

        # TODO: get token from user and if it is valid continue

        # TODO: clone the repository in the directory where is present the app_updater

        # TODO: install the dependencies

        # TODO: create the database

        # TODO: create the license asking the operator the expiration date

        # TODO: install environment setup asking operator each value offering a default value

        # TODO: write the .version.yaml file with the current release version and commit shas

        # TODO: send mail with a resume of the new changes
        pass

    def update_source_code(self):

        token = self._get_api_token()
        github_repository = GithubRepository(token)

        if self._there_is_a_newer_version(github_repository):
            self._update_to_new_version_if_operator_wants(github_repository)

        # TODO: ask the operator if wants to update the database

        # TODO: ask the operator if wants to update the license

        # TODO: if operator wants to update the license, ask him the new expiration date

        # TODO : show operator the current environment setup and ask him if wants to update it

        # TODO : if operator wants to update it, ask him each value offering a the current one as default value

        # TODO: send mail with a resume of the new changes

        pass

    @classmethod
    def _get_api_token_from_user(cls):
        return pwinput('Enter your API TOKEN: ')

    @classmethod
    def _get_api_token(cls):
        for _ in range(cls.max_input_retries):
            api_token = cls._get_api_token_from_user()
            if GithubRepository._is_token_valid(api_token):
                return api_token
        raise Exception('Max retries exceeded')

    def _there_is_a_newer_version(self, github_repository: GithubRepository) -> bool:
        # FIXME : it's not a good idea to set values ina method that does another thing
        # but for now is the easy and fast way to do it, I will refactor later
        self.current_release_version = version.parse(self._get_current_local_version())
        self.remote_release_version = version.parse(github_repository.release)

        return self.current_release_version < self.remote_release_version

    def _get_current_local_version(self) -> str:
        current_local_version = self._get_version_info_from_file('.version.yaml')
        release_version = current_local_version.get('release_version')
        return release_version

    @staticmethod
    def _get_version_info_from_file(filepath: str) -> dict:

        if not os.path.isfile(filepath):
            raise Exception("El archivo no existe")

        with open(filepath, 'r') as file:
            data = yaml.safe_load(file)
        return data

    def _update_to_new_version_if_operator_wants(self, github_repository: GithubRepository) -> None:
        # TODO: refactor when the CLI class is created
        user_messages = UserMessages(
            prints=[
                f"La version actual es: {self.current_release_version}",
                f"Hay una nueva version disponible: {self.remote_release_version}",
            ],
            input="Desea actualizar la app? [Y/n]",
        )
        if self._operator_wants(user_messages):
            self._update_to_new_version(github_repository)

    def _operator_wants(self, user_messages: UserMessages) -> bool:
        # FIXME: this method must go in another class with the responsabilty
        # to comunicate with the operator, a CLI class, when that class is created migrated this to there
        for print_message in user_messages.prints:
            print(print_message)

        answer = input(user_messages.input).lower()
        return answer == self.user_input_true

    def _update_to_new_version(self, github_repository: GithubRepository):
        commit_of_last_release = github_repository.commit_of_last_release
        github_repository.change_source_code_version(commit_of_last_release)
