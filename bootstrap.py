from src.config._container import Application
from preprocessing.typesense_indexing import typesense_indexing


def bootstrap(app: Application):
    env = app.environment()
    typesense_indexing(env)
