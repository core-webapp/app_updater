from datetime import datetime
from unittest.mock import (
    call,
    mock_open,
    patch,
    MagicMock,
    Mock,
)

import pytest
import yaml

from src.app_updater import AppUpdater
from src.data_protocols import UserMessages
from src.github_repository import GithubRepository


@pytest.fixture
def mock_github_repository() -> GithubRepository:
    with patch.object(GithubRepository, '__init__', return_value=None):
        github_repository = GithubRepository(
            'fake_api_token',
            'fake_organization_name',
            'fake_repository_name',
        )
    return github_repository


@patch.object(GithubRepository, 'change_source_code_version')
@patch.object(GithubRepository, 'get_commit_sha_of_version_tag')
def test_update_to_new_version(
    patched_get_commit_sha_of_version_tag: MagicMock,
    patched_change_source_code_version: MagicMock,
    mock_github_repository: GithubRepository,
):
    # prepare
    fake_version_tag = 'fake_version_tag'
    fake_version_commit = 'fake_version_commit'
    patched_get_commit_sha_of_version_tag.return_value = fake_version_commit

    app_updater = AppUpdater()

    # test
    app_updater._update_to_new_version(mock_github_repository, fake_version_tag)

    # asserts
    mock_github_repository.get_commit_sha_of_version_tag.assert_called_once_with(fake_version_tag)
    mock_github_repository.change_source_code_version.assert_called_once_with(fake_version_commit)
