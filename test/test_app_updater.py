from unittest.mock import (
    MagicMock,
    Mock,
    patch,
)

import pytest

from src.app_updater import AppUpdater
from src.github_repository import GithubRepository


@pytest.mark.parametrize(
    "user_input, expected", [
        ('1234567890', '1234567890'),
        ('asdfasdkjkñljñljklñkjñadfs', 'asdfasdkjkñljñljklñkjñadfs'),
        ('', ''),
    ]
)
@patch('src.app_updater.pwinput')
def test_get_api_token_from_user(
    pwinput_mock: MagicMock,
    user_input: str,
    expected: str,
):
    pwinput_mock.return_value = user_input
    result = AppUpdater._get_api_token_from_user()
    assert result == expected


@patch.object(AppUpdater, '_get_api_token_from_user')
@patch.object(GithubRepository, '_is_token_valid')
def test_get_api_token_max_retries_exceeded(
    patched_is_token_valid: MagicMock,
    patched_get_api_token_from_user: MagicMock,
):

    token = "some_token"
    patched_get_api_token_from_user.return_value = token
    patched_is_token_valid.side_effect = [False] * AppUpdater.max_input_retries

    with pytest.raises(Exception, match='Max retries exceeded'):
        AppUpdater._get_api_token()


@pytest.mark.parametrize(
    "amount_of_bad_tokens", [0, 1, 2],
)
@patch.object(AppUpdater, '_get_api_token_from_user')
@patch.object(GithubRepository, '_is_token_valid')
def test_get_api_token(
    patched_is_token_valid: MagicMock,
    patched_get_api_token_from_user: MagicMock,
    amount_of_bad_tokens: int,
):
    token = "some_token"
    patched_get_api_token_from_user.return_value = token
    patched_is_token_valid.side_effect = [False] * amount_of_bad_tokens + [True]
    result_token = AppUpdater._get_api_token()
    assert result_token == token


@patch('src.app_updater.GithubRepository')
@patch.object(AppUpdater, '_get_api_token')
def test_get_github_repository(
    patched_get_api_token: MagicMock,
    mock_github_repository: MagicMock,
):
    token = "some_token"
    patched_get_api_token.return_value = token

    github_repository_instanse = Mock()
    mock_github_repository.return_value = github_repository_instanse

    result = AppUpdater._get_github_repository()

    mock_github_repository.assert_called_once_with(token)
    assert result == github_repository_instanse
