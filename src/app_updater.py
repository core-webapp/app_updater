from pathlib import Path
import subprocess
import traceback
from src.version_control_provider import LocalConfigProvider, VersionControlProvider

from src.email_sender import EmailSender
from .github_repository import GithubRepository


class AppUpdater:
    max_input_retries = 3
    organization_name = "core-webapp"
    repository_name = "core_legacy"
    user_input_true = "y"
    license_path = Path() / repository_name / "state" / "utils" / "license.yaml"
    requirements_path = Path() / repository_name / "requirements.txt"

    # TODO where should we add the developers? harcoded here or in a config file?
    developers: tuple[str]

    # TODO where should we mail credentials? harcoded here or in a config file?
    user_mail: str
    password_mail: str

    changes_made = []

    def __init__(
        self, version_control_provider: VersionControlProvider = LocalConfigProvider
    ) -> None:
        self.version_control_provider = version_control_provider()

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

    def update_source_code_automaticaly(self) -> None:
        version_control_data = self.version_control_provider.get_config()
        github_repository = GithubRepository(
            version_control_data["token"],
            self.organization_name,
            version_control_data["local_repository_path"],
            self.repository_name,
        )

        self._update_to_new_version(github_repository, version_control_data["version"])

        # self._install_dependencies_from_requirements()

        # self._run_database_migration()
        # self._send_email_with_resume_of_changes()

    def _update_to_new_version(
        self, github_repository: GithubRepository, version_tag: str = "qa"
    ) -> None:
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

    def _send_email_with_resume_of_changes(self):
        changes_made = self.changes_made

        email_sender = EmailSender()

        for user_target in self.developers:
            email_sender.send_email(user_target, "actualizacion Core", changes_made)
