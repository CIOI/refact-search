from pytest import fixture
from src.search import SearchService


@fixture
def search_service():
    return SearchService()
