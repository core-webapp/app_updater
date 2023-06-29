from unittest import mock
from unittest.mock import MagicMock

import pytest

from src.app_updater import AppUpdater


@pytest.mark.parametrize(
    "user_input, expected", [
        ('1234567890', '1234567890'),
        ('asdfasdkjkñljñljklñkjñadfs', 'asdfasdkjkñljñljklñkjñadfs'),
        ('', ''),
    ]
)
@mock.patch('src.app_updater.pwinput')
def test_get_api_token_from_user(
    pwinput_mock: MagicMock,
    user_input: str,
    expected: str,
):
    pwinput_mock.return_value = user_input
    result = AppUpdater._get_api_token_from_user()
    assert result == expected
