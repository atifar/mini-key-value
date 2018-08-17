import os

import pytest
from app import create_app
from config import Config


class TestConfig(Config):
    TESTING = True
    MONGO_DBNAME = 'test_' + Config.MONGO_DBNAME


@pytest.fixture
def app():
    app = create_app(TestConfig)

    yield app

@pytest.fixture
def client(app):
    return app.test_client()
