from unittest.mock import (
    MagicMock,
    Mock,
    patch,
)

from github import (
    Auth,
    BadCredentialsException,
)

from src.github_repository import GithubRepository


@patch.object(GithubRepository, '_get_commit_sha_of_release')
@patch.object(GithubRepository, '_get_last_release')
@patch.object(GithubRepository, '_get_github_account')
def test_github_repository_init(
    patched_get_github_account: MagicMock,
    patched_get_last_release: MagicMock,
    patched_get_commit_sha_of_release: MagicMock,
):
    token = "some_token"
    organizacion_name = "some_organization"
    repository_name = "some_repository"

    mock_repo = Mock()
    mock_github_account = Mock()
    mock_github_account.get_repo.return_value = mock_repo
    patched_get_github_account.return_value = mock_github_account

    fake_last_release = "fake_last_release"
    patched_get_last_release.return_value = fake_last_release
    fake_commit_sha = "fake_commit_sha"
    patched_get_commit_sha_of_release.return_value = fake_commit_sha

    expected_version_info = {
        "last_release": fake_last_release,
        "commit_sha": fake_commit_sha,
        "commit_short_sha": fake_commit_sha[:7],
    }

    # test
    github_repository = GithubRepository(token, organizacion_name, repository_name)

    # asserts
    assert github_repository.api_token == token
    assert github_repository.organizacion_name == organizacion_name
    assert github_repository.repository_name == repository_name

    patched_get_github_account.assert_called_once_with(token)
    mock_github_account.get_repo.assert_called_once_with(f'{organizacion_name}/{repository_name}')
    patched_get_last_release.assert_called_once()
    patched_get_commit_sha_of_release.assert_called_once_with(fake_last_release)

    assert github_repository.version_info == expected_version_info


@patch('src.github_repository.Github')
@patch.object(Auth, 'Token')
def test_get_github_account(
    mock_auth_with_token: MagicMock,
    mock_github: MagicMock
):
    # prepare
    token = "some_token"

    mock_auth_instance = Mock()
    mock_auth_with_token.return_value = mock_auth_instance

    mock_github_instance = Mock()
    mock_github.return_value = mock_github_instance

    # test
    result = GithubRepository._get_github_account(token)

    # asserts
    mock_auth_with_token.assert_called_once_with(token)
    mock_github.assert_called_once_with(auth=mock_auth_instance)
    assert result == mock_github_instance


@patch.object(GithubRepository, '_get_github_account')
def test_is_token_valid_with_valid_token(
    patched_get_github_account: MagicMock,
):
    # prepare
    token = "valid_token"
    mock_github_account = Mock()
    patched_get_github_account.return_value = mock_github_account

    mock_user = Mock()
    mock_user.login = "username"
    mock_github_account.get_user.return_value = mock_user

    # test
    result = GithubRepository._is_token_valid(token)

    # asserts
    patched_get_github_account.assert_called_once_with(token)
    assert result is True


@patch.object(GithubRepository, '_get_github_account')
def test_is_token_valid_with_invalid_token(patched_get_github_account):
    # prepare
    token = "invalid_token"
    mock_github_account = Mock()
    patched_get_github_account.return_value = mock_github_account

    mock_github_account.get_user.side_effect = BadCredentialsException('status', 'data', 'header')

    # test
    result = GithubRepository._is_token_valid(token)

    # asserts
    patched_get_github_account.assert_called_once_with(token)
    assert result is False
