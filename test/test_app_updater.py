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


@pytest.mark.parametrize(
    "current_version, remote_version, expected", [
        ('1.0.0', '1.0.0', False),
        ('1.0.0', '1.0.1', True),
        ('1.0.1', '1.0.0', False),
        ('v1.0.0', 'v1.0.0', False),
        ('v1.0.0', 'v1.0.1', True),
        ('v1.0.1', 'v1.0.0', False),
    ]
)
@patch.object(AppUpdater, '_get_current_local_version')
def test_there_is_a_newer_version(
    patched_get_current_local_version: MagicMock,
    current_version: str,
    remote_version: str,
    expected: bool,
):
    # prepare
    patched_get_current_local_version.return_value = current_version
    mock_github_repository = Mock()
    mock_github_repository.release = remote_version

    app_updater = AppUpdater()

    # test
    result = app_updater._there_is_a_newer_version(mock_github_repository)

    # asserts
    patched_get_current_local_version.assert_called_once()
    assert result == expected


@patch.object(AppUpdater, '_get_version_info_from_file')
def test_get_current_local_version(patch_get_version_info_from_file: MagicMock):
    expected_last_release = 'fake_last_release'

    mock_current_local_version = {
        "release_version": expected_last_release,
        "commit_sha": 'fake_commit_sha',
        "commit_short_sha": 'commit_short_sha',
    }
    patch_get_version_info_from_file.return_value = mock_current_local_version
    app_updater = AppUpdater()

    # test
    result = app_updater._get_current_local_version()
    patch_get_version_info_from_file.assert_called_once_with('.version.yaml')
    assert result == expected_last_release


def test_get_version_info_from_file_valid_file():

    mock_filepath = 'path/to/file.yaml'
    mock_yaml_file = '''
    release: 1.0.0
    commit_sha: 1q2w3e4r5t6y7u8i9o0p
    commit_short_sha: 1q2w3e4
    last_update: 2020-01-01T00:00:00Z
    '''

    with patch("builtins.open", mock_open(read_data=mock_yaml_file)) as mock_file:
        with patch("os.path.isfile", return_value=True) as mock_os_path_isfile:
            version_info = AppUpdater._get_version_info_from_file(mock_filepath)

    mock_os_path_isfile.assert_called_once_with(mock_filepath)
    mock_file.assert_called_once_with(mock_filepath, 'r')
    assert version_info == {
        'release': '1.0.0',
        'commit_sha': '1q2w3e4r5t6y7u8i9o0p',
        'commit_short_sha': '1q2w3e4',
        'last_update': datetime.fromisoformat('2020-01-01T00:00:00Z'),
    }


def test_get_version_info_from_file_invalid_file():
    mock_filepath = "path/to/invalid/file.yaml"

    with patch("os.path.isfile", return_value=False):
        with pytest.raises(Exception) as e_info:
            AppUpdater._get_version_info_from_file(mock_filepath)

    assert str(e_info.value) == "El archivo no existe"


def test_get_version_info_from_file_invalid_yaml():
    mock_yaml_content = """
    release 1.0.0
    commit_sha: 1q2w3e4r5t6y7u8i9o0p
    commit_short_sha: 1q2w3e4
    last_update: 2020-01-01T00:00:00Z
    """  # The YAML is invalid because first row doesn't have the ':' after 'release'
    mock_filepath = "path/to/file.yaml"

    with patch("builtins.open", mock_open(read_data=mock_yaml_content)) as mock_file:
        with patch("os.path.isfile", return_value=True):
            with pytest.raises(yaml.YAMLError):
                AppUpdater._get_version_info_from_file(mock_filepath)

    mock_file.assert_called_once_with(mock_filepath, 'r')


@patch.object(AppUpdater, '_update_to_new_version')
@patch.object(AppUpdater, '_operator_wants')
def test_update_to_new_version_if_operator_wants_when_answesr_is_yes(
    patched_operator_wants: MagicMock,
    patched_update_to_new_version: MagicMock,
):
    # prepare
    patched_operator_wants.return_value = True
    fake_current_release_version = 'fake_current_release_version'
    fake_remote_release_version = 'fake_remote_release_version'
    mock_github_repository = Mock()
    fake_user_message = UserMessages(
        prints=[
            f"La version actual es: {fake_current_release_version}",
            f"Hay una nueva version disponible: {fake_remote_release_version}",
        ],
        input="Desea actualizar la app? [Y/n]",
    )

    app_updater = AppUpdater()
    app_updater.current_release_version = fake_current_release_version
    app_updater.remote_release_version = fake_remote_release_version

    # test
    app_updater._update_to_new_version_if_operator_wants(mock_github_repository)

    # asserts
    patched_operator_wants.assert_called_once_with(fake_user_message)
    patched_update_to_new_version.assert_called_once_with(mock_github_repository)


@patch.object(AppUpdater, '_update_to_new_version')
@patch.object(AppUpdater, '_operator_wants')
def test_update_to_new_version_if_operator_wants_when_answers_no_or_anything_different_from_yes(
    patched_operator_wants: MagicMock,
    patched_update_to_new_version: MagicMock,
):
    # prepare
    patched_operator_wants.return_value = False
    fake_current_release_version = 'fake_current_release_version'
    fake_remote_release_version = 'fake_remote_release_version'
    mock_github_repository = Mock()
    fake_user_message = UserMessages(
        prints=[
            f"La version actual es: {fake_current_release_version}",
            f"Hay una nueva version disponible: {fake_remote_release_version}",
        ],
        input="Desea actualizar la app? [Y/n]",
    )

    app_updater = AppUpdater()
    app_updater.current_release_version = fake_current_release_version
    app_updater.remote_release_version = fake_remote_release_version

    # test
    app_updater._update_to_new_version_if_operator_wants(mock_github_repository)

    # asserts
    patched_operator_wants.assert_called_once_with(fake_user_message)
    patched_update_to_new_version.assert_not_called()


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
