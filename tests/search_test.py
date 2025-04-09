from pytest import fixture
from typesense import Client
from src.config._environment import Environment


@fixture
def client():
    env = Environment()

    client = Client(
        {
            "api_key": env.typesense_api_key,
            "nodes": [
                {
                    "host": "localhost",  # For Typesense Cloud use xxx.a1.typesense.net
                    "port": "8108",  # For Typesense Cloud use 443
                    "protocol": "http",  # For Typesense Cloud use https
                }
            ],
            "connection_timeout_seconds": 2,
        }
    )
    return client


def test_search(client):
    search_parameters = {
        "q": "black",
        "query_by": "name",
        "sort_by": "product_id:desc",
    }
    results = client.collections["products"].documents.search(search_parameters)
    assert results["hits"] is not None
    for result in results["hits"]:
        print(result["document"]["serial_number"], result["document"]["name"])
        assert "black" in result["document"]["name"]
