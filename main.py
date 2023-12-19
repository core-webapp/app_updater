from src.app_updater import AppUpdater
from src.version_control_provider import CoreConfigProvider

if __name__ == "__main__":
    AppUpdater(version_control_provider=CoreConfigProvider).update_source_code_automaticaly()
