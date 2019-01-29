#!.env/bin/python
# -*- code: utf-8 -*-
# prospector/__main__.py

import aumbry
from docopt import docopt
from gunicorn.app.base import BaseApplication
from gunicorn.workers.sync import SyncWorker
from prospector.app import ProspectorService
from prospector.config import AppConfig


class CustomWorker(SyncWorker):
    """
    Gunicorn Workers
    :return worker
    """

    def handle_quit(self, sig, frame):
        self.app.application.stop(sig)
        super(CustomWorker, self).handle_quit(sig, frame)

    def run(self):
        self.app.application.start()
        super(CustomWorker, self).run()


class GunicornApp(BaseApplication):
    """
    Load Gunicorn settings from an external resource
    """

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super(GunicornApp, self).__init__()

    def load_config(self):
        for key, value in self.options.items():
            self.cfg.set(key.lower(), value)

        self.cfg.set('worker_class', 'prospector.__main__.CustomWorker')

    def load(self):
        return self.application


def main():
    docopt(__doc__)

    cfg = aumbry.load(
        aumbry.FILE,
        AppConfig,
        {
            'CONFIG_FILE_PATH': 'config/config.yaml'
        }
    )

    api_app = ProspectorService(cfg)
    gunicorn_app = GunicornApp(api_app, cfg.gunicorn)
    gunicorn_app.run()
