import os

from flask import Flask

from config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # sanity check
    @app.route('/sanity')
    def sanity_check():
        return 'Sanity check passed.'

    return app
