from pwinput import pwinput


class AppUpdater:

    @classmethod
    def _get_api_token_from_user(cls):
        return pwinput('Enter your API TOKEN: ')
