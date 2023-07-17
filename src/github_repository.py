from pathlib import Path

from github import (
    Auth,
    BadCredentialsException,
    Github,
    GitRelease,
)
from git import Repo


class GithubRepository:

    def __init__(self, api_token: str, organizacion_name: str, repository_name: str) -> None:

        self.api_token = api_token
        self.organizacion_name = organizacion_name
        self.repository_name = repository_name

        self.source_code_path = Path.cwd() / repository_name

        self.github_account = self._get_github_account(self.api_token)
        self.repository = self.github_account.get_repo(f'{self.organizacion_name}/{self.repository_name}')

        last_release = self._get_last_release()
        commit_sha = self._get_commit_sha_of_release(last_release)
        commit_short_sha = commit_sha[:7]

        self.version_info = {
            "last_release": last_release,
            "commit_sha": commit_sha,
            "commit_short_sha": commit_short_sha,
        }

    @property
    def last_release(self) -> str:
        return self.version_info.get('last_release')

    @property
    def commit_of_last_release(self) -> str:
        return self.version_info.get('commit_sha')

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

    def _get_last_release(self) -> str:
        latest_release = self.repository.get_latest_release()
        return latest_release.tag_name

    def _get_commit_sha_of_release(self, release: GitRelease.GitRelease) -> str:
        release_commit = self.repository.get_git_ref(f"tags/{release.tag_name}")
        return release_commit.object.sha

    def _clone_repository(self, repository_url: str, path_to_clone_the_app: str):
        repo_url_with_token = repository_url.replace('https://', f'https://{self.api_token}@')
        Repo.clone_from(repo_url_with_token, path_to_clone_the_app)

    def change_source_code_version(self, commit: str) -> None:
        self._fetch_and_checkout(commit)

    def _fetch_and_checkout(self, commit: str) -> None:
        # TODO: check if local_repository_path exists ?? or maybe this ewhen the process willbe automatic
        local_repository = Repo(self.source_code_path)
        local_repository.remote().fetch()
        local_repository.git.checkout(commit)
