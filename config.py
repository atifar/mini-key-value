import os


class Config(object):
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'sekrit-o-flask')
    MONGO_DBNAME = os.environ.get('MONGO_DBNAME', 'kv_db')
    MONGO_HOST = os.environ.get('MONGO_HOST', 'mongodb://localhost')
    MONGO_PORT = int(os.environ.get('MONGO_PORT', 27017))
