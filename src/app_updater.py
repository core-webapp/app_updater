from pathlib import Path
import base64
import os
import subprocess
import traceback
import yaml

from packaging import version
from pwinput import pwinput

from src.data_protocols import UserMessages
from src.email_sender import EmailSender
from .github_repository import GithubRepository


class AppUpdater:
    max_input_retries = 3
    organization_name = "core-webapp"
    repository_name = "core_legacy"
    user_input_true = 'y'
    license_path = Path() / repository_name / 'state' / 'utils' / 'license.yaml'
    requirements_path = Path() / repository_name / 'requirements.txt'
    config_file_path = Path() / '.config.yaml'

    # TODO where should we add the developers? harcoded here or in a config file?
    developers: tuple[str]

    # TODO where should we mail credentials? harcoded here or in a config file?
    user_mail: str
    password_mail: str

    changes_made = []

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

    def update_source_code_automaticaly(self):

        token = self._get_api_token()
        github_repository = GithubRepository(
            token,
            self.organization_name,
            self.repository_name,
        )

        version_tag = self._get_version_tag_to_update()
        self._update_to_new_version(github_repository, version_tag)

        # self._install_dependencies_from_requirements()

        # self._run_database_migration()
        # self._send_email_with_resume_of_changes()

    @classmethod
    def _get_api_token(cls) -> str:
        return cls._get_api_token_automaticaly()

    @classmethod
    def _get_api_token_automaticaly(cls) -> str:
        with open(cls.config_file_path, 'rb') as file:
            raw_yaml_config = file.read()
            config = yaml.safe_load(raw_yaml_config)
            token = config.get('token')
        return token

    @classmethod
    def _get_version_tag_to_update(cls) -> str:
        with open(cls.config_file_path, 'rb') as file:
            raw_yaml_config = file.read()
            config = yaml.safe_load(raw_yaml_config)
            token = config.get('version')
        return token

    def _operator_wants(self, user_messages: UserMessages) -> bool:
        # FIXME: this method must go in another class with the responsabilty
        # to comunicate with the operator, a CLI class, when that class is created migrated this to there
        for print_message in user_messages.prints:
            print(print_message)

        answer = input(user_messages.input).lower()
        return answer == self.user_input_true

    def _update_to_new_version(self, github_repository: GithubRepository, version_tag: str = 'qa') -> None:
        version_commit = github_repository.get_commit_sha_of_version_tag(version_tag)
        github_repository.change_source_code_version(version_commit)
        self._log_change(
            f"Se actualizo a la version {version_tag} - commit {version_commit}\n\n"
        )

    def _log_change(self, change: str) -> None:
        self.changes_made.append(change)

    def _install_dependencies_from_requirements(self) -> None:
        try:
            subprocess.check_call(["pip", "install", "-r", self.requirements_path])
            print("Dependencias instaladas con éxito.")
        except subprocess.CalledProcessError:
            print("Hubo un error al instalar las dependencias.")
            traceback.print_exc()
        except Exception as e:
            print(f"Ocurrió un error inesperado: {e}")
            traceback.print_exc()

    def update_the_license_if_operator_wants(self):
        user_messages = UserMessages(
            prints=[],
            input="Desea actualizar la app? [Y/n]",
        )
        if self._operator_wants(user_messages):
            self._update_the_license()

    def _update_the_license(self) -> None:

        license = self._get_the_license_decoded()
        license = self._update_expitation_date_if_operator_wants(license)
        license = self._update_the_maximum_number_of_processes_if_operator_wants(license)
        self._save_the_license_encoded(license)
        self._log_change("Se actualizo la licencia:\n\n")
        self._log_change(license)

    def _get_the_license_decoded(self) -> str:
        encodede_license = self._get_license_from_file()
        decoded_license = self._decode_license(encodede_license)
        return decoded_license

    def _get_license_from_file(self) -> str:
        with open(self.license_path, 'rb') as file:
            encodede_license = file.read()
        return encodede_license

    def _decode_license(self, encodede_license: str) -> str:
        decoded_license = base64.b64decode(encodede_license)
        raw_yaml_license = decoded_license.decode('utf-8')
        license = yaml.safe_load(raw_yaml_license)
        return license

    def _update_expitation_date_if_operator_wants(self, license: str) -> dict:
        # TODO: refactor when the CLI class is created
        expiration_date = self._get_expiration_date_from_license(license)
        user_messages = UserMessages(
            prints=[
                f"La fecha de expiracion actual es: {expiration_date}",
            ],
            input="Desea actualizar la app? [Y/n]",
        )
        if self._operator_wants(user_messages):
            self._update_expiration_date_asking_the_value_to_the_operator(license)

        return license

    def _get_expiration_date_from_license(self, license: str) -> str:
        return license.get('license').get('expiration_date')

    def _update_expiration_date_asking_the_value_to_the_operator(self, license: str) -> dict:
        license['license']['expiration_date'] = self._get_new_expiration_date_from_operator()
        return license

    def _get_new_expiration_date_from_operator(self) -> str:
        new_expiration_date = input("Ingrese la nueva fecha de expiracion: ")
        return new_expiration_date

    def _update_the_maximum_number_of_processes_if_operator_wants(self, license: str) -> dict:
        maximum_number_of_processes = self._get_maximum_number_of_processes(license)
        user_messages = UserMessages(
            prints=[
                f"El maximo numero de procesos actual es: {maximum_number_of_processes}",
            ],
            input="Desea actualizar la app? [Y/n]",
        )
        if self._operator_wants(user_messages):
            license = self._update_maximum_number_of_processes_asking_the_value_to_the_operator(license)
        return license

    def _get_maximum_number_of_processes(self, license: str) -> str:
        return license.get('environment').get('license').get('maximum_number_of_processes')

    def _update_maximum_number_of_processes_asking_the_value_to_the_operator(self, license: str) -> dict:
        new_maximum_number_of_processes = self._get_new_maximum_number_of_processes_from_operator()
        license['license']['maximum_number_of_processes'] = new_maximum_number_of_processes
        return license

    def _get_new_maximum_number_of_processes_from_operator(self) -> str:
        new_maximum_number_of_processes = input("Ingrese la nueva fecha de expiracion: ")
        return new_maximum_number_of_processes

    def _save_the_license_encoded(self, license: dict) -> None:
        encoded_license = self._encode_license(license)
        with open(self.license_path, 'wb') as file:
            file.write(encoded_license)

    def _encode_license(self, license: dict) -> str:
        raw_yaml_license = yaml.dump(license)
        encoded_license = base64.b64encode(raw_yaml_license.encode('utf-8'))
        return encoded_license

    def _send_email_with_resume_of_changes(self):

        changes_made = self.changes_made

        email_sender = EmailSender()

        for user_target in self.developers:
            email_sender.send_email(user_target, 'actualizacion Core', changes_made)
