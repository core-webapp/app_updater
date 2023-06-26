from pwinput import pwinput


class AppUpdater:

    def _get_api_token_from_user(self):
        return pwinput('Enter your API TOKEN: ')
