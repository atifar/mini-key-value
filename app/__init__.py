import json

from flask import Flask, jsonify, request, Response
from flask_pymongo import PyMongo

from config import Config


mongo = PyMongo()


def create_app(config_class=Config):
    # create and configure the application
    app = Flask(__name__)
    app.config.from_object(config_class)

    # connect to the database server
    mongo.init_app(app)

    def build_response(resp, status_code):
        """
        Helper function to build JSON responses (success and error).
        """
        return Response(
            mimetype="application/json",
            response=json.dumps(resp),
            status=status_code
        )

    def validate_key_data(raw_data, keys):
        """
        Validate raw POST data for 'create_key' endpoint. Return a
        <clean_data (dict), is_valid (bool), error_msg (str)> 3-tuple.
        """
        clean_data, is_valid, error_msg = ({}, False, '')
        if 'key' not in raw_data:
            error_msg = {
                'error': 'Please provide the missing "key" parameter!'
            }
        elif 'value' not in raw_data:
            error_msg = {
                'error': 'Please provide the missing "value" parameter!'
            }
        elif keys.find({'key': raw_data['key']}).count():
            error_msg = {
                'error': f"Can't create duplicate key ({raw_data['key']})."
            }
        else:
            is_valid = True
            clean_data = {
                'key': raw_data['key'],
                'value': raw_data['value']
            }
        return clean_data, is_valid, error_msg

    def validate_value_data(raw_data):
        """
        Validate raw PUT data for 'update_key' endpoint. Return a
        <clean_value (str or [...]), is_valid (bool), error_msg (str)>
        3-tuple.
        """
        clean_value, is_valid, error_msg = ('', False, '')
        if 'value' not in raw_data:
            error_msg = {
                'error': 'Please provide the missing "value" parameter!'
            }
        elif not any([isinstance(raw_data['value'], t) for t in (str, list)]):
            error_msg = {
                'error': 'The "value" parameter must be a string or a list '
                'of simple types.'
            }
        else:
            is_valid = True
            clean_value = raw_data['value']
        return clean_value, is_valid, error_msg

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
        return build_response(data, 200)

    @app.route('/keys', methods=['POST'])
    def create_key():
        keys = mongo.db.keys
        clean_data, is_valid, error_msg = validate_key_data(
            request.get_json(), keys)
        if is_valid:
            keys.insert_one(clean_data)
            data = {
                'key': clean_data['key'],
                'value': clean_data['value'],
                'http_url': request.url_root + 'keys/' + clean_data['key']
            }
            return build_response(data, 201)
        return build_response(error_msg, 400)

    @app.route('/keys/<key>', methods=['PUT'])
    def update_key(key):
        keys = mongo.db.keys
        clean_value, is_valid, error_msg = validate_value_data(
            request.get_json())
        if is_valid:
            result = keys.update_one(
                {'key': key},
                {'$set': {'key': key, 'value': clean_value}}
            )
            if result.modified_count:  # successful update
                return build_response(None, 204)
            else:  # unsuccessful update
                error_msg = {'error': 'Update failed.'}
                return build_response(error_msg, 400)
        else:
            return build_response(error_msg, 400)

    @app.route('/keys/<key>', methods=['DELETE'])
    def delete_key(key):
        keys = mongo.db.keys
        keys.find_one_or_404({'key': key})
        return build_response('', 204)

    return app
