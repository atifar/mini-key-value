import os
import pytest
from app import create_app, mongo
from config import Config


class TestConfig(Config):
    TESTING = True
    MONGO_DBNAME = 'test_' + Config.MONGO_DBNAME
    MONGO_HOST = os.environ.get('MONGO_HOST', 'mongodb://localhost')
    MONGO_URI = f'{MONGO_HOST}:27017/{MONGO_DBNAME}'


@pytest.fixture
def app():
    app = create_app(TestConfig)
    app_context = app.app_context()
    app_context.push()
    yield app
    app_context.pop()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def keys():
    # access (and create, if necessary) the "keys" collection
    yield mongo.db.keys
    # drop "keys" collection to clean up after each test
    mongo.db.keys.drop()


@pytest.fixture
def add_to_keys(keys):

    def _add_to_keys(new_doc):
        keys.insert_one(new_doc)

    return _add_to_keys
