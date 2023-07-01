from pwinput import pwinput

from .github_repository import GithubRepository


class AppUpdater:
    max_input_retries = 3

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

    @classmethod
    def _get_github_repository(cls):
        api_token = cls._get_api_token()
        return GithubRepository(api_token)
