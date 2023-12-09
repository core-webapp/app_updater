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


@pytest.mark.parametrize(
    'user_input, expected_result', [
        ('y', True),
        ('Y', True),
        ('yes', False),
        ('YES', False),
        ('n', False),
        ('N', False),
    ]
)
@patch('builtins.print')
@patch('builtins.input')
def test_operator_wants(
    patched_input: MagicMock,
    patched_print: MagicMock,
    user_input: str,
    expected_result: bool,
):
    # prepare
    fake_user_messages = UserMessages(
        prints=[
            "print1",
            "print2",
        ],
        input="input",
    )
    fake_answer = user_input
    patched_input.return_value = fake_answer

    app_updater = AppUpdater()

    # test

    result = app_updater._operator_wants(fake_user_messages)

    # asserts
    patched_print.assert_has_calls(map(call, fake_user_messages.prints))
    patched_input.assert_called_once_with(fake_user_messages.input)
    assert result == expected_result


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
