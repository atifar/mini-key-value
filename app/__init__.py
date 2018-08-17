import os

from flask import Flask, jsonify, request
from pymongo import MongoClient

from config import Config


def create_app(config_class=Config):
    # create and configure the application
    app = Flask(__name__)
    app.config.from_object(config_class)

    # connect to the database server
    client = MongoClient(
        host=app.config['MONGO_HOST'],
        port=app.config['MONGO_PORT']
    )

    # create the database
    db = client[app.config['MONGO_DBNAME']]

    # sanity check
    @app.route('/sanity')
    def sanity_check():
        return 'Sanity check passed.'

    @app.route('/', methods=['GET'])
    def home():
        data = {'keys_url': request.url_root + 'keys'}
        resp = jsonify(data)
        resp.status_code = 200
        return resp

    return app
