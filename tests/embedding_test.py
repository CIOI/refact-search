from src.config._container import Application
from src.config.helpers._override import mock_overrides
import pytest
from src.embedding.clip import ClipEmbeddingModel


@pytest.fixture(scope="module")
def container():
    container = Application()
    mock_overrides(container)

    yield container


@pytest.fixture(scope="module")
def logger(container):
    return container.logger()


@pytest.fixture(scope="module")
def embedding_model(container) -> ClipEmbeddingModel:
    return container.embedding_model()


def test_embedding_model(embedding_model):
    assert embedding_model is not None


def test_model_load(embedding_model):
    embedding_model.model_load()
    assert embedding_model.model is not None


def test_get_text_embedding(embedding_model, logger):
    embedding = embedding_model.get_text_embedding(
        {
            "name": "Nike Air Max 270",
            "description": "Comfortable athletic shoes with air cushioning technology",
        }
    )
    print("embedding", embedding)
    assert embedding is not None
