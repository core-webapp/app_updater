import os
from src.app_updater import AppUpdater

if __name__ == '__main__':
    if not os.getenv("CORE_BE_TOKEN"):
        print("No se ha configurado el token de acceso a core-be")
    AppUpdater().update_source_code_automaticaly()
