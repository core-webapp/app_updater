from github import (
    Auth,
    BadCredentialsException,
    Github,
)


class GithubRepository:

    @classmethod
    def _is_token_valid(cls, token: str) -> bool:
        try:
            github = cls._get_github_account(token)
            github.get_user().login
            return True
        except BadCredentialsException:
            return False

    @staticmethod
    def _get_github_account(token: str) -> Github:
        auth = Auth.Token(token)
        return Github(auth=auth)