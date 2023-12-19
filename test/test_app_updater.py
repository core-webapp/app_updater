from unittest.mock import (
    patch,
    MagicMock,
)

import pytest

from src.app_updater import AppUpdater
from src.github_repository import GithubRepository
from src.version_control_provider import VersionControlConfigs, VersionControlProvider


@pytest.fixture
def mock_github_repository() -> GithubRepository:
    with patch.object(GithubRepository, '__init__', return_value=None):
        github_repository = GithubRepository(
            'fake_api_token',
            'fake_organization_name',
            'fake_repository_name',
        )
    return github_repository


@pytest.fixture
def mock_version_control_provider() -> VersionControlProvider:
    class FakeVersionControlProvider(VersionControlProvider):
        def get_config(self) -> VersionControlConfigs:
            return {
                'token': 'fake_token',
                'version': 'fake_version',
                'local_repository_path': 'fake_local_repository_path',
            }
    yield FakeVersionControlProvider


@patch.object(GithubRepository, 'change_source_code_version')
@patch.object(GithubRepository, 'get_commit_sha_of_version_tag')
def test_update_to_new_version(
    patched_get_commit_sha_of_version_tag: MagicMock,
    patched_change_source_code_version: MagicMock,
    mock_github_repository: GithubRepository,
    mock_version_control_provider: VersionControlProvider,
):
    # prepare
    fake_version_tag = 'fake_version_tag'
    fake_version_commit = 'fake_version_commit'
    patched_get_commit_sha_of_version_tag.return_value = fake_version_commit

    # test
    AppUpdater(
        version_control_provider=mock_version_control_provider
    )._update_to_new_version(
            mock_github_repository,
            fake_version_tag,
        )

    # asserts
    mock_github_repository.get_commit_sha_of_version_tag.assert_called_once_with(fake_version_tag)
    mock_github_repository.change_source_code_version.assert_called_once_with(fake_version_commit)
