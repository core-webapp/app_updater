from pwinput import pwinput

from .github_repository import GithubRepository


class AppUpdater:
    max_input_retries = 3
    organization_name = "core-webapp"
    repository_name = "app_updater"

    def install_source_code(self):

        # TODO: get token from user and if it is valid continue

        # TODO: clone the repository in the directory where is present the app_updater

        # TODO: install the dependencies

        # TODO: create the database

        # TODO: create the license asking the operator the expiration date

        # TODO: install environment setup asking operator each value offering a default value

        # TODO: send mail with a resume of the new changes
        pass

    def update_source_code(self):

        token = self._get_api_token()
        github_repository = GithubRepository(token)

        # TODO: compare local version with remote version and return the newer one

        # TODO: if local version is older than remote version ask th operator if wants to update to new

        # TODO: if operator wants to update, make a git pull

        # TODO: if operator doesn't want to update continue con update process

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

