from flask import Flask, jsonify, request
from flask_pymongo import PyMongo

from config import Config


mongo = PyMongo()


def create_app(config_class=Config):
    # create and configure the application
    app = Flask(__name__)
    app.config.from_object(config_class)

    # connect to the database server
    mongo.init_app(app)

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

    @app.route('/keys', methods=['GET'])
    def list_keys():
        keys = mongo.db.keys
        data = [
            {
                'key': k['key'],
                'http_url': request.url_root + 'keys/' + k['key']
            } for k in keys.find()
        ]
        resp = jsonify(data)
        resp.status_code = 200
        return resp

    @app.route('/keys/<key>', methods=['GET'])
    def get_key(key):
        keys = mongo.db.keys
        doc = keys.find_one_or_404({'key': key})
        data = {
            'key': doc['key'],
            'value': doc['value'],
            'http_url': request.url_root + 'keys/' + doc['key']
        }
        resp = jsonify(data)
        resp.status_code = 200
        return resp

    return app
