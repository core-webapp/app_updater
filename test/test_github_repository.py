from unittest.mock import (
    MagicMock,
    Mock,
    patch,
)

from git import Repo
from github import (
    Auth,
    BadCredentialsException,
)

from src.github_repository import GithubRepository


def get_github_repository_mock(
    token="some_token",
    organizacion_name="some_organization",
    repository_name="some_repository",
):

    with patch.object(GithubRepository, '_get_github_account'):
        with patch.object(GithubRepository, '_get_last_release'):
            with patch.object(GithubRepository, '_get_commit_sha_of_release', return_value="fake_commit_sha"):

                github_repository = GithubRepository(
                    api_token=token,
                    organizacion_name=organizacion_name,
                    repository_name=repository_name,
                )
    return github_repository


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


@patch.object(GithubRepository, '_get_commit_sha_of_release')
@patch.object(GithubRepository, '_get_last_release')
@patch.object(GithubRepository, '_get_github_account')
def test_last_release_property(
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

    github_repository = GithubRepository(token, organizacion_name, repository_name)

    # test
    last_release = github_repository.last_release

    # asserts
    assert last_release == fake_last_release


@patch.object(GithubRepository, '_get_commit_sha_of_release')
@patch.object(GithubRepository, '_get_last_release')
@patch.object(GithubRepository, '_get_github_account')
def test_commit_of_last_release_property(
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
    expected_commit_of_last_release = "fake_commit_sha"
    patched_get_commit_sha_of_release.return_value = expected_commit_of_last_release

    github_repository = GithubRepository(token, organizacion_name, repository_name)

    # test
    commit_of_last_release = github_repository.commit_of_last_release

    # asserts
    assert commit_of_last_release == expected_commit_of_last_release


def test_get_last_release():

    # prepare
    expected_last_release = "expected_last_release"

    mock_latest_release = Mock()
    mock_latest_release.tag_name = expected_last_release

    mock_repository = Mock()
    mock_repository.get_latest_release.return_value = mock_latest_release

    mock_github_repository = get_github_repository_mock()
    mock_github_repository.repository = mock_repository

    # test
    last_release = mock_github_repository._get_last_release()

    # asserts
    mock_repository.get_latest_release.assert_called_once()
    assert last_release == expected_last_release


def test_get_commit_sha_of_release():

    # prepare
    expected_commit_sha = "expected_commit_sha"

    mock_release = Mock()
    mock_release.tag_name = "some_tag_name"

    mock_release_commit = Mock()
    mock_release_commit.object.sha = expected_commit_sha

    mock_repository = Mock()
    mock_repository.get_git_ref.return_value = mock_release_commit

    mock_github_repository = get_github_repository_mock()
    mock_github_repository.repository = mock_repository

    # test
    last_release = mock_github_repository._get_commit_sha_of_release(mock_release)

    # asserts
    mock_repository.get_git_ref.assert_called_once_with(f"tags/{mock_release.tag_name}")
    assert last_release == expected_commit_sha


@patch.object(GithubRepository, '_fetch_and_checkout')
def test_change_source_code_version(patched_fetch_and_checkout: MagicMock):
    # prepare
    mock_github_repository = get_github_repository_mock()
    fake_commit = "fake_commit"

    # test
    mock_github_repository.change_source_code_version(fake_commit)

    # asserts
    patched_fetch_and_checkout.assert_called_once_with(fake_commit)


@patch('src.github_repository.Repo')
def test_fetch_and_checkout(patched_repo: MagicMock):
    # prepare
    mock_repository = Mock()
    patched_repo.return_value = mock_repository

    mock_github_repository = get_github_repository_mock()
    fake_commit = "fake_commit"

    # test
    mock_github_repository._fetch_and_checkout(fake_commit)

    # asserts
    patched_repo.assert_called_once_with(mock_github_repository.source_code_path)
    mock_repository.remote.assert_called_once()
    mock_repository.remote().fetch.assert_called_once()
    mock_repository.git.checkout.assert_called_once_with(fake_commit)

