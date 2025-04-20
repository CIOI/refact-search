from src.config._container import Application
from src.config.helpers._override import mock_overrides
import pytest


@pytest.fixture(scope="module")
def container():
    container = Application()
    mock_overrides(container)

    yield container


@pytest.fixture(scope="module")
def qdrant_manager(container):
    return container.managers.qdrant_manager()


def test_qdrant_manager(qdrant_manager):
    assert qdrant_manager is not None


@pytest.mark.asyncio
async def test_create_collection(qdrant_manager):
    await qdrant_manager.create_collection("test")
    assert await qdrant_manager.collection_exists("test")


@pytest.mark.asyncio
async def test_delete_collection(qdrant_manager):
    await qdrant_manager.delete_collection("test")
    assert not await qdrant_manager.collection_exists("test")
